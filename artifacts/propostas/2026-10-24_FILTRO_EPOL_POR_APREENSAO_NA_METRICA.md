# Proposta — filtrar as métricas do ePol por atributos da apreensão na própria métrica

Data: 2026-10-24. Situação (2026-10-26): **aplicada pelo desenvolvedor**. A lista gerada está correta e o filtro funciona para a classe de descapitalização (`FATO_APREENSOES`). Subclasse/material não filtravam porque a `DIM_TNBIA` estava isolada no app (`%ITEM_SUBCLASSE_KEY` ≠ `%SUBCLASSESKEY`). **Corrigido em 2026-10-27** na origem (tra 0727 grava `%SUBCLASSESKEY`) e no app 052; desde então `GestãoBens Item Material`, `... Classe`, `... Categoria` e `... Subclasse Código` filtram as métricas do ePol. **Concluída.**

## Problema

Ao selecionar um atributo da apreensão (subclasse TNBIA, tipo de item, classe de descapitalização), as métricas do ePol zeram. Na link table, a seleção só alcança as linhas que têm a chave selecionada (`%SUBCLASSESKEY`, `%APREENSOESKEY`), e as linhas de Casos_Data não têm essas chaves.

Levar essas chaves para as linhas de Casos_Data (LEFT JOIN no tra 067) foi medido em 2026-10-24: o Casos_Data passaria de **1.123.515 para 6.630.048 linhas** (+5,5 milhões; 78.363 casos com itens). **Inviável.**

## Solução: o filtro vai para a métrica

Em cada métrica do ePol com data, acrescentar dois modificadores:

1. `[%CASOSKEY] = P({<datas limpas>} [%CASOSKEY])`: restringe aos casos que têm apreensão com os atributos selecionados, em qualquer data. Isso segue a decisão de que cada indicador conta pela sua própria data.
2. `[campo da apreensão] =` para todos os campos das tabelas de apreensão: anula essas seleções para as linhas de Casos_Data, que não as têm.

Sem seleção de apreensão, o resultado não muda: `P()` devolve os mesmos casos que as linhas de Casos_Data já alcançam pelas outras seleções.

A lista de campos de apreensão é **gerada na carga**, lendo as tabelas do modelo. Assim um campo novo em `DIM_APREENSOES` entra sozinho na lista.

## Mudanças

### 1. `app/02_subrotinas_variaveis_de_ambiente_e_efetivo/021_SUBROTINAS.qvs` — nova SUB (acrescentar ao final)

```qlik
//-----------------------------------------------------------------------------------------------
//   Função:     GerarListaSemSelecaoTabelas
//   Objetivo:   Gera em vNomeVariavel o texto "[Campo1]=,[Campo2]=,..." com os campos que
//               existem SOMENTE nas tabelas de vListaTabelas (separadas por '|'), mais os
//               campos de vCamposExtras (já no formato "[Campo]=,[Campo]=").
//               Usada em set analysis para anular seleções de um grupo de tabelas.
//               Campos compartilhados com tabelas fora da lista (ex.: unidade, caso) NÃO
//               entram, para não anular seleções de outros domínios.
//   Requisito:  chamar depois da carga das tabelas (fatos, link table e dimensões).
//-----------------------------------------------------------------------------------------------
SUB GerarListaSemSelecaoTabelas(vNomeVariavel, vListaTabelas, vCamposExtras)
    LET vListaGerada = '$(vCamposExtras)';
    FOR vIdxTabela = 0 TO NoOfTables() - 1
        LET vTabela = TableName($(vIdxTabela));
        IF SubStringCount('|$(vListaTabelas)|', '|$(vTabela)|') > 0 THEN
            FOR vIdxCampo = 1 TO NoOfFields('$(vTabela)')
                LET vCampo = FieldName($(vIdxCampo), '$(vTabela)');
                LET vCampoForaDaLista = 0;
                FOR vIdxTabela2 = 0 TO NoOfTables() - 1
                    LET vTabela2 = TableName($(vIdxTabela2));
                    IF SubStringCount('|$(vListaTabelas)|', '|$(vTabela2)|') = 0 THEN
                        IF FieldNumber('$(vCampo)', '$(vTabela2)') > 0 THEN
                            LET vCampoForaDaLista = 1;
                        END IF
                    END IF
                NEXT vIdxTabela2
                IF $(vCampoForaDaLista) = 0 AND Index('$(vListaGerada)', '[$(vCampo)]=') = 0 THEN
                    LET vListaGerada = '$(vListaGerada)' & If(Len('$(vListaGerada)') > 0, ',', '') & '[$(vCampo)]=';
                END IF
            NEXT vIdxCampo
        END IF
    NEXT vIdxTabela
    LET $(vNomeVariavel) = '$(vListaGerada)';
    LET vQtdCamposGerados = SubStringCount('$(vListaGerada)', ']=');
    TRACE >>> $(vNomeVariavel) gerada com $(vQtdCamposGerados) campos;
    LET vListaGerada = Null();
    LET vQtdCamposGerados = Null();
END SUB
//-----------------------------------------------------------------------------------------------
```

Limitação: campo com apóstrofo (`'`) no nome quebra o `LET`. Os campos de apreensão de hoje não têm apóstrofo; conferir no TRACE.

### 2. `app/07_variaveis_de_metricas/076_VARIAVEIS_DE_METRICAS_DO_EPOL.qvs` — gerar a lista e o filtro

Logo depois do bloco "FILTRO DE ANO MÍNIMO":

```qlik
//==============================================================================================
// FILTRO POR ATRIBUTOS DA APREENSÃO (2026-10-24)
//
// As linhas de Casos_Data não têm as chaves das apreensões. Para que as métricas do ePol
// respondam a seleções de apreensão (subclasse TNBIA, tipo de item, classe de
// descapitalização), o filtro é feito na métrica:
//   - [%CASOSKEY] = P(...): casos com apreensão que atende à seleção, em qualquer data;
//   - $(vSemSelAtributosApreensao): anula as seleções nos campos de apreensão para as
//     linhas de Casos_Data.
// Não se usa LEFT JOIN no tra 067: levaria o Casos_Data de 1,1 para 6,6 milhões de linhas.
//==============================================================================================

CALL GerarListaSemSelecaoTabelas(
    'vSemSelAtributosApreensao',
    'FATO_APREENSOES|DIM_APREENSOES|DIM_TNBIA',
    '[%APREENSOESKEY]=,[%SUBCLASSESKEY]='
);

SET vFCasoComApreensaoSelecionada =
    [%CASOSKEY] = P({<[Data]=,[Ano]=,[Mês]=,[Mês (Num)]=,[Tipo da Data]=,[Tipo do Fato]=>} [%CASOSKEY])
    ,$(vSemSelAtributosApreensao);
```

### 3. Mesmo arquivo — acrescentar o filtro aos filtros base com data

Acrescentar `,$(vFCasoComApreensaoSelecionada)` ao final de cada filtro base **com data** (linhas 871-886 e 897-898 no código de 2026-10-24). Exemplo:

```qlik
SET vFCasosData = [Tipo do Fato] = {'Casos_Data'},$(vFCasoComApreensaoSelecionada);
SET vFPrisEmFlagr = [Proc_Data Tipo] = {'Prisão Flagrante'},[Tipo do Fato] = {'Casos_Data'},$(vFCasoComApreensaoSelecionada);
// ... idem para vFPrisEmFlagrInt, vFPrisEmFlagrExt, vFIplInstInicProp, vFReRecAtiv,
//     vFDurMedIplRelat, vFFlaInstBase, vFFlaInstInt, vFFlaInstExt, vFTcoInst,
//     vFIndiciamFront, vFDurMedReRecAtivRelatComTipo, vFDurMedReRecAtivRelatSemTipo
```

**Não** acrescentar nos filtros "Em Andamento" (`vFIplEmAndSemRel`, `vFIplEmAndVazio`, `vFReRecAtivEmAndSemRel`, `vFReRecAtivEmAndVazio`) nesta etapa. Eles têm outra lógica de datas; avaliar depois se também devem responder à apreensão.

Todas as variantes (12 por métrica, por efetivo, Pareto, proporções e percentuais) herdam o filtro, porque são montadas a partir desses filtros base.

## Validação depois do reload

1. TRACE: `vSemSelAtributosApreensao gerada com N campos`. Conferir no editor de variáveis se a lista tem os campos de `DIM_APREENSOES`/`DIM_TNBIA` e **não** tem campos de unidade, caso ou operação.
2. **Sem seleção**: os valores das métricas do ePol não mudam (comparar `vIplInstDtMesAno`, `vIplRelatProcDtDtMesAno`, `vFlaInstDtMesAnoInst`, `vIndiciamDtMesAno`).
3. **Com uma subclasse selecionada**: as métricas do ePol deixam de zerar e mostram só os casos com apreensão daquela subclasse.
4. **Com operação de fronteira selecionada**: os valores continuam iguais aos de hoje (o join do 067 continua valendo).
5. Tempo de resposta dos gráficos do ePol aceitável (o `P()` roda sobre ~360 mil casos).

## Reaproveitamento

A mesma SUB serve para outros filtros cruzados sem join, por exemplo métricas do ePol filtradas por atributos dos eventos: `CALL GerarListaSemSelecaoTabelas('vSemSelAtributosEventos', 'FATO_EVENTOS_OPERACIONAIS|DIM_EVENTOS_OPERACIONAIS|...', '[%EVENTOSKEY]=')`.
