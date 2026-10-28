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
   métricas do 073 prontas (aguardando reload); medidas mestras do 082 ainda são cópia do 081 (modelo).
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

Métricas do app (pasta `app/07_variaveis_de_metricas`): 071 controle, 072 operações, 073 eventos (radicais `vEven*`, `vApre*`, `vCapt*`),
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
- (2026-10-23) IPL único em `TEMP_DIM_CASOS` (teste no reload: nenhum duplicado): o 051 exclui `Proc. Tipo = 'NC'` e o 101 usa INNER JOIN. Os joins de unidade do caso são 1:1.
- (2026-10-23) O 052 já carrega `Data/Ano/Mês do Evento Prisão` na DIM_EVENTOS_PRISOES.
- (2026-10-27) **064**: LEFT JOIN com itens ePol restaurado (as métricas de operações voltam a responder a atributos de apreensão;
  custa ~84 mil linhas na link table).
- (2026-10-27) **`DIM_TNBIA` ligada ao modelo**: a chave era `%ITEM_SUBCLASSE_KEY` (nenhuma outra tabela do app tinha esse nome) e
  passou a ser `%SUBCLASSESKEY`, igual à link table, na origem (tra 0727) e no app 052. Antes, selecionar `GestãoBens Item Material`,
  `... Classe`, `... Categoria` ou `... Subclasse Código` não filtrava nenhuma métrica.
- (2026-10-27) **ePol filtrado por atributo de apreensão** (subclasse, material, classe, categoria, classe de descapitalização) funcionando
  pelo filtro na métrica (`P()` sobre `%CASOSKEY` + `vSemSelAtributosApreensao` gerada pela SUB `GerarListaSemSelecaoTabelas` no app 021;
  aplicado nos filtros base com data do app 076). Proposta: `artifacts/propostas/2026-10-24_FILTRO_EPOL_POR_APREENSAO_NA_METRICA.md`.
- (2026-10-28) **`[Evento em Unidade Diferente do Caso]`** ('Sim'/'Não'/'Sem caso') no `FATO_EVENTOS_OPERACIONAIS`: calculado no tra 068
  (`MAP_IPL_UNIDADE_SIGLA_DO_CASO`, mesma regra do `vCarregaUnidAreaDirCoorGeralDoCaso`, inclusive FICCO/GISE), carregado no app 032 e usado em
  `vFEvenPr10Exec` (app 073). Teste do filtro aprovado pelo desenvolvedor. Proposta: `artifacts/propostas/2026-10-27_FLAG_EVENTO_EM_UNIDADE_DIFERENTE_DO_CASO.md`.
- (2026-10-28) **073**: colisão com o 072 resolvida (os `CALL` de `vPris*EmOper`/`vBusc*EmOper` estão comentados); filtros sem `>` sobrando;
  SUBs `GerarMetricaSomaCompletaEvenApre` e `...EvenPris` definidas uma vez cada. Radicais próprios: `vEven*`, `vBaseApre`/`vApre*`, `vBaseCapt`/`vCapt*`.
  `vBaseCapt`/`vCapt*` deixaram de somar `nome_cpf_preso` e passaram a contar presos distintos (`GerarMetricaContagemCompletaEvenPris`,
  `Count(distinct nome_cpf_preso)`); a SUB `GerarMetricaContagemCompletaEvenApre` conta `distinct id_evento_apreensao`.
- (2026-10-24) `[Ano]` sem anos anteriores a 2022: Casos_Data filtrado no tra 039 e data nula para casos instaurados antes de 2022 no tra 066.
- (2026-10-23) Métricas do ePol (076) cortadas em 2022 (`vAnoMinimoEpol`); correção do `=` que faltava nas variantes de ano anterior.

**Ainda abertos:**
- **Volume da link table**: medido em 2026-10-23 com **2.419.461 linhas** (antes ~61 milhões; redução de ~96%).
  Por `[Tipo do Fato]`: Casos_Data 1.202.265 (~50%), Apreensões 619.277, Casos 363.389, Operações 101.243, eventos ~133 mil.
  Nenhuma linha com `Tipo do Fato` nulo.
- **067**: os dois LEFT JOINs com operações (SIGACrim e Palas) **ficam**; ambos funcionam (teste de 2026-10-24).
- **Filtros cruzados possivelmente quebrados** pelos joins retirados em `668c9e5`/alterações locais (061, 064, 065, 066, 068, 069, 0610):
  rodar a matriz de testes de `docs/link_table_relacionamentos.md` e restaurar só os joins que um filtro realmente usado exigir.
- **0610**: `Data` e `Tipo do Fato` vêm de LEFT JOIN com o evento (hoje todas as prisões casam; frágil se os filtros de ano divergirem).
- **082 (em reescrita)**: SUBs e `CALL` ainda com nomes e aliases do 081 — risco de sobrescrever as medidas mestras de operações (ver 7.1).
- `.gitignore`: a regra `*key*` ignora qualquer arquivo com "key" no nome (não só credenciais). `.pipeline-state.json` versionado por exceção
  (`!.pipeline-state.json`, commit `21cc1cc`).
- Rótulos "Externo/Estrangeiro" nos nomes das TEMP_LINK de 069/0610, embora incluam eventos PF.
- `StoreCsv` de tabelas com dados pessoais (032, 033, 034, 051) em pasta compartilhada — verificar PII.
- Os `000_MAIN.qvs` não têm `$(Include=...)`, então a ordem de carga real não está no repositório.
- Arquivo avulso `qlik/planilha resultados operacionais para MJ EM NÚMEROS.qvs` (teste) fora das camadas.
- Nomes fora do padrão: acento em `tra/07_dimensoes/074_..._RECUPERAÇÃO_...`, minúsculas em `0318_..._Mun_Faixa_de_Fronteira...`
  e `076_..._Palas_...`, espaço em `ext/05_casos_deduplicados/051 TEMP_TEMP_DIM_CASOS.qvs`, sufixo `_` em vários `07_dimensoes/07xx_..._.qvs`.
- `qtd_presos` se repete por unidade participante, com risco de inflar somas.

## 7.1 Ponto de retomada (atualizado em 2026-10-28)

**Próxima tarefa: medidas mestras dos eventos operacionais** (`app/08_variaveis_de_medidas_mestras/082_...`), a partir das
métricas do `app/07_variaveis_de_metricas/073_...`.

- O 082 está sendo reescrito a partir do 081 (commit `58563c2`, de ~19,6 mil para ~1,7 mil linhas, com SUBs). Situação em 2026-10-28:
  - já renomeadas: `GerarMedidasMestrasEventoOperacional6` (usa `$(vTemSelecaoDatasContextoFato)` e variantes `...DtMesAnoEven`) e
    `GerarTitulosERodapesEventosOperacionais`;
  - ainda com o **mesmo nome do 081**: `GerarMedidasSoPfKpi`, `GerarBlocoPorOperacaoHomologada`, `GerarBlocoPorOperacaoHomologadaApre`,
    `GerarBlocoCadastradas`. Se o 082 carregar depois do 081, essas SUBs são redefinidas;
  - os `CALL` ainda são os do 081 (`GerarMedidasMestrasDeflagracao6('OperacoesHomologadas', 'vOperHom')` etc.): **recriam as
    `vMedidaMestra*` de operações** e, se as SUBs redefinidas forem diferentes, sobrescrevem as medidas do 081. Trocar por aliases e
    radicais de eventos (`vEven*`, `vApre*`, `vCapt*`) e pelas SUBs renomeadas antes do reload que incluir o 082.
- O 073 está corrigido (colisão com o 072, `>` sobrando, SUBs, contagem de presos distintos por `nome_cpf_preso`). Ainda não passou por reload
  depois da última correção.
- Radicais do 073 a usar no 082: `vEvenBase`, `vEvenPf`/`Ext`/`Est` (+ `Exec`/`Info`/`Apoi`), `vEvenPr10Info`, `vEvenPr10Exec`;
  `vBaseApre`, `vApre*`; `vBaseCapt`, `vCapt*` (inclui `vCaptCGAP*`).
- `vEvenPr10Exec` = eventos PF de execução direta em unidade diferente da unidade do caso (`[Evento em Unidade Diferente do Caso] = {'Sim'}`).
- Datas dos eventos na link table: `Tipo da Data` = `'Evento Operacional'`, `'Evento Apreensão'`, `'Evento Prisão'`; campos próprios
  `[Ano do Evento ...]` nas dimensões 0715/0716/0717. Unidade: `unidade_participante` (`[Unidade Sigla do Evento Operacional]`).
- Avaliar se as métricas de eventos devem ter o corte de 2022 (como o 076) e o filtro por atributo de apreensão na métrica.

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
- 2026-10-23 — Distinguir **datas** de **filtros cruzados por atributo**: cada indicador conta pela sua própria data (sem "datas relacionadas"), mas um LEFT JOIN que leva a chave de outro fato é necessário quando as métricas de um fato precisam ser filtradas pelos atributos do outro. Na link table, a seleção só alcança as linhas que contêm a chave selecionada. Por isso o join do 067 (Casos_Data × operações SIGACrim) fica: sem ele, as métricas do ePol filtradas por operação (ex.: área de fronteira) zeram.
- 2026-10-23 — Manter o limite de ano no app 076 mesmo com Casos_Data filtrado no tra 039 — as variantes por instauração usam `[Ano da Instauração]` de casos antigos que continuam no modelo por atributos; o limite também protege contra mudanças futuras no tra.
- 2026-10-27 — Chaves com o mesmo conteúdo devem ter o mesmo nome em todas as camadas (ex.: `%SUBCLASSESKEY` na link table e na DIM_TNBIA) — nome diferente isola a tabela no app sem gerar erro.
- 2026-10-24 — Filtro cruzado de alto volume vai para a métrica, não para a link table: quando o LEFT JOIN multiplicaria demais as linhas (ex.: Casos_Data × itens ePol = +5,5 milhões), usar `P()` sobre a chave comum (caso) e anular as seleções do outro domínio no set analysis.
- 2026-10-27 — Comparação entre dois campos da mesma linha (ex.: unidade participante × unidade do caso) é calculada no tra e gravada como campo do fato (`[Evento em Unidade Diferente do Caso]` no 068, via `ApplyMap` por IPL) — o set analysis não compara campos linha a linha e as linhas de eventos da link table não têm a unidade do caso; o campo não acrescenta linhas à link table. Validado em 2026-10-28.
- 2026-10-28 — Métricas de prisões em eventos (`vBaseCapt`/`vCapt*`, app 073) contam presos distintos (`Count(distinct nome_cpf_preso)`) — `Sum(nome_cpf_preso)` somava um campo de texto. Contagens de apreensões em eventos usam `distinct id_evento_apreensao`.
- 2026-10-23 — Casos_Data carregado só a partir de 2022 (tra 039, `vAnoMinimoAnalise` no tra 021) — linhas anteriores não entram em nenhuma métrica.
