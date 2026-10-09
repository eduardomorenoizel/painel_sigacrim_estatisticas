# Esquema da LINK_TABLE_APREENSOES_OPERACOES_CASOS

A `LINK_TABLE_APREENSOES_OPERACOES_CASOS` é a tabela de ligação central do modelo dimensional. Ela resolve as relações de muitos-para-muitos entre os fatos, sendo construída por CONCATENATE de várias `TEMP_LINK_TABLE` geradas em cada script de carga da pasta `qlik/tra/06_fatos` (061 cria a tabela; 062 a 0610 concatenam). Ela é gravada em `T3_LINK_TABLE_APREENSOES_OPERACOES_CASOS.qvd` por `qlik/tra/07_dimensoes/0722_DIM_UNIDADE_SUBUNIDADE.qvs` (depois que `0721_DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO.qvs` lê dela as siglas de unidade do caso). A camada app (`app/04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs`) só carrega o QVD.

Desde 2026-10-09 as chaves de caso usam o **Caso (IPL) no formato `AAAA.NNNNNNN`** (campo `IPL`, criado na camada ext pela variável `vTransformaProcIdentificacaoEmCaso`, ou por `vCorrigeIplsSigacrim`/`vCorrigeIplsPalas` nas operações), e não mais o `"Proc. Identificação"`, porque o tipo do procedimento (IPL/FLA/TC/RE) muda durante a tramitação.

---

## Chaves primárias — ligação com tabelas fato

```
LINK_TABLE_APREENSOES_OPERACOES_CASOS
│
├── [%CASOSKEY]          ──────────────► FATO_CASOS
│                                         (AutoNumberHash128("IPL"))
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
├── [%EVENTOSAPREENSOESKEY] ──► FATO_EVENTOS_APREENSOES
│                                                    (AutoNumberHash128(id_evento_apreensao))
│
├── [%EVENTOSPRISOESKEY]    ──► FATO_EVENTOS_PRISOES
│                                                    (AutoNumberHash128(id_evento_prisao))
│
└── [%SUBCLASSESKEY]     ──────────────► (nenhuma tabela; a DIM_TNBIA liga por %ITEM_SUBCLASSE_KEY)
                                          (AutoNumberHash128("GestãoBens Item Material Subclasse Código"))
```

---

## Chaves secundárias — ligação com dimensões

```
[%PROC_IDENTIFICACAO_KEY]   ──► DIM_CASOS, DIM_CASOS_TIPO_PENAL, DIM_MATERIA_RE, DIM_INFORMACOES_CASOS
                                (AutoNumberHash128("IPL"))
[%ID_OPERACAO_KEY]          ──► DIM_OPERACOES (e dimensões de atributos/filtros de operação)
[%GESTAO_BENS_ITEM_ID_KEY]  ──► DIM_APREENSOES
[%PROC_DATA_ID_KEY]         ──► DIM_CASOS_DATA
[%ID_EVENTOS_KEY]           ──► DIM_EVENTOS_OPERACIONAIS
[%ITEM_SUBCLASSE_KEY]       ──► DIM_TNBIA
[%ID_EVENTOS_APREENSOES_KEY]──► DIM_EVENTOS_APREENSOES
[%ID_EVENTOS_PRISOES_KEY]   ──► DIM_EVENTOS_PRISOES
[%UNIDADE_KEY]              ──► DIM_UNIDADE, DIM_SERVIDOR_ATIVO, DIM_HIERARQUIA_TECNICA,
                                DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO, DIM_UNIDADE_SUBUNIDADE, DIM_CIRCUNSCRICAO_PF
                                (unidade do caso em 061, 062, 064, 066, 067; UNIDADE da operação em 063, 065;
                                 unidade_participante em 068, 069, 0610)
```

---

## Chaves contribuídas por cada fato

Cada script de carga gera uma `TEMP_LINK_TABLE` que é concatenada na `LINK_TABLE` final. A tabela abaixo indica quais chaves cada fato preenche.

| Fato / Fonte                               | `%CASOS` | `%CASOSDATA` | `%OPERACOES` | `%APREENSOES` | `%EVENTOS` | `%EVENTOSAPR` | `%EVENTOSPRI` | `%SUBCLASSES` |
|---                                         |  :---:   |    :---:     |    :---:     |     :---:     |   :---:    |     :---:     |     :---:     |     :---:     |
| **FATO_APREENSOES** ePol (061)             |    ✓     |     ✓*      |      ✓       |      (✓)      |    ✓      |       ✓       |       —       |       ✓       |
| **FATO_APREENSOES** SIGACrim (062)         |    ✓     |     ✓*      |      ✓       |      (✓)      |    —       |      —        |      —        |      —        |
| **FATO_APREENSOES** Palas (063)            |    ✓     |     ✓*      |      ✓       |      (✓)      |    —       |      —        |      —        |      —        |
| **FATO_OPERACOES** SIGACrim (064)          |    ✓     |     ✓*      |     (✓)      |       ✓*      |    ✓*      |      ✓*       |      ✓*      |      ✓*       |
| **FATO_OPERACOES** Palas (065)             |    ✓     |     ✓*      |     (✓)      |       ✓*      |    —       |      —        |      —        |     ✓*       |
| **FATO_CASOS** (066)                       |   (✓)    |     ✓*      |      ✓*      |       ✓*      |    ✓*      |      ✓*       |      —       |      ✓*       |
| **FATO_CASOS_DATA** (067)                  |    ✓     |    (✓)      |      ✓*      |       ✓*      |    ✓*      |      ✓*       |      —       |      ✓*       |
| **FATO_EVENTOS_OPERACIONAIS** (068)        |    ✓     |     —        |     ✓       |       ✓*      |    (✓)     |      ✓*       |      ✓*      |     ✓*        |
| **FATO_EVENTOS_APREENSOES** (069)          |    ✓     |     —        |      ✓       |       —       |     ✓      |     (✓)       |      —       |      ✓        |
| **FATO_EVENTOS_PRISOES** (0610)            |    ✓     |     —        |      ✓       |       —       |     ✓      |      —        |     (✓)      |      —        |

> (✓) = chave primária na carga base do TEMP_LINK  
> ✓ = chave gerada na carga base do TEMP_LINK  
> ✓* = chave adicionada via LEFT JOIN de outra tabela temporária  
> — = chave não preenchida (NULL implícito)
>
> Situação em 2026-10-09 (código atual). Em relação à versão anterior: 061, 066 e 067 passaram a trazer `%EVENTOSAPREENSOESKEY`; 064 ganhou dois LEFT JOINs (eventos-apreensões e eventos-prisões por `ID_OPERACAO`); 069 e 0610 passaram a ter `%CASOSKEY` (IPL) e `%OPERACOESKEY` na carga base. Cada ✓* é um LEFT JOIN 1:N que multiplica linhas (ver "Diagnóstico de volume").

---

## Campos de data e classificação analítica na Link Table

Cada linha da Link Table carrega campos de data e classificação que funcionam como **dimensão de tempo centralizada**, permitindo filtrar e agregar todos os fatos por data sem criar dimensões de calendário separadas por fato.

|     Campo      |             Conteúdo             |
|      ---       |               ---                |
|     `Data`     | Data do evento relevante do fato |
|     `Ano`      |            `YEAR('Data)`         |
|     `Mês`      |       `MONTH(Data)` (texto)      |
|   `Mês (Num)`  |       `MONTH(Data)` (número)     |
| `Tipo da Data` |           `'Apreensão'`         \| `'Instauração do Caso'` \| `'Deflagração da Operação'` \|    `'Evento do Caso'`    \|            `'Evento Operacional'`            \| `'Evento Apreensão Externo/Estrangeiro'` \| `'Evento Prisão Externo/Estrangeiro'` |
|     `Fonte`    |        `'Apreensões ePol'`      \| `'Apreensões SIGACrim'` \|     `'Apreensões Palas'`    \|  `'Operações SIGACrim'`  \|              `'Operações Palas'`             \|              `'Casos ePol'`              \|          `'Casos_Data ePol'`         \| `'Eventos Operacionais SIGACrim'` \| `'Eventos Apreensões SIGACrim'` \| `'Eventos Prisões SIGACrim'` |
| `Tipo do Fato` |           `'Apreensões'`        \|      `'Operações'`      \|          `'Casos'`          \|      `'Casos_Data'`      \| `'Eventos Operacionais'` \| `'Eventos Apreensões Externos/Estrangeiros'` \| `'Eventos Prisões Externos/Estrangeiros'` |

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
| `069_FATO_EVENTOS_APREENSOES.qvs` | FATO_EVENTOS_APREENSOES | `TEMP_LINK_TABLE_..._EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` |
| `0610_FATO_EVENTOS_PRISOES.qvs` | FATO_EVENTOS_PRISOES | `TEMP_LINK_TABLE_..._EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` |
| `tra/07_dimensoes/0721_DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO.qvs` | (lê `Unidade Sigla do Caso` da link table) | — |
| `tra/07_dimensoes/0722_DIM_UNIDADE_SUBUNIDADE.qvs` | grava a link table (`StoreAndDrop`) | — |
| `app/04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs` | carrega o QVD com lista explícita de campos | — |

Observação: os valores `'... Externo/Estrangeiro'` de `Tipo da Data`/`Tipo do Fato` e os nomes das TEMP_LINK de 069/0610 são herdados; desde a unificação (033/034 `*_UNIFICADOS`) esses blocos incluem também eventos PF.

---

## Diagnóstico de volume (2026-10-09)

A link table passou de **61 milhões de linhas** e o app ficou lento. A causa está nos blocos de `tra/06_fatos`: cada bloco faz **LEFT JOIN com tabelas 1:N de outros fatos** para levar à linha as chaves "relacionadas" (as antigas "datas específicas relacionadas", por exemplo apreensões das operações deflagradas no período). No Qlik, um LEFT JOIN repete a linha para cada correspondência, e joins encadeados se multiplicam (produto por chave).

| Bloco | Tipo do Fato / Tipo da Data | Data comum | Unidade comum | LEFT JOINs que trazem chaves de outros fatos |
|---|---|---|---|---|
| 061 Apreensões ePol | Apreensões / Apreensão | `GestãoBens Item Data Apreensão` | `vCarregaUnidAreaDirCoorGeralDoCaso` (join por IPL) | todos os `Proc_Data ID` do caso |
| 062 Apreensões SIGACrim (2024) | Apreensões / Apreensão | `DT_DEFLAGRACAO` | caso (join por IPL) | todos os `Proc_Data ID` do caso |
| 063 Apreensões Palas | Apreensões / Apreensão | `DT_DEFLAGRACAO` | `UNIDADE` da operação Palas | todos os `Proc_Data ID` do caso |
| 064 Operações SIGACrim | Operações / Deflagração da Operação | `DT_DEFLAGRACAO` | caso (join por IPL) | itens ePol da operação; `Proc_Data ID` do caso; eventos da operação; eventos-apreensões da operação; eventos-prisões da operação |
| 065 Operações Palas | Operações / Deflagração da Operação | `DT_DEFLAGRACAO` | `UNIDADE` da operação Palas | itens ePol (por caso e operação); `Proc_Data ID` do caso |
| 066 Casos | Casos / Instauração do Caso | `Proc. Data Instauração` | caso (na carga base) | operações SIGACrim do caso; itens ePol do caso (com evento e evento-apreensão); `Proc_Data ID` do caso |
| 067 Casos_Data | Casos_Data / Evento do Caso | `Proc_Data Data` | caso (join por IPL) | operações SIGACrim do caso; itens ePol do caso (com evento e evento-apreensão) |
| 068 Eventos operacionais | Eventos Operacionais / Evento Operacional | `dt_evento` | unidade participante **e** join com a unidade do caso | itens ePol do evento; eventos-apreensões do evento; eventos-prisões do evento |
| 069 Eventos apreensões | Eventos Apreensões Externos/Estrangeiros / Evento Apreensão Externo/Estrangeiro | `dt_apreensao` | unidade participante | nenhum |
| 0610 Eventos prisões | Eventos Prisões Externos/Estrangeiros / Evento Prisão Externo/Estrangeiro | `dt_evento` (via join com o evento) | unidade participante | nenhum (o join só traz a data) |

Pontos de atenção do código atual:
- **066 é o maior suspeito**: casos × operações do caso × itens apreendidos do caso × linhas de Casos_Data do caso. 067 e 064 vêm em seguida; 061 multiplica cada item pelas linhas de Casos_Data do caso.
- **068** ainda faz o join com `vCarregaUnidAreaDirCoorGeralDoCaso`. Como a carga base já tem `%UNIDADE_KEY` (unidade participante), o join casa por `%PROC_IDENTIFICACAO_KEY` **e** `%UNIDADE_KEY`. Pela decisão de 2026-10-09, eventos usam só a unidade do evento, então esse join deve sair.
- **Unicidade do IPL**: `TEMP_DIM_CASOS` (ext 111) faz LEFT JOIN de `TEMP_TEMP_DIM_CASOS` por `IPL` sem filtro, então um IPL com mais de um `Proc. Identificação` gera mais de uma linha. Todo join com a unidade do caso duplicaria linhas e a DIM_CASOS ficaria sem chave única. Teste sugerido: `LOAD IPL, Count(DISTINCT "Proc. Identificação") AS n RESIDENT TEMP_DIM_CASOS GROUP BY IPL;` e verificar `n > 1`.
- Cada chave aparece duas vezes (par fato/dimensão), e cada linha carrega ~20 campos de texto de data e de unidade/área por "dono".

### Desenho enxuto proposto

**Uma linha de link por linha de fato**, sem JOIN entre fatos:

| Campo | Conteúdo |
|---|---|
| chave do fato | a mesma chave do `FATO_*` (ex.: `%APREENSOESKEY`, `%OPERACOESKEY`) |
| `%DATA_KEY` | data comum do fato (número inteiro) → calendário (`DIM_CALENDARIO`: Data, Ano, Mês, Mês (Num) etc.) |
| `%UNIDADE_KEY` | uma única unidade por fato: caso (ePol, SIGACrim), `UNIDADE` da operação (Palas), unidade participante (eventos) |
| `%AREA_KEY` | área de atribuição comum → dimensão de área (Área, Diretoria, CG) |
| `Tipo do Fato` | um valor por fato (as métricas já filtram por ele) |

Cada `FATO_*` continua ligado às suas próprias dimensões pela chave do fato. Saem da link table as chaves de outros fatos, `Ano`/`Mês`/`Mês (Num)` (vão para o calendário), `Tipo da Data` (redundante com `Tipo do Fato`) e os textos de unidade/área (vão para dimensões). Cada indicador passa a contar de forma independente pelo período.

**Estimativa (a confirmar no reload)**: soma das linhas dos fatos, sem multiplicação, na ordem de **5 a 10 milhões de linhas, contra 61 milhões hoje**, e cerca de 6 colunas em vez de ~40. Para medir a distribuição atual, contar `[Tipo do Fato]` na link table no fim do 0722, antes do `StoreAndDrop`.
