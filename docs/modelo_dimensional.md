# Modelo Dimensional — Estatísticas Criminais DICOR

Estado do repositório em 2026-10-08. O modelo carregado no app (`qlik/app/03_fatos/032_FATOS.qvs`,
`04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs` e `05_dimensoes/052_DIMENSOES.qvs`) tem 7 tabelas fato, uma link table e
cerca de 40 dimensões. Os QVDs vêm da camada `tra` com prefixo `T3_`.

```
                       DIM_CASOS (+ TIPO_PENAL, MATERIA_RE, INFORMACOES_CASOS)
                                 │ %PROC_IDENTIFICACAO_KEY
 DIM_OPERACOES (+ atributos) ────┤ %ID_OPERACAO_KEY
 DIM_APREENSOES ─────────────────┤ %GESTAO_BENS_ITEM_ID_KEY
 DIM_CASOS_DATA ─────────────────┤ %PROC_DATA_ID_KEY
 DIM_EVENTOS_OPERACIONAIS ───────┤ %ID_EVENTOS_KEY
 DIM_EVENTOS_APREENSOES_... ─────┤ %ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY
 DIM_EVENTOS_PRISOES_... ────────┤ %ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY
 DIM_TNBIA ──────────────────────┤ %ITEM_SUBCLASSE_KEY
 DIM_UNIDADE e afins ────────────┤ %UNIDADE_KEY
                                 │
               LINK_TABLE_APREENSOES_OPERACOES_CASOS
                                 │
   ┌──────────────┬──────────────┼───────────────┬───────────────────┬─────────────────────┐
FATO_CASOS  FATO_CASOS_DATA  FATO_OPERACOES  FATO_APREENSOES  FATO_EVENTOS_OPERACIONAIS  FATO_EVENTOS_APREENSOES_...
                                                                                          FATO_EVENTOS_PRISOES_...
```

Detalhes da link table em [link_table_relacionamentos.md](link_table_relacionamentos.md).

---

## 1. Tabelas fato

| Fato | Grão | Chave | Fontes | Script `tra` | Conteúdo principal |
|---|---|---|---|---|---|
| `FATO_APREENSOES` | item apreendido (ePol) ou operação (SIGACrim 2024, Palas 2022–2023) | `%APREENSOESKEY` | `DIM_CASOS_APREENSAO_BENS`, `SIGACrim`, `Palas_Operacoes_Tratadas_2022_2023`, CGPRE | 061, 062, 063 | quantidades normalizadas (drogas, armas, munições, cigarros), valor estimado, valores de descapitalização LVL1 e LVL2, flags de item de interesse/descapitalização |
| `FATO_OPERACOES` | operação | `%OPERACOESKEY` | `SIGACrim` (homologadas), Palas | 064, 065 | ~200 campos: sinalizadores Sim/Não, majorantes, medidas cautelares, quantidades expedidas/cumpridas, vítimas resgatadas, valores |
| `FATO_CASOS` | caso (`Proc. Identificação`) | `%CASOSKEY` | ePol `DIM_CASOS` | 066 | situação, tipo de instauração, flags (flagrante, TC, iniciativa interna/externa, execução direta), quantidades de presos, indiciados, mandados |
| `FATO_CASOS_DATA` | evento de data do caso (`Proc_Data ID`) | `%CASOSDATAKEY` | ePol `DIM_CASOS_DATA` | 067 | IDs de instauração/relato/encerramento por tipo de procedimento, durações, presos, indiciamentos, fiança |
| `FATO_EVENTOS_OPERACIONAIS` | participação de uma unidade num evento (`id_ordem_original_evento`) | `%EVENTOSKEY` | `TabelaoEventos` deduplicado (`tra/03/032`) | 068 | `houve_apreensao`, `houve_prisao`, `qtd_presos` (repetem em cada unidade participante) |
| `FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` | apreensão de evento (`id_evento_apreensao`) | `%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY` | `Eventos_Apreensoes` (`tra/03/033`) | 069 | `qt_item`, `st_selecionado` |
| `FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` | prisão de evento (`id_evento_prisao`) | `%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY` | `Eventos_Prisoes` (`tra/03/034`) | 0610 | `cd_tipo_prisao`, `cd_documento`, `st_nao_cpf`, `nome_cpf_preso` (anonimizado) |

Observações:
- Apesar do nome `..._EXTERNAS_ESTRANGEIRO`, os scripts 033 e 034 hoje também carregam eventos PF (o filtro
  `WHERE MATCH(cd_tipo_evento_fk, 'estrangeiro', 'externo')` está comentado).
- As apreensões de eventos PF são vinculadas por inferência a itens do ePol em `tra/05/051` (caso + subclasse, depois
  quantidade, data e menor ID). Uma mesma apreensão pode, portanto, aparecer no ePol (`FATO_APREENSOES`) e no evento.
- `ID_OPERACAO` de cada item ePol é definido em `tra/05/053`: primeiro o do evento vinculado (051), depois o dos
  intervalos de deflagração por IPL e por RE_SEQUESTRO (052).

## 2. Dimensões (principais)

| Dimensão | Chave | Script `tra` | Conteúdo |
|---|---|---|---|
| `DIM_OPERACOES` | `%ID_OPERACAO_KEY`, `%ID_FILTROS_OPERACAO_KEY` | 071, 073 | dados da operação e datas específicas (prevista, deflagração, cadastro, início, homologação, gPol) |
| atributos de operação (`DIM_PAIS_COOPERACAO_POLICIAL`, `DIM_FACCAO_DESCRICAO`, `DIM_GPOL_*`, `DIM_EFETIVOS_GPOL` etc.) | `%ID_OPERACAO_KEY` | 072 | listas multivaloradas despivotadas |
| `DIM_INFORMACOES_GERAIS`, `DIM_MEDIDAS_EXTRAORDINARIAS`, `DIM_RESULTADOS_DEFLAGRACAO`, `DIM_SETORIAIS_*` | `%ID_FILTROS_OPERACAO_KEY` | 075, 076, 0726 | filtros despivotados (Sim/Não → linhas) |
| `DIM_Caso_de_RE_de_Recuperação_de_Ativos` | `%ID_OPERACAO_KEY` | 074 | RE de recuperação de ativos |
| `DIM_APREENSOES` | `%GESTAO_BENS_ITEM_ID_KEY` | 077, 078, 079 | atributos do item (ePol), ou da operação como "item" (SIGACrim, Palas) |
| `DIM_TNBIA` | `%ITEM_SUBCLASSE_KEY` | 0727 | taxonomia de materiais (subclasse, classe, categoria) |
| `DIM_CASOS` | `%PROC_IDENTIFICACAO_KEY` | 0710 | atributos e datas específicas do caso |
| `DIM_INFORMACOES_CASOS` | `%PROC_IDENTIFICACAO_KEY` | 0711 | filtros despivotados do caso |
| `DIM_CASOS_TIPO_PENAL` | `%PROC_IDENTIFICACAO_KEY` | 0712 | tipos penais (N por caso) |
| `DIM_MATERIA_RE` | `%PROC_IDENTIFICACAO_KEY` | 0713 | matéria de RE |
| `DIM_CASOS_DATA` | `%PROC_DATA_ID_KEY` | 0714 | data/hora e partes da data do Proc_Data |
| `DIM_EVENTOS_OPERACIONAIS` | `%ID_EVENTOS_KEY` | 0715 | evento, tipo (pf/externo/estrangeiro), datas, participação, local |
| `DIM_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` | `%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY` | 0716 | item, categoria, classe, data, local |
| `DIM_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` | `%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY` | 0717 | preso (anonimizado), documento, local |
| `DIM_UNIDADE` | `%UNIDADE_KEY` | 0719 | cadastro da unidade |
| `DIM_HIERARQUIA_TECNICA` | `%UNIDADE_KEY` | 0720 | central/regional/base/descentralizada, PJ/NPJ |
| `DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO` | `%UNIDADE_KEY` | 0721 | tipo de unidade, órgão, especializadas (montada a partir da link) |
| `DIM_UNIDADE_SUBUNIDADE` | `%UNIDADE_KEY` | 0722 | `HierarchyBelongsTo` (unidade → todas as superiores) |
| `DIM_CIRCUNSCRICAO_PF` → `DIM_TB_MUNICIPIOS_BRASIL` | `%UNIDADE_KEY`, `%CODIGO_IBGE` | 0723, 0724 | municípios da circunscrição |
| `DIM_SERVIDOR_ATIVO` | `%UNIDADE_KEY` | 0718 | efetivo por unidade |
| `DIM_OPERACOES_SEM_AREA` | (sem chave) | ext 081 | tabela de controle |

## 3. Datas

- **Data comum:** `Data`, `Ano`, `Mês`, `Mês (Num)` na link table, preenchidas com a data do próprio fato. É a única usada
  pela alta administração (decisão de 2026-10-08).
- **Datas específicas:** nas dimensões (`Ano da Deflagração` em `DIM_OPERACOES`, datas do caso em `DIM_CASOS`,
  `Proc_Data Data` em `DIM_CASOS_DATA`, `Data do Evento Operacional` em `DIM_EVENTOS_OPERACIONAIS` etc.). Filtram o próprio
  fato e os fatos que carregam a mesma chave na própria linha.
- Não há calendário mestre; ano e mês são calculados em cada bloco da link.

## 4. Unidade comum

`%UNIDADE_KEY` é a "unidade do registro": unidade do caso (com a correção FICCO/GISE de `MapIPLUnidadeFiccoGise`) para
apreensões, operações SIGACrim, casos e Casos_Data; unidade Palas para Palas; unidade participante para eventos.

## 5. Ordem de carga

Os `000_MAIN.qvs` não têm `$(Include=...)`, então a ordem real está no editor do Qlik. A numeração dos arquivos sugere:
- `ext`: 01 → 17 (fontes → `15_output/151_GRAVA_QVD.qvs` → section access)
- `tra`: 01 → 02 (variáveis e sub-rotinas) → 03 (carrega QVDs `E2_TEMP_*`) → 04 (mappings) → 05 (ajustes: evento e
  operação do item) → 06 (fatos e blocos da link) → 07 (dimensões; 0722 grava a link) → 08 → 09
- `app`: 01 → 02 → 03 (fatos) → 04 (link) → 05 (dimensões) → 06 → 07 (métricas) → 08 (medidas mestras) → 09 → 10 → 11

Dentro de `tra/06`, a ordem numérica é 061, 0610, 062… (ordem de string); 061 precisa rodar primeiro porque cria a link.
