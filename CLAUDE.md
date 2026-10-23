# CLAUDE.md — Painel SIGACrim Estatísticas Criminais

Memória persistente do projeto. Lida automaticamente pelo Claude Code em toda sessão.
**Idioma de trabalho: português brasileiro.**

Última revisão completa do repositório: **2026-10-23** (arquivos como estavam no disco, inclusive alterações ainda sem commit).

## 1. Contexto

Aplicativo de BI em Qlik Sense do NGE/COP/DICOR da Polícia Federal. Integra, num único painel,
dados de vários outros painéis/fontes para atender às demandas de gestão estratégica das
Diretorias, das Unidades Regionais (SR) e das Descentralizadas.

Domínios integrados:
- Operações (SIGACrim Homologadas, Palas Operações Tratadas 2022–2023)
- Eventos operacionais (TabelaoEventos)
- Apreensões, incluindo valores de descapitalização (ePol DIM_CASOS_APREENSAO_BENS, SIGACrim, Palas, CGPRE drogas/armas/munições)
- Prisões (Eventos_Prisoes)
- Procedimentos investigativos (ePol DIM_CASOS, DIM_CASOS_DATA, DIM_CASOS_TIPO_PENAL)
- Unidades (DIM_UNIDADE, hierarquia técnica, circunscrição, municípios/UF, faixa de fronteira)
- Efetivo de servidores (DIM_SERVIDOR_ATIVO — sem terceirizados e estagiários)

Recorte temporal: as análises valem **a partir de 2022**. IPLs (casos) anteriores a 2022 entram no modelo
só para dar atributos (unidade, data de instauração etc.) a apreensões, operações e eventos de 2022 em diante;
não entram em nenhuma métrica com data.

## 2. Objetivos atuais (em ordem de prioridade)

1. **Enxugar a link table** (chegou a 61 milhões de linhas e deixou o app lento): uma linha por linha de fato,
   só com as chaves e a data comuns, sem LEFT JOIN entre fatos. **Em andamento**: a maior parte dos joins já saiu
   (commit `668c9e5` e alterações locais) e a link table caiu para **2.505.344 linhas** (2026-10-23); faltam 064 e 067. Detalhes em
   [docs/link_table_relacionamentos.md](docs/link_table_relacionamentos.md) ("Diagnóstico de volume" e "Próximos passos").
2. **Concluir a modelagem dos eventos operacionais, dos eventos de apreensões e dos eventos de prisões**
   (fatos, dimensões, integração à link table, métricas e medidas mestras). Fatos e dimensões prontos;
   métricas do 073 em construção; medidas mestras do 082 ainda são cópia do 081 (modelo).
3. Refatorar o repositório (limpeza de duplicados, padronização de nomes, organização das camadas).
4. Outras melhorias de desempenho, qualidade de dados e usabilidade.

## 3. Tipos de página do app (requisito de UX)

- **Painéis** — comparações históricas, visualizações rápidas, informações essenciais, leitura rápida.
- **Análises** — comparações por UF, SR, Descentralizadas, Bases e Efetivos; exploração em profundidade;
  insights; responder ao "por quê"; filtros e detalhamentos.
- **Relatórios** — maior granularidade, informações granulares, exportação, interação com detalhes de tabelas e linhas.

## 4. Arquitetura existente (resumo)

Três apps encadeados por QVDs (ext → tra → app). Essa separação é **intencional**. Cada camada tem
`00_orquestracao/000_MAIN.qvs` como ponto de entrada:
- `qlik/ext/` — extração das fontes → QVDs intermediários. Aqui é criado o campo `IPL`
  (Caso no formato `AAAA.NNNNNNN`, pela variável `vTransformaProcIdentificacaoEmCaso`).
  Casos: `05_casos_deduplicados/051` (deduplica a DIM_CASOS por `Proc. Identificação` com `LastValue`, **sem `Proc. Tipo = 'NC'`**)
  e `10_casos/101_TEMP_DIM_CASOS` (carrega só os IPLs usados pelas outras fontes + relatados a partir de 2022 + em andamento,
  sem migrados do Sinpro, com INNER JOIN). Casos_Data em `11_casos_data/111`.
- `qlik/tra/` — transformação e **toda a modelagem dimensional** → `FATO_*`, `DIM_*` e a **link table**.
  A `LINK_TABLE_APREENSOES_OPERACOES_CASOS` é montada nos scripts de `tra/06_fatos/` (061 cria, 062 a 0610 concatenam)
  e gravada em `tra/07_dimensoes/0722_DIM_UNIDADE_SUBUNIDADE.qvs`. Otimização da link table se faz no tra.
- `qlik/app/` — só carrega o modelo (fatos 032, link table 042, dimensões 052) e define as métricas (07x)
  e medidas mestras (08x) como variáveis; section access.

Modelo: star schema com link table. Chaves de caso na link table: `%CASOSKEY` / `%PROC_IDENTIFICACAO_KEY`
= `AutoNumberHash128("IPL")`. Documentação em `docs/`:
- [docs/arquitetura_bi.md](docs/arquitetura_bi.md)
- [docs/modelo_dimensional.md](docs/modelo_dimensional.md)
- [docs/link_table_relacionamentos.md](docs/link_table_relacionamentos.md)
- [docs/dicionario_indicadores.md](docs/dicionario_indicadores.md)

Métricas do app (pasta `app/07_variaveis_de_metricas`): 071 controle, 072 operações, 073 eventos (em construção),
074 apreensões, 075 drogas/armas/munições, 076 ePol. Medidas mestras (pasta `app/08_...`): 081 operações,
082 eventos (cópia do 081 usada como modelo), 083 apreensões, 084 drogas/armas/munições, 085 ePol, 086 efetivo.

## 5. Regras obrigatórias

Seguir **[padroes_qvs.md](padroes_qvs.md)** (fonte oficial). Destaques:
- Nomes de scripts `NNN_DESCRITIVO.qvs`, MAIÚSCULAS, português, sem acentos/espaços, sem versão no nome.
- Toda métrica e medida mestra em script (nada criado manualmente no front-end).
- Section access em script separado, ao final de cada camada.
- Nunca versionar dados (`.qvd`, `.csv`, `.xlsx`) nem credenciais.
- Commits semânticos (`feat:`, `fix:`, `refactor:`, `docs:`).
- Nunca usar sintaxe SQL em LOAD do Qlik (CASE WHEN, IS NULL, BETWEEN, IN, HAVING, aliases de tabela etc.).
- Não alterar os scripts de `qlik/` sem aprovação: as propostas são geradas em `artifacts/propostas/` e aplicadas após validação.

## 6. Como trabalhamos

- **Este repositório é a fonte da verdade.** Decisões tomadas em qualquer canal (Claude Code no VS Code ou no
  Claude Desktop, chat do Claude.ai, Cowork) devem ser registradas aqui (seção 8) e nos `docs/`; as conversas
  desses canais não ficam salvas no repositório.
- Uso o plugin **Qlik Agents** em pipeline de fases (0 a 8). Estado oficial em **`.pipeline-state.json`** — sempre ler antes de continuar.
  Na prática, desde 2026-10-09 o trabalho tem sido feito em tarefas pontuais fora do pipeline (registradas em `workLog` no `.pipeline-state.json`).
- Projeto brownfield: `inputs/` aponta para os scripts e docs existentes (não foram copiados — ver `inputs/README.md`).
- MCP do Qlik Cloud: não disponível (ambiente Qlik Sense Enterprise/Desktop). Validação de carga é feita por mim manualmente, e eu reporto os resultados.
- Commitar com frequência: há muitas alterações locais sem commit; sem commit, outra sessão (ou outro canal) não consegue saber o que mudou.
- Para retomar: "Continue o pipeline do SIGACrim" ou descrever a tarefa pontual.

## 7. Problemas conhecidos (revistos em 2026-10-23)

**Resolvidos no código atual:**
- (2026-10-09) não há mais arquivos `_ATUAL_FUNCIONANDO` nem `Untitled-1.js`; 037 renomeado; eventos de apreensões e prisões
  renomeados para `*_UNIFICADOS` / `FATO_EVENTOS_*`; chaves de caso passaram para `IPL`.
- (2026-10-23) LEFT JOINs entre fatos retirados de 061, 064 (Casos_Data e eventos), 065, 066, 068, 069 e 0610.
- (2026-10-23) O 068 não faz mais LEFT JOIN com a unidade do caso: eventos usam só a unidade participante.
- (2026-10-23) Duplicidade de IPL muito reduzida: o 051 exclui `Proc. Tipo = 'NC'` e o 101 usa INNER JOIN.
- (2026-10-23) O 052 já carrega `Data/Ano/Mês do Evento Prisão` na DIM_EVENTOS_PRISOES.
- (2026-10-23) Métricas do ePol (076) cortadas em 2022 (`vAnoMinimoEpol`); correção do `=` que faltava nas variantes de ano anterior.

**Ainda abertos:**
- **Volume da link table**: medido em 2026-10-23 com **2.505.344 linhas** (antes ~61 milhões; redução de ~96%).
  Ainda falta a distribuição por `[Tipo do Fato]` para saber o peso dos joins restantes (064, 067).
- **064**: LEFT JOIN com itens ePol por caso + operação (cada operação × itens). Redundante com o 061.
- **067**: LEFT JOIN com operações SIGACrim por caso (cada linha de Casos_Data × operações do caso) — provavelmente o maior
  fan-out restante; e o LEFT JOIN com operações Palas, que na prática não liga nada (casa por `%CASOSKEY` + `%OPERACOESKEY`).
- **Anos anteriores a 2022 em `[Ano]`**: vêm das linhas do 066 (instauração) e do 067 (Casos_Data) dos IPLs antigos.
  `Min([Ano])` nos títulos do 085 mostra esses anos. Proposta: anular/filtrar as datas < 2022 nesses blocos (ver docs).
- **IPL único em `TEMP_DIM_CASOS`** ainda não confirmado (migrados fora do padrão; 83 casos listados no 051). Teste no docs.
- **0610**: `Data` e `Tipo do Fato` vêm de LEFT JOIN com o evento; prisões sem evento correspondente ficam fora das métricas.
- **073 (métricas de eventos, em construção)**:
  - cria `vPrisCumprEmOper`, `vPrisExpedEmOper`, `vPrisPrevCumprEmOper`, `vPrisPrevExpedEmOper`, `vPrisTempCumprEmOper`,
    que **já existem no 072** (operações). Como o 073 carrega depois, ele sobrescreve as métricas de operações usadas pelo 081;
  - filtros `vFAprePf`, `vFApreExt`, `vFApreEst`, `vFCaptPf`, `vFCaptExt`, `vFCaptEst`, `vFCaptCGAP` terminam com `>` sobrando
    (o `{< ... >}` final fica com `> >`);
  - `CALL GerarMetricaSomaCompletaEvenApre` sem a SUB definida; a SUB `GerarMetricaSomaCompletaEvenPris` está definida duas vezes
    (a segunda provavelmente deveria ser a `...EvenApre`);
  - `Sum(nome_cpf_preso)` soma um campo de texto; para contar presos, usar contagem distinta.
- Rótulos "Externo/Estrangeiro" nos nomes das TEMP_LINK de 069/0610, embora incluam eventos PF.
- `StoreCsv` de tabelas com dados pessoais (032, 033, 034, 051) em pasta compartilhada — verificar PII.
- Os `000_MAIN.qvs` não têm `$(Include=...)`, então a ordem de carga real não está no repositório.
- Arquivo avulso `qlik/planilha resultados operacionais para MJ EM NÚMEROS.qvs` (teste) fora das camadas.
- Nomes fora do padrão: acento em `tra/07_dimensoes/074_..._RECUPERAÇÃO_...`, minúsculas em `0318_..._Mun_Faixa_de_Fronteira...`
  e `076_..._Palas_...`, espaço em `ext/05_casos_deduplicados/051 TEMP_TEMP_DIM_CASOS.qvs`, sufixo `_` em vários `07_dimensoes/07xx_..._.qvs`.
- `qtd_presos` se repete por unidade participante, com risco de inflar somas.

## 8. Decisões tomadas

Registrar aqui toda decisão relevante (data — decisão — motivo).

- 2026-09-30 — Usar o pipeline Qlik Agents com CLAUDE.md como memória do projeto — evitar repetir contexto entre sessões.
- 2026-09-30 — `inputs/` referencia os arquivos existentes em vez de copiá-los — evitar duplicação e divergência.
- 2026-10-09 — A arquitetura de 3 apps (ext extrai; tra transforma e faz toda a modelagem, inclusive a link table; app só carrega o modelo e define métricas e medidas mestras em variáveis) é intencional — a otimização da link table é feita no tra.
- 2026-10-09 — Manter só datas comuns na link table e abandonar as "datas específicas relacionadas" (ex.: apreensões das operações deflagradas no período) — a link table passou de 61 milhões de linhas e o app ficou lento; cada indicador conta de forma independente por período.
- 2026-10-09 — Correlações na link table pelo Caso (IPL) no formato `AAAA.NNNNNNN`, não pelo `Proc. Identificação` — o tipo do procedimento (IPL/FLA/TC/RE) muda durante a tramitação; a DIM_CASOS mantém o `Proc. Identificação` atual.
- 2026-10-09 — Unidade comum: unidade do caso para ePol e SIGACrim (a unidade da operação é sempre a do caso); Palas usa a `UNIDADE` da operação; eventos PF, externos e estrangeiros usam só a unidade do evento (unidade participante) — regra única por fonte.
- 2026-10-09 — Métricas 073 e medidas mestras 082 de eventos partem de modelos copiados de operações — não são erro; as métricas de eventos estão sendo escritas.
- 2026-10-14 — Cada bloco da link table leva só as chaves do próprio fato, sem LEFT JOIN com outros fatos (commit `668c9e5`) — eliminar o fan-out.
- 2026-10-15 — Excluir `Proc. Tipo = 'NC'` na deduplicação da DIM_CASOS (ext 051) e carregar a TEMP_DIM_CASOS com INNER JOIN (ext 101) — os NC originais não são apagados quando viram IPL e duplicariam o Caso (IPL).
- 2026-10-20 — Métricas do ePol (076) com data só mostram anos >= 2022 (variável `vAnoMinimoEpol`, com interseção `*=` com a seleção do usuário); métricas "Em Andamento" ficam sem esse corte — elas não têm histórico de datas e se referem à data da carga. Aplicado no `qlik/app/07_variaveis_de_metricas/076_...` em 2026-10-20.
- 2026-10-23 — IPLs anteriores a 2022 ficam no modelo só para dar atributos às investigações de apreensões, operações e eventos a partir de 2022; não entram em métricas. Anos < 2022 não são selecionáveis no app.
- 2026-10-23 — `app/08_.../082_VARIAVEIS_DE_MEDIDAS_MESTRAS_DE_EVENTOS_OPERACIONAIS.qvs` é cópia do 081 usada como modelo para as medidas mestras dos eventos — não é erro.
