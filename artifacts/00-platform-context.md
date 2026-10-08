# Contexto da plataforma — Painel SIGACrim Estatísticas Criminais

**Data:** 2026-10-08 (refeito do zero; substitui a versão de 2026-09-30)
**Base:** leitura de todo o repositório no commit `a4325df` (ext 31, tra 66, app 30 scripts `.qvs`).
**Ambiente:** Qlik Sense Enterprise/Desktop, sem MCP do Qlik Cloud. Nenhuma afirmação aqui foi validada por recarga; o que
depende de dados está marcado como inferência.

---

## 1. Visão geral

| Camada | Scripts | Entrada | Saída |
|---|---|---|---|
| `qlik/ext` | 31 | fontes `lib://` (QVDs corporativos e planilhas) | `E2_TEMP_*.qvd` |
| `qlik/tra` | 66 | `E2_TEMP_*.qvd`, planilhas de apoio | `T3_FATO_*.qvd`, `T3_DIM_*.qvd`, `T3_LINK_TABLE_APREENSOES_OPERACOES_CASOS.qvd`, CSVs de auditoria |
| `qlik/app` | 30 | `T3_*.qvd` | modelo + variáveis de métricas e medidas mestras geradas por sub-rotinas |

Fora das camadas: `qlik/planilha resultados operacionais para MJ EM NÚMEROS.qvs` (script de teste para gerar a planilha "MJ em
Números", commit `728f9d0`).

Os três `000_MAIN.qvs` só definem variáveis de locale; não há `$(Include=...)`. A ordem real de execução está no editor do
Qlik e não pode ser confirmada pelo repositório.

## 2. Linhagem por domínio

| Domínio | Fonte | ext | tra (carga → ajuste → fato → dimensão) | app |
|---|---|---|---|---|
| Operações SIGACrim | `CORP_DICOR_COP/SIGACrim.qvd` | 081 | 036 → 054 → 064 → 071, 072, 075 | `FATO_OPERACOES`, `DIM_OPERACOES` + atributos |
| Operações Palas 2022–2023 | `MD_SIGACRIM/Palas_Operacoes_Tratadas_2022_2023.qvd` | 082 | 037 → 065 → 073, 076 | idem |
| Eventos | `CORP_DICOR_COP/TabelaoEventos.qvd` | 071 | 032 (deduplicação, `id_ordem_original_evento`) → 068 → 0715 | `FATO_EVENTOS_OPERACIONAIS`, `DIM_EVENTOS_OPERACIONAIS` |
| Apreensões de eventos | `Eventos_Apreensoes.qvd` | 073 | 032, 033 → 051 → 069 → 0716 | `FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` + dim |
| Prisões de eventos | `Eventos_Prisoes.qvd` | 072 | 032, 034 → 0610 → 0717 | `FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` + dim |
| Apreensões ePol | `MD_EPOL/DIM_CASOS_APREENSAO_BENS.qvd` | 091 (dedup.) | 038 (+ CGPRE) → 051, 052, 053 → 061 → 077 | `FATO_APREENSOES`, `DIM_APREENSOES` |
| Apreensões SIGACrim 2024 | `SIGACrim.qvd` | 081 | 036 → 062 → 078 | `FATO_APREENSOES` |
| Apreensões Palas | Palas | 082 | 037 → 063 → 079 | `FATO_APREENSOES` |
| Drogas, armas, munições | planilhas CGPRE | 041 | 035 → 038 | dentro de `FATO_APREENSOES` |
| Casos | `MD_EPOL/DIM_CASOS.qvd` | 051 (dedup.), 111 | 0310 → 066 → 0710, 0711, 0713 | `FATO_CASOS`, `DIM_CASOS` |
| Casos_Data | `MD_EPOL/DIM_CASOS_DATA.qvd` | 101 | 039 → 067 → 0714 | `FATO_CASOS_DATA`, `DIM_CASOS_DATA` |
| Tipo penal | `CORP_DADOS_AUXILIARES/DIM_CASOS_TIPO_PENAL.qvd` | 121 | 0311 → 0712 | `DIM_CASOS_TIPO_PENAL` |
| Unidades | `DIM_UNIDADE`, `HIERARQUIA_TECNICA_PF_v8.xlsx`, `DIM_CIRCUNSCRICAO_PF`, municípios, UF, fronteira | 141 a 146 | 0313 a 0318 → 0719 a 0726 | `DIM_UNIDADE` e afins |
| Efetivo | `DIM_SERVIDOR_ATIVO` | 131 | 0312 → 0718 | `DIM_SERVIDOR_ATIVO` |
| Taxonomia | TNBIA (derivada do ePol) | 031 | 031 → 0727 | `DIM_TNBIA` |

## 3. Lógicas de negócio relevantes na `tra`

- **Deduplicação de eventos (032):** um evento pode ser registrado várias vezes por unidades diferentes e ter várias
  participações. Os eventos são unificados por tipo (PF: IPL + data; externo: data + força/UF + município; estrangeiro:
  país + data), priorizando presos em comum, depois apreensões em comum, depois a carga mais recente. A participação de cada
  unidade é deduplicada pela prioridade execução direta > informação > apoio. Resultado: `TEMP_TABELAOEVENTOS_ID_UNIFICADO`,
  uma linha por participação (`id_ordem_original_evento`).
- **Unidade das apreensões e prisões de eventos (033, 034):** cada `id_evento` é atribuído a uma única unidade participante
  (a de maior prioridade, desempate pelo menor `id_ordem_original_evento`). Nomes e CPFs de presos são anonimizados.
- **Evento do item ePol (051):** matching hierárquico entre apreensão de evento PF e item do ePol por caso + subclasse,
  depois menor diferença de quantidade, de data e menor `GestãoBens Item ID`, garantindo 1:1.
- **Operação do item ePol (052, 053):** 1º a operação do evento vinculado; 2º a operação cujo intervalo de deflagração
  (por IPL ou por RE_SEQUESTRO) contém a data da apreensão; 3º nula.
- **Unidade do caso (`vCarregaUnidAreaDirCoorGeralDoCaso`, tra/02/021):** usa a unidade FICCO/GISE do Argos quando
  existir (`MapIPLUnidadeFiccoGise`), senão `Proc. Unidade Exercício`. Área vazia, `-` ou "Não identificado" vira "Tráfico de
  drogas" / DICOR / CGPRE.
- **Descapitalização (061):** valores LVL1/LVL2 por regras de ano (2024 usa a lista ePol de 31/03/2025; 2025 em diante usa
  vínculo e destinação), excluindo procedimentos migrados do SINPRO.

## 4. Modelo no app

Ver `docs/modelo_dimensional.md` e `docs/link_table_relacionamentos.md`. Resumo:
- 7 fatos, 1 link table de 39 colunas (~12 milhões de linhas), ~40 dimensões.
- Toda métrica filtra `[Tipo do Fato]`.
- Dimensões ligadas por chaves `%..._KEY` com o mesmo valor das chaves de fato (pares duplicados).

## 5. Achados (verificados no código)

| # | Severidade | Onde | Achado |
|---|---|---|---|
| 1 | Crítico (desempenho) | `tra/06/061` a `068` | `LEFT JOIN` 1:N entre fatos na montagem da link table multiplicam linhas (itens × Proc_Data × operações × participações). Plano em `03-plano-otimizacao-link-table.md` |
| 2 | Alto | `tra/03/033`, `034` x `068`, `069`, `0610`, `0716`, `0717` | Nomes de tabela divergentes (`..._PF_EXTERNAS_ESTRANGEIRO` x `..._EXTERNAS_ESTRANGEIRO`); no repositório, nada cria o segundo nome. A confirmar com o app real |
| 3 | Alto | `app/073`, `082` | Métricas de eventos são clones das de operações; não há métricas de prisões nem de apreensões de eventos |
| 4 | Médio | `tra/06/068` | Join com `TEMP_DIM_CASOS` por duas chaves (`%PROC_IDENTIFICACAO_KEY` e `%UNIDADE_KEY`): atributos "do Caso" só preenchidos quando a unidade do caso é a participante |
| 5 | Médio | `FATO_EVENTOS_OPERACIONAIS` | `qtd_presos`, `houve_prisao`, `houve_apreensao` no grão de participação; somas sem unidade contam o evento várias vezes |
| 6 | Médio | `tra/03/033` + `tra/05/051` | Apreensões de eventos PF podem existir no ePol e no fato de eventos; risco de dupla contagem quando houver métricas |
| 7 | Médio | `tra/06` | Chaves `AutoNumberHash128` gravadas em QVD: só valem dentro da mesma execução da `tra` |
| 8 | Médio | `app/032`, `042`, `052` | `LOAD DISTINCT` em todas as cargas de QVD, inclusive a link table |
| 9 | Médio | `tra/07/0721` | Hierarquia da unidade montada lendo a link inteira; cobre só siglas de unidade de caso |
| 10 | Baixo | `000_MAIN.qvs` (3) | Sem `$(Include=...)` |
| 11 | Baixo | nomes | `037_..._2032_2033`; acento em `074_..._RECUPERAÇÃO_...`; minúsculas em `ext/146`, `tra/0318`, `tra/076`; espaço em `ext/05/051 TEMP_TEMP_DIM_CASOS.qvs`; `_` final em `0710`, `0712`, `0713`, `0714`, `077`, `078`, `079`; script de teste solto em `qlik/` |
| 12 | Baixo | `tra/02/021`, `ext/02/021` | Variáveis de caminho antigas (`T_`, `T2_`, `E_`) ainda definidas; o fluxo atual usa `E2_` e `T3_` |

Resolvidos desde 2026-09-30: arquivos `_ATUAL_FUNCIONANDO` e `Untitled-1.js` foram removidos; a modelagem de prisões e
apreensões de eventos foi concluída.

## 6. Sub-rotinas e variáveis compartilhadas

| Onde | Itens |
|---|---|
| `ext/02/022`, `tra/02/022` | `StoreCsv`, `StoreAndDropCsv`, `Store`, `StoreAndDrop` (grava em `pPathStore & pTableName`) |
| `ext/02/021` | caminhos das fontes, `vCarregaDados` (`'Atuais'` ou `'IPO_2025'`), `vCarrega*` por fonte, correções de IPL |
| `tra/02/021` | caminhos, listas de fronteira, `vTransformaProcIdentificacaoEmCaso`, `vCorrigeIplsSigacrim`, `vCorrigeIplsPalas`, `vCarregaUnidAreaDirCoorGeral{DaOperacao, DoCaso, DoEventoOperacional, DoEventoExternoEstrangeiro}`, `vCarregaDatasDaCasos*` |
| `app/02/021` | `CriarVariavel*` (contagem, soma, média, relativa, percentual, anteriores, Reais/Mi/Bi) e `TratarExpansaoMacro` |
| `app/02/023` | modificadores de efetivo (`vConjSemRelDatasAreaCasoOperacaoBem` etc.) |

## 7. Restrições da plataforma

- Sem MCP e sem acesso aos dados: contagens e tamanhos dependem de o Eduardo recarregar e reportar.
- Planilhas (sheets) do app não estão no repositório.
- Conexões `lib://` e planilhas de section access ficam fora do repositório.

## 8. Perguntas em aberto

1. O app real tem algum passo que cria `TEMP_EVENTOS_*_EXTERNAS_ESTRANGEIRO` (sem `PF`)? (achado 2)
2. Quantas linhas tem cada fato hoje (itens ePol, operações, casos, Proc_Data, participações, apreensões e prisões de
   eventos)? Serve para estimar a link depois da Etapa A do plano.
3. Alguma tela de Análises usa um filtro de um fato para ver outro (ex.: subclasse apreendida → operações)? Define se
   vale criar indicadores pré-calculados nas dimensões.
4. Para apreensões de eventos PF, qual a fonte oficial de contagem: o ePol ou o evento? (achado 6)
