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

**Histórico.** Em 2026-10-09 a link table passava de **61 milhões de linhas**, por LEFT JOINs 1:N entre fatos em quase todos os blocos. O commit `668c9e5` (2026-10-14) e alterações locais posteriores retiraram a maior parte desses joins. **Medição de 2026-10-23: 2.505.344 linhas** (redução de ~96%). A distribuição por `[Tipo do Fato]` ainda não foi medida (ver "Como medir"); ela mostra quanto ainda pesam os joins do 064 e do 067.

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
- **0610**: o bloco base não tem `Data` nem `Tipo do Fato`; ambos vêm do LEFT JOIN com o evento. Uma prisão cujo `id_ordem_original_evento` não esteja em `TEMP_TABELAOEVENTOS_ID_UNIFICADO` fica com `Tipo do Fato` nulo e some de todas as métricas. Verificar no reload: `Count({<[Tipo do Fato]={'Eventos Prisões'}>} [%EVENTOSPRISOESKEY])` contra o número de linhas da `FATO_EVENTOS_PRISOES`.
- **Anos anteriores a 2022 no campo `[Ano]`**: IPLs antigos entram no modelo só para dar atributos (unidade, data de instauração) a apreensões, operações e eventos a partir de 2022. Mas as linhas do 066 (`Instauração do Caso`) e do 067 (`Evento do Caso`) desses IPLs trazem as datas antigas para `[Data]`/`[Ano]`. As métricas do ePol já cortam em 2022 (`vAnoMinimoEpol` no app 076), mas `Min([Ano])` e as listas de ano mostram esses anos.

### Próximos passos propostos (a validar com reload)

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
