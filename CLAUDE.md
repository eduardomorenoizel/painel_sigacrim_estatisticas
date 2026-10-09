# CLAUDE.md — Painel SIGACrim Estatísticas Criminais

Memória persistente do projeto. Lida automaticamente pelo Claude Code em toda sessão.
**Idioma de trabalho: português brasileiro.**

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

## 2. Objetivos atuais (em ordem de prioridade)

1. **Enxugar a link table** (passou de 61 milhões de linhas e deixou o app lento): uma linha por linha de fato,
   só com as chaves e a data comuns, sem LEFT JOIN entre fatos. Diagnóstico em
   [docs/link_table_relacionamentos.md](docs/link_table_relacionamentos.md) (seção "Diagnóstico de volume").
2. **Concluir a modelagem dos eventos operacionais, dos eventos de apreensões e dos eventos de prisões**
   (fatos, dimensões, integração à link table, métricas e medidas mestras).
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
- `qlik/ext/` — extração das fontes → QVDs intermediários (`E2_*`). Aqui é criado o campo `IPL`
  (Caso no formato `AAAA.NNNNNNN`, pela variável `vTransformaProcIdentificacaoEmCaso`).
- `qlik/tra/` — transformação e **toda a modelagem dimensional** → `FATO_*`, `DIM_*` e a **link table**
  (`T3_*`). A `LINK_TABLE_APREENSOES_OPERACOES_CASOS` é montada nos scripts de `tra/06_fatos/` (061 cria,
  062 a 0610 concatenam) e gravada em `tra/07_dimensoes/0722_DIM_UNIDADE_SUBUNIDADE.qvs`. Otimização da link table se faz no tra.
- `qlik/app/` — só carrega o modelo (fatos 032, link table 042, dimensões 052) e define as métricas (07x)
  e medidas mestras (08x) como variáveis; section access.

Modelo: star schema com link table. Chaves de caso na link table: `%CASOSKEY` / `%PROC_IDENTIFICACAO_KEY`
= `AutoNumberHash128("IPL")`. Documentação em `docs/`:
- [docs/arquitetura_bi.md](docs/arquitetura_bi.md)
- [docs/modelo_dimensional.md](docs/modelo_dimensional.md)
- [docs/link_table_relacionamentos.md](docs/link_table_relacionamentos.md)
- [docs/dicionario_indicadores.md](docs/dicionario_indicadores.md)

## 5. Regras obrigatórias

Seguir **[padroes_qvs.md](padroes_qvs.md)** (fonte oficial). Destaques:
- Nomes de scripts `NNN_DESCRITIVO.qvs`, MAIÚSCULAS, português, sem acentos/espaços, sem versão no nome.
- Toda métrica e medida mestra em script (nada criado manualmente no front-end).
- Section access em script separado, ao final de cada camada.
- Nunca versionar dados (`.qvd`, `.csv`, `.xlsx`) nem credenciais.
- Commits semânticos (`feat:`, `fix:`, `refactor:`, `docs:`).
- Nunca usar sintaxe SQL em LOAD do Qlik (CASE WHEN, IS NULL, BETWEEN, IN, HAVING, aliases de tabela etc.).
- Não alterar os scripts de `qlik/` sem aprovação: as propostas são geradas em `artifacts/` e aplicadas após validação.

## 6. Como trabalhamos (Qlik Agents)

- Uso o plugin **Qlik Agents** em pipeline de fases (0 a 8). Estado oficial em **`.pipeline-state.json`** — sempre ler antes de continuar.
- Projeto brownfield: `inputs/` aponta para os scripts e docs existentes (não foram copiados — ver `inputs/README.md`).
- MCP do Qlik Cloud: não disponível (ambiente Qlik Sense Enterprise/Desktop). Validação de carga é feita por mim manualmente, e eu reporto os resultados.
- Para retomar: "Continue o pipeline do SIGACrim".

## 7. Problemas conhecidos (levantados em 2026-09-30, revistos em 2026-10-09)

Resolvidos no código atual (2026-10-09): não há mais arquivos `_ATUAL_FUNCIONANDO` nem `Untitled-1.js`;
o 037 foi renomeado para `037_TEMP_PALAS_OPERACOES_TRATADAS_2022_2023.qvs`; eventos de apreensões e de
prisões foram renomeados para `*_UNIFICADOS` / `FATO_EVENTOS_APREENSOES` / `FATO_EVENTOS_PRISOES`;
as chaves de caso passaram de `"Proc. Identificação"` para `IPL`.

Ainda abertos:
- **Link table com ~61 milhões de linhas** por LEFT JOINs entre fatos (fan-out). Principais: 066 (casos ×
  operações × itens × Casos_Data), 067, 064 (6 LEFT JOINs, incluindo os novos de eventos-apreensões e
  eventos-prisões), 061 (itens × Casos_Data do caso) e 068 (evento × itens × eventos-apreensões × eventos-prisões).
- O 068 ainda faz LEFT JOIN com `vCarregaUnidAreaDirCoorGeralDoCaso` (contraria a decisão de 2026-10-09 de usar
  só a unidade do evento) e, como os dois lados têm `%UNIDADE_KEY`, o join casa por caso **e** unidade.
- `TEMP_DIM_CASOS` (ext 111) pode ter mais de uma linha por `IPL` (o LEFT JOIN com `TEMP_TEMP_DIM_CASOS` traz
  todos os `Proc. Identificação` do mesmo ano.número, sem filtro): DIM_CASOS sem chave única e joins de unidade
  do caso que duplicam linhas. A confirmar no reload.
- Rótulos "Externo/Estrangeiro" (Tipo do Fato, Tipo da Data, campos de unidade, nomes de TEMP_LINK) continuam,
  embora 069/0610 agora incluam também eventos PF.
- Nomes fora do padrão: acento em `074_..._RECUPERAÇÃO_...`, minúsculas em `0318_..._Mun_Faixa_de_Fronteira...`, `076_..._Palas_...`, espaço em `ext/05_casos_deduplicados/051 TEMP_TEMP_DIM_CASOS.qvs`.
- README e padroes_qvs.md divergem das pastas reais (ex.: `05_temp_casos` vs `05_casos_deduplicados`, `09_apreensoes` vs `09_apreensoes_deduplicadas`).

Achados da Fase 0 (detalhes em `artifacts/00-platform-context.md`):
- Os `000_MAIN.qvs` não têm `$(Include=...)`, então a ordem de carga real não está no repositório.
- As métricas 073 e as medidas 082 de eventos são modelos copiados de operações, ainda não usados. Ainda não há métricas de prisões nem de apreensões de eventos.
- `qtd_presos` se repete por unidade participante, com risco de inflar somas.

## 8. Decisões tomadas

Registrar aqui toda decisão relevante (data — decisão — motivo).

- 2026-09-30 — Usar o pipeline Qlik Agents com CLAUDE.md como memória do projeto — evitar repetir contexto entre sessões.
- 2026-09-30 — `inputs/` referencia os arquivos existentes em vez de copiá-los — evitar duplicação e divergência.
- 2026-10-09 — A arquitetura de 3 apps (ext extrai; tra transforma e faz toda a modelagem, inclusive a link table; app só carrega o modelo e define métricas e medidas mestras em variáveis) é intencional — a otimização da link table é feita no tra.
- 2026-10-09 — Manter só datas comuns na link table e abandonar as "datas específicas relacionadas" (ex.: apreensões das operações deflagradas no período) — a link table passou de 61 milhões de linhas e o app ficou lento; cada indicador conta de forma independente por período.
- 2026-10-09 — Correlações na link table pelo Caso (IPL) no formato `AAAA.NNNNNNN`, não pelo `Proc. Identificação` — o tipo do procedimento (IPL/FLA/TC/RE) muda durante a tramitação; a DIM_CASOS mantém o `Proc. Identificação` atual.
- 2026-10-09 — Unidade comum: unidade do caso para ePol e SIGACrim (a unidade da operação é sempre a do caso); Palas usa a `UNIDADE` da operação; eventos PF, externos e estrangeiros usam só a unidade do evento (unidade participante) — regra única por fonte.
- 2026-10-09 — Métricas 073 e medidas mestras 082 de eventos são modelos copiados de operações, ainda não usados — não são erro; as métricas de eventos ainda serão escritas.
