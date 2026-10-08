# Plano de otimização da link table e do script

**Data:** 2026-10-08
**Status:** proposta, aguardando aprovação do Eduardo. Nenhum script de `qlik/` foi alterado.
**Substitui:** `03a-proposta-enxugar-link-table.md` (de 2026-10-08, manhã), que tratava só das colunas e não das linhas.
**Base:** leitura completa de `qlik/tra/06_fatos/061` a `0610`, `qlik/tra/07_dimensoes/0721` e `0722`,
`qlik/app/03_fatos/032`, `qlik/app/04_tabela_de_ligacao/042`, `qlik/app/05_dimensoes/052` e `qlik/app/07_*` e `08_*`.

---

## 1. Decisão de negócio que orienta o plano

> A alta administração só usa as **datas comuns** (`Data`, `Ano`, `Mês`). Ao selecionar um ano, cada indicador mostra os
> seus próprios registros daquele ano: apreensões apreendidas no ano, operações deflagradas no ano, eventos ocorridos no ano.
> O cruzamento por datas específicas (ex.: "flagrantes dos casos que tiveram apreensão nesta data") não é necessário.
> (Eduardo, 2026-10-08)

Consequência: a link table não precisa materializar combinações entre fatos diferentes. Ela só precisa de **uma linha por
registro de cada fato**, com as chaves que aquele registro naturalmente possui.

---

## 2. Por que a link table explode (diagnóstico)

Cada script de `tra/06_fatos` monta um bloco da link table e depois faz `LEFT JOIN` com tabelas que têm **várias linhas por
chave** (relação 1:N). Cada `LEFT JOIN` desse tipo multiplica as linhas do bloco. Os multiplicadores se acumulam:

| Script | Tipo do Fato | Linhas base | `LEFT JOIN` que multiplicam (1:N) | Linhas resultantes (por caso / operação) |
|---|---|---|---|---|
| 061 | Apreensões (ePol) | 1 por item | `DIM_CASOS_DATA` por caso | itens × Proc_Data do caso |
| 062 | Apreensões (SIGACrim 2024) | 1 por operação | `DIM_CASOS_DATA` por caso | operações × Proc_Data |
| 063 | Apreensões (Palas) | 1 por operação | `DIM_CASOS_DATA` por caso | operações × Proc_Data |
| 064 | Operações (SIGACrim) | 1 por operação | itens ePol da operação; `DIM_CASOS_DATA`; participações de eventos da operação | operação × itens × Proc_Data × participações |
| 065 | Operações (Palas) | 1 por operação | itens ePol; `DIM_CASOS_DATA` | operação × itens × Proc_Data |
| 066 | Casos | 1 por caso | operações do caso; itens do caso; `DIM_CASOS_DATA` | caso × operações × itens × Proc_Data |
| 067 | Casos_Data | 1 por Proc_Data | operações do caso; itens do caso | Proc_Data × operações × itens |
| 068 | Eventos Operacionais | 1 por participação de unidade | itens ePol do evento; apreensões de eventos; prisões de eventos | participação × itens × apreensões × prisões |
| 069 | Eventos Apreensões | 1 por apreensão de evento | nenhum | sem multiplicação |
| 0610 | Eventos Prisões | 1 por prisão de evento | nenhum (o join de datas é 1:1) | sem multiplicação |

O `LEFT JOIN` com `TEMP_DIM_CASOS` (unidade, área, diretoria e CG do caso) é 1:1 por caso e **não** multiplica.

Exemplo (ilustrativo, números inventados): um caso com 40 registros em `DIM_CASOS_DATA`, 3 operações e 2.000 itens apreendidos
gera, só no bloco 067, 40 × 3 × 2.000 = **240.000 linhas**, e de novo 3 × 2.000 × 40 no bloco 066, e assim por diante.
Bastam poucos casos grandes para chegar às dezenas de milhões. Esse é o mecanismo dos 61 milhões (e dos ~12 milhões atuais).

### O que essas linhas cruzadas fazem hoje

Todas as métricas filtram o próprio fato com `[Tipo do Fato] = {'...'}` (072 a 076). Então as linhas cruzadas **não entram
nas somas e contagens por data comum**: a linha de "Casos_Data" carregando uma chave de apreensão nunca é usada por uma
métrica de apreensões. Elas só servem a dois usos:

1. As variantes "correlacionadas" das métricas (sufixo `Defl`/`Even` nos comentários de 072 e 073), que deixam de filtrar o
   próprio tipo de data.
2. Fazer um filtro de um fato propagar para os outros fatos (ex.: selecionar "Cocaína" e ver quantas **operações** apreenderam
   cocaína).

O primeiro uso foi descartado pela decisão da seção 1. O segundo é discutido na seção 5.

---

## 3. Resposta à pergunta do Eduardo

> "A partir da fato apreensões eu tinha criado links para a DIM_CASOS_DATA [...] eu pensava que, se calculasse os flagrantes nos
> Proc. Identificação da apreensão, eu teria que fazer isso. Estava correto meu raciocínio?"

**Em parte.** O raciocínio estaria certo num banco relacional, onde só se cruza o que está na mesma linha. No Qlik não é
necessário, porque o motor associativo propaga a seleção por **valores de chave compartilhados**, não por linhas
materializadas:

- A linha de apreensão já carrega `%CASOSKEY` (o caso dela).
- A linha de Casos_Data também carrega `%CASOSKEY`.
- Numa tabela com a dimensão `Proc. Identificação` e as medidas "itens apreendidos" e "flagrantes", cada linha da tabela mostra
  os dois números daquele caso, sem que exista nenhuma linha "apreensão × flagrante" na link table.

O que o cruzamento materializado acrescentava era só a possibilidade de filtrar flagrantes **pela data da apreensão** (a
correlação por data específica), que é exatamente o que a decisão da seção 1 dispensa. Se um dia precisar de uma pergunta desse
tipo, ela se resolve na expressão, sem linhas extras, com `P()`:

```
// Flagrantes instaurados nos casos que tiveram apreensão no período selecionado
Count({<
    [Tipo do Fato] = {'Casos_Data'},
    [Foi Instaurado por Flagrante] = {'Sim'},
    [Ano] = , [Mês] = , [Data] = ,
    [%CASOSKEY] = P({<[Tipo do Fato] = {'Apreensões'}>} [%CASOSKEY])
>} DISTINCT [Proc_Data Flagrante Instaurado ID])
```

(Expressão de exemplo, não testada, montada a partir do filtro `vFFlaInstBase` de `app/076`.)

---

## 4. Proposta em etapas

As etapas são independentes e podem ser aplicadas e validadas uma de cada vez. A Etapa A é a que resolve a lentidão.

### Etapa A. Uma linha por registro de fato (remover os `LEFT JOIN` 1:N)

Regra única: **cada bloco da link table só leva as chaves que o próprio registro possui (relação N:1).** Nenhum `LEFT JOIN`
que traga várias linhas por chave.

| Script | Remover | Manter |
|---|---|---|
| 061 Apreensões ePol | join com `TEMP_DIM_CASOS_DATA` | item, caso, `ID_OPERACAO` inferido (051 a 053), evento inferido, subclasse; join 1:1 com `TEMP_DIM_CASOS` (unidade do caso) |
| 062 Apreensões SIGACrim | join com `TEMP_DIM_CASOS_DATA` | operação, caso; join 1:1 com `TEMP_DIM_CASOS` |
| 063 Apreensões Palas | join com `TEMP_DIM_CASOS_DATA` | operação, caso, unidade Palas |
| 064 Operações SIGACrim | joins com `TEMP_DIM_CASOS_APREENSAO_BENS`, `TEMP_DIM_CASOS_DATA` e `TEMP_TABELAOEVENTOS_ID_UNIFICADO` | operação, caso; join 1:1 com `TEMP_DIM_CASOS` |
| 065 Operações Palas | joins com `TEMP_DIM_CASOS_APREENSAO_BENS` e `TEMP_DIM_CASOS_DATA` | operação, caso, unidade Palas |
| 066 Casos | joins com `TEMP_SIGACrimHomologadas`, `TEMP_DIM_CASOS_APREENSAO_BENS` e `TEMP_DIM_CASOS_DATA` | caso, unidade do caso |
| 067 Casos_Data | joins com `TEMP_SIGACrimHomologadas` e `TEMP_DIM_CASOS_APREENSAO_BENS` | Proc_Data, caso; join 1:1 com `TEMP_DIM_CASOS` |
| 068 Eventos Operacionais | joins com `TEMP_DIM_CASOS_APREENSAO_BENS`, apreensões e prisões de eventos; **e o join com `TEMP_DIM_CASOS`** (ver nota) | participação, evento, caso, operação, unidade participante |
| 069 Eventos Apreensões | nada | como está, **acrescentando** `%CASOSKEY`/`%PROC_IDENTIFICACAO_KEY` e `%OPERACOESKEY`/`%ID_OPERACAO_KEY` do evento (N:1; `Proc. Identificação` e `ID_OPERACAO` já estão na tabela de 033) |
| 0610 Eventos Prisões | o join com `TEMP_TABELAOEVENTOS_ID_UNIFICADO` só para buscar a data (usar `dt_prisao`, que 034 já traz) | como está, **acrescentando** caso e operação do evento, como em 069 |

Nota sobre 068: o bloco já traz `%UNIDADE_KEY` da unidade participante. O `LEFT JOIN` com `TEMP_DIM_CASOS` traz outro
`%UNIDADE_KEY` (o do caso), então o Qlik junta por **duas** chaves e só preenche a unidade do caso quando ela é igual à unidade
participante. Para eventos, a unidade comum deve ser a participante; o join pode sair.

Resultado esperado: `linhas da link = soma das linhas de cada fato` (participações de eventos contam uma vez por unidade
participante, como hoje). O número exato depende dos dados; para medir antes e depois, rodar no fim da `tra`:

```
CONTAGEM_LINK:
LOAD
    [Tipo do Fato],
    Count([Tipo do Fato]) AS LINHAS
RESIDENT LINK_TABLE_APREENSOES_OPERACOES_CASOS
GROUP BY [Tipo do Fato];
```

**O que continua funcionando sem os joins:**
- Todas as métricas por data comum (filtram `[Tipo do Fato]`).
- Filtros por atributos de um "pai" direto: selecionar `Ano da Deflagração` (DIM_OPERACOES) continua filtrando as apreensões
  daquelas operações, porque a linha de apreensão carrega a chave da operação. O mesmo vale para atributos do caso
  (DIM_CASOS) sobre apreensões, operações, Casos_Data e eventos.
- A visão por caso (todas as apreensões, prisões e buscas de um `Proc. Identificação`), que era o objetivo original do app,
  desde que cada bloco carregue a chave do caso. Hoje 069 e 0610 não carregam; por isso a tabela acima os acrescenta.

**O que deixa de propagar (comportamento novo):** um filtro num atributo exclusivo de um fato "filho" zera as medidas dos
outros fatos. Exemplos: selecionar a subclasse "Cocaína" (DIM_TNBIA/DIM_APREENSOES) zera a contagem de operações; selecionar um
`Proc_Data Tipo` zera as apreensões. É o mesmo efeito que o Eduardo descreveu ao selecionar uma data específica, agora também
para atributos. Ver a seção 5 para as alternativas.

### Etapa B. Tirar as 8 chaves duplicadas

A link carrega cada chave duas vezes com o mesmo valor, uma para a fato e outra para a dimensão:

| Fato | Dimensão |
|---|---|
| `%CASOSKEY` | `%PROC_IDENTIFICACAO_KEY` |
| `%OPERACOESKEY` | `%ID_OPERACAO_KEY` |
| `%APREENSOESKEY` | `%GESTAO_BENS_ITEM_ID_KEY` |
| `%CASOSDATAKEY` | `%PROC_DATA_ID_KEY` |
| `%EVENTOSKEY` | `%ID_EVENTOS_KEY` |
| `%SUBCLASSESKEY` | `%ITEM_SUBCLASSE_KEY` |
| `%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY` | `%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY` |
| `%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY` | `%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY` |

Fato e dimensão podem pendurar na mesma chave sem criar referência circular. Mudança só no `app`: em `032_FATOS.qvs`, renomear
a chave de cada fato para o nome da chave da dimensão (ex.: `[%CASOSKEY] AS [%PROC_IDENTIFICACAO_KEY]`) e, em
`042_TABELA_DE_LIGACAO.qvs`, deixar de carregar as 8 colunas de fato. `%SUBCLASSESKEY` não tem tabela própria no app e pode
simplesmente sair. Não afeta métricas (nenhuma referencia essas chaves).

### Etapa C. Tirar atributos de texto da link

Colunas de baixa cardinalidade custam pouco por linha, mas são 18 colunas de texto repetidas em todas as linhas e que podem
ir para dimensões (a link tem 39 colunas: 17 chaves, 4 de classificação/data e 18 de calendário, unidade e área):

- `Ano`, `Mês`, `Mês (Num)` → um calendário (`DIM_CALENDARIO`) ligado por `Data`. As métricas continuam usando `[Ano]` e
  `[Mês]` sem mudança, porque os nomes dos campos se mantêm.
- `Unidade Sigla/UF do Caso`, `do Evento Operacional`, `do Evento Externo/Estrangeiro` → já existe `%UNIDADE_KEY` em todas as
  linhas como "unidade do registro" (unidade do caso para apreensões, operações e casos; unidade participante para eventos).
  Os atributos de unidade vêm das dimensões de unidade.
- `Área de Atribuição`, `Diretoria`, `Coordenação-Geral` (3 versões) → nova chave `%AREA_KEY` ligada a uma dimensão pequena
  de área → diretoria → CG.
- `Fonte`, `Tipo da Data`, `Tipo do Fato` podem continuar na link (são poucos valores).

Esta etapa mexe no front-end: gráficos e filtros que usam `Unidade Sigla do Caso` ou `Área de Atribuição do Evento
Operacional` precisam apontar para os campos comuns. As planilhas do Qlik não estão no repositório, então antes desta etapa é
preciso um inventário dos objetos que usam esses campos. Também afeta `0721` (a hierarquia é montada a partir da link) e as
listas de modificadores de efetivo em `app/023`.

### Etapa D. Enxugar as variantes de medidas

As sub-rotinas de 072 a 076 geram 12 variantes por métrica: {data comum, data específica} × {todas, "PF em Números"} ×
{seleção, ano atual, ano anterior}. Com a decisão da seção 1, as 6 variantes de data específica podem sair, o que reduz
pela metade as variáveis de 07x e 08x (hoje 073 tem 205 KB e 082 tem 940 KB). Fazer depois da Etapa A, quando estiver
confirmado que nenhuma tela usa as variantes `Defl`.

---

## 5. Se algum cruzamento entre fatos ainda for necessário

Três opções, todas sem multiplicar linhas da link:

1. **Expressão com `P()`/`E()`** (exemplo na seção 3). Bom para poucas medidas pontuais.
2. **Indicador pré-calculado na dimensão "pai"**: por exemplo, em `DIM_OPERACOES`, os campos "Teve apreensão de cocaína (Sim/Não)"
   ou "Qtd. de itens apreendidos", calculados na `tra` com `GROUP BY ID_OPERACAO`. O usuário filtra a operação por esse
   atributo, e todas as medidas continuam independentes.
3. **Ponte dedicada**, só para um par de fatos e só se a pergunta for frequente (ex.: tabela `OPERACAO_SUBCLASSE` com uma
   linha por operação e subclasse apreendida). Cresce com o número de pares distintos, não com o produto de todos os fatos.

---

## 6. Outras otimizações do script

| # | Onde | Achado | Proposta |
|---|---|---|---|
| 1 | todos os `000_MAIN.qvs` | Não têm `$(Include=...)`; a ordem real de carga está só no editor do Qlik | Escrever os `$(Include=...)` na ordem real, para o repositório ser a fonte da verdade (`padroes_qvs.md` §4) |
| 2 | `tra/03/033` e `034` x `tra/06/068`, `069`, `0610`, `tra/07/0716`, `0717` | 033/034 criam `TEMP_EVENTOS_*_PF_EXTERNAS_ESTRANGEIRO`; os outros leem `TEMP_EVENTOS_*_EXTERNAS_ESTRANGEIRO` (sem `PF`). No repositório nenhum script cria o nome sem `PF` | Confirmar com o Eduardo se o app real tem um passo que não está no repositório; se não, alinhar os nomes |
| 3 | `tra/06` | `AutoNumberHash128` gravado em QVD: o número só vale dentro da mesma execução da `tra` | Manter as chaves naturais (texto) nos QVDs da `tra` e aplicar `AutoNumber` uma vez no fim do `app` (`AUTONUMBER [%...];`) |
| 4 | `app/032`, `042`, `052` | `LOAD DISTINCT` em todos os QVDs, incluindo os 12 milhões de linhas da link | Tirar o `DISTINCT` onde a `tra` já garante unicidade; deduplicar uma vez só, na `tra` |
| 5 | `tra/07/0721` | Lê os ~12 milhões de linhas da link para extrair as siglas | Montar a partir de `TEMP_DIM_CASOS` (ou de todas as unidades, ver item 7) |
| 6 | `tra/06/061` | ~1.400 linhas de `If` aninhados repetindo os mesmos `ApplyMap` em cada coluna de descapitalização | Calcular classe, flags e ano uma vez num `LOAD` precedente e reutilizar nas colunas |
| 7 | `DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO` | Só cobre siglas que aparecem como unidade de caso; unidades que só aparecem como participantes de eventos ficam sem hierarquia | Gerar a hierarquia para todas as `%UNIDADE_KEY` da link |
| 8 | `FATO_EVENTOS_OPERACIONAIS` | `qtd_presos`, `houve_prisao` e `houve_apreensao` estão no grão de participação (evento × unidade); somar sem a unidade conta o mesmo evento várias vezes | Nas métricas, somar por evento (`Aggr` por `id_evento`) ou guardar `qtd_presos` só na participação prioritária |
| 9 | `069` e `061`/`051` | Com a inclusão dos eventos PF em 033, apreensões de eventos PF podem estar tanto em `FATO_APREENSOES` (item ePol vinculado em 051) quanto em `FATO_EVENTOS_APREENSOES_...` | Definir a regra de contagem antes de escrever as métricas de apreensões de eventos (ex.: eventos PF contam pelo ePol; externos e estrangeiros, pelo evento) |
| 10 | `app/073` e `082` | Ainda são clones das métricas de operações (`Tipo do Fato = 'Operações'`); não há métricas de prisões nem de apreensões de eventos | Escrever depois da Etapa A, já com a regra do item 9 |

---

## 7. Ordem sugerida e validação

1. Medir o tamanho atual (contagem por `Tipo do Fato`, tamanho do QVD da link, RAM e tempo de abertura do app).
2. Etapa A na `tra` (só remoção de blocos `LEFT JOIN`) e recarga.
3. Comparar os KPIs das telas de **Painéis** por data comum (devem ficar iguais) e medir de novo.
4. Etapa B no `app`.
5. Inventário do front-end, depois Etapas C e D.
6. Itens da seção 6, um por PR.

Validação de carga é manual (ambiente Qlik Sense Enterprise, sem MCP).
