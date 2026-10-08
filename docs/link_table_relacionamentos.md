# LINK_TABLE_APREENSOES_OPERACOES_CASOS

Tabela de ligação central do modelo. Liga 7 tabelas fato e as dimensões compartilhadas (caso, operação, item apreendido,
evento, unidade, data).

- **Montagem:** na camada `tra`, um bloco por fato em `qlik/tra/06_fatos/061` a `0610`. O bloco de 061 cria a tabela; os
  demais montam uma `TEMP_LINK_TABLE_..._<FATO>` e fazem `CONCATENATE` nela.
- **Gravação:** `qlik/tra/07_dimensoes/0722_DIM_UNIDADE_SUBUNIDADE.qvs` → `T3_LINK_TABLE_APREENSOES_OPERACOES_CASOS.qvd`.
- **Carga no app:** `qlik/app/04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs` (`LOAD DISTINCT` das 39 colunas).
- **Tamanho:** ~12 milhões de linhas (comentário em `tra/07/0721`); já chegou a 61 milhões.

Estado descrito: repositório em 2026-10-08. Para a proposta de redução, ver
[artifacts/03-plano-otimizacao-link-table.md](../artifacts/03-plano-otimizacao-link-table.md).

---

## 1. Colunas (39)

### Chaves para as tabelas fato

| Chave | Tabela | Origem do valor |
|---|---|---|
| `%CASOSKEY` | `FATO_CASOS` | `AutoNumberHash128("Proc. Identificação")` |
| `%CASOSDATAKEY` | `FATO_CASOS_DATA` | `AutoNumberHash128("Proc_Data ID")` |
| `%OPERACOESKEY` | `FATO_OPERACOES` | `AutoNumberHash128(ID_OPERACAO)` |
| `%APREENSOESKEY` | `FATO_APREENSOES` | ePol: `"GestãoBens Item ID"`; SIGACrim: `'SIGACrim_' & ID_OPERACAO`; Palas: `ID_OPERACAO` |
| `%EVENTOSKEY` | `FATO_EVENTOS_OPERACIONAIS` | `AutoNumberHash128(id_ordem_original_evento)` (participação de uma unidade num evento) |
| `%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY` | `FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` | `AutoNumberHash128(id_evento_apreensao)` |
| `%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY` | `FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` | `AutoNumberHash128(id_evento_prisao)` |
| `%SUBCLASSESKEY` | (nenhuma no app) | `AutoNumberHash128("GestãoBens Item Material Subclasse Código")` |

### Chaves para as dimensões

Cada uma tem **o mesmo valor** da chave de fato correspondente (duplicação; ver plano, Etapa B).

| Chave | Dimensões |
|---|---|
| `%PROC_IDENTIFICACAO_KEY` | `DIM_CASOS`, `DIM_CASOS_TIPO_PENAL`, `DIM_MATERIA_RE`, `DIM_INFORMACOES_CASOS` |
| `%ID_OPERACAO_KEY` | `DIM_OPERACOES` e as dimensões de atributos de operação (país, organismo, GPOL, RE etc.) |
| `%GESTAO_BENS_ITEM_ID_KEY` | `DIM_APREENSOES` |
| `%PROC_DATA_ID_KEY` | `DIM_CASOS_DATA` |
| `%ID_EVENTOS_KEY` | `DIM_EVENTOS_OPERACIONAIS` |
| `%ITEM_SUBCLASSE_KEY` | `DIM_TNBIA` |
| `%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY` | `DIM_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` |
| `%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY` | `DIM_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` |
| `%UNIDADE_KEY` | `DIM_UNIDADE`, `DIM_HIERARQUIA_TECNICA`, `DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO`, `DIM_UNIDADE_SUBUNIDADE`, `DIM_CIRCUNSCRICAO_PF`, `DIM_SERVIDOR_ATIVO` |

### Data comum e classificação

| Coluna | Uso |
|---|---|
| `Data`, `Ano`, `Mês`, `Mês (Num)` | Data comum: cada bloco preenche com a data do próprio fato (tabela abaixo) |
| `Tipo da Data` | Qual data foi usada (ex.: `Apreensão`, `Deflagração da Operação`) |
| `Fonte` | Sistema de origem (ex.: `Apreensões ePol`, `Operações Palas`) |
| `Tipo do Fato` | Fato do registro; **todas as métricas filtram por ele** |

### Atributos de unidade e área (15 colunas de texto)

`Unidade Sigla`, `Unidade UF`, `Área de Atribuição`, `Diretoria` e `Coordenação-Geral`, em três versões:
`... do Caso`, `... do Evento Operacional` e `... do Evento Externo/Estrangeiro`. Preenchidas pelas variáveis
`vCarregaUnidAreaDirCoorGeralDoCaso`, `...DoEventoOperacional` e `...DoEventoExternoEstrangeiro`
(`tra/02/021`).

---

## 2. O que cada bloco contribui

| Script | `Tipo do Fato` / `Fonte` | Data comum (`Tipo da Data`) | Chaves próprias (N:1) | `LEFT JOIN` 1:N (multiplicam linhas) | Unidade (`%UNIDADE_KEY`) |
|---|---|---|---|---|---|
| 061 | Apreensões / Apreensões ePol | data da apreensão do item (`Apreensão`) | item, caso, operação, evento, subclasse | `DIM_CASOS_DATA` do caso | do caso |
| 062 | Apreensões / Apreensões SIGACrim (só 2024) | deflagração (`Apreensão`) | operação (como item), caso | `DIM_CASOS_DATA` do caso | do caso |
| 063 | Apreensões / Apreensões Palas | deflagração (`Apreensão`) | operação (como item), caso | `DIM_CASOS_DATA` do caso | unidade Palas |
| 064 | Operações / Operações SIGACrim | deflagração | operação, caso | itens ePol da operação; `DIM_CASOS_DATA`; participações de eventos da operação | do caso |
| 065 | Operações / Operações Palas | deflagração | operação, caso | itens ePol; `DIM_CASOS_DATA` | unidade Palas |
| 066 | Casos / Casos ePol | instauração do caso | caso | operações do caso; itens do caso; `DIM_CASOS_DATA` | do caso |
| 067 | Casos_Data / Casos_Data ePol | data do Proc_Data (`Evento do Caso`) | Proc_Data, caso | operações do caso; itens do caso | do caso |
| 068 | Eventos Operacionais / Eventos Operacionais SIGACrim | data do evento | participação, caso, operação | itens ePol do evento; apreensões e prisões de eventos | unidade participante |
| 069 | Eventos Apreensões Externos/Estrangeiros | data da apreensão do evento | apreensão de evento, participação, subclasse | nenhum | unidade participante |
| 0610 | Eventos Prisões Externos/Estrangeiros | data do evento | prisão de evento, participação | nenhum | unidade participante |

Os `LEFT JOIN` com `TEMP_DIM_CASOS` (atributos de unidade e área do caso) são 1:1 por caso e não multiplicam linhas.
Exceção em 068: como o bloco já tem `%UNIDADE_KEY` da unidade participante, o join com o caso acontece por duas chaves
(`%PROC_IDENTIFICACAO_KEY` e `%UNIDADE_KEY`), e os atributos "do Caso" só são preenchidos quando a unidade do caso é a mesma
unidade participante.

---

## 3. Como as métricas usam a link

- Toda métrica filtra o próprio fato: `[Tipo do Fato] = {'Operações'}`, `{'Apreensões'}`, `{'Casos_Data'}` etc. (072 a 076),
  normalmente com `[Tipo da Data]` correspondente.
- Por isso, as linhas geradas pelos `LEFT JOIN` 1:N não entram nas métricas por data comum. Elas só servem às variantes
  correlacionadas por data específica e à propagação de filtros entre fatos. A decisão de 2026-10-08 (só datas comuns) torna
  essas linhas desnecessárias; ver o plano.
- As métricas de efetivo (`app/023`) limpam dezenas de campos de data, caso, operação e item no set analysis para contar
  servidores só pela unidade.
