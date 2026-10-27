# Esquema da LINK_TABLE_APREENSOES_OPERACOES_CASOS

A `LINK_TABLE_APREENSOES_OPERACOES_CASOS` é a tabela de ligação central do modelo dimensional. Ela resolve as relações de muitos-para-muitos entre os fatos, sendo construída por CONCATENATE de várias `TEMP_LINK_TABLE` geradas em cada script de carga da pasta `qlik/tra/06_fatos` (061 cria a tabela; 062 a 0610 concatenam). Ela é gravada em `LINK_TABLE_APREENSOES_OPERACOES_CASOS.qvd` por `qlik/tra/07_dimensoes/0722_DIM_UNIDADE_SUBUNIDADE.qvs` (depois que `0721_DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO.qvs` lê dela as siglas de unidade do caso). A camada app (`app/04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs`) só carrega o QVD, com lista explícita de campos.

Desde 2026-10-09 as chaves de caso usam o **Caso (IPL) no formato `AAAA.NNNNNNN`** (campo `IPL`, criado na camada ext pela variável `vTransformaProcIdentificacaoEmCaso`, ou por `vCorrigeIplsSigacrim`/`vCorrigeIplsPalas` nas operações), e não mais o `"Proc. Identificação"`, porque o tipo do procedimento (IPL/FLA/TC/RE) muda durante a tramitação.

A partir do commit `668c9e5` (2026-10-14, "perf: preservando somente as chaves próprias do FATO e eliminando fan-out") e de alterações locais posteriores (ainda sem commit em 2026-10-23), cada bloco leva, em regra, **só as chaves do próprio fato**. Restam três LEFT JOINs entre fatos (064 e 067), descritos em "Diagnóstico de volume".

> Esta revisão (2026-10-23) descreve os arquivos **como estão no disco**, inclusive alterações ainda não commitadas. As referências a commits indicam só onde a mudança começou.

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
└── [%SUBCLASSESKEY]     ──────────────► DIM_TNBIA (desde 2026-10-27; antes a DIM_TNBIA usava %ITEM_SUBCLASSE_KEY e ficava isolada)
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
[%ID_EVENTOS_APREENSOES_KEY]──► DIM_EVENTOS_APREENSOES
[%ID_EVENTOS_PRISOES_KEY]   ──► DIM_EVENTOS_PRISOES
[%UNIDADE_KEY]              ──► DIM_UNIDADE, DIM_SERVIDOR_ATIVO, DIM_HIERARQUIA_TECNICA,
                                DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO, DIM_UNIDADE_SUBUNIDADE, DIM_CIRCUNSCRICAO_PF
                                (unidade do caso em 061, 062, 064, 066, 067; UNIDADE da operação em 063, 065;
                                 unidade_participante em 068, 069, 0610)
```

Observação: a app (042) carrega só as chaves `%...KEY` de fato e `%UNIDADE_KEY`; os pares de dimensão gravados por 067 (`%PROC_IDENTIFICACAO_KEY`, `%PROC_DATA_ID_KEY`) não são lidos pela app.

---

## Chaves contribuídas por cada fato (código de 2026-10-23)

Cada script de carga gera uma `TEMP_LINK_TABLE` que é concatenada na `LINK_TABLE` final. A tabela abaixo indica quais chaves cada fato preenche.

| Fato / Fonte                               | `%CASOS` | `%CASOSDATA` | `%OPERACOES` | `%APREENSOES` | `%EVENTOS` | `%EVENTOSAPR` | `%EVENTOSPRI` | `%SUBCLASSES` | Unidade |
|---                                         |  :---:   |    :---:     |    :---:     |     :---:     |   :---:    |     :---:     |     :---:     |     :---:     |  :---:  |
| **FATO_APREENSOES** ePol (061)             |    ✓     |      —       |      ✓       |      (✓)      |    ✓       |       ✓       |       —       |       ✓       | caso (join 1:1) |
| **FATO_APREENSOES** SIGACrim (062)         |    ✓     |      —       |      ✓       |      (✓)      |    —       |      —        |      —        |      —        | caso (join 1:1) |
| **FATO_APREENSOES** Palas (063)            |    ✓     |      —       |      ✓       |      (✓)      |    —       |      —        |      —        |      —        | operação Palas |
| **FATO_OPERACOES** SIGACrim (064)          |    ✓     |      —       |     (✓)      |      ✓*       |    —       |      —        |      —        |      ✓*       | caso (join 1:1) |
| **FATO_OPERACOES** Palas (065)             |    ✓     |      —       |     (✓)      |      —        |    —       |      —        |      —        |      —        | operação Palas |
| **FATO_CASOS** (066)                       |   (✓)    |      —       |      —       |      —        |    —       |      —        |      —        |      —        | caso (na base) |
| **FATO_CASOS_DATA** (067)                  |    ✓     |     (✓)      |      ✓*      |      —        |    —       |      —        |      —        |      —        | caso (join 1:1) |
| **FATO_EVENTOS_OPERACIONAIS** (068)        |    ✓     |      —       |      ✓       |      —        |   (✓)      |      —        |      —        |      —        | unidade participante |
| **FATO_EVENTOS_APREENSOES** (069)          |    ✓     |      —       |      ✓       |      —        |    ✓       |     (✓)       |      —        |      ✓        | unidade participante |
| **FATO_EVENTOS_PRISOES** (0610)            |    ✓     |      —       |      ✓       |      —        |    ✓       |      —        |     (✓)       |      —        | unidade participante |

> (✓) = chave primária na carga base do TEMP_LINK
> ✓ = chave gerada na carga base do TEMP_LINK
> ✓* = chave adicionada via LEFT JOIN de outra tabela (multiplica linhas, ver "Diagnóstico de volume")
> — = chave não preenchida (NULL implícito)
>
> "join 1:1" = LEFT JOIN com `vCarregaUnidAreaDirCoorGeralDoCaso` por `%CASOSKEY`; só não multiplica linhas se o `IPL` for único em `TEMP_DIM_CASOS`.
>
> Mudanças desde 2026-10-09 (commit `668c9e5` e alterações locais sem commit): saíram os LEFT JOINs de 061 (Casos_Data), 064 (Casos_Data, eventos, eventos-apreensões, eventos-prisões), 065 (itens ePol, Casos_Data), 066 (operações, itens, Casos_Data), 068 (unidade do caso, itens, eventos-apreensões, eventos-prisões), 069 e 0610.

---

## Campos de data e classificação analítica na Link Table

Cada linha da Link Table carrega campos de data e classificação que funcionam como **dimensão de tempo centralizada**, permitindo filtrar e agregar todos os fatos por data sem criar dimensões de calendário separadas por fato.

|     Campo      |             Conteúdo             |
|      ---       |               ---                |
|     `Data`     | Data do evento relevante do fato |
|     `Ano`      |            `YEAR(Data)`          |
|     `Mês`      |       `MONTH(Data)` (texto)      |
|   `Mês (Num)`  |       `MONTH(Data)` (número)     |
| `Tipo da Data` | `'Apreensão'` \| `'Instauração do Caso'` \| `'Deflagração da Operação'` \| `'Evento do Caso'` \| `'Evento Operacional'` \| `'Evento Apreensão'` \| `'Evento Prisão'` |
|     `Fonte`    | `'Apreensões ePol'` \| `'Apreensões SIGACrim'` \| `'Apreensões Palas'` \| `'Operações SIGACrim'` \| `'Operações Palas'` \| `'Casos ePol'` \| `'Casos_Data ePol'` \| `'Eventos Operacionais SIGACrim'` \| `'Eventos Apreensões SIGACrim'` \| `'Eventos Prisões SIGACrim'` |
| `Tipo do Fato` | `'Apreensões'` \| `'Operações'` \| `'Casos'` \| `'Casos_Data'` \| `'Eventos Operacionais'` \| `'Eventos Apreensões'` \| `'Eventos Prisões'` |

Data comum por bloco: 061 `GestãoBens Item Data Apreensão`; 062, 063, 064, 065 `DT_DEFLAGRACAO`; 066 `Proc. Data Instauração`; 067 `Proc_Data Data`; 068 `dt_evento`; 069 `dt_apreensao`; 0610 `dt_evento` (trazida por LEFT JOIN com `TEMP_TABELAOEVENTOS_ID_UNIFICADO` por `%EVENTOSKEY`, junto com `Tipo da Data`, `Fonte` e `Tipo do Fato`).

Nenhuma métrica do app filtra `[Tipo do Fato] = {'Casos'}` nem `[Tipo da Data] = {'Instauração do Caso'}`: as linhas do 066 servem só para associar o caso (atributos e métricas "Em Andamento").

---

## Arquivos fonte

| Script | Fato carregado | TEMP_LINK gerada |
|---|---|---|
| `061_FATO_APREENSOES_DIM_CASOS_APREENSAO_BENS.qvs` | FATO_APREENSOES (ePol) | `LINK_TABLE_APREENSOES_OPERACOES_CASOS` (inicial) |
| `062_FATO_APREENSOES_SIGACRIMHOMOLOGADAS.qvs` | FATO_APREENSOES (SIGACrim, só 2024) | `TEMP_LINK_TABLE_..._APREENSOES_SIGACRIM` |
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

Observação: os nomes das TEMP_LINK de 069/0610 (`..._EXTERNAS_ESTRANGEIRO`) são herdados; desde a unificação (033/034 `*_UNIFICADOS`) esses blocos incluem também eventos PF.

---

## Diagnóstico de volume (revisto em 2026-10-23)

**Histórico.** Em 2026-10-09 a link table passava de **61 milhões de linhas**, por LEFT JOINs 1:N entre fatos em quase todos os blocos. O commit `668c9e5` (2026-10-14) e alterações locais posteriores retiraram a maior parte desses joins. **Medição de 2026-10-23: 2.419.461 linhas** (redução de ~96% sobre os ~61 milhões). Uma medição anterior no mesmo dia (2.505.344) era de outro reload. Nenhuma linha com `Tipo do Fato` nulo. Distribuição informada pelo desenvolvedor:

| Tipo do Fato | Linhas | % | Chave própria distinta | Operações distintas | Linhas extras por fan-out |
|---|---:|---:|---:|---:|---|
| Casos_Data | 1.202.265 | 49,7% | 1.192.846 `%CASOSDATAKEY` | 12.537 | ~9.400 (0,8%), join do 067 com operações |
| Apreensões | 619.277 | 25,6% | — | 12.287 | — |
| Casos | 363.389 | 15,0% | — | 0 | — (uma linha por caso) |
| Operações | 101.243 | 4,2% | — | 17.166 | ~84.000 (~5,9 linhas por operação), join do 064 com itens ePol |
| Eventos Operacionais | 50.781 | 2,1% | — | 1.123 | — |
| Eventos Apreensões | 43.856 | 1,8% | — | 911 | — |
| Eventos Prisões | 38.650 | 1,6% | — | 1.076 | — |
| **Total** | **2.419.461** | | | | |

Conclusões: os fan-outs restantes são pequenos (~94 mil linhas, ~4%). O tamanho que sobra vem do próprio Casos_Data (1,19 milhão de linhas distintas), em boa parte de IPLs antigos que estão no modelo só por atributos. Todas as prisões de eventos têm `Tipo do Fato` (a suspeita sobre o 0610 não se confirmou).

Teste de IPL duplicado em `TEMP_DIM_CASOS` (2026-10-23): **nenhum IPL duplicado**. Os joins com a unidade do caso (061, 062, 064, 067) são 1:1.

**LEFT JOINs que ainda multiplicam linhas:**

| Bloco | Join | Efeito |
|---|---|---|
| 064 Operações SIGACrim | itens ePol (`TEMP_DIM_CASOS_APREENSAO_BENS`) por `%CASOSKEY` + `%OPERACOESKEY`, trazendo `%APREENSOESKEY` e `%SUBCLASSESKEY` | cada operação vira uma linha por item ePol da operação. É redundante: as linhas do 061 já ligam item, caso e operação. **Candidato a remover.** |
| 067 Casos_Data | operações SIGACrim (`TEMP_SIGACrimHomologadas`) por `%CASOSKEY`, trazendo `%OPERACOESKEY` | cada linha de Casos_Data vira uma linha por operação do caso. Casos_Data é a tabela mais longa do ePol, então este é provavelmente **o maior fan-out restante**. **Candidato a remover.** |
| 067 Casos_Data | operações Palas por `%CASOSKEY` + `%OPERACOESKEY` | depois do join anterior, a tabela já tem `%OPERACOESKEY`; o Qlik casa pelas duas chaves e linhas com `%OPERACOESKEY` nulo não casam. Na prática **não liga nenhuma operação Palas** ao Casos_Data. Remover junto com o anterior. |

**Joins de unidade do caso (061, 062, 064, 067).** São 1:1 se o `IPL` for único em `TEMP_DIM_CASOS`. No código atual (commit `c0f84c1` de 2026-10-15 e alterações locais) a ext exclui `Proc. Tipo = 'NC'` (051) e usa INNER JOIN (101), o que elimina a principal fonte de duplicidade. Ainda podem existir IPLs repetidos (procedimentos migrados fora do padrão, os 83 casos listados no cabeçalho do 051). Teste sugerido no tra, antes do 061:

```qlik
TESTE_IPL_DUPLICADO:
LOAD IPL, Count("Proc. Identificação") AS QtdLinhas
RESIDENT TEMP_DIM_CASOS
GROUP BY IPL;
// Verificar no visualizador de dados se há QtdLinhas > 1
```

**Outros pontos de atenção:**
- **0610**: o bloco base não tem `Data` nem `Tipo do Fato`; ambos vêm do LEFT JOIN com o evento. Medição de 2026-10-23: nenhuma linha com `Tipo do Fato` nulo. Continua frágil se um dia o filtro de eventos do tra 032 (`Year(dt_evento) > 2023`) e o das prisões divergirem.
- **Anos anteriores a 2022 no campo `[Ano]`**: IPLs antigos entram no modelo só para dar atributos (unidade, data de instauração) a apreensões, operações e eventos a partir de 2022. Mas as linhas do 066 (`Instauração do Caso`) e do 067 (`Evento do Caso`) desses IPLs trazem as datas antigas para `[Data]`/`[Ano]`. As métricas do ePol já cortam em 2022 (`vAnoMinimoEpol` no app 076), mas `Min([Ano])` e as listas de ano mostram esses anos.

Linhas por período (2026-10-23; "antes de 2022" inclui linhas sem data): Casos_Data 79.676 antes / 1.122.589 a partir de 2022; Casos 67.081 antes / 296.308 a partir de 2022.

Proposta detalhada: [artifacts/propostas/2026-10-23_ENXUGAMENTO_LINK_TABLE_064_066_067.md](../artifacts/propostas/2026-10-23_ENXUGAMENTO_LINK_TABLE_064_066_067.md) (filtra Casos_Data no tra 039, em vez de no 067).

**Situação em 2026-10-24:** aplicadas a variável `vAnoMinimoAnalise` (tra 021), o filtro de Casos_Data a partir de 2022 (tra 039) e a data nula para casos instaurados antes de 2022 (tra 066). **Rejeitadas** a remoção dos joins do 067 (sem eles, as métricas do ePol filtradas por operação zeram; o join com Palas funciona) e a remoção do join do 064 (ao selecionar uma subclasse, as métricas de operações e do ePol zeraram; o join deve ser restaurado).

**Regra:** na link table, a seleção de um valor só alcança as linhas que contêm aquela chave. Um LEFT JOIN que leva a chave de outro fato é necessário sempre que as métricas de um fato precisam ser filtradas pelos atributos do outro. O fan-out é o preço desse filtro cruzado.

### Matriz de testes de filtros cruzados (a rodar)

Os joins retirados no commit `668c9e5` e nas alterações locais podem ter quebrado filtros cruzados que ninguém testou ainda. Para cada filtro (linha), selecionar um valor e verificar se cada família de métricas (coluna) continua com valor quando deveria:

| Filtro selecionado | Operações | Apreensões | ePol (Casos_Data) | Eventos (oper., apreensões, prisões) |
|---|---|---|---|---|
| Atributo da operação (ex.: área de fronteira) | — | ? | ✓ (join do 067) | ? |
| Subclasse / material / classe / categoria (DIM_TNBIA) | ✓ join do 064 restaurado (2026-10-27) | ✓ (desde a correção da chave, 2026-10-27) | ✓ filtro na métrica (2026-10-27) | ? |
| Classe de descapitalização (FATO_APREENSOES) | ✓ join do 064 restaurado (2026-10-27) | ✓ | ✓ filtro na métrica (2026-10-27) | ? |
| Atributo do caso (ex.: tipo penal, área de atribuição) | ? | ? | — | ? |
| Atributo do evento (ex.: tipo de evento pf/externo/estrangeiro) | ? | ? | ? | — |
| Unidade, UF, SR | ? | ? | ? | ? |

Legenda: ✓ funciona; ✗ zera; ? a testar. Restaurar (ou criar) só os joins que um filtro realmente usado no app exigir.

Observação sobre ePol × subclasse: as linhas de Casos_Data não têm `%SUBCLASSESKEY`. Restaurar o LEFT JOIN do 067 com os itens ePol foi medido em 2026-10-24: o Casos_Data passaria de 1.123.515 para 6.630.048 linhas (78.363 casos com itens) — inviável. A solução proposta é filtrar na métrica: [artifacts/propostas/2026-10-24_FILTRO_EPOL_POR_APREENSAO_NA_METRICA.md](../artifacts/propostas/2026-10-24_FILTRO_EPOL_POR_APREENSAO_NA_METRICA.md).

**Regra para filtros cruzados:** se o LEFT JOIN gera poucas linhas (ex.: 064 operações × itens, ~84 mil), usar o join; se gera milhões (ex.: 067 Casos_Data × itens), filtrar na métrica com `P()` sobre a chave comum.

### Próximos passos propostos (a validar com reload) — texto original de 2026-10-23, ver situação acima

1. **064**: remover o LEFT JOIN com `TEMP_DIM_CASOS_APREENSAO_BENS`.
2. **067**: remover os LEFT JOINs com `TEMP_SIGACrimHomologadas` e com `TEMP_Palas_Operacoes_Tratadas_2022_2023`. A relação Casos_Data ↔ operação continua existindo pelo caso (`%CASOSKEY`).
3. **066**: manter uma linha por caso (necessária para as métricas "Em Andamento" e para os atributos), mas só preencher `Data`/`Ano`/`Mês`/`Mês (Num)` quando `Year([Proc. Data Instauração]) >= 2022`. Nenhuma métrica usa `Tipo do Fato = 'Casos'`.
4. **067**: carregar na link table só as linhas com `Year("Proc_Data Data") >= 2022`, ou anular a data das anteriores como no 066. As métricas do ePol com data já ignoram essas linhas, e a redução de linhas é direta.
5. Rodar o teste de `IPL` duplicado e confirmar que os joins de unidade do caso são 1:1.

Os passos 3 e 4 resolvem também o `Min([Ano])` menor que 2022 nos títulos das medidas.

### Como medir

No fim do `0722_DIM_UNIDADE_SUBUNIDADE.qvs`, antes do `StoreAndDrop` da link table:

```qlik
TESTE_VOLUME_LINK_TABLE:
LOAD [Tipo do Fato], Count([Tipo do Fato]) AS QtdLinhas
RESIDENT LINK_TABLE_APREENSOES_OPERACOES_CASOS
GROUP BY [Tipo do Fato];
```

Comparar a soma com os 61 milhões de 2026-10-09 e registrar o resultado no `CLAUDE.md` (seção 7).

### Desenho enxuto (meta de longo prazo, decidido em 2026-10-09)

**Uma linha de link por linha de fato**, sem JOIN entre fatos:

| Campo | Conteúdo |
|---|---|
| chave do fato | a mesma chave do `FATO_*` (ex.: `%APREENSOESKEY`, `%OPERACOESKEY`) |
| `%DATA_KEY` | data comum do fato (número inteiro) → calendário (`DIM_CALENDARIO`: Data, Ano, Mês, Mês (Num) etc.) |
| `%UNIDADE_KEY` | uma única unidade por fato: caso (ePol, SIGACrim), `UNIDADE` da operação (Palas), unidade participante (eventos) |
| `%AREA_KEY` | área de atribuição comum → dimensão de área (Área, Diretoria, CG) |
| `Tipo do Fato` | um valor por fato (as métricas já filtram por ele) |

Cada `FATO_*` continua ligado às suas próprias dimensões pela chave do fato. Saem da link table as chaves de outros fatos, `Ano`/`Mês`/`Mês (Num)` (vão para o calendário), `Tipo da Data` (redundante com `Tipo do Fato`) e os textos de unidade/área (vão para dimensões). O código atual já cumpre a maior parte do item "sem JOIN entre fatos"; faltam 064/067, o calendário e a saída dos textos de unidade/área.
