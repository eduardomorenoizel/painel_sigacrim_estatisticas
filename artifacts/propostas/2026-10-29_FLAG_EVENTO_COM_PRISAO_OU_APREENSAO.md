# Proposta — Campo `[Evento com Prisão ou Apreensão]`, filtros `vFEvenPr10Exec`/`vFEvenPr10Info` e correção do `|` no 073 (2026-10-29)

## Motivo

Especificações completas dos dois filtros Pr10 do app 073, revistas pelo desenvolvedor em 2026-10-29:

**`vFEvenPr10Exec`**
> Eventos PF (`cd_tipo_evento_fk = 'pf'`), em que a unidade do evento (`unidade_participante`) se identifica como executora
> (`cd_tipo_participacao = 'execucao_direta'`), **que tenham gerado prisões ou apreensões** (`houve_apreensao = 'Sim'` ou
> `houve_prisao = 'Sim'`), e cujos procedimentos cartorários foram lavrados em outra unidade (`[Evento em Unidade Diferente do Caso] = 'Sim'`).

**`vFEvenPr10Info`**
> Eventos de qualquer tipo (PF, externos e estrangeiros) em que a unidade do evento (`unidade_participante`) é prestadora de informações
> (`cd_tipo_participacao = 'prestacao_info'`), **que tenham gerado prisões ou apreensões** (`houve_apreensao = 'Sim'` ou `houve_prisao = 'Sim'`)
> realizadas por outras unidades ou por outras forças policiais.

| Requisito | `vFEvenPr10Exec` hoje | `vFEvenPr10Info` hoje |
|---|---|---|
| Tipo de evento | `cd_tipo_evento_fk = {'pf'}` ✅ | sem filtro (qualquer tipo) ✅ |
| Participação da unidade do evento | `execucao_direta` ✅ | `prestacao_info` ✅ |
| Gerou prisão ou apreensão | **falta** | **falta** |
| Lavratura em outra unidade | `[Evento em Unidade Diferente do Caso] = {'Sim'}` ✅ | não se aplica |
| Prisão/apreensão feita por outra unidade ou força | não se aplica | ✅ garantido pela deduplicação (ver abaixo) |

**Por que o `vFEvenPr10Info` não precisa de outro filtro para "realizadas por outras unidades ou forças":** na primeira etapa da
deduplicação (tra 032), cada `unidade_participante` fica com **uma só participação por evento**, a de maior prioridade
(execução direta > prestação de informação > prestação de apoio). Assim, uma unidade com `prestacao_info` num evento não tem
`execucao_direta` nesse mesmo evento. Quem executou foi outra unidade da PF (eventos PF) ou outra força policial (eventos externos e
estrangeiros). Essa premissa é conferida no item 6 da validação.

A condição "gerou prisão ou apreensão" não estava em nenhum dos dois filtros, e é um **OU** entre dois campos. Numa lista de modificadores do set analysis,
`houve_apreensao = {'Sim'}, houve_prisao = {'Sim'}` funciona como **E**: só contaria eventos com prisão *e* apreensão.

**Solução (caminho A, escolhido em 2026-10-29):** calcular o OU no tra 068 e gravá-lo como campo do `FATO_EVENTOS_OPERACIONAIS`.
É a mesma regra do `[Evento em Unidade Diferente do Caso]` (decisão de 2026-10-27). A granularidade é a mesma (`%EVENTOSKEY` = `id_ordem_original_evento`),
e a link table **não ganha linhas**.

**A unidade é sempre a `unidade_participante`.** A `unidade_registradora` não entra (decisão de 2026-10-29): várias unidades podem registrar o
mesmo evento, a deduplicação do tra 032/033 escolhe o evento sem levar a unidade registradora em conta, e por isso ela não é uma informação útil.

### Valores dos campos de origem (reportados pelo desenvolvedor em 2026-10-29, contagem de `%EVENTOSKEY` no app)

| `houve_apreensao` | `houve_prisao` | Linhas |
|---|---|---|
| Não | Sim | 37.621 |
| Sim | Sim | 8.253 |
| Sim | Não | 5.039 |
| nulo | nulo | 1 |

- Os valores são `'Sim'`/`'Não'`, com inicial maiúscula.
- **Não existe a combinação Não/Não.** Com os dados de hoje, a nova condição só exclui a linha com os dois campos nulos. Os
  dois filtros devem mudar no máximo 1 evento, somados. Mesmo assim, a regra precisa estar no filtro: se a fonte passar a gravar eventos sem
  prisão nem apreensão, eles serão excluídos.

Valores do campo novo: `'Sim'` (houve prisão ou apreensão) e `'Não'` (nenhuma das duas, ou os dois campos nulos).

## 1. tra `06_fatos/068_FATO_EVENTOS_OPERACIONAIS.qvs`

No `LOAD` do `FATO_EVENTOS_OPERACIONAIS`, depois de `houve_prisao,`:

```qlik
    houve_apreensao, // Boleano sim/não
    houve_prisao, // Boleano sim/não

    // Evento que gerou prisão ou apreensão (OU entre houve_apreensao e houve_prisao).
    // Calculado aqui porque o set analysis não faz OU entre dois campos na mesma lista de modificadores.
    // Valores na origem: 'Sim' / 'Não' (verificado em 2026-10-29). Os dois nulos viram 'Não'.
    IF(
        houve_apreensao = 'Sim' OR houve_prisao = 'Sim',
        'Sim',
        'Não'
    ) AS [Evento com Prisão ou Apreensão], // Texto 'Sim' / 'Não'
```

## 2. app `03_fatos/032_FATOS.qvs`

```qlik
[FATO_EVENTOS_OPERACIONAIS]:
LOAD DISTINCT
    [%EVENTOSKEY]
    ,[houve_apreensao]
    ,[houve_prisao]
    ,[Evento com Prisão ou Apreensão]
    ,[Evento em Unidade Diferente do Caso]
    ,[qtd_presos]
FROM [$(vCaminhoTransformadosV3)FATO_EVENTOS_OPERACIONAIS.qvd]
(qvd);
```

## 3. app `07_variaveis_de_metricas/073_VARIAVEIS_DE_METRICAS_DE_EVENTOS_OPERACIONAIS.qvs`

### 3.1 Filtros `vFEvenPr10Info` e `vFEvenPr10Exec` (linhas 925–931)

Substituir a linha 925 (`vFEvenPr10Info`), o comentário e o `SET` do `vFEvenPr10Exec` (linhas 926–931) por:

```qlik
// Eventos de qualquer tipo (pf, externo, estrangeiro) em que a unidade do evento (unidade_participante) é prestadora de
// informações (cd_tipo_participacao = 'prestacao_info') e que geraram prisões ou apreensões ([Evento com Prisão ou Apreensão] = 'Sim',
// isto é, houve_apreensao = 'Sim' ou houve_prisao = 'Sim') realizadas por outras unidades ou outras forças policiais.
// "Por outras unidades/forças" não precisa de filtro: na deduplicação do tra 032, cada unidade participante fica com uma só
// participação por evento (execução direta > prestação de informação > prestação de apoio); quem tem 'prestacao_info' não executou.
// A unidade registradora não é considerada.
SET vFEvenPr10Info  = cd_tipo_participacao = {'prestacao_info'}, [Evento com Prisão ou Apreensão] = {'Sim'}, [Tipo do Fato] = {'Eventos Operacionais'};

// Eventos PF (cd_tipo_evento_fk = 'pf') em que a unidade do evento (unidade_participante) se identifica como executora
// (cd_tipo_participacao = 'execucao_direta'), que geraram prisões ou apreensões ([Evento com Prisão ou Apreensão] = 'Sim',
// isto é, houve_apreensao = 'Sim' ou houve_prisao = 'Sim') e cujos procedimentos cartorários foram lavrados em outra unidade
// ([Evento em Unidade Diferente do Caso] = 'Sim'). A unidade registradora não é considerada.
// Os dois campos são calculados no tra 068 (FATO_EVENTOS_OPERACIONAIS):
//   artifacts/propostas/2026-10-27_FLAG_EVENTO_EM_UNIDADE_DIFERENTE_DO_CASO.md
//   artifacts/propostas/2026-10-29_FLAG_EVENTO_COM_PRISAO_OU_APREENSAO.md
// [Tipo da Data] = {'Evento Operacional'} não entra aqui: o GerarConjunto12Even já o acrescenta nas variantes por [Ano].
// Sem '>' no final: o SUB ainda acrescenta modificadores depois do filtro.
SET vFEvenPr10Exec  = cd_tipo_evento_fk = {'pf'}, cd_tipo_participacao = {'execucao_direta'}, [Evento com Prisão ou Apreensão] = {'Sim'}, [Evento em Unidade Diferente do Caso] = {'Sim'}, [Tipo do Fato] = {'Eventos Operacionais'};
```

**Ordem de aplicação:** aplicar este item só **depois** do reload do tra com o item 1. Se o campo ainda não existir no modelo, as métricas
`vEvenPr10Info*` e `vEvenPr10Exec*` podem dar erro de expressão ou ignorar a condição em silêncio. Nos dois casos, o resultado fica errado.

### 3.2 Correção do `|` sobrando na SUB `GerarConjunto12EvenApre` (linha 104)

Independe dos itens 1 e 2; pode ser aplicada já.

Hoje (linhas 101–105):

```qlik
                $($(vNomeFiltro))
                ,[Ano do Evento Apreensão] = {@(=MAX([Ano do Evento Apreensão]-1))}|
                $($(vNomeFiltro))
                ,[Ano do Evento Apreensão] = {@(=MAX([Ano do Evento Apreensão]-1))}|
                ,$(vConjEvenApreDtMesAnoEvenAprePfEmNumeros)
```

Correto (retirar o `|` do fim da linha 104):

```qlik
                $($(vNomeFiltro))
                ,[Ano do Evento Apreensão] = {@(=MAX([Ano do Evento Apreensão]-1))}|
                $($(vNomeFiltro))
                ,[Ano do Evento Apreensão] = {@(=MAX([Ano do Evento Apreensão]-1))}
                ,$(vConjEvenApreDtMesAnoEvenAprePfEmNumeros)
```

**Efeito do erro atual:** a lista fica com 13 partes em vez de 12. A 12ª variante, que gera as variáveis
`v*PfEmNumAnoEvenApreAnterior`, fica sem `$(vConjEvenApreDtMesAnoEvenAprePfEmNumeros)`, e a 13ª é ignorada pelo `FOR i = 1 TO 12`.
O reload não acusa erro. Afeta os 13 radicais de apreensões em eventos (`vBaseApre`, `vApre*`), inclusive os `SomAnter`.
As SUBs `GerarConjunto12Even` e `GerarConjunto12EvenPris` estão corretas.

## Validação após o reload

1. O reload do tra deve terminar sem erro.
2. No app, fazer uma caixa de tabela com `houve_apreensao`, `houve_prisao`, `[Evento com Prisão ou Apreensão]` e
   `Count([%EVENTOSKEY])`. O resultado esperado, com os dados de 2026-10-29:
   - Não/Sim/Sim: 37.621
   - Sim/Sim/Sim: 8.253
   - Sim/Não/Sim: 5.039
   - nulo/nulo/Não: 1
3. Comparar `$(vEvenPr10ExecDtMesAno)` e `$(vEvenPr10InfoDtMesAno)` antes e depois do item 3.1, sem seleções e com um ano
   selecionado. Somadas, as diferenças devem ser de 0 ou 1 evento.
4. Contar a link table por `[Tipo do Fato]`: o número de linhas não deve mudar.
5. Para o item 3.2, com um `[Ano do Evento Apreensão]` selecionado, comparar `$(vBaseAprePfEmNumAnoEvenApreAnterior)`
   com `$(vBaseApreAnoEvenApreAnterior)`. Depois da correção, a variante
   PF EM NÚMEROS deve ser menor ou igual à variante sem esse corte. Antes, as duas davam o mesmo valor.
