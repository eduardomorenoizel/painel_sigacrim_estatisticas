# Proposta — enxugamento final da link table (tra 021, 039, 064, 066, 067)

Data: 2026-10-23. Situação (2026-10-23, informada pelo desenvolvedor):

| Mudança | Situação |
|---|---|
| 1. Variável `vAnoMinimoAnalise` (tra 021) | **Aplicada** |
| 2. Casos_Data a partir de 2022 (tra 039) | **Aplicada** |
| 3. Sem join com itens ePol (tra 064) | **Rejeitada (2026-10-24)**: ao selecionar uma subclasse, as métricas de operações e do ePol zeraram. Restaurar o join. |
| 4. Data nula para casos instaurados antes de 2022 (tra 066) | **Aplicada (2026-10-24)**, funcionando |
| 5. Sem join com operações (tra 067) | **Rejeitada**: zerou métricas do ePol filtradas por operação. O segundo join (Palas) **funciona** (teste de 2026-10-24), ao contrário do que esta proposta afirmava. |

**Correção do raciocínio da mudança 5.** A justificativa "a relação Casos_Data ↔ operação continua pelo `%CASOSKEY`" estava errada. Na link table, ao selecionar uma operação, só ficam possíveis as linhas que têm aquele `%OPERACOESKEY`; linhas de Casos_Data sem essa chave saem, mesmo sendo do mesmo caso. O join do 067 existe para permitir filtrar métricas do ePol por atributos da operação e deve ficar.

**Risco da mudança 3 (mesmo mecanismo).** Sem o join do 064, as linhas de operação não têm `%APREENSOESKEY`/`%SUBCLASSESKEY`; ao filtrar por atributo da apreensão (item, subclasse TNBIA, classe de descapitalização), as métricas de operações podem zerar. Se esse filtro for usado, desfazer a mudança 3.

## Base (medições de 2026-10-23)

| Tipo do Fato | Linhas | Antes de 2022 (ou sem data) | 2022 em diante |
|---|---:|---:|---:|
| Casos_Data | 1.202.265 | 79.676 | 1.122.589 |
| Casos | 363.389 | 67.081 | 296.308 |
| Operações | 101.243 (17.166 operações) | — | — |
| Link table total | 2.419.461 | | |

Observação: o teste `If([Ano] >= 2022, ...)` coloca as linhas **sem data** no grupo "antes de 2022".

## Objetivos

1. Tirar os dois LEFT JOINs que ainda multiplicam linhas (064 e 067).
2. Tirar do campo `[Ano]` os anos anteriores a 2022 (IPLs antigos estão no modelo só por atributos), o que resolve `Min([Ano])` nos títulos.
3. Não perder nenhuma associação usada pelas métricas, inclusive as "Em Andamento".

## Mudanças

### 1. `tra/02_subrotinas_e_variaveis/021_VARIAVEIS_CAMINHOS_UNIDADES_AREAS_DIRETORIAS_CGS.qvs` — nova variável

Acrescentar junto às demais variáveis:

```qlik
// Ano mínimo das análises: IPLs (casos) anteriores entram no modelo só para
// dar atributos às apreensões, operações e eventos a partir deste ano.
SET vAnoMinimoAnalise = 2022;
```

### 2. `tra/03_carregamento_qvds/039_TEMP_DIM_CASOS_DATA.qvs` — só Casos_Data a partir de 2022

Filtrar na carga, para que fato (067), link table (067) e dimensão (0714) fiquem coerentes:

```qlik
TEMP_DIM_CASOS_DATA:
LOAD
    *
FROM [$(vCaminhoExtraidosV2)TEMP_DIM_CASOS_DATA.qvd]
(qvd)
WHERE Year("Proc_Data Data") >= $(vAnoMinimoAnalise);
```

- Efeito: até −79.676 linhas na link table (e o mesmo na FATO_CASOS_DATA e na DIM_CASOS_DATA).
- Linhas sem `Proc_Data Data` também saem. Nenhuma métrica do ePol usa Casos_Data sem data (todas as variantes do 076 filtram ano >= 2022).
- O `WHERE` torna a leitura do QVD não otimizada; com ~1,2 milhão de linhas o custo é pequeno.

### 3. `tra/06_fatos/064_FATO_OPERACOES_SIGACRIMHOMOLOGADAS.qvs` — remover join com itens ePol

Comentar ou apagar o bloco (linhas 499-505 no código de 2026-10-23):

```qlik
// REMOVIDO em 2026-10-23: redundante com o 061 (as linhas de apreensões ePol já ligam
// %CASOSKEY, %OPERACOESKEY e %APREENSOESKEY) e multiplicava cada operação pelos itens.
// LEFT JOIN (TEMP_LINK_TABLE_APREENSOES_OPERACOES_CASOS_OPERACOES_SIGACRIM)
// LOAD DISTINCT
//     AutoNumberHash128("IPL") AS [%CASOSKEY],
//     AutoNumberHash128(ID_OPERACAO) AS [%OPERACOESKEY],
//     AutoNumberHash128("GestãoBens Item ID") AS [%APREENSOESKEY],
//     AutoNumberHash128("GestãoBens Item Material Subclasse Código") AS [%SUBCLASSESKEY]
// RESIDENT TEMP_DIM_CASOS_APREENSAO_BENS;
```

- Efeito: cerca de −84.000 linhas (de 101.243 para algo próximo de 17.166 + operações Palas).
- Manter o LEFT JOIN com `vCarregaUnidAreaDirCoorGeralDoCaso` (1:1, confirmado sem IPL duplicado).

### 4. `tra/06_fatos/066_FATO_CASOS_DIM_CASOS.qvs` — manter a linha do caso, sem data antiga

A linha de cada caso continua (associação com DIM_CASOS, métricas "Em Andamento", unidade do caso). Só a data fica nula quando a instauração é anterior a 2022. Trocar as linhas 178-181:

```qlik
    If(Year([Proc. Data Instauração]) >= $(vAnoMinimoAnalise),
        Date([Proc. Data Instauração])) as Data,
    If(Year([Proc. Data Instauração]) >= $(vAnoMinimoAnalise),
        YEAR(date([Proc. Data Instauração]))) as "Ano",
    If(Year([Proc. Data Instauração]) >= $(vAnoMinimoAnalise),
        MONTH(date([Proc. Data Instauração]))) as "Mês",
    If(Year([Proc. Data Instauração]) >= $(vAnoMinimoAnalise),
        Num(MONTH(date([Proc. Data Instauração])))) as "Mês (Num)",
```

- Efeito: 0 linhas a menos; até 67.081 linhas deixam de levar anos antigos para `[Ano]`.
- Nenhuma métrica do app filtra `[Tipo do Fato] = {'Casos'}` nem `[Tipo da Data] = {'Instauração do Caso'}`.

### 5. `tra/06_fatos/067_FATO_CASOS_DATA_DIM_CASOS_DATA.qvs` — remover joins com operações

Comentar ou apagar os dois blocos (linhas 163-173 no código de 2026-10-23):

```qlik
// REMOVIDO em 2026-10-23: cada linha de Casos_Data era multiplicada pelas operações do caso;
// a relação Casos_Data <-> operação continua pelo %CASOSKEY. O join com Palas casava por
// %CASOSKEY + %OPERACOESKEY e, na prática, não ligava nenhuma operação.
// LEFT JOIN (TEMP_LINK_TABLE_APREENSOES_OPERACOES_CASOS_FATO_CASOS_DATA)
// LOAD DISTINCT
//     AutoNumberHash128("IPL") AS [%CASOSKEY],
//     AutoNumberHash128(ID_OPERACAO) AS [%OPERACOESKEY]
// RESIDENT TEMP_SIGACrimHomologadas;
//
// LEFT JOIN (TEMP_LINK_TABLE_APREENSOES_OPERACOES_CASOS_FATO_CASOS_DATA)
// LOAD DISTINCT
//     AutoNumberHash128("IPL") AS [%CASOSKEY],
//     AutoNumberHash128(ID_OPERACAO) AS [%OPERACOESKEY]
// RESIDENT TEMP_Palas_Operacoes_Tratadas_2022_2023;
```

- Efeito: cerca de −9.400 linhas.
- Manter o LEFT JOIN com `vCarregaUnidAreaDirCoorGeralDoCaso` (1:1).

## Efeito total estimado

Cerca de −173 mil linhas (~7%): de 2.419.461 para ~2,25 milhões. O ganho grande (61 milhões → 2,4 milhões) já foi feito; esta etapa é de limpeza do modelo e corrige o `Min([Ano])`.

## Validação depois do reload

1. Reload do tra e do app sem erro; sem chaves sintéticas novas.
2. Repetir a contagem por `[Tipo do Fato]` e o teste por período: o grupo "antes de 2022" de Casos_Data deve sumir; o de Casos deve aparecer só como linhas sem data.
3. Conferir que estes valores **não mudam** (comparar com o app antes da mudança):
   - `vIplInstDtMesAno`, `vIplRelatProcDtDtMesAno`, `vFlaInstDtMesAnoInst` (ePol, com data);
   - `vIplEmAnd`, `vReRecAtivEmAnd` (Em Andamento);
   - uma métrica de operações (ex.: `vOperHom`) e uma de apreensões.
4. Sem seleção, `Min([Ano])` deve ser 2022.
