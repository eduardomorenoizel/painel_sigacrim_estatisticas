# Proposta — Campo `[Evento em Unidade Diferente do Caso]` (2026-10-27)

## Motivo

O filtro `vFEvenPr10Exec` (app 073) deve considerar só eventos em que a unidade participante
(`[Unidade Sigla do Evento Operacional]`) é diferente da unidade do caso (`[Unidade Sigla do Caso]`).

- O set analysis não compara dois campos da mesma linha: a seleção é feita valor a valor, por campo.
- Desde 2026-10-23 as linhas de eventos na link table não têm `[Unidade Sigla do Caso]`: o LEFT JOIN do 068 com a unidade do caso
  foi retirado. Os dois campos nunca aparecem na mesma linha.

**Solução:** calcular a comparação no tra 068 e gravá-la como campo do `FATO_EVENTOS_OPERACIONAIS`.
A granularidade é a mesma: `%EVENTOSKEY` = `id_ordem_original_evento`, isto é, uma linha por evento × unidade participante × participação,
com um único `IPL` e uma única `unidade_participante`. Usa `ApplyMap`, então a link table **não ganha nenhuma linha**.

Valores: `'Sim'` (unidades diferentes), `'Não'` (mesma unidade), `'Sem caso'` (evento sem IPL ou IPL fora da `TEMP_DIM_CASOS`).

## 1. tra `06_fatos/068_FATO_EVENTOS_OPERACIONAIS.qvs`

Antes de `FATO_EVENTOS_OPERACIONAIS:`, criar o mapeamento IPL → unidade do caso. A regra é a mesma do `vCarregaUnidAreaDirCoorGeralDoCaso` (tra 021),
inclusive a correção FICCO/GISE:

```qlik
// IPL -> Unidade Sigla do Caso (mesma regra do vCarregaUnidAreaDirCoorGeralDoCaso, tra 021)
MAP_IPL_UNIDADE_SIGLA_DO_CASO:
MAPPING LOAD DISTINCT
    IPL,
    Upper(Trim(
        IF(
            ApplyMap('MapIPLUnidadeFiccoGise', IPL, 0) > 0,
            ApplyMap('MapIPLUnidadeFiccoGise', IPL),
            "Proc. Unidade Exercício"
        )
    ))
RESIDENT TEMP_DIM_CASOS;
```

No `LOAD` do `FATO_EVENTOS_OPERACIONAIS`, depois de `houve_prisao,`:

```qlik
    // Unidade participante diferente da unidade do caso (IPL)
    IF(
        ApplyMap('MAP_IPL_UNIDADE_SIGLA_DO_CASO', IPL, '#SEM_CASO#') = '#SEM_CASO#',
        'Sem caso',
        IF(
            Upper(Trim(unidade_participante)) = ApplyMap('MAP_IPL_UNIDADE_SIGLA_DO_CASO', IPL),
            'Não',
            'Sim'
        )
    ) AS [Evento em Unidade Diferente do Caso], // Texto 'Sim' / 'Não' / 'Sem caso'
```

## 2. app `03_fatos/032_FATOS.qvs`

```qlik
[FATO_EVENTOS_OPERACIONAIS]:
LOAD DISTINCT
    [%EVENTOSKEY]
    ,[houve_apreensao]
    ,[houve_prisao]
    ,[Evento em Unidade Diferente do Caso]
    ,[qtd_presos]
FROM [$(vCaminhoTransformadosV3)FATO_EVENTOS_OPERACIONAIS.qvd]
(qvd);
```

## 3. app `07_variaveis_de_metricas/073_...` (já aplicado)

```qlik
SET vFEvenPr10Exec = cd_tipo_evento_fk = {'pf'}, cd_tipo_participacao = {'execucao_direta'}, [Evento em Unidade Diferente do Caso] = {'Sim'}, [Tipo do Fato] = {'Eventos Operacionais'};
```

## Validação após o reload

1. O reload do tra deve terminar sem erro. Se aparecer "Mapping table not found" para `MapIPLUnidadeFiccoGise`, ou "table not found" para
   `TEMP_DIM_CASOS`, a ordem de carga precisa ser revista.
2. Fazer uma caixa de tabela com `[Evento em Unidade Diferente do Caso]` e `Count(DISTINCT [%EVENTOSKEY])`, filtrada por
   `cd_tipo_evento_fk = 'pf'`. Conferir se a proporção de `'Sim'` é plausível.
3. Conferir o formato das duas siglas: tabela com `IPL`, `[Unidade Sigla do Evento Operacional]` e `[Unidade Sigla do Caso]`
   (do caso, via DIM/link) para alguns `'Sim'`. Se as siglas vierem em formatos diferentes (ex.: `DRE/SR/PF/SP` × `DRE/SR/PF/SP `
   ou abreviações diferentes), quase tudo vira `'Sim'`, e a comparação precisa de normalização.
4. Contar a link table por `[Tipo do Fato]`: o número de linhas não deve mudar.
