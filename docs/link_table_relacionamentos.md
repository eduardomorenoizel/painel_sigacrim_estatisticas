# Esquema da LINK_TABLE_APREENSOES_OPERACOES_CASOS

A `LINK_TABLE_APREENSOES_OPERACOES_CASOS` é a tabela de ligação central do modelo dimensional. Ela resolve as relações de muitos-para-muitos entre os fatos, sendo construída por CONCATENATE de várias `TEMP_LINK_TABLE` geradas em cada script de carga da pasta `06_fatos`.

---

## Chaves primárias — ligação com tabelas fato

```
LINK_TABLE_APREENSOES_OPERACOES_CASOS
│
├── [%CASOSKEY]          ──────────────► FATO_CASOS
│                                         (AutoNumberHash128("Proc. Identificação"))
│
├── [%CASOSDATAKEY]      ──────────────► FATO_CASOS_DATA
│                                         (AutoNumberHash128("Proc_Data ID"))
│
├── [%OPERACOESKEY]      ──────────────► FATO_OPERACOES
│                                         (AutoNumberHash128(ID_OPERACAO))
│
├── [%APREENSOESKEY]     ──────────────► FATO_APREENSOES
│                                         ├── ePol:     AutoNumberHash128("GestãoBens Item ID")
│                                         ├── SIGACrim: AutoNumberHash128('SIGACrim'&'_'&ID_OPERACAO)
│                                         └── Palas:    AutoNumberHash128(ID_OPERACAO)
│
├── [%EVENTOSKEY]        ──────────────► FATO_EVENTOS_OPERACIONAIS
│                                         (AutoNumberHash128(id_ordem_original_evento))
│
├── [%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY] ──► FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO
│                                                    (AutoNumberHash128(id_evento_apreensao))
│
├── [%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY]    ──► FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO
│                                                    (AutoNumberHash128(id_evento_prisao))
│
└── [%SUBCLASSESKEY]     ──────────────► DIM_SUBCLASSES (dimensão)
                                          (AutoNumberHash128("GestãoBens Item Material Subclasse Código"))
```

---

## Chaves secundárias — ligação com dimensões

```
[%PROC_IDENTIFICACAO_KEY]                          ──► DIM_CASOS
[%ID_OPERACAO_KEY]                                 ──► DIM_OPERACOES
[%GESTAO_BENS_ITEM_ID_KEY]                         ──► DIM_CASOS_APREENSAO_BENS
[%PROC_DATA_ID_KEY]                                ──► DIM_CASOS_DATA
[%ID_EVENTOS_KEY]                                  ──► DIM_EVENTOS (TABELAO)
[%ITEM_SUBCLASSE_KEY]                              ──► DIM_SUBCLASSES
[%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY] ──► FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO
[%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY]    ──► FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO
[%UNIDADE_KEY]                                     ──► DIM_UNIDADE  (Palas somente)
```

---

## Chaves contribuídas por cada fato

Cada script de carga gera uma `TEMP_LINK_TABLE` que é concatenada na `LINK_TABLE` final. A tabela abaixo indica quais chaves cada fato preenche.

| Fato / Fonte                               | `%CASOS` | `%CASOSDATA` | `%OPERACOES` | `%APREENSOES` | `%EVENTOS` | `%EVENTOSAPR` | `%EVENTOSPRI` | `%SUBCLASSES` |
|---                                         |  :---:   |    :---:     |    :---:     |     :---:     |   :---:    |     :---:     |     :---:     |     :---:     |
| **FATO_APREENSOES** ePol (061)             |    ✓     |     ✓*      |      ✓       |       ✓       |    ✓      |       —       |       —       |       ✓       |
| **FATO_APREENSOES** SIGACrim (062)         |    ✓     |     ✓*      |      ✓       |       ✓       |    —       |      —        |      —        |      —        |
| **FATO_APREENSOES** Palas (063)            |    ✓     |     ✓*      |      ✓       |       ✓       |    —       |      —        |      —        |      —        |
| **FATO_OPERACOES** SIGACrim (064)          |    ✓     |     ✓*      |      ✓       |       ✓*      |    ✓*      |      —        |      —       |      ✓*       |
| **FATO_OPERACOES** Palas (065)             |    ✓     |     ✓*      |      ✓       |       ✓*      |    —       |      —        |      —        |     ✓*       |
| **FATO_CASOS** (066)                       |    ✓     |     ✓*      |      ✓*      |       ✓*      |    ✓*      |      —        |      —       |      ✓*       |
| **FATO_CASOS_DATA** (067)                  |    ✓     |     ✓       |      ✓*      |       ✓*      |    ✓*      |      —        |      —       |      —        |
| **FATO_EVENTOS_OPERACIONAIS** (068)        |    ✓     |     —        |     ✓       |       ✓*      |     ✓      |      ✓*       |      ✓*      |     ✓*        |
| **FATO_EVENTOS_APREENSOES** Ext/Estr (069) |    —     |     —        |      —       |       —       |     ✓      |      ✓        |      —       |      ✓        |
| **FATO_EVENTOS_PRISOES** Ext/Estr (0610)   |    —     |     —        |      —       |       —       |     ✓      |      —        |      ✓       |      —        |

> ✓ = chave gerada na carga base do TEMP_LINK  
> ✓* = chave adicionada via LEFT JOIN de outra tabela temporária  
> — = chave não preenchida (NULL implícito)

---

## Campos de data e classificação analítica na Link Table

Cada linha da Link Table carrega campos de data e classificação que funcionam como **dimensão de tempo centralizada**, permitindo filtrar e agregar todos os fatos por data sem criar dimensões de calendário separadas por fato.

| Campo | Conteúdo |
|---|---|
| `Data` | Data do evento relevante do fato |
| `Ano` | `YEAR(Data)` |
| `Mês` | `MONTH(Data)` (texto) |
| `Mês (Num)` | `MONTH(Data)` (número) |
| `Tipo da Data` | `'Apreensão'` \| `'Instauração do Caso'` \| `'Deflagração da Operação'` \| `'Evento do Caso'` \| `'Evento Operacional'` \| `'Evento Apreensão Externo/Estrangeiro'` \| `'Evento Prisão Externo/Estrangeiro'` |
| `Fonte` | `'Apreensões ePol'` \| `'Apreensões SIGACrim'` \| `'Apreensões Palas'` \| `'Operações SIGACrim'` \| `'Operações Palas'` \| `'Casos ePol'` \| `'Casos_Data ePol'` \| `'Eventos Operacionais SIGACrim'` \| `'Eventos Apreensões SIGACrim'` \| `'Eventos Prisões SIGACrim'` |
| `Tipo do Fato` | `'Apreensões'` \| `'Operações'` \| `'Casos'` \| `'Eventos Operacionais'` \| `'Eventos Apreensões Externos/Estrangeiros'` \| `'Eventos Prisões Externos/Estrangeiros'` |

---

## Arquivos fonte

| Script | Fato carregado | TEMP_LINK gerada |
|---|---|---|
| `061_FATO_APREENSOES_DIM_CASOS_APREENSAO_BENS.qvs` | FATO_APREENSOES (ePol) | `LINK_TABLE_APREENSOES_OPERACOES_CASOS` (inicial) |
| `062_FATO_APREENSOES_SIGACRIMHOMOLOGADAS.qvs` | FATO_APREENSOES (SIGACrim) | `TEMP_LINK_TABLE_..._APREENSOES_SIGACRIM` |
| `063_FATO_APREENSOES_PALAS_OPERACOES_TRATADAS_2022_2023.qvs` | FATO_APREENSOES (Palas) | `TEMP_LINK_TABLE_..._APREENSOES_PALAS` |
| `064_FATO_OPERACOES_SIGACRIMHOMOLOGADAS.qvs` | FATO_OPERACOES (SIGACrim) | `TEMP_LINK_TABLE_..._OPERACOES_SIGACRIM` |
| `065_FATO_OPERACOES_PALAS_OPERACOES_TRATADAS_2022_2023.qvs` | FATO_OPERACOES (Palas) | `TEMP_LINK_TABLE_..._OPERACOES_PALAS` |
| `066_FATO_CASOS_DIM_CASOS.qvs` | FATO_CASOS | `TEMP_LINK_TABLE_..._FATO_CASOS` |
| `067_FATO_CASOS_DATA_DIM_CASOS_DATA.qvs` | FATO_CASOS_DATA | `TEMP_LINK_TABLE_..._FATO_CASOS_DATA` |
| `068_FATO_EVENTOS_OPERACIONAIS.qvs` | FATO_EVENTOS_OPERACIONAIS | `TEMP_LINK_TABLE_..._EVENTOS_OPERACIONAIS` |
| `069_FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO.qvs` | FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO | `TEMP_LINK_TABLE_..._EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` |
| `0610_FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO.qvs` | FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO | `TEMP_LINK_TABLE_..._EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` |
