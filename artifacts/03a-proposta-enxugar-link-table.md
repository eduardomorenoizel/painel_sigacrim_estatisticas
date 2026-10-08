# Proposta: enxugar a LINK_TABLE_APREENSOES_OPERACOES_CASOS

**Data:** 2026-10-08
**Status:** proposta, aguardando aprovação. Nenhum script de `qlik/` foi alterado.
**Base:** leitura de `qlik/tra/06_fatos/061` a `0610`, `qlik/tra/02_.../021`, `qlik/tra/07_dimensoes/0719`, `0721`, `0722`,
`qlik/app/03_fatos/032`, `qlik/app/04_.../042`, `qlik/app/05_.../052`, `qlik/app/02_.../023`, `qlik/app/07_*`, `qlik/app/08_*`,
e `artifacts/00-platform-context.md` (achados 3.5).

---

## 1. Resumo

A link table tem hoje **39 colunas**. A proposta a reduz para **17**, em duas etapas independentes:

| Etapa | O que sai da link | Onde mexe | Medidas afetadas |
|---|---|---|---|
| **1. Chaves duplicadas** | 8 chaves (um par fato/dimensão com o mesmo valor) | só `app/032` e `app/042` | **nenhuma** |
| **2. Atributos de unidade e área** | 15 colunas de texto (Sigla, UF, Área, Diretoria e CG, em 3 versões) | `tra` 021, 061 a 0610, 0719, 0721, nova DIM de área; `app` 042, 052, 023, 074 | **1 variável de métrica** (074) e **2 listas de modificadores de efetivo** (023), mais os gráficos do front-end que usam esses campos |

Resultado final por linha da link: 8 chaves de fato, `%UNIDADE_KEY`, `%AREA_KEY` (nova), `Data`, `Ano`, `Mês`, `Mês (Num)`,
`Tipo da Data`, `Fonte`, `Tipo do Fato`.

O número de **linhas** não muda (o fan-out de 068 é outro problema, tratado à parte). O ganho é de largura: menos colunas por
linha numa tabela que o próprio `0721` descreve como de ~12 milhões de linhas. Estimativa (não medida): as 8 chaves duplicadas
são campos de alta cardinalidade, cerca de 20 bits por linha cada, algo na ordem de 200 MB de RAM a menos. Confirmar com o
tamanho do app antes e depois.

---

## 2. Etapa 1: eliminar as 8 chaves duplicadas

### 2.1 Diagnóstico

Em todos os 10 scripts que montam a link (061 a 0610), cada chave de fato é gerada **na mesma instrução e com a mesma
expressão** que a chave de dimensão correspondente. Nos `LEFT JOIN`, as duas também entram sempre juntas. Logo, em toda linha,
os pares abaixo têm valor idêntico (ou são ambos nulos):

| Chave do fato (sai) | Chave da dimensão (fica) | Expressão comum | Quem usa a chave que fica (app) |
|---|---|---|---|
| `%CASOSKEY` | `%PROC_IDENTIFICACAO_KEY` | `AutoNumberHash128("Proc. Identificação")` | DIM_CASOS, DIM_CASOS_TIPO_PENAL, DIM_MATERIA_RE, DIM_INFORMACOES_CASOS |
| `%OPERACOESKEY` | `%ID_OPERACAO_KEY` | `AutoNumberHash128(ID_OPERACAO)` | DIM_OPERACOES, DIM_GPOL_*, DIM_EFETIVOS_GPOL, DIM_Caso_de_RE_..., dimensões do loop `vTabela` |
| `%APREENSOESKEY` | `%GESTAO_BENS_ITEM_ID_KEY` | ePol: `"GestãoBens Item ID"`; SIGACrim: `'SIGACrim_'&ID_OPERACAO`; Palas: `ID_OPERACAO` | DIM_APREENSOES |
| `%SUBCLASSESKEY` | `%ITEM_SUBCLASSE_KEY` | `"GestãoBens Item Material Subclasse Código"` | DIM_TNBIA (`%SUBCLASSESKEY` não liga a nada hoje) |
| `%CASOSDATAKEY` | `%PROC_DATA_ID_KEY` | `"Proc_Data ID"` | DIM_CASOS_DATA |
| `%EVENTOSKEY` | `%ID_EVENTOS_KEY` | `id_ordem_original_evento` | DIM_EVENTOS_OPERACIONAIS |
| `%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY` | `%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY` | `id_evento_apreensao` | DIM_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO |
| `%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY` | `%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY` | `id_evento_prisao` | DIM_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO |

### 2.2 Mudança proposta

Ficam as chaves de **dimensão** (nomes mais descritivos e usadas por ~20 tabelas). Os 7 fatos passam a usar a mesma chave da
sua dimensão. Isso cabe inteiro na camada `app`, sem reprocessar `tra`:

- `app/03_fatos/032_FATOS.qvs`: renomear a chave de cada fato no LOAD, por exemplo
  `[%CASOSKEY] AS [%PROC_IDENTIFICACAO_KEY]` (7 linhas, uma por fato).
- `app/04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs`: retirar as 8 chaves da lista de campos.

Fato, dimensão(ões) e link passam a compartilhar um único campo. Um campo comum a 3 ou mais tabelas é uma única associação:
não gera chave sintética nem referência circular. O caminho de seleção fica equivalente ao de hoje, porque as duas chaves
sempre tiveram o mesmo valor em cada linha.

Numa segunda passada (limpeza, junto da etapa 2), as mesmas chaves podem deixar de ser geradas em `tra` 061 a 0610.

### 2.3 Validação antes de aplicar

Rodar uma vez no app atual (script de diagnóstico, descartável) e confirmar que todas as colunas resultam em **0**:

```
// Diagnóstico: cada coluna deve resultar em 0
DIAG_PARES_CHAVES:
LOAD
    Sum(IF(Alt([%CASOSKEY], -1) <> Alt([%PROC_IDENTIFICACAO_KEY], -1), 1, 0)) AS DivergeCasos,
    Sum(IF(Alt([%OPERACOESKEY], -1) <> Alt([%ID_OPERACAO_KEY], -1), 1, 0)) AS DivergeOperacoes,
    Sum(IF(Alt([%APREENSOESKEY], -1) <> Alt([%GESTAO_BENS_ITEM_ID_KEY], -1), 1, 0)) AS DivergeApreensoes,
    Sum(IF(Alt([%SUBCLASSESKEY], -1) <> Alt([%ITEM_SUBCLASSE_KEY], -1), 1, 0)) AS DivergeSubclasses,
    Sum(IF(Alt([%CASOSDATAKEY], -1) <> Alt([%PROC_DATA_ID_KEY], -1), 1, 0)) AS DivergeCasosData,
    Sum(IF(Alt([%EVENTOSKEY], -1) <> Alt([%ID_EVENTOS_KEY], -1), 1, 0)) AS DivergeEventos,
    Sum(IF(Alt([%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY], -1) <> Alt([%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY], -1), 1, 0)) AS DivergeEvApr,
    Sum(IF(Alt([%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY], -1) <> Alt([%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY], -1), 1, 0)) AS DivergeEvPri
RESIDENT LINK_TABLE_APREENSOES_OPERACOES_CASOS;
```

### 2.4 Impacto nas medidas

**Nenhum.** Nenhuma variável de `07x`, `08x` ou `023` referencia campos `%...KEY` (só `032`, `042` e `052` os citam).
As medidas contam campos naturais das dimensões (`[Proc. Identificação]`, `[ID_OPERACAO]`, `[GestãoBens Item ID]` etc.), que
continuam associados. Conferir depois da carga: os KPIs principais de cada fato (operações, apreensões, casos, eventos) devem
bater com os valores atuais, sem seleção e com uma seleção de UF.

---

## 3. Etapa 2: tirar unidade, UF, área, diretoria e CG da link

### 3.1 Diagnóstico

A link carrega 15 colunas de texto em 3 versões paralelas, mais um `%UNIDADE_KEY` cujo significado depende da linha:

| Fonte da linha | Colunas preenchidas | `%UNIDADE_KEY` vem de |
|---|---|---|
| Apreensões ePol e SIGACrim, Operações SIGACrim, Casos, Casos_Data | `... do Caso` (via `vCarregaUnidAreaDirCoorGeralDoCaso`) | unidade do caso (corrigida por FICCO/GISE) |
| Apreensões e Operações Palas | `... do Caso`, mas com a unidade e a área da **operação Palas** | `UNIDADE` do Palas |
| Eventos Operacionais (068) | `... do Evento Operacional` e, em parte, `... do Caso` | `unidade_participante` |
| Eventos Apreensões e Prisões Ext/Estr (069, 0610) | `... do Evento Externo/Estrangeiro` | `unidade_participante` |

Problemas que isso causa:

1. **Defeito em 068** (já listado na Fase 0): o `LEFT JOIN` dos atributos do caso também traz `%UNIDADE_KEY`, então o join
   casa por caso **e** unidade. "Unidade/Área/Diretoria/CG do Caso" só aparecem num evento quando a unidade do caso é igual
   à unidade participante.
2. **Três campos para a mesma pergunta.** Para comparar por SR ou UF entre fatos, o usuário precisa escolher entre
   "Unidade UF do Caso", "do Evento Operacional" e "do Evento Externo/Estrangeiro". Nenhum deles filtra todos os fatos.
3. **UF e sigla já existem em DIM_UNIDADE** (`Unidade Sigla`, `Unidade UF`), ligada pelo mesmo `%UNIDADE_KEY`.
4. **Área, Diretoria e CG não são atributos da unidade.** Dependem da área de atribuição do caso, da operação ou do evento
   (uma SR tem casos de várias áreas). Diretoria e CG derivam da área por mapeamento, com duas exceções por unidade
   (unidade central `/PF` e Assuntos Internos em DRIP/SIP/NIP). Por isso a proposta **não** coloca área e diretoria em
   DIM_UNIDADE, e sim numa dimensão própria e pequena.
5. **DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO** (0721) é montada só com as siglas "do Caso": unidades que aparecem só em eventos
   ficam sem tipo de unidade, base, especializada etc.

### 3.2 Modelo proposto

```
                    DIM_UNIDADE ── DIM_HIERARQUIA_TECNICA, DIM_HIERARQUIA_UNIDADE (ex-..._SIGLA_DO_CASO),
                         │         DIM_UNIDADE_SUBUNIDADE, DIM_CIRCUNSCRICAO_PF, DIM_SERVIDOR_ATIVO
                   %UNIDADE_KEY
                         │
FATOS ── chaves ── LINK_TABLE ── %AREA_KEY ── DIM_AREA_ATRIBUICAO (Área, Diretoria, Coordenação-Geral)
                         │
                  Data, Ano, Mês, Tipo da Data, Fonte, Tipo do Fato
```

- **`%UNIDADE_KEY` = "unidade do fato"**, uma por linha, com a regra de hoje por fonte: unidade do caso (corrigida) para
  casos, apreensões e operações SIGACrim; unidade Palas para Palas; unidade participante para os três tipos de evento.
  Sigla e UF passam a ser lidas de DIM_UNIDADE (`Unidade Sigla`, `Unidade UF`) e filtram todos os fatos de uma vez.
- **`%AREA_KEY` (nova)** = `AutoNumberHash128(Área & '|' & Diretoria & '|' & CG)`, calculada em `tra` com as mesmas
  expressões de hoje (as exceções de Diretoria e CG continuam valendo). `DIM_AREA_ATRIBUICAO` guarda as combinações
  distintas, dezenas de linhas, com os campos `Área de Atribuição`, `Diretoria`, `Coordenação-Geral`.
- **A unidade e a área "do caso" continuam disponíveis em DIM_CASOS**, que já tem `Proc. Unidade Exercício` (sem a correção
  FICCO/GISE). Acrescentar `Unidade Sigla do Caso`, `Unidade UF do Caso`, `Área de Atribuição do Caso`, `Diretoria do Caso`
  e `Coordenação-Geral do Caso` (1 linha por caso). Do mesmo modo, `DIM_EVENTOS_OPERACIONAIS` pode ganhar
  `Unidade Participante do Evento`. Assim, "eventos pela unidade do caso" continua possível via a dimensão do caso, sem
  colunas na link.
- **Cobertura de DIM_UNIDADE:** hoje ela filtra `"Unidade Situação" = 'Ativa'`. Siglas de fatos antigos de unidades extintas
  ficariam sem sigla/UF, coisa que hoje não acontece (o texto está na link). Proposta: em `0719`, acrescentar as siglas da
  link que não existem em DIM_UNIDADE, com `Unidade UF = SubField(sigla, '/', -1)` e `Unidade Situação = 'Não cadastrada'`.
- **0721** passa a ler as siglas distintas de todas as fontes (não só "do Caso") e se chama `DIM_HIERARQUIA_UNIDADE`;
  o campo `Tipo da Unidade do Caso` vira `Tipo da Unidade`.
- O `LEFT JOIN` de `vCarregaUnidAreaDirCoorGeralDoCaso` em 068 sai, o que elimina o defeito do item 3.1.1.

### 3.3 Scripts alterados

| Camada | Script | Mudança |
|---|---|---|
| tra | `021_VARIAVEIS_...` | os 3 blocos `vCarregaUnidAreaDirCoorGeral*` passam a gerar só `%UNIDADE_KEY` e os campos de área para `%AREA_KEY` |
| tra | `061`, `062`, `064`, `066`, `067`, `068` | trocar o `LEFT JOIN ... vCarregaUnidAreaDirCoorGeralDoCaso` por `%UNIDADE_KEY` + `%AREA_KEY` |
| tra | `063`, `065` (Palas) | idem, a partir de `UNIDADE` e `AREAATRIBUICAOPALAS` |
| tra | `069`, `0610` | idem, a partir de `unidade_participante` e `ds_area_atribuicao` |
| tra | `0710` (DIM_CASOS) | acrescentar os 5 atributos "do Caso" |
| tra | `0719`, `0721` | cobertura de siglas e hierarquia para todas as fontes |
| tra | novo `0728_DIM_AREA_ATRIBUICAO.qvs` | dimensão de área |
| app | `042` | retirar as 15 colunas; incluir `%AREA_KEY` |
| app | `052` | carregar `DIM_AREA_ATRIBUICAO`; novos campos em DIM_CASOS; renomear a hierarquia |
| app | `023`, `074` | ver 3.4 |
| docs | `link_table_relacionamentos.md` | atualizar (já diverge do código: `%UNIDADE_KEY` "Palas somente", `DIM_SUBCLASSES`) |

### 3.4 Impacto nas medidas

Busca feita em `app/02`, `app/07` e `app/08`. Só estes pontos citam os campos que saem da link:

| Arquivo | Variável | Hoje | Depois | Efeito no número |
|---|---|---|---|---|
| `074_..._APREENSOES.qvs:372` | `vFApreDesvio` | `[Área de Atribuição do Caso] = {'Desvio de Recursos Públicos'}` | `[Área de Atribuição] = {'Desvio de Recursos Públicos'}` | igual (nas linhas de apreensões, a área já é a do caso, ou a do Palas nas linhas Palas) |
| `023_VARIAVEIS_DE_EFETIVO.qvs:72-74` | `vConjSemRelDatasAreaCasoOperacaoBem` | limpa `[Área de Atribuição do Caso]`, `[Diretoria do Caso]`, `[Coordenação-Geral do Caso]` | limpar `[Área de Atribuição]`, `[Diretoria]`, `[Coordenação-Geral]` e também os campos do caso em DIM_CASOS | igual, desde que a lista seja atualizada; **se esquecer, o efetivo passa a ser filtrado pela área selecionada** |
| `023_VARIAVEIS_DE_EFETIVO.qvs:269, 283` | `vConjTotalComRelUnidades` | lista `[Unidade Sigla do Caso]`, `[Unidade UF do Caso]` | trocar por `[Tipo da Unidade]` e manter os de DIM_CASOS | igual |

As medidas de eventos (`073`, `082`) não usam nenhum desses campos: continuam como estão (clones de operações, assunto de
outra frente).

**O que muda de verdade, e precisa ser comunicado aos usuários:**

- **Totais sem seleção de unidade ou área: não mudam.** Nenhuma linha de fato muda.
- **Casos, apreensões e operações por unidade, UF ou diretoria: não mudam**, se a validação 3.5 confirmar que a sigla e a UF de
  DIM_UNIDADE batem com as que estão hoje na link.
- **Eventos por unidade do caso: mudam (correção).** Hoje faltam os eventos cuja unidade participante difere da unidade do
  caso, por causa do defeito em 068.
- **Eventos por unidade: passam a responder pela unidade participante** no mesmo campo usado para os outros fatos. Uma
  seleção de SR passa a filtrar operações, casos, apreensões e eventos juntos, o que hoje exige três campos.

**Front-end (não versionado):** gráficos, filtros e dimensões mestras que usam os 15 campos antigos vão quebrar ou ficar
vazios. Não dá para listá-los a partir do repositório. Antes de aplicar a etapa 2, é preciso um inventário no app
(Qlik Sense: painel de ativos, ou exportar o app e procurar os nomes). Tabela de troca:

| Campo antigo (link) | Campo novo |
|---|---|
| `Unidade Sigla do Caso`, `... do Evento Operacional`, `... do Evento Externo/Estrangeiro` | `Unidade Sigla` (DIM_UNIDADE); para "do caso" específico, `Unidade Sigla do Caso` em DIM_CASOS |
| `Unidade UF do Caso`, `... do Evento ...` | `Unidade UF` (DIM_UNIDADE); ou `Unidade UF do Caso` em DIM_CASOS |
| `Área de Atribuição do Caso`, `... do Evento ...` | `Área de Atribuição` (DIM_AREA_ATRIBUICAO) |
| `Diretoria do Caso`, `... do Evento ...` | `Diretoria` (DIM_AREA_ATRIBUICAO) |
| `Coordenação-Geral do Caso`, `... do Evento ...` | `Coordenação-Geral` (DIM_AREA_ATRIBUICAO) |
| `Tipo da Unidade do Caso` | `Tipo da Unidade` |

### 3.5 Validação antes de aplicar

1. Siglas da link sem correspondência em DIM_UNIDADE (por fonte): quantas e quais.
2. Para as que existem: `Unidade UF do Caso` (link) igual a `Unidade UF` (DIM_UNIDADE)? Contar divergências.
3. Siglas Palas (`UNIDADE`) no mesmo formato de `Unidade Sigla` (ex.: `DRE/SR/PF/SP`)?
4. Depois da carga nova: tabela de controle com contagem por `Tipo do Fato` x `Unidade UF`, antes e depois; só os eventos
   podem divergir, e a diferença deve ser explicada pelo defeito de 068.

---

## 4. Ordem sugerida

1. Rodar o diagnóstico 2.3 no app atual. Se der 0, aplicar a **etapa 1** (2 arquivos do app, reversível, sem efeito nas medidas).
2. Rodar as validações 3.5 (1 a 3) e fazer o inventário do front-end.
3. Aplicar a **etapa 2** em `tra` e `app` num único ciclo de carga, com 023 e 074 ajustados, e conferir 3.5.4.
4. Atualizar `docs/link_table_relacionamentos.md` e registrar a decisão no CLAUDE.md.

Fora deste escopo, mas relacionado: `Ano`, `Mês` e `Mês (Num)` também poderiam sair da link para um calendário por `Data`;
e o fan-out de 068 (itens x apreensões-evento x prisões-evento) continua multiplicando linhas.

---

## 5. Decisão pendente

**Qual unidade representa um evento operacional na comparação por unidade?**
- **Unidade participante (recomendado):** um único campo de unidade para todos os fatos; a unidade do caso continua em DIM_CASOS.
- **Manter duas chaves de unidade** (`%UNIDADE_CASO_KEY` e `%UNIDADE_EVENTO_KEY`): preserva as duas visões na link, mas exige
  duas cópias das 6 dimensões de unidade (role-playing) e mantém o problema de três campos para a mesma pergunta.
