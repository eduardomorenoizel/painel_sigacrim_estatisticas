# Dicionário de Indicadores — Estatísticas Criminais DICOR

Como as métricas e medidas mestras estão organizadas no script (`qlik/app/07_*` e `08_*`). Estado do repositório em
2026-10-08. Este documento descreve a estrutura e os filtros-base; a lista completa de variáveis está nos próprios scripts.

---

## 1. Organização

| Camada | Arquivo | Tema | Filtro-base (`[Tipo do Fato]`) |
|---|---|---|---|
| métricas | `071_VARIAVEIS_DE_METRICAS_DE_CONTROLE` | conjuntos de datas, "PF em Números", controles | — |
| métricas | `072_VARIAVEIS_DE_METRICAS_OPERACIONAIS` | operações | `'Operações'` (+ `ETAPAOPERACAO = 'Homologada'`) |
| métricas | `073_VARIAVEIS_DE_METRICAS_DE_EVENTOS_OPERACIONAIS` | eventos | **ainda `'Operações'`** (clone de 072) |
| métricas | `074_VARIAVEIS_DE_METRICAS_DE_APREENSOES` | apreensões e descapitalização | `'Apreensões'` |
| métricas | `075_..._DROGAS_E_ARMAS_E_MUNICOES` | drogas, armas, munições | `'Apreensões'` |
| métricas | `076_VARIAVEIS_DE_METRICAS_DO_EPOL` | casos e procedimentos | `'Casos_Data'` (+ `[Tipo da Data] = 'Evento do Caso'`) |
| medidas | `081` a `085` | medidas mestras dos mesmos temas | — |
| medidas | `086_VARIAVEIS_DE_MEDIDAS_MESTRAS_DE_EFETIVO` | efetivo | limpa campos de data, caso, operação e item (`vConjSemRelDatasAreaCasoOperacaoBem`, `app/023`) |

Sub-rotinas genéricas de criação de variáveis: `app/02_.../021_SUBROTINAS.qvs` (`CriarVariavelContagem`,
`CriarVariavelSoma`, `CriarVariavelRelativa`, versões `Anteriores`, `Reais`, `Mi`, `Bi`, `Percentual` etc.).
Sub-rotinas de geração em lote ficam dentro de cada arquivo de métricas (`GerarConjunto12Defl`, `GerarConjunto12Apre`,
`GerarConjunto12ProcData`, `GerarMetricaSomaCompleta`, `GerarPorEfet6` etc.) e de medidas (`GerarMedidasMestrasDeflagracao6`,
`GerarMedidasApreTotSomAnter`, `GerarMedidasMestrasEpolProcData6` etc.).

## 2. Variantes geradas por métrica

As sub-rotinas `GerarConjunto12*` produzem 12 conjuntos para cada métrica:

| Eixo | Valores |
|---|---|
| Data | data comum (`[Tipo da Data]` do próprio fato + `Data`/`Ano`/`Mês`) ou data específica (ex.: `Ano da Deflagração`) |
| Escopo | todas as unidades ou "PF em Números" (`vConjOpDtMesAnoPfEmNumeros`) |
| Período | seleção atual, ano atual, ano anterior |

As medidas mestras escolhem a variante conforme o que o usuário selecionou (`vTemSelecaoDatasContextoFato`,
`vTemSelecaoDatasCalendario`, `vTemSelecaoAnoDeflagracao` em 081, 083, 084) e geram formatos `Tot` (para gráficos por
data), sem `Tot` (por unidade ou local), `SomAnter` (acumulado/Pareto), `Kpi*` e `PorEfet` (por servidor).

Com a decisão de 2026-10-08 (só datas comuns), as 6 variantes de data específica podem ser removidas. Ver
[../artifacts/03-plano-otimizacao-link-table.md](../artifacts/03-plano-otimizacao-link-table.md), Etapa D.

## 3. Filtros-base por tema (exemplos reais)

**Operações (072):**
- `vFBase`: `ETAPAOPERACAO = {'Homologada'}, [Tipo do Fato] = {'Operações'}`
- `vFFront`: + `AREA_FRONTEIRA = {"SIM"}`
- `vFMaj`: + `MAJORANTE_OPERACAO_PJ = {'Sim'}`
- `vFRecAtiv`: + `[Tem Sequestro] = {'SIM'}`
- `vFRelatDefl`: + `[Foi relatada após deflagrada] = {'Sim'}`

**Apreensões (074, 075):**
- `vFApreBase`: `[Tipo do Fato] = {'Apreensões'}`
- `vFApreDesvio`: + `[Área de Atribuição do Caso] = {'Desvio de Recursos Públicos'}` (usa coluna da link)
- `vFApreFront`: + `AREA_FRONTEIRA = {"SIM"}`
- armas por espécie: `[GestãoBens Item Arma Espécie CGPRE] = {'Pistola'}` etc.
- valores somados: colunas de `FATO_APREENSOES` (`Valor Total Descapitalização`, `1 ... LVL1` a `6 ... LVL1`,
  `1.1 ... LVL2` a `5.2 ... LVL2`, `1+2+3+5.2 Sequestros e bloqueios ...`) e quantidades normalizadas
  (`Item Quantidade Apreendida Cocaína (kg)`, `... Maconha (kg)`, `... Armas (un)`, `... Munições (un)` etc.)

**ePol (076):**
- `vFCasosData`: `[Tipo do Fato] = {'Casos_Data'}`
- `vFPrisEmFlagr`: + `[Proc_Data Tipo] = {'Prisão Flagrante'}` (e variantes interna/externa)
- `vFFlaInstBase`: + `[Foi Instaurado por Flagrante] = {'Sim'}`, contando `[Proc_Data Flagrante Instaurado ID]`
- `vFTcoInst`, `vFReRecAtiv`, `vFDurMedIplRelat` etc.
- Métricas "em andamento" (`vFIplEmAndSemRel`, `vFIplEmAndVazio`) não filtram `Tipo do Fato` e limpam as datas.

## 4. Lacunas conhecidas

- **Eventos (073/082):** são clones das métricas de operações e filtram `'Operações'`. Faltam métricas sobre
  `FATO_EVENTOS_OPERACIONAIS`, `FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` e `FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO`.
- **Grão dos eventos:** `qtd_presos`, `houve_prisao` e `houve_apreensao` repetem em cada unidade participante; somar sem a
  dimensão de unidade conta o mesmo evento mais de uma vez.
- **Possível dupla contagem de apreensões:** apreensões de eventos PF podem estar no ePol (`FATO_APREENSOES`, vinculadas em
  `tra/05/051`) e também no fato de apreensões de eventos. Definir a regra antes de escrever as métricas.
