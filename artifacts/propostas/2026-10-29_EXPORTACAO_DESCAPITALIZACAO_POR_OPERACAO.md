# Proposta — Exportação `DESCAPITALIZACAO_POR_OPERACAO.csv` para os outros aplicativos da COP (2026-10-29)

> **Situação (2026-10-29): aplicada no tra 063 e validada pelo desenvolvedor (itens 1 a 6).**
> Pontos de atenção: (1) campos 1/2 do 062 corrigidos; (2) e (3) validados; (4) sem colisão, porque o `ID_OPERACAO` do Palas tem o prefixo `'palas-'`.
>
> **Revisão de 2026-11-04 (a aplicar e validar):** duas colunas novas no fim da tabela, `IPL_RE_Operacoes` e `IPL_RE_Apreensoes`.
> Mudanças no código já aplicado no 063:
> 1. **Passo 1:** a ponte ganha `Trim(IPL) AS IPL_APREENSAO` nos três `LOAD` e **não é mais removida** logo depois do `MAPPING LOAD`.
>    O `DROP TABLE TEMP_PONTE_APREENSAO_OPERACAO_EXPORTACAO;` sai do passo 1 e vai para o fim do passo 4c.
> 2. **Passos 4b e 4c (novos):** entram logo depois de `SET vFmtExportCsv = ;`, antes do `LET vLinhasDescapPorOperacao`.
>
> O bloco de código abaixo já está completo, com essas mudanças.
>
> **Situação da revisão de 2026-11-04:** aplicada no 063 e validada pelo desenvolvedor (itens 1 a 7).
>
> **Revisão 2 de 2026-11-04: aplicada no 063 e validada pelo desenvolvedor em 2026-11-06 (item 8).** O `IPL_RE_Apreensoes`
> vazio só aparece em operações do Palas sem IPL, o que é comum no Palas. O `> 05` da linha 322 foi corrigido.
>
> Conteúdo da revisão 2:
> - **Só operações com descapitalização:** entram só os `ID_OPERACAO` com `Sum([Valor Total Descapitalização]) > 0`. O passo 4 ganhou
>   um preceding load com `WHERE [Valor Total Descapitalização] > 0` em cima do `GROUP BY`, que faz o papel do HAVING.
>   As somas de cada operação não mudam, porque todas as linhas da operação continuam na soma.
> - **`IPL_RE_Apreensoes` só com apreensões que têm descapitalização:**
>   - O passo 3b, novo, guarda as `%APREENSOESKEY` com `[Valor Total Descapitalização] > 0` numa tabela temporária.
>   - O passo 4c filtra a ponte com `Exists([%APREENSOESKEY_COM_DESCAP_EXPORTACAO], [%APREENSOESKEY])` e remove essa tabela no fim.
> - **Correção no 063 aplicado:** a linha 322 tem `Len(Trim(ID_OPERACAO)) > 05`. O certo é `> 0`; do jeito que está, ficam de fora os
>   `ID_OPERACAO` com até 5 caracteres no `IPL_RE_Operacoes` do SIGACrim.
>
> Onde inserir no 063:
> - **Passo 3b:** novo bloco logo antes do comentário `// 4. Soma por operação`.
> - **Passo 4:** quatro linhas novas entre `NoConcatenate` e `LOAD ID_OPERACAO,` do `DESCAPITALIZACAO_POR_OPERACAO`:
>   `LOAD`, `*`, `WHERE [Valor Total Descapitalização] > 0;` e o `LOAD` original.
> - **Passo 4c:** trocar o `WHERE` e o `DROP TABLE` pelos do bloco abaixo.

## Motivo

Pedido do desenvolvedor em 2026-10-29: durante a carga do tra, gerar uma tabela com os valores de descapitalização
LVL1 e LVL2 **por operação**, somando **só o `FATO_APREENSOES`**, e só as apreensões vinculadas a uma operação
(`ID_OPERACAO` não nulo). Revisão de 2026-10-29: o filtro vale só para o `ID_OPERACAO`. Uma operação sem
`NOME_OPERACAO`, o que é praticamente impossível, entra com o nome vazio. Os valores seguem o formato numérico brasileiro do Qlik,
com vírgula decimal. Só entram as **operações homologadas** (`ETAPAOPERACAO = 'Homologada'`). No SIGACrim, o filtro usa o campo
`ETAPAOPERACAO`. As operações do Palas 2022–2023 são todas homologadas, como no tra 073, que grava `'Homologada' AS ETAPAOPERACAO`.
As apreensões do ePol vinculadas a uma operação não homologada, ou a uma operação que não está no SIGACrim nem no Palas, ficam de fora. A tabela é gravada em QVD e em CSV em `$(vCaminhoCORPDICORCOP)` (tra 021),
com as SUBs `Store` e `StoreAndDropCsv` (tra 022), e removida da memória logo depois. Ela não faz parte do modelo do app.

Campos (na ordem da figura enviada):

| # | Campo |
|---|---|
| 1 | `ID_OPERACAO` |
| 2 | `NOME_OPERACAO` |
| 3 | `Valor Total Descapitalização` |
| 4 | `1 Valor Bens Imóveis Apreendidos/Sequestrados LVL1` |
| 5 | `2 Valor Bens Móveis e Semoventes Apreendidos/Sequestrados LVL1` |
| 6 | `2.1 Valor Pedras, Metais Preciosos, Joias e Obras de Arte LVL2` |
| 7 | `2.2 Valor Semoventes LVL2` |
| 8 | `2.3 Valor Veículos aéreos LVL2` |
| 9 | `2.4 Valor Veículos aquáticos LVL2` |
| 10 | `2.5 Valor Veículos terrestres LVL2` |
| 11 | `2.6 Valor Outros bens Móvies LVL2` (grafia igual à do fato) |
| 12 | `3 Valor Criptoativos apreendidos/sequestrados LVL1` |
| 13 | `4 Valor Títulos  Valores Mobiliários e Direitos Apreendidos/Sequestrados LVL1` (dois espaços, igual ao fato) |
| 14 | `5 Valores Monetários Apreendidos/Sequestrados LVL1` |
| 15 | `5.1 Valores Monetários em espécie LVL2` |
| 16 | `5.2 Valores Monetários bloqueados via Bacenjud ou similares LVL2` |
| 17 | `6 Valor Itens de Descapitalização Destruídos no Local LVL1` |
| 18 | `IPL_RE_Operacoes` (2026-11-04): `IPL` e `RE_SEQUESTRO` da operação, separados por vírgula, sem repetição. O `RE_SEQUESTRO` só existe no SIGACrim |
| 19 | `IPL_RE_Apreensoes` (2026-11-04): IPLs das apreensões da operação **que têm descapitalização** (`[Valor Total Descapitalização] > 0`), separados por vírgula, sem repetição |

Revisão 2 (2026-11-04): só entram as operações com `Sum([Valor Total Descapitalização]) > 0`.

## Onde inserir

**tra `06_fatos/063_FATO_APREENSOES_PALAS_OPERACOES_TRATADAS_2022_2023.qvs`, logo antes de**
`CALL StoreAndDrop('FATO_APREENSOES', '$(vCaminhoTransformadosV3)');` (linha 137).

Por que nesse ponto:
- é o único momento em que o `FATO_APREENSOES` já tem as três fontes (ePol 061, SIGACrim 062, Palas 063) e ainda está em memória
  (a linha 137 grava e remove a tabela);
- as três tabelas de origem com o `ID_OPERACAO` ainda estão carregadas: `TEMP_DIM_CASOS_APREENSAO_BENS` (removida no 077),
  `TEMP_SIGACrimHomologadas` e `TEMP_Palas_Operacoes_Tratadas_2022_2023` (removidas no 079);
- o `FATO_APREENSOES` não tem `ID_OPERACAO`. A ponte `%APREENSOESKEY` → `ID_OPERACAO` é refeita com **as mesmas expressões de chave**
  do 061/062/063, e o `NOME_OPERACAO` vem das mesmas tabelas que alimentam as DIM_OPERACOES (071 e 073).

Não usei a link table porque a `%OPERACOESKEY` é um número do `AutoNumberHash128` e não devolve o `ID_OPERACAO` original.

## Código

```qlik
TRACE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>;
TRACE >>> Gerando DESCAPITALIZACAO_POR_OPERACAO para exportação (COP);
TRACE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>;
/*******************************************************************************
    TABELA PARA EXPORTAÇÃO - NÃO FAZ PARTE DO MODELO DO APP
    DESCAPITALIZACAO_POR_OPERACAO.csv

    Tabela para exportação e uso em outros aplicativos da COP/DICOR/PF.
    Soma, por operação (ID_OPERACAO e NOME_OPERACAO), os valores de
    descapitalização LVL1 e LVL2 do FATO_APREENSOES (ePol 061 + SIGACrim 062 +
    Palas 063).
    - Só entram as apreensões vinculadas a uma operação: as linhas com
      ID_OPERACAO nulo ou vazio são descartadas. Uma operação sem
      NOME_OPERACAO (praticamente impossível) entra com o nome vazio.
    - Só entram as operações homologadas (ETAPAOPERACAO = 'Homologada' no
      SIGACrim; todas as do Palas 2022-2023, como no tra 073).
    - Valores no formato numérico brasileiro (#.##0,00, vírgula decimal).
    - O FATO_APREENSOES não tem o ID_OPERACAO. A ponte [%APREENSOESKEY] ->
      ID_OPERACAO é refeita com as mesmas expressões de chave do 061, 062 e 063.
    - O NOME_OPERACAO vem das mesmas fontes das DIM_OPERACOES (071 e 073).
    - Fica neste ponto do 063 porque é o último momento em que o FATO_APREENSOES
      (completo) e as tabelas TEMP de origem estão em memória.
    - Gravada em $(vCaminhoCORPDICORCOP) (tra 021) e removida da memória pela
      SUB StoreAndDropCsv (tra 022).
*******************************************************************************/

// 1. Ponte [%APREENSOESKEY] -> ID_OPERACAO (+ IPL da apreensão), com as mesmas
//    chaves do FATO_APREENSOES. A ponte fica em memória até o passo 4c, que usa o
//    IPL_APREENSAO para montar a coluna IPL_RE_Apreensoes.
TEMP_PONTE_APREENSAO_OPERACAO_EXPORTACAO:
NoConcatenate
// ePol (061): chave = GestãoBens Item ID; ID_OPERACAO definido no 053; IPL do item
LOAD DISTINCT
    AutoNumberHash128("GestãoBens Item ID") AS [%APREENSOESKEY],
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(IPL) AS IPL_APREENSAO
RESIDENT TEMP_DIM_CASOS_APREENSAO_BENS
WHERE Len(Trim(ID_OPERACAO)) > 0;

// SIGACrim (062): chave = 'SIGACrim_' & ID_OPERACAO, só 2024 (mesmo filtro do 062).
// A "apreensão" é a própria operação, então o IPL da apreensão é o IPL da operação.
CONCATENATE (TEMP_PONTE_APREENSAO_OPERACAO_EXPORTACAO)
LOAD DISTINCT
    AutoNumberHash128('SIGACrim'&'_'&ID_OPERACAO) AS [%APREENSOESKEY],
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(IPL) AS IPL_APREENSAO
RESIDENT TEMP_SIGACrimHomologadas
WHERE YEAR(DT_DEFLAGRACAO) = 2024
    AND Len(Trim(ID_OPERACAO)) > 0;

// Palas (063): chave = ID_OPERACAO (o filtro de valores do 063 não é necessário:
// as chaves sem linha no fato simplesmente não são usadas). IPL da operação.
CONCATENATE (TEMP_PONTE_APREENSAO_OPERACAO_EXPORTACAO)
LOAD DISTINCT
    AutoNumberHash128(ID_OPERACAO) AS [%APREENSOESKEY],
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(IPL) AS IPL_APREENSAO
RESIDENT TEMP_Palas_Operacoes_Tratadas_2022_2023
WHERE Len(Trim(ID_OPERACAO)) > 0;

MAP_APREENSAO_ID_OPERACAO_EXPORTACAO:
MAPPING LOAD
    [%APREENSOESKEY],
    ID_OPERACAO
RESIDENT TEMP_PONTE_APREENSAO_OPERACAO_EXPORTACAO;

// 2. ID_OPERACAO -> NOME_OPERACAO (SIGACrim tem prioridade; Palas como segunda opção)
MAP_NOME_OPERACAO_SIGACRIM_EXPORTACAO:
MAPPING LOAD DISTINCT
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(NOME_OPERACAO) AS NOME_OPERACAO
RESIDENT TEMP_SIGACrimHomologadas
WHERE Len(Trim(ID_OPERACAO)) > 0
    AND Len(Trim(NOME_OPERACAO)) > 0;

MAP_NOME_OPERACAO_PALAS_EXPORTACAO:
MAPPING LOAD DISTINCT
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(NOME_OPERACAO) AS NOME_OPERACAO
RESIDENT TEMP_Palas_Operacoes_Tratadas_2022_2023
WHERE Len(Trim(ID_OPERACAO)) > 0
    AND Len(Trim(NOME_OPERACAO)) > 0;

// 2b. Operações homologadas (ETAPAOPERACAO = 'Homologada').
//     - SIGACrim: pelo campo ETAPAOPERACAO.
//     - Palas 2022-2023: todas são homologadas (o tra 073 grava 'Homologada' AS ETAPAOPERACAO).
TEMP_OPERACOES_HOMOLOGADAS_EXPORTACAO:
NoConcatenate
LOAD DISTINCT
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    'Sim' AS [Operação Homologada]
RESIDENT TEMP_SIGACrimHomologadas
WHERE Len(Trim(ID_OPERACAO)) > 0
    AND ETAPAOPERACAO = 'Homologada';

CONCATENATE (TEMP_OPERACOES_HOMOLOGADAS_EXPORTACAO)
LOAD DISTINCT
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    'Sim' AS [Operação Homologada]
RESIDENT TEMP_Palas_Operacoes_Tratadas_2022_2023
WHERE Len(Trim(ID_OPERACAO)) > 0;

MAP_OPERACAO_HOMOLOGADA_EXPORTACAO:
MAPPING LOAD
    ID_OPERACAO,
    [Operação Homologada]
RESIDENT TEMP_OPERACOES_HOMOLOGADAS_EXPORTACAO;

DROP TABLE TEMP_OPERACOES_HOMOLOGADAS_EXPORTACAO;

// 3. Linhas do FATO_APREENSOES com operação homologada. Ficam de fora as linhas
//    sem ID_OPERACAO e as de operações não homologadas (ou ausentes das fontes de operações).
//    O NOME_OPERACAO não é filtrado: se vier nulo, a operação entra com o nome vazio.
TEMP_DESCAPITALIZACAO_POR_OPERACAO:
NoConcatenate
LOAD
    *
WHERE Len(Trim(ID_OPERACAO)) > 0
    AND ApplyMap('MAP_OPERACAO_HOMOLOGADA_EXPORTACAO', ID_OPERACAO, 'Não') = 'Sim';
LOAD
    *,
    ApplyMap('MAP_NOME_OPERACAO_SIGACRIM_EXPORTACAO', ID_OPERACAO,
        ApplyMap('MAP_NOME_OPERACAO_PALAS_EXPORTACAO', ID_OPERACAO, Null())
    ) AS NOME_OPERACAO;
LOAD
    ApplyMap('MAP_APREENSAO_ID_OPERACAO_EXPORTACAO', [%APREENSOESKEY], Null()) AS ID_OPERACAO,
    [Valor Total Descapitalização],
    [1 Valor Bens Imóveis Apreendidos/Sequestrados LVL1],
    [2 Valor Bens Móveis e Semoventes Apreendidos/Sequestrados LVL1],
    [2.1 Valor Pedras, Metais Preciosos, Joias e Obras de Arte LVL2],
    [2.2 Valor Semoventes LVL2],
    [2.3 Valor Veículos aéreos LVL2],
    [2.4 Valor Veículos aquáticos LVL2],
    [2.5 Valor Veículos terrestres LVL2],
    [2.6 Valor Outros bens Móvies LVL2],
    [3 Valor Criptoativos apreendidos/sequestrados LVL1],
    [4 Valor Títulos  Valores Mobiliários e Direitos Apreendidos/Sequestrados LVL1],
    [5 Valores Monetários Apreendidos/Sequestrados LVL1],
    [5.1 Valores Monetários em espécie LVL2],
    [5.2 Valores Monetários bloqueados via Bacenjud ou similares LVL2],
    [6 Valor Itens de Descapitalização Destruídos no Local LVL1]
RESIDENT FATO_APREENSOES;

// 3b. Apreensões com descapitalização ([Valor Total Descapitalização] > 0).
//     Usada no passo 4c: a coluna IPL_RE_Apreensoes só mostra os Casos dessas apreensões.
TEMP_APREENSOES_COM_DESCAP_EXPORTACAO:
NoConcatenate
LOAD DISTINCT
    [%APREENSOESKEY] AS [%APREENSOESKEY_COM_DESCAP_EXPORTACAO]
RESIDENT FATO_APREENSOES
WHERE [Valor Total Descapitalização] > 0;

// 4. Soma por operação. Valores no padrão brasileiro do Qlik: vírgula decimal e
//    ponto como separador de milhar (igual a DecimalSep/ThousandSep do 000_MAIN).
//    No CSV (delimitador ','), o STORE põe entre aspas os valores que têm vírgula.
//    O LOAD de cima (preceding load) mantém só as operações com algum valor de
//    descapitalização (Sum do [Valor Total Descapitalização] > 0). Funciona como
//    um HAVING, que não existe no LOAD do Qlik.
SET vFmtExportCsv = '#.##0,00', ',', '.';

DESCAPITALIZACAO_POR_OPERACAO:
NoConcatenate
LOAD
    *
WHERE [Valor Total Descapitalização] > 0;
LOAD
    ID_OPERACAO,
    NOME_OPERACAO,
    Num(Sum([Valor Total Descapitalização]), $(vFmtExportCsv)) AS [Valor Total Descapitalização],
    Num(Sum([1 Valor Bens Imóveis Apreendidos/Sequestrados LVL1]), $(vFmtExportCsv)) AS [1 Valor Bens Imóveis Apreendidos/Sequestrados LVL1],
    Num(Sum([2 Valor Bens Móveis e Semoventes Apreendidos/Sequestrados LVL1]), $(vFmtExportCsv)) AS [2 Valor Bens Móveis e Semoventes Apreendidos/Sequestrados LVL1],
    Num(Sum([2.1 Valor Pedras, Metais Preciosos, Joias e Obras de Arte LVL2]), $(vFmtExportCsv)) AS [2.1 Valor Pedras, Metais Preciosos, Joias e Obras de Arte LVL2],
    Num(Sum([2.2 Valor Semoventes LVL2]), $(vFmtExportCsv)) AS [2.2 Valor Semoventes LVL2],
    Num(Sum([2.3 Valor Veículos aéreos LVL2]), $(vFmtExportCsv)) AS [2.3 Valor Veículos aéreos LVL2],
    Num(Sum([2.4 Valor Veículos aquáticos LVL2]), $(vFmtExportCsv)) AS [2.4 Valor Veículos aquáticos LVL2],
    Num(Sum([2.5 Valor Veículos terrestres LVL2]), $(vFmtExportCsv)) AS [2.5 Valor Veículos terrestres LVL2],
    Num(Sum([2.6 Valor Outros bens Móvies LVL2]), $(vFmtExportCsv)) AS [2.6 Valor Outros bens Móvies LVL2],
    Num(Sum([3 Valor Criptoativos apreendidos/sequestrados LVL1]), $(vFmtExportCsv)) AS [3 Valor Criptoativos apreendidos/sequestrados LVL1],
    Num(Sum([4 Valor Títulos  Valores Mobiliários e Direitos Apreendidos/Sequestrados LVL1]), $(vFmtExportCsv)) AS [4 Valor Títulos  Valores Mobiliários e Direitos Apreendidos/Sequestrados LVL1],
    Num(Sum([5 Valores Monetários Apreendidos/Sequestrados LVL1]), $(vFmtExportCsv)) AS [5 Valores Monetários Apreendidos/Sequestrados LVL1],
    Num(Sum([5.1 Valores Monetários em espécie LVL2]), $(vFmtExportCsv)) AS [5.1 Valores Monetários em espécie LVL2],
    Num(Sum([5.2 Valores Monetários bloqueados via Bacenjud ou similares LVL2]), $(vFmtExportCsv)) AS [5.2 Valores Monetários bloqueados via Bacenjud ou similares LVL2],
    Num(Sum([6 Valor Itens de Descapitalização Destruídos no Local LVL1]), $(vFmtExportCsv)) AS [6 Valor Itens de Descapitalização Destruídos no Local LVL1]
RESIDENT TEMP_DESCAPITALIZACAO_POR_OPERACAO
GROUP BY ID_OPERACAO, NOME_OPERACAO;

DROP TABLE TEMP_DESCAPITALIZACAO_POR_OPERACAO;
SET vFmtExportCsv = ;

// 4b. IPL_RE_Operacoes: IPL e RE_SEQUESTRO da operação numa só coluna, separados
//     por vírgula, sem repetição e em ordem crescente (AAAA.NNNNNNN).
//     - SIGACrim: IPL + RE_SEQUESTRO. O RE_SEQUESTRO pode ter vários números
//       separados por ':' (normalizados no ext 081), por isso o SubField.
//     - Palas: só IPL (não tem RE_SEQUESTRO).
TEMP_IPL_RE_OPERACOES_EXPORTACAO:
NoConcatenate
LOAD DISTINCT
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(IPL) AS PROC_EXPORTACAO
RESIDENT TEMP_SIGACrimHomologadas
WHERE Len(Trim(ID_OPERACAO)) > 0
    AND Len(Trim(IPL)) > 0;

CONCATENATE (TEMP_IPL_RE_OPERACOES_EXPORTACAO)
LOAD
    *
WHERE Len(PROC_EXPORTACAO) > 0;
LOAD DISTINCT
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(SubField(RE_SEQUESTRO, ':')) AS PROC_EXPORTACAO
RESIDENT TEMP_SIGACrimHomologadas
WHERE Len(Trim(ID_OPERACAO)) > 0
    AND Len(Trim(RE_SEQUESTRO)) > 0;

CONCATENATE (TEMP_IPL_RE_OPERACOES_EXPORTACAO)
LOAD DISTINCT
    Trim(ID_OPERACAO) AS ID_OPERACAO,
    Trim(IPL) AS PROC_EXPORTACAO
RESIDENT TEMP_Palas_Operacoes_Tratadas_2022_2023
WHERE Len(Trim(ID_OPERACAO)) > 0
    AND Len(Trim(IPL)) > 0;

LEFT JOIN (DESCAPITALIZACAO_POR_OPERACAO)
LOAD
    ID_OPERACAO,
    Concat(DISTINCT PROC_EXPORTACAO, ',', Num#(KeepChar(PROC_EXPORTACAO, '0123456789'))) AS IPL_RE_Operacoes
RESIDENT TEMP_IPL_RE_OPERACOES_EXPORTACAO
GROUP BY ID_OPERACAO;

DROP TABLE TEMP_IPL_RE_OPERACOES_EXPORTACAO;

// 4c. IPL_RE_Apreensoes: IPLs das apreensões da operação (ponte do passo 1) que
//     têm descapitalização ([Valor Total Descapitalização] > 0, passo 3b),
//     separados por vírgula, sem repetição e em ordem crescente.
//     - ePol: IPL de cada item apreendido com descapitalização vinculado à operação.
//     - SIGACrim 2024 e Palas: a apreensão é a própria operação (IPL da operação).
LEFT JOIN (DESCAPITALIZACAO_POR_OPERACAO)
LOAD
    ID_OPERACAO,
    Concat(DISTINCT IPL_APREENSAO, ',', Num#(KeepChar(IPL_APREENSAO, '0123456789'))) AS IPL_RE_Apreensoes
RESIDENT TEMP_PONTE_APREENSAO_OPERACAO_EXPORTACAO
WHERE Len(IPL_APREENSAO) > 0
    AND Exists([%APREENSOESKEY_COM_DESCAP_EXPORTACAO], [%APREENSOESKEY])
GROUP BY ID_OPERACAO;

DROP TABLES
    TEMP_PONTE_APREENSAO_OPERACAO_EXPORTACAO,
    TEMP_APREENSOES_COM_DESCAP_EXPORTACAO;

LET vLinhasDescapPorOperacao = NoOfRows('DESCAPITALIZACAO_POR_OPERACAO');
TRACE >>> DESCAPITALIZACAO_POR_OPERACAO: $(vLinhasDescapPorOperacao) operações;

// 5. Grava em QVD e em CSV na mesma pasta e remove da memória.
//    O QVD vem primeiro, porque a StoreAndDropCsv remove a tabela.
//    - lib://CORP_DICOR_COP/DESCAPITALIZACAO_POR_OPERACAO.qvd (SUB Store, tra 022)
//    - lib://CORP_DICOR_COP/DESCAPITALIZACAO_POR_OPERACAO.csv (SUB StoreAndDropCsv, tra 022)
CALL Store('DESCAPITALIZACAO_POR_OPERACAO', '$(vCaminhoCORPDICORCOP)');
CALL StoreAndDropCsv('DESCAPITALIZACAO_POR_OPERACAO', '$(vCaminhoCORPDICORCOP)');

LET vLinhasDescapPorOperacao = ;

TRACE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>;
TRACE >>> Concluída exportação DESCAPITALIZACAO_POR_OPERACAO (COP);
TRACE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>;
```

Notas sobre o código:
- As SUBs `Store` e `StoreAndDropCsv` acrescentam a extensão ao nome da tabela. Os arquivos finais são
  `lib://CORP_DICOR_COP/DESCAPITALIZACAO_POR_OPERACAO.qvd` e `lib://CORP_DICOR_COP/DESCAPITALIZACAO_POR_OPERACAO.csv`.
- O `CALL Store` precisa vir antes do `CALL StoreAndDropCsv`, porque essa segunda SUB remove a tabela.
- No QVD, os valores continuam numéricos, e o formato `#.##0,00` vale só para a exibição. Um app que carregar o QVD
  pode usar `Sum()` direto.
- No CSV, os valores ficam como texto no padrão brasileiro (ex.: `"1.234.567,89"`). Um app da COP com `DecimalSep=','` e
  `ThousandSep='.'` (o padrão brasileiro) lê esses valores como números. Com outra configuração, usar `Num#(campo, '#.##0,00', ',', '.')`.
- As tabelas temporárias têm campos com o mesmo nome do `FATO_APREENSOES`, mas são removidas antes do fim do script e por isso
  não geram chave sintética. Os `MAPPING` são descartados sozinhos no fim da carga.
- Cada `[%APREENSOESKEY]` recebe uma só operação (o `MAPPING` usa a primeira ocorrência). Por isso a soma nunca duplica um valor.
- Uma operação sem valor numa classe fica com `0,00` (o `Sum` de nulos dá 0).

## Pontos de atenção (dados de origem, não mudados por esta proposta)

1. **SIGACrim 062, campos 1 e 2 possivelmente trocados**: `VL_SEQUESTRO_VALOR_MOVEIS AS "1 Valor Bens Imóveis..."` e
   `VL_SEQUESTRO_VALOR_ESTIMADO_IMOVEIS AS "2 Valor Bens Móveis..."` (linhas 63 e 64). Se estiverem trocados, o CSV herda o erro
   para as operações de 2024 do SIGACrim. O app também.
2. **Palas 063 só tem `1+2` somados**: esse campo não está na lista pedida. Nas operações de 2022 e 2023, os campos 1, 2 e 2.x ficam
   em 0, mas o `Valor Total Descapitalização` inclui os bens. Nessas operações, a soma das classes LVL1 não fecha com o total.
3. **ePol 2022 e 2023 em 0 de propósito** (061): nesses anos os valores vêm do Palas.
4. **Possível colisão de chave**: o Palas usa `AutoNumberHash128(ID_OPERACAO)` e o ePol usa `AutoNumberHash128("GestãoBens Item ID")`
   como `%APREENSOESKEY`. Se algum `ID_OPERACAO` do Palas tiver o mesmo texto de algum `GestãoBens Item ID`, as duas linhas ficam com a mesma chave
   (o problema já existe no app). Isso é conferido no item 5 da validação.

## Validação (reload do tra)

1. A carga termina sem erro, e o TRACE mostra `DESCAPITALIZACAO_POR_OPERACAO: N operações`.
2. O arquivo `DESCAPITALIZACAO_POR_OPERACAO.csv` existe em `lib://CORP_DICOR_COP/` e tem os 17 campos (19 a partir de 2026-11-04) na ordem da tabela acima.
   Abra o CSV num editor de texto (não no Excel): os valores devem estar no padrão brasileiro e **entre aspas** (ex.: `"1.234.567,89"`).
   Se aparecerem sem aspas, a vírgula decimal quebra as colunas. Nesse caso, avise para trocar o delimitador desse arquivo (ex.: `;`).
   O `DESCAPITALIZACAO_POR_OPERACAO.qvd` está na mesma pasta, com o mesmo número de linhas do CSV. Num app de teste, a carga
   `LOAD * FROM [lib://CORP_DICOR_COP/DESCAPITALIZACAO_POR_OPERACAO.qvd] (qvd);` traz os valores como números: `Sum()` funciona sem conversão.
3. Nenhuma linha com `ID_OPERACAO` vazio, e nenhum `ID_OPERACAO` repetido. Linhas com `NOME_OPERACAO` vazio são aceitas, mas devem ser raras.
   Informe quantas aparecerem.
3b. Todas as operações do CSV são homologadas. No app, com `ETAPAOPERACAO` diferente de `'Homologada'` selecionado, nenhum `ID_OPERACAO`
   selecionado deve estar no CSV.
4. A soma da coluna `Valor Total Descapitalização` do CSV é igual a `Sum([Valor Total Descapitalização])` no app com a seleção
   `ID_OPERACAO` = todos os não nulos. A soma do CSV também deve ser menor que o total geral, porque as apreensões sem operação ficam de fora.
5. (Colisão) No app, a medida `Count(DISTINCT [Fonte])` por `%APREENSOESKEY` na link table, com `[Tipo do Fato] = 'Apreensões'`,
   nunca passa de 1.
6. Conferir 2 ou 3 operações conhecidas (uma do Palas, uma do SIGACrim de 2024 e uma do ePol de 2025) contra o app.
7. (2026-11-04) Colunas `IPL_RE_Operacoes` e `IPL_RE_Apreensoes`:
   - **Formato:** no CSV, os valores com mais de um número saem entre aspas (ex.: `"2024.0001234,2024.0005678"`) e não quebram as colunas.
   - **Operação do SIGACrim com `RE_SEQUESTRO`:** o `IPL_RE_Operacoes` traz o IPL e todos os REs do campo, sem repetição.
   - **Operação do Palas:** o `IPL_RE_Operacoes` traz só o IPL.
   - **Operação com várias apreensões do ePol:** o `IPL_RE_Apreensoes` traz os IPLs distintos dos itens. Confira no app com
     `Concat(DISTINCT IPL, ',')` filtrando a operação.
   - **Vazios:** informe quantas linhas ficaram com uma das duas colunas vazia.
8. (2026-11-04, revisão 2) Filtros de descapitalização:
   - **Só operações com valor:** nenhuma linha do CSV tem `Valor Total Descapitalização` = `0,00`. Informe o número de operações
     do TRACE antes e depois da mudança.
   - **Totais:** a soma da coluna `Valor Total Descapitalização` não muda em relação à versão anterior, porque só saem operações com total 0.
   - **`IPL_RE_Apreensoes`:** escolha uma operação do ePol que antes mostrava Casos de apreensões sem valor. No app, filtre a operação
     e use `Concat(DISTINCT {<[Valor Total Descapitalização] = {">0"}>} IPL, ',')`. O resultado deve bater com a coluna.
   - **`IPL_RE_Apreensoes` vazia:** só deve acontecer se a operação tiver total > 0 sem IPL nas apreensões com valor. Informe quantas linhas.
