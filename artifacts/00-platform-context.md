# Documento de Contexto da Plataforma - Painel SIGACrim Estatísticas Criminais

**Artifact ID:** 00-platform-context
**Version:** 1.0
**Status:** Draft (aguardando confirmação do desenvolvedor na Fase 1)
**Dependencies:** CLAUDE.md, inputs/README.md, qlik/ext, qlik/tra, qlik/app, padroes_qvs.md, README.md, docs/arquitetura_bi.md, docs/modelo_dimensional.md, docs/link_table_relacionamentos.md, docs/dicionario_indicadores.md, .gitignore, histórico git (somente leitura)
**Downstream Consumers:** data-architect, script-developer, expression-developer, viz-architect
**Data da análise:** 2026-09-30
**Método:** análise estática dos .qvs (sem MCP, sem ambiente Qlik). Nenhum script foi executado. Tudo que é inferência está marcado como INFERÊNCIA ou A CONFIRMAR.

---

## 0. Materiais de entrada (inputs/)

| Categoria | Situação | Onde |
|---|---|---|
| existing-apps | Fornecido (referência, não cópia) | qlik/ext, qlik/tra, qlik/app (132 arquivos) |
| platform-libraries | Fornecido (referência) | qlik/*/02_* e padroes_qvs.md |
| upstream-architecture | Fornecido (referência) | docs/*.md, README.md |
| source-documentation | AUSENTE (pasta vazia) | layouts de TabelaoEventos, Eventos_Prisoes, Eventos_Apreensoes, SIGACrim, Palas, ePol não documentados; só há os campos vistos nos LOADs |
| MCP Qlik Cloud | Indisponível | validação de carga é manual (desenvolvedor) |

**Estado do repositório git (leitura):** 96 commits; há 8 arquivos com modificações não commitadas, todos da frente de eventos (tra 033 PF, 034 PF, 052, 068, 069, 0610, 0716, 0717). CLAUDE.md e artifacts/ ainda não rastreados. Os últimos commits (`f52846e`, `bd84016`, `e14176c`, `b3a2c88`) tratam de associar eventos PF ao item de apreensão. Conclusão: a modelagem de eventos está em desenvolvimento ativo (trabalho em andamento).

---

## 1. Inventário das 3 camadas: ATIVO x ÓRFÃO/DUPLICADO

### 1.1 Achado crítico: os 000_MAIN.qvs NÃO contêm `$(Include=...)`

Os três arquivos de orquestração (`qlik/ext/00_orquestracao/000_MAIN.qvs`, `qlik/tra/00_orquestracao/000_MAIN.qvs`, `qlik/app/00_orquestracao/000_Main.qvs`) contêm apenas TRACE de abertura e `SET` de formatos regionais pt-BR (ThousandSep, DateFormat 'DD/MM/YYYY', FirstWeekDay=6, MonthNames etc.). Um `grep -i include` em todo `qlik/` retorna zero ocorrências.

Consequências:
- Não é possível determinar, a partir do repositório, quais scripts estão "incluídos". `padroes_qvs.md` (seções 1 e 4) afirma que a ordem é controlada por `$(Include=...)` no MAIN; isso NÃO corresponde à realidade dos arquivos.
- INFERÊNCIA: o app Qlik (Enterprise/Desktop) é montado copiando o conteúdo dos .qvs para o editor de script, por pasta/ordem numérica, ou por mecanismo externo ao repositório.
- Como critério de "ativo" adotei EVIDÊNCIA DE CONSUMO: um script é considerado ativo se cria tabelas/QVDs consumidos a jusante por outro script, ou se é citado em padroes_qvs.md/docs.
- Diferença de caixa: app usa `000_Main.qvs` (padrão e docs dizem `000_MAIN.qvs`).
- Risco de ordenação lexicográfica: nomes de 3 dígitos e 4 dígitos misturados (`031_`, `032_` ... `0310_`) ordenam alfabeticamente com os de 4 dígitos ANTES (ex.: `0310_` < `031_` porque `0` < `_`). Em tra/03 e tra/07 a ordem alfabética difere da numérica. Se alguma ferramenta concatenar por ordem alfabética, a carga muda. A CONFIRMAR (pergunta 1).

### 1.2 Camada ext (extração) - 31 arquivos .qvs em pastas 00 a 17

Todos os arquivos numerados abaixo são considerados ATIVOS (nenhum duplicado). Fluxo: cada script carrega uma fonte, cria `TEMP_*` residentes, e `15_output/151_GRAVA_QVD.qvs` grava tudo em `E2_*.qvd` (via `StoreAndDrop`).

| Pasta | Arquivos | Papel |
|---|---|---|
| 00, 01, 17 | 000_MAIN, 011_START_LOAD_TIME, 171_END_LOAD_TIME | locale e cronômetro (`vReloadStart`, `ReloadLog`) |
| 02 | 021_VARIAVEIS_EXTRACAO, 022_SUBROTINAS | caminhos, seletor `vCarregaDados`, SUBs Store |
| 03 | 031_TEMP_TNBIA | TNBIA derivado de DIM_CASOS_APREENSAO_BENS |
| 04 | 041_TEMP_ARMAS_MUNICOES_DROGAS_FINAL_CGPRE | 9 xlsx CGPRE concatenados |
| 05 | 050_START, `051 TEMP_TEMP_DIM_CASOS` (nome com espaço), 059_END | DIM_CASOS deduplicado (GROUP BY + LastValue) |
| 06 | 061_AREA_DIRETORIA_CG | Area_Diretoria_CG.xlsx + áreas dos casos |
| 07 | 071_TEMP_TABELAOEVENTOS, 072_TEMP_EVENTOS_PRISOES, 073_TEMP_EVENTOS_APREENSOES | eventos (foco) |
| 08 | 081_TEMP_TEMP_SIGACRIMHOMOLOGADAS, 082_TEMP_PALAS_OPERACOES_TRATADAS_2022_2023 | operações |
| 09 | 090_START, 091_TEMP_DIM_CASOS_APREENSAO_BENS, 099_END | itens de apreensão deduplicados |
| 10, 11, 12 | 101 CASOS_DATA, 111 TEMP_DIM_CASOS (conjunto de casos relevantes), 121 TIPO_PENAL | casos |
| 13, 14 | 131 SERVIDOR_ATIVO; 141 a 146 (unidade, hierarquia técnica, circunscrição, municípios, UF, faixa de fronteira) | efetivo e unidades |
| 15, 16 | 151_GRAVA_QVD, 161_SECTION_ACCESS | saída e segurança |

Observação: a ordem física exigida é 05 (TEMP_TEMP_DIM_CASOS) antes de 07 (join LEFT em 071), 08, 10, 11 e 06; e 111 dropa `TEMP_TEMP_DIM_CASOS` ao final (linha 244).

### 1.3 Camada tra (transformação) - 69 arquivos .qvs (+ 1 .js)

| Pasta | ATIVOS (por consumo) | ÓRFÃO / DUPLICADO / OBSERVAÇÃO |
|---|---|---|
| 02 | 021_VARIAVEIS_CAMINHOS_UNIDADES_AREAS_DIRETORIAS_CGS, 022_SUBROTINAS | sem duplicata |
| 03 | 031, 0310 a 0318, 035, 036, 038, 039, **032_TEMP_TABELAOEVENTOS_ID_UNIFICADO**, **033_TEMP_EVENTOS_APREENSOES_PF_EXTERNAS_ESTRANGEIRO**, **034_TEMP_EVENTOS_PRISOES_PF_EXTERNAS_ESTRANGEIRO**, 037 | ver pares abaixo; 037 tem nome com "2032_2033" mas carrega `TEMP_Palas_Operacoes_Tratadas_2022_2023` (erro só no nome do arquivo) |
| 04 | 041_MAPPING_LOADS (23 KB, ~35 mapping tables) | mapping `MapIdOrdemOriginalEventoIdOperacao` (linha 366) definido e NUNCA consumido (código morto) |
| 05 | 051_ADICIONA_EVENTOPF_AO_ITEM_APREENSAO (WIP, tem defeitos, ver 4.6), 052_ADICIONA_ID_OPERACAO_AO_ITEM_APREENSAO, 053_AJUSTE_ERRO_SINC_TEMP_SIGACRIMHOMOLOGADAS | 051_..._ATUAL_FUNCIONANDO e `Untitled-1.js` (ver abaixo) |
| 06 | 061 a 069, 0610 (10 fatos) | sem duplicata |
| 07 | 071 a 079, 0710 a 0727 (27 arquivos) | sem duplicata (README diz 23 DIMs; são 27 arquivos) |
| 08, 09 | 081_SECTION_ACCESS, 091_END_LOAD_TIME | - |

**Pares duplicados em tra (o MAIN não inclui nenhum; a coluna "usado pela cadeia atual" é INFERÊNCIA por consumo):**

| Par | Versão A (sem sufixo) | Versão B (`_ATUAL_FUNCIONANDO`) | Qual a cadeia atual consome |
|---|---|---|---|
| 032 | `032_TEMP_TABELAOEVENTOS_ID_UNIFICADO.qvs` (98 KB, ~1750 linhas): evolução; acrescenta `TEMP_TABELAOEVENTOS_UNID_PARTICIPANTE_DEDUPLICADA`, `NoConcatenate`, `id_evento` original (sem renomear) | `..._ATUAL_FUNCIONANDO.qvs` (95 KB): versão anterior; renomeia `id_evento_unificado AS id_evento` | Ambos criam a mesma tabela `TEMP_TABELAOEVENTOS_ID_UNIFICADO` e dropam as mesmas temporárias; só UM pode existir no script (o segundo falharia por tabelas já dropadas). Os consumidores (068, 069, 0610, 0715, 064, 066, 067, 041) funcionam com ambos os esquemas de campo. Qual está ativo: A CONFIRMAR |
| 033 | `033_TEMP_EVENTOS_APREENSOES_PF_EXTERNAS_ESTRANGEIRO.qvs`: cria `TEMP_EVENTOS_APREENSOES_PF_EXTERNAS_ESTRANGEIRO` (inclui eventos PF) | `033_..._EXTERNAS_ESTRANGEIRO_ATUAL_FUNCIONANDO.qvs`: cria `TEMP_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` (só externo/estrangeiro) | A cadeia atual (051, 069, 0716, 068) consome a tabela `..._PF_EXTERNAS_...`. A tabela da versão B não é consumida por nenhum script: B é código morto |
| 034 | `034_TEMP_EVENTOS_PRISOES_PF_EXTERNAS_ESTRANGEIRO.qvs` | `034_..._EXTERNAS_ESTRANGEIRO_ATUAL_FUNCIONANDO.qvs` | idem: 0610, 0717, 068 consomem `TEMP_EVENTOS_PRISOES_PF_EXTERNAS_ESTRANGEIRO`; B é código morto |
| 051 | `051_ADICIONA_EVENTOPF_AO_ITEM_APREENSAO.qvs` (WIP, autor/data 15/09/2026, com o bloco novo de match por IPL+Subclasse) | `..._ATUAL_FUNCIONANDO.qvs`: contém somente o IntervalMatch por data (bloco 2 do A) | A é superconjunto de B. O bloco novo de A tem defeitos (4.6). B é a última versão sabidamente funcional. Qual está ativo: A CONFIRMAR |
| 052 | `052_ADICIONA_ID_OPERACAO_AO_ITEM_APREENSAO.qvs` (modificado, não commitado) | `05_ajustes_qvds_originais/Untitled-1.js` (11.410 bytes): rascunho quase idêntico ao 052 (mesmo algoritmo IntervalMatch IPL/RE_SEQUESTRO; comentários mencionam "prioridade para ID_OPERACAO vindo do id_ordem_original_evento", ideia não implementada em nenhum lugar) | Untitled-1.js é rascunho órfão, extensão errada, rastreado no git |

Nota: o nome "ATUAL_FUNCIONANDO" viola padroes_qvs.md 3.4 (versão no nome) e, semanticamente, o que está "funcionando" (B) é o mais ANTIGO. Os sem sufixo (A) são os que os fatos/dimensões novos exigem.

### 1.4 Camada app - 30 arquivos

Todos ATIVOS por consumo, sem duplicatas de nome: 011, 021_SUBROTINAS, 022_VARIAVEIS_DE_AMBIENTE, 023_VARIAVEIS_DE_EFETIVO, 031/032/033 (fatos), 041/042/043 (link), 051/052/053 (dimensões), 061, 071 a 076, 081 a 086, 091, 101, 111.

Duplicação de conteúdo (não de nome): `082_VARIAVEIS_DE_MEDIDAS_MESTRAS_DE_EVENTOS_OPERACIONAIS.qvs` (940 KB, 19.598 linhas) é uma cópia desdobrada (sem SUB, 382 SET/LET) das medidas mestras de OPERAÇÕES do 081 (cabeçalho ainda diz "Medidas Mestras Operacionais"; 176 variáveis `vMedidaMestra*` com os mesmos nomes do 081; referencia `$(vOperHom...)`, não `vEvenOper...`). Ver seção 4.

### 1.5 Fora das camadas

- `qlik/planilha resultados operacionais para MJ EM NÚMEROS.qvs` (38 KB): script avulso na raiz de qlik/, com paths `lib://` fixos e arquivos de 09-09-2026 (`descapitalizacao_baggio_09-09-2026.xlsx` etc.); nada o referencia. Fora do padrão de camadas. Commit `728f9d0` o descreve como "tabela de teste".
- `scripts/` e `QVDs/` citados em README.md/arquitetura_bi.md NÃO existem no repositório.

---

## 2. Fontes, conexões e linhagem

### 2.1 Catálogo de conexões (lib://)

Variáveis de caminho definidas em `qlik/ext/02_.../021_VARIAVEIS_EXTRACAO.qvs` (e repetidas em tra/021 e app/022).

| Conexão | Tipo | Uso | Variável |
|---|---|---|---|
| `lib://CORP_DICOR_COP/` | Pasta (QVDs corporativos) | TabelaoEventos.qvd, Eventos_Prisoes.qvd, Eventos_Apreensoes.qvd, SIGACrim.qvd (+ SIGACrimMaquinarios.qvd citado em script avulso) | `vCaminhoQvdSigacrim` |
| `lib://MD_SIGACRIM/` | Pasta | Palas_Operacoes_Tratadas_2022_2023.qvd; SIGACrimMaquinariosHom.qvd (lido DIRETO na camada tra, 041 linha 379, fora do padrão ext) | `vCaminhoQvdPalas` |
| `lib://MD_EPOL/` | Pasta | DIM_CASOS.qvd, DIM_CASOS_DATA.qvd, DIM_CASOS_APREENSAO_BENS.qvd (e, pela variável, DIM_CASOS_TIPO_PENAL.qvd) | `vCaminhoQvdEpol` |
| `lib://CORP_DADOS_AUXILIARES/qvd/` | Pasta | DIM_SERVIDOR_ATIVO, DIM_UNIDADE, DIM_CIRCUNSCRICAO_PF, TB_MUNICIPIOS_BRASIL, TB_UF_BRASIL | `vCaminhoQvdCorpDadosAuxiliares` |
| `lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/` | Pasta (xlsx auxiliares + QVDs próprios) | ver 2.2 | `vCaminhoTabelasCorpDicorNge` |
| `.../E2_` | prefixo de arquivo (ext grava) | QVDs extraídos da camada ext | `vCaminhoExtraidosV2` |
| `.../T3_` | prefixo (tra grava, app lê) | QVDs transformados FATO_*, DIM_*, LINK_TABLE | `vCaminhoTransformadosV3` |
| `.../PAINEL_APREENSOES_IZEL/` | Pasta de "testes" | snapshots `..._01_04_2026.qvd` do modo IPO_2025 | `vCaminhoTabelasTeste`, `vCaminhoQvdIpo2025` |

Variações por ambiente: nenhum mecanismo dev/test/prod encontrado. Existe um seletor de DADOS, não de ambiente: `vCarregaDados` = 'Atuais' | 'IPO_2025' (snapshots de 01/04/2026). Prefixos herdados E_, E2_, T_, T2_, T3_ coexistem (`vCaminhoExtraidos`, `vCaminhoTransformados`, `V2`, `V3` definidos; só E2_ e T3_ são usados de fato).

Arquivos xlsx/xls em CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/: armas_final, municoes_final, Drogas_2022 a 2025_Izel_2, armas_2026_2, municoes_2026_2, drogas_2026_2, Area_Diretoria_CG, HIERARQUIA_TECNICA_PF_v8, Mun_Faixa_de_Fronteira_Cidades_Gemeas_2024.xls, `CONSOLIDADA - Bens Interesse e Descapitalização Izel.xlsx` (abas de mapeamento, inclusive MapApreensoesEventosPF), descapitalizao_epol_31_03_2025 (sic), `Ops Argus Izel.xlsx`, DPF-CAC-PR, DPF-GRA-PR, RECURSO_HUMANOS_BRUTOS_ARGOS, SECTION_ACCESS_*.xlsx (3).

### 2.2 Arquitetura: multi-app, pipeline de QVDs em 3 apps (INFERÊNCIA: 3 apps/scripts de reload separados)

Classificação: **multi-app, ext -> tra -> app, encadeado por QVDs** (confiança ALTA: as pontes E2_ e T3_ são explícitas em 151_GRAVA_QVD e nos `StoreAndDrop` de tra/06 e tra/07). Dependência de reload: ext deve terminar antes de tra; tra antes de app. Nenhuma agenda de reload está no repositório.

Padrão de gravação: SUB `StoreAndDrop(pTableName, pPathStore)` grava `<caminho><tabela>.qvd` e dropa. Não há carga incremental (todas as cargas são completas; ver 5.3).

### 2.3 Linhagem por domínio (ext -> tra -> app)

**Operações (SIGACrim homologadas e Palas)**
- SIGACrim.qvd -> ext 081 (`TEMP_TEMP_TEMP_SIGACrimHomologadas` -> `TEMP_TEMP_SIGACrimHomologadas`, SplitColon/Tokens/Normalizado, `DIM_OPERACOES_SEM_AREA`) -> E2_TEMP_TEMP_SIGACrimHomologadas.qvd -> tra 036 -> tra 053 (recria como `TEMP_SIGACrimHomologadas` com UnidadeBase/AreaBase/DiretoriaBase/CoordenacaoBase e dropa o TEMP_TEMP) -> 064 FATO_OPERACOES, 062 FATO_APREENSOES (SIGACrim), 071/072/075 DIMs -> T3_FATO_OPERACOES, T3_DIM_OPERACOES, T3_DIM_* -> app 032/052.
- Palas_Operacoes_Tratadas_2022_2023.qvd -> ext 082 -> E2_TEMP_Palas... -> tra 037 -> 065 FATO_OPERACOES (Palas), 063 FATO_APREENSOES (Palas), 073/076 DIMs.
- Nota: FATO_OPERACOES e FATO_APREENSOES são concatenados de duas fontes (SIGACrim + Palas) sob o mesmo nome de tabela.

**Eventos operacionais (foco)**
- TabelaoEventos.qvd -> ext 071 (`recno() AS id_ordem_original_evento`; filtra `ds_etapa_evento='Homologada'` E `Year(dt_evento) > 2023`; LEFT JOIN de "Proc. Identificação" via IPL a partir de TEMP_TEMP_DIM_CASOS) -> E2_TEMP_TABELAOEVENTOS.qvd -> tra 032 (deduplicação em 2 níveis, ver 4.2) -> `TEMP_TABELAOEVENTOS_ID_UNIFICADO` -> 068 FATO_EVENTOS_OPERACIONAIS, 0715 DIM_EVENTOS_OPERACIONAIS; também consumido por 041 (mappings de flagrante interno PF e `MapIdOrdemOriginalEventoIdOperacao`), 051, 064, 066, 067 (chaves %EVENTOSKEY nos links).
- Eventos_Prisoes.qvd -> ext 072 -> E2_TEMP_EVENTOS_PRISOES.qvd -> tra 032 (anonimização, CPF válido) -> tra 034 -> `TEMP_EVENTOS_PRISOES_PF_EXTERNAS_ESTRANGEIRO` -> 0610 FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO, 0717 DIM_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO.
- Eventos_Apreensoes.qvd -> ext 073 -> E2_TEMP_EVENTOS_APREENSOES.qvd -> tra 032 -> tra 033 (+ TNBIA para código de subclasse; xlsx MapApreensoesEventosPF para eventos PF) -> `TEMP_EVENTOS_APREENSOES_PF_EXTERNAS_ESTRANGEIRO` -> 069 FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO, 0716 DIM_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO; e 051 (liga evento PF ao item de apreensão ePol).

**Apreensões (ePol, SIGACrim, Palas, CGPRE, descapitalização)**
- DIM_CASOS_APREENSAO_BENS.qvd (MD_EPOL; ~8M linhas brutas segundo comentário) -> ext 091 (GROUP BY "GestãoBens Item ID" com LastValue, ano de apreensão > 2021, conversão monetária em preceding LOAD) -> E2_TEMP_TEMP_DIM_CASOS_APREENSAO_BENS.qvd -> tra 038 -> 051/052 (acrescentam id_ordem_original_evento e ID_OPERACAO por IntervalMatch) -> 061 FATO_APREENSOES (ePol; 71 KB; onde é calculada a descapitalização LVL1/LVL2) e 077 DIM_APREENSOES.
- Descapitalização: regras vêm de mappings em tra 041 sobre `CONSOLIDADA - Bens Interesse e Descapitalização Izel.xlsx` (`MapItemInteresse`, `MapItemDescapitalizacao`, `MapClasse_LVL_1`, `MapClasse_LVL_2`, `MapItemDestrAmb`, `MapFatorCigarros`, `MapCocainaIDs` etc.) e `descapitalizao_epol_31_03_2025.xlsx`; valores de maquinário destruído de `SIGACrimMaquinariosHom.qvd`; regras por ano (2024 com regra de corte em 31/03/25; >2024 regra nova) codificadas dentro de IFs aninhados em 061.
- CGPRE armas/munições/drogas: 9 xlsx -> ext 041 -> E2_TEMP_TEMP_TEMP_ARMAS... -> tra 035 -> 061.
- TNBIA: ext 031 (derivado de DIM_CASOS_APREENSAO_BENS) -> tra 031 -> 0727 DIM_TNBIA e `MapItemMaterialID`/`MapSubClasseItemMaterialID`.
- SIGACrim e Palas também geram FATO_APREENSOES (062, 063) e DIM_APREENSOES (078, 079).

**Prisões**
- Não existe fato único de prisões. Há 3 origens separadas, sem integração entre si: (a) Eventos_Prisoes.qvd (FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO), (b) contagens de prisões dentro de FATO_OPERACOES (`QTD_CUMPRIDA_PRISAO_PREVENTIVA`, `QTD_EXPEDIDA_PRISAO_*`, medidas `vMedidaMestraPrisoes*EmOperacoes`), (c) prisões em flagrante do ePol (medidas 085 `PrisoesEmFlagrante*`, via flags de DIM_CASOS).

**Casos/procedimentos ePol**
- DIM_CASOS.qvd -> ext 051 (dedup LastValue, ~3M linhas) -> TEMP_TEMP_DIM_CASOS (auxiliar; usada por 061, 071, 081, 082, 101, 111; dropada em 111) -> ext 111 `TEMP_DIM_CASOS` (união de chaves de eventos PF, SIGACrim, Palas, apreensões, casos relatados a partir de 2022 ou em andamento, CASOS_DATA) -> E2_TEMP_DIM_CASOS.qvd -> tra 0310 (flags de flagrante, fronteira) -> 066 FATO_CASOS, 0710/0711/0712/0713 DIMs. DIM_CASOS_DATA: ext 101 -> tra 039 -> 067 FATO_CASOS_DATA, 0714. DIM_CASOS_TIPO_PENAL: ext 121 -> tra 0311 -> 0712.

**Unidades**
- DIM_UNIDADE, HIERARQUIA_TECNICA_PF_v8.xlsx, DIM_CIRCUNSCRICAO_PF, TB_MUNICIPIOS_BRASIL, TB_UF_BRASIL, Mun_Faixa_de_Fronteira: ext 141-146 -> tra 0313-0318 -> 0719/0720/0721/0722/0723/0724/0725/0726 -> `[%UNIDADE_KEY]` = AutoNumberHash128("Unidade Sigla"). Complementos: mappings `MapIPLUnidadeFiccoGise` (Ops Argus Izel.xlsx), `MapCorrigeUnidSuperiorDpfCacDpfGra`.

**Efetivo**
- DIM_SERVIDOR_ATIVO.qvd -> ext 131 -> tra 0312 -> 0718 DIM_SERVIDOR_ATIVO (chave `%UNIDADE_KEY`); RECURSO_HUMANOS_BRUTOS_ARGOS.xlsx em mapping de lotação (041). No app: 023_VARIAVEIS_DE_EFETIVO (76 KB, 180 SET/LET de modificadores de conjunto) e 086 (medidas de efetivo geradas em loop `TabelaMedidasMestrasEfetivo`).

---

## 3. Modelo de dados atual

### 3.1 Tabelas de fato carregadas no app (app/03_fatos/032_FATOS.qvs)

`FATO_APREENSOES` (chave `%APREENSOESKEY`), `FATO_OPERACOES` (`%OPERACOESKEY`), `FATO_CASOS` (`%CASOSKEY`), `FATO_CASOS_DATA` (`%CASOSDATAKEY`), `FATO_EVENTOS_OPERACIONAIS` (`%EVENTOSKEY`; campos houve_apreensao, houve_prisao, qtd_presos), `FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` (`%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY`; qt_item, st_selecionado), `FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` (`%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY`; cd_tipo_prisao, cd_documento, st_nao_cpf, nome_cpf_preso).

### 3.2 Dimensões carregadas no app (app/05_dimensoes/052_DIMENSOES.qvs)

Chaves secundárias `%X_KEY`: DIM_OPERACOES, DIM_GPOL_UF_MUNICIPIOS_DEFLAGRACAO, DIM_GPOL_UNIDADE_SIGLA_DEFLAGRACAO, DIM_EFETIVOS_GPOL, DIM_Caso_de_RE_de_Recuperação_de_Ativos, dimensões de atributos (loop `vTabela`) e DIM_INFORMACOES_GERAIS / DIM_MEDIDAS_EXTRAORDINARIAS / DIM_RESULTADOS_DEFLAGRACAO / DIM_SETORIAIS_DAMAZ|DICOR|DCIBER (por `%ID_FILTROS_OPERACAO_KEY`), DIM_APREENSOES (`%GESTAO_BENS_ITEM_ID_KEY`), DIM_CASOS / DIM_CASOS_TIPO_PENAL / DIM_MATERIA_RE (`%PROC_IDENTIFICACAO_KEY`), DIM_CASOS_DATA (`%PROC_DATA_ID_KEY`), DIM_INFORMACOES_CASOS, DIM_OPERACOES_SEM_AREA, DIM_EVENTOS_OPERACIONAIS (`%ID_EVENTOS_KEY`), DIM_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO (`%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY`), DIM_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO (`%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY`), DIM_TNBIA (`%ITEM_SUBCLASSE_KEY`), e as dimensões de unidade (todas por `%UNIDADE_KEY`): DIM_UNIDADE, DIM_SERVIDOR_ATIVO, DIM_HIERARQUIA_TECNICA, DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO, DIM_UNIDADE_SUBUNIDADE, DIM_CIRCUNSCRICAO_PF (+ `%CODIGO_IBGE` com DIM_TB_MUNICIPIOS_BRASIL).

### 3.3 Link table (`LINK_TABLE_APREENSOES_OPERACOES_CASOS`)

Construída em tra/06_fatos: 061 cria a tabela; 062 a 0610 fazem `CONCATENATE` de uma `TEMP_LINK_TABLE_..._<fato>` por fato; 0722 a grava em T3_. O app a lê em `app/04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs` com lista explícita de 39 campos.

Campos-chave na link table (hash `AutoNumberHash128` sobre o valor natural):

| Chave de fato (liga a FATO_*) | Origem do hash | Chave de dimensão (liga a DIM_*) |
|---|---|---|
| `%CASOSKEY` | "Proc. Identificação" | `%PROC_IDENTIFICACAO_KEY` (DIM_CASOS, tipo penal, matéria RE) |
| `%CASOSDATAKEY` | "Proc_Data ID" | `%PROC_DATA_ID_KEY` |
| `%OPERACOESKEY` | ID_OPERACAO | `%ID_OPERACAO_KEY` |
| `%APREENSOESKEY` | "GestãoBens Item ID" (ePol); 'SIGACrim'&'_'&ID_OPERACAO; ID_OPERACAO (Palas) | `%GESTAO_BENS_ITEM_ID_KEY` |
| `%SUBCLASSESKEY` | "GestãoBens Item Material Subclasse Código" | `%ITEM_SUBCLASSE_KEY` (DIM_TNBIA) |
| `%EVENTOSKEY` | id_ordem_original_evento | `%ID_EVENTOS_KEY` (DIM_EVENTOS_OPERACIONAIS) |
| `%EVENTOSAPREENSOESEXTERNASESTRANGEIRASKEY` | id_evento_apreensao | `%ID_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRAS_KEY` |
| `%EVENTOSPRISOESEXTERNASESTRANGEIRASKEY` | id_evento_prisao | `%ID_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRAS_KEY` |
| `%UNIDADE_KEY` (compartilhada) | "Proc. Unidade Exercício" corrigido (casos); unidade_participante (eventos); sigla (operações Palas) | DIM_UNIDADE e demais dimensões de unidade |

Cada chave existe DUAS vezes (uma para o fato, outra para a dimensão), padrão que dobra a largura da link table (docs falam em "4 chaves"; são 8 pares mais `%UNIDADE_KEY`).

Campos analíticos na própria link table: `Data`, `Ano`, `Mês`, `Mês (Num)`, `Tipo da Data`, `Fonte`, `Tipo do Fato`, e atributos de unidade/área/diretoria/CG separados por contexto (do Caso; do Evento Operacional; do Evento Externo/Estrangeiro).

`Tipo da Data` / `Tipo do Fato` / `Fonte` usados pelas métricas: 'Apreensão', 'Instauração do Caso', 'Deflagração da Operação', 'Evento do Caso', 'Evento Operacional', 'Evento Apreensão Externo/Estrangeiro', 'Evento Prisão Externo/Estrangeiro'.

### 3.4 Calendário

NÃO existe tabela de calendário mestre no repositório (grep "calend" só acha variáveis `vTemSelecaoDatasCalendario`). A "dimensão de tempo" é o conjunto de campos `Data/Ano/Mês/Mês (Num)/Tipo da Data` dentro da link table: uma linha por combinação chave x data, com `Tipo da Data` discriminando o tipo de data. Além disso, cada DIM tem seus próprios campos de data (`Ano da Deflagração`, `Ano da Apreensão`, `Data do Evento Operacional`, ...). docs/modelo_dimensional.md ("Calendário Canônico (Master Calendar) ... configurada na camada app/") descreve algo que não existe.

### 3.5 Riscos de chave sintética e referência circular (INFERÊNCIA, não verificável sem executar)

1. **Fan-out na link table de eventos (068):** a `TEMP_LINK_TABLE_..._EVENTOS_OPERACIONAIS` recebe 3 `LEFT JOIN` sucessivos pela mesma chave `%ID_EVENTOS_KEY` (itens de apreensão ePol; eventos-apreensão; eventos-prisão). Cada join multiplica linhas: um evento com A itens x B apreensões-evento x C presos gera A x B x C linhas. Contagens distintas resistem, somas por dimensões de unidade/data podem inflar. A VALIDAR.
2. **Conflito de chave no join do caso em 068:** a carga inicial traz `[%UNIDADE_KEY]` do evento (`unidade_participante`); o LEFT JOIN seguinte usa `vCarregaUnidAreaDirCoorGeralDoCaso`, que TAMBÉM define `[%UNIDADE_KEY]` (unidade do caso). Como o join no Qlik é natural por TODOS os campos comuns, ele passa a casar por `%PROC_IDENTIFICACAO_KEY` E `%UNIDADE_KEY` juntos: "Unidade/Área/Diretoria/CG do Caso" só preenchem quando a unidade do caso coincide com a unidade participante do evento. Provável defeito. (Em 069 e 0610 esses joins estão comentados.)
3. **`%UNIDADE_KEY` compartilhado** entre a link table e 6 dimensões: essas dimensões associam-se diretamente entre si e com a link por um único campo (ok), mas todo evento/caso/operação passa a ter 3 "unidades" diferentes (do caso, do evento, da operação) mapeadas para o mesmo campo `%UNIDADE_KEY`; o conteúdo depende da linha. Ambiguidade semântica ao filtrar por unidade.
4. **Campo `IPL`** só existe em DIM_EVENTOS_OPERACIONAIS no app (sem colisão), mas o mesmo evento carrega `nr_caso` (DIM_EVENTOS_APREENSOES) e `[Caso]` (DIM_CASOS): nomes diferentes, sem associação. Os eventos de apreensão/prisão NÃO têm chave de caso/operação própria: chegam ao caso apenas via `%EVENTOSKEY`/`%ID_EVENTOS_KEY` das linhas do 068.
5. **Granularidade de FATO_EVENTOS_OPERACIONAIS:** uma linha por `id_ordem_original_evento` = evento x unidade participante deduplicada. `qtd_presos` é o total do evento repetido em cada unidade participante: `Sum(qtd_presos)` conta em dobro/triplo eventos com várias unidades. As apreensões e prisões (fatos 069/0610) são atribuídas a UMA unidade (FirstSortedValue) e não sofrem esse problema.
6. **Duplo caminho para o mesmo evento:** as linhas de link de 061, 064, 066, 067 também trazem `%EVENTOSKEY`, então um evento pode alcançar um caso por dois caminhos (linhas de 068 e linhas de 061/064/066/067). Não gera loop (tudo está na mesma link table) mas gera redundância de linhas.
7. **Documentos divergem do código:** docs falam `DIM_SUBCLASSES` e `%SUBCLASSESKEY`; o código usa `DIM_TNBIA` + `%ITEM_SUBCLASSE_KEY` (o `%SUBCLASSESKEY` existe na link mas nenhuma dimensão o usa; só o par `%ITEM_SUBCLASSE_KEY` liga a DIM_TNBIA).
8. **`SET HidePrefix='%'`** (app 022) esconde todas as chaves; ok.

---

## 4. Área de foco: modelagem de eventos operacionais, apreensões e prisões

### 4.1 Quadro de situação

| Componente | Arquivos | Situação |
|---|---|---|
| Extração dos 3 QVDs de eventos | ext 071, 072, 073, 151 | COMPLETO (mas com filtro rígido: só 'Homologada' e `Year(dt_evento) > 2023` em 071; 072/073 sem filtro próprio) |
| Deduplicação e unificação de eventos | tra 032 (98 KB) | COMPLETO, complexo, em evolução (WIP: novo arquivo A com unidades participantes deduplicadas; versão B anterior mantida) |
| Fato eventos operacionais | tra 068 | PARCIAL: só 3 campos analíticos (houve_apreensao, houve_prisao, qtd_presos); defeitos 3.5 (1, 2, 5) |
| Fato eventos de apreensão | tra 069 | PARCIAL: só qt_item e st_selecionado; `un_item` fica na DIM; sem valor, sem descapitalização |
| Fato eventos de prisão | tra 0610 | PARCIAL: cd_tipo_prisao, cd_documento, st_nao_cpf, nome_cpf_preso; sem medida de contagem pronta |
| Dimensões de eventos | tra 0715, 0716, 0717 | PARCIAL a COMPLETO (atributos descritivos ok; nomes "Externo/Estrangeiro" enganosos, pois agora cobrem também eventos PF) |
| Integração à link table | 068, 069, 0610 + campos em 042 app | COMPLETO estruturalmente (chaves de fato e dimensão para os 3 eventos), com riscos 3.5 |
| Ligação evento PF -> item de apreensão ePol | tra 051 | INCOMPLETO / com defeitos (4.6) |
| Ligação operação -> item de apreensão | tra 052 | Funcional (modificado, não commitado) |
| Métricas de eventos | app 073 (205 KB) | PLACEHOLDER: clone das métricas de operações (4.4) |
| Medidas mestras de eventos | app 082 (940 KB) | PLACEHOLDER: clone desdobrado do 081 (4.4) |
| Scaffolding em 071 (controle) | vConjEven*, vAnoEvenSelecionado etc. | Iniciado (2 defeitos de cópia, 4.4) |
| Dimensão calendário dedicada | - | AUSENTE (3.4) |
| Dimensão de tipo de evento / participação / unidade executora | - | AUSENTE como dimensão própria (campos soltos em DIM_EVENTOS_OPERACIONAIS) |

### 4.2 Lógica de deduplicação (tra 032) - o coração do modelo de eventos

Fatos sobre o TabelaoEventos descritos no cabeçalho do 032:
- Um `id_evento` se repete por unidade participante e tipo de participação (`execucao_direta` > `prestacao_info` > `prestacao_apoio` > sem participação, prioridade 1/2/3/999). A chave substituta `id_ordem_original_evento = recno()` (criada no ext 071) identifica cada participação.
- Três tipos de evento (`cd_tipo_evento_fk`): 'pf' (individualizado por IPL + data em `id_eventos_pf`), 'externo' (data + força/UF + município/UF em `id_eventos_externos`), 'estrangeiro' (país + data em `id_eventos_estrangeiros`).
- Dedup em duas etapas: (1) por (id_evento, unidade_participante) escolhe a menor `id_ordem_original_evento` com maior prioridade; (2) entre eventos distintos do mesmo indivíduo-evento, mantém o evento com mais presos em comum (empate: mais presos totais; depois o mais recente), e depois o mesmo critério por apreensões em comum, para os que não foram deduplicados por presos.
- Contagem de presos: CPF válido como identificador; sem CPF/inválido usa nome (UPPER/TRIM); dedup dentro do mesmo evento; nomes e CPFs anonimizados por mappings (`Mapno_presoNomesAnonimizados`, `Mapds_cpfCPFAnonimizados`, `MapCPFLimpoFlCPFValido`, `MAP_ID_EVENTO_NOME_PRESO_CPF_VALIDO`).
- Resultado: `TEMP_TABELAOEVENTOS_ID_UNIFICADO`, 1 linha por (evento unificado x unidade participante deduplicada), com `tem_relacao_operacoes AS ID_OPERACAO`, `prioridade_participante_evento`, "Proc. Identificação".
- O bloco "pares de eventos com presos/apreensões em comum" está repetido 6 vezes (PF, externo, estrangeiro x prisão, apreensão) por copia e cola (linhas ~570 a ~1490).
- 033/034 atribuem cada apreensão/prisão a UMA unidade participante (FirstSortedValue por `prioridade * 1e9 + id_ordem_original_evento`), evitando multiplicar quantidades pelo número de unidades.

### 4.3 Construção das chaves e do relacionamento evento -> caso/operação/apreensão

- `%EVENTOSKEY` = AutoNumberHash128(id_ordem_original_evento).
- Evento -> caso: por "Proc. Identificação" (join por IPL feito na ext 071; o commit `b3a2c88` inclui casos "NC").
- Evento -> operação: `tem_relacao_operacoes AS ID_OPERACAO` (sem tratamento de eventos ligados a mais de uma operação; ver pergunta 12).
- Evento PF -> item de apreensão ePol: 051 (inferência por IPL + Subclasse e, em seguida, por intervalo de data). Eventos externos/estrangeiros apreensão -> subclasse TNBIA via `cd_item_epol_fk` -> `MapItemMaterialID`; eventos PF via texto `ds_item` -> `MapApreensoesEventosPF` (xlsx CONSOLIDADA...). Ligação por texto livre; itens sem mapeamento ficam com subclasse NULL (a validação `TEMP_VALIDACAO` em 033 grava CSV para auditoria manual e nunca é dropada).

### 4.4 Métricas e medidas mestras (ponto mais incompleto)

- `app/07.../073_VARIAVEIS_DE_METRICAS_DE_EVENTOS_OPERACIONAIS.qvs`: 207 SET/LET, ~5.000 linhas. Cabeçalho e comentários dizem "Eventos Operacionais Homologados", mas as expressões usam `ETAPAOPERACAO = {'Homologada'}` (384 ocorrências), `[Tipo do Fato] = {'Operações'}`, `[Tipo da Data] = {'Deflagração da Operação'}` (192 ocorrências) e listas de nomes `vEvenOperHom*`, `vEvenOperPris*...`. Nenhuma referência a `qtd_presos`, `houve_prisao`, `houve_apreensao`, `qt_item`, `nome_cpf_preso`, `'Evento Operacional'`, `%EVENTOSKEY`: é um CLONE das métricas de operações (072) com radical renomeado. As variáveis `vEvenOper*` (240 ocorrências) não são consumidas por nenhum outro arquivo.
- `app/08.../082_..._DE_EVENTOS_OPERACIONAIS.qvs`: 19.598 linhas, 176 variáveis `vMedidaMestra*` com os MESMOS nomes do 081 (`vMedidaMestraOperacoesHomologadas...`, `...PrisoesCumpridasEmOperacoes...`), referenciando `$(vOperHom...)`. Se 081 e 082 forem executados no mesmo app, 082 sobrescreve 081 com conteúdo equivalente; se só um for usado, o outro é peso morto. Não há nenhuma medida sobre `FATO_EVENTOS_*`.
- Prisões e apreensões de EVENTOS não têm nenhuma métrica nem medida mestra (nenhuma contagem de `nome_cpf_preso`, `id_evento_prisao`, soma de `qt_item`).
- Em `071_VARIAVEIS_DE_METRICAS_DE_CONTROLE.qvs` já existem `vConjEvenDtMesAnoPfEmNumeros`, `vConjEvenDtMesAnoEvenPfEmNumeros`, `vConjEvenPris...`, `vConjEvenApre...` e `vAnoEvenSelecionado`, `vAnoEvenPrisSelecionado`, `vAnoEvenApreSelecionado`, com defeitos de cópia: `vConjEvenApreDtMesAnoEvenAprePfEmNumeros` usa o campo `[Data do Evento Prisão Externo/Estrangeiro]` (deveria ser o de Apreensão); os comentários repetem "somente operações homologadas até o dia 5"; os `Call TratarExpansaoMacro` estão comentados.
- Dicionário de indicadores (docs/dicionario_indicadores.md) descreve "Prisões Externas" e "Apreensões Externas" com fórmula "Contagem de eventos"; não define fórmula, grão nem filtro; e cita medidas (`Sum([Quantidade Prisões Cumpridas])`, `Sum([Quantidade Maconha Erradicada])`) cujos campos não existem no código (o código usa `QTD_CUMPRIDA_PRISAO_PREVENTIVA` etc.).

### 4.5 Ausências para "concluir a modelagem" (lista objetiva)

1. Confirmar/fechar qual 032/033/034/051 é o vigente (pergunta 2) e eliminar os demais.
2. Corrigir 051 (4.6) e decidir a regra de atribuição evento PF -> item.
3. Resolver o fan-out e o conflito de `%UNIDADE_KEY` no link de 068 (3.5 itens 1 e 2).
4. Definir grão e medida canônica de "presos", "apreensões" e "eventos" (contar `nome_cpf_preso` distinto? por evento unificado ou por unidade?).
5. Enriquecer os fatos (069: valor/quantidade normalizada; 0610: tipo de prisão decodificado, flags) e as dimensões (tipo de evento, participação, unidade executora, país).
6. Criar métricas e medidas mestras reais para eventos/apreensões de eventos/prisões de eventos (substituir 073 e 082).
7. Definir o tratamento de datas (calendário canônico ou manter na link table).
8. Renomear "Externo/Estrangeiro" onde o conteúdo agora inclui PF.
9. Documentar filtros de escopo (homologado e ano > 2023).

### 4.6 Defeitos concretos encontrados (por arquivo)

- `tra/05.../051_ADICIONA_EVENTOPF_AO_ITEM_APREENSAO.qvs` (versão A): (a) `FROM TEMP_EVENTOS_APREENSOES_PF_EXTERNAS_ESTRANGEIRO` deveria ser `RESIDENT` (FROM tenta ler arquivo); (b) carrega o campo `IPL`, que NÃO existe em `TEMP_EVENTOS_APREENSOES_PF_EXTERNAS_ESTRANGEIRO` (033 carrega "Proc. Identificação", não IPL); (c) o primeiro `Left Join` traz `id_ordem_original_evento`; o segundo `Left Join` (IntervalMatch) também traz `id_ordem_original_evento`, que passa a ser campo comum no join, então a segunda atribuição só casa quando o valor já existe: o fallback por data não preenche os que ficaram sem match no bloco 1. Comportamento a validar em execução.
- `tra/03/033 PF`: `TEMP_VALIDACAO` gravada em CSV e nunca dropada; StoreCsv em pasta raiz compartilhada.
- `tra/03/034 PF`: `NOME_PRESO` é referenciado no LOAD residente de `TEMP_EVENTOS_PRISOES` (campo existe, criado em 032 linha 187, mas o campo em CAIXA ALTA é sensível a maiúsculas; ok enquanto 032 permanecer com esse nome).
- `tra/06/068`: conflito de `%UNIDADE_KEY` (3.5-2); campo `Data` = `dt_evento` como texto (tipo "Data como texto" nos comentários).
- `tra/06/069`: `LOAD` sem `DISTINCT` na fato (ok se `id_evento_apreensao` for único); link só tem `%SUBCLASSESKEY`/eventos, sem caso/operação (dependência total do 068).
- `tra/07/0717`: dropa `TEMP_TABELAOEVENTOS_ID_UNIFICADO`, `TEMP_EVENTOS_APREENSOES_PF_...`, `TEMP_EVENTOS_PRISOES_PF_...` ao final. Qualquer novo script que precise dessas tabelas deve ficar antes de 0717.
- `tra/04/041`: `MapIdOrdemOriginalEventoIdOperacao` sem uso.
- `ext/07/071`: `Year(dt_evento)` sobre campo texto (DD/MM/AAAA): funciona apenas se `DateFormat` estiver 'DD/MM/YYYY' (está definido no MAIN); `WHERE Match(...)>0` e ano > 2023 fixos no código.

---

## 5. Catálogo de sub-rotinas e variáveis

### 5.1 Sub-rotinas (Subroutine Inventory)

**ext/02/022_SUBROTINAS.qvs e tra/02/022_SUBROTINAS.qvs (idênticas)**

| Nome | Parâmetros | Propósito | Limitações | Uso |
|---|---|---|---|---|
| `StoreCsv` | pTableName, pPathStore | `STORE` em `<caminho><tabela>.csv` (txt, delimiter ',') | não dropa; sem controle de encoding; caminho sem validação | tra 032/033/034 (auditoria) |
| `StoreAndDropCsv` | pTableName, pPathStore | STORE CSV + DROP | idem | pouco usada |
| `Store` | pTableName, pPathStore | `STORE ... INTO [...qvd](QVD)` | sem incremental; sobrescreve | pouco usada |
| `StoreAndDrop` | pTableName, pPathStore | STORE QVD + DROP TABLE | pTableName deve ser nome exato; falha se a tabela não existir | ext 151 (19x), tra 06/07 (todas as FATO_/DIM_) |

Duplicada em dois arquivos (ext e tra); não há biblioteca única compartilhada.

**app/02/021_SUBROTINAS.qvs (fábrica de variáveis de métricas)**: `TratarExpansaoMacro(vNomeVariavel)` (troca '@' por '$' para adiar expansão), `CriarVariavelContagem`, `CriarVariavelContagemSomaAnteriores`, `CriarVariavelMedia`, `CriarVariavelSoma`, `CriarVariavelSomaReais`, `CriarVariavelSomaMi`, `CriarVariavelSomaBi`, `CriarVariavelSomaAnteriores`, `CriarVariavelSomaReaisAnteriores`, `CriarVariavelSomaMiAnteriores`, `CriarVariavelSomaBiAnteriores`, `CriarVariavelRelativa`, `CriarVariavelRelativaPercentual`, `CriarVariavelRelativaSomaAnteriores`, `CriarVariavelRelativaReais`, `CriarVariavelRelativaMi`, `CriarVariavelRelativaBi`, `CriarVariavelRelativaReaisSomaAnteriores`, `CriarVariavelContagemPercentualdoTotal`, `CriarVariavelSomaPercentualdoTotal`, `CriarVariavelRelativaVezesDezMil`. Assinatura padrão `(vNomeVariavel, vConjunto, vCampo)` ou `(vNomeVariavel, vNumerador, vDenominador)`. Cada uma faz `SET $(vNome) = NUM(Agregador({< $(vConjunto) >} $(vCampo)), fmt)` e depois trata '@'. Limitação: produzem texto de expressão; nenhum teste de existência do campo (campo inexistente vira expressão que retorna NULL, sem erro).

**app/07 (sub-rotinas locais por arquivo, com nomes repetidos)**
- 072: `GerarConjunto12Defl`, `GerarConjunto12Cad`, `GerarListaNomes12`, `GerarListaNomes12Cad`, `GerarListaNomesSomAnter12(Cad)`, `GerarListaCampo12`, `ExecutarLoopContagem12`, `ExecutarLoopSoma12`, `ExecutarLoopContagemSomAnter12`, `ExecutarLoopSomAnter12`, `GerarPorEfet6(Cad)`, `GerarMetricaContagemCompleta(Cad)`, `GerarMetricaSomaCompleta`, `GerarMetricaSomaSomente`, `_GerarListasProporcao12`, `GerarProporcao12`, `GerarProporcaoPercentual12`.
- 074: `GerarConjunto12Apre`, `GerarListaNomes12Apre`, `GerarListaNomesSomAnter12Apre`, `GerarListaCampo12`, `GerarPorEfet6Reais|Mi|Bi`, `GerarMetricaReaisCompleta|MiCompleta|BiCompleta`, `GerarProporcaoAprePercentual`, `GerarProporcaoMiPorOper`.
- 075: repete `GerarConjunto12Apre`, `GerarListaNomes12Apre`, `GerarListaNomesSomAnter12Apre`, `GerarListaCampo12`, `GerarPorEfet6`, `GerarMetricaSomaCompleta`.
- 076 (ePol): ~26 SUBs `Gerar*ProcData`, `*InstData`, `ExecutarLoop*`, `GerarMetricaEmAnd`, `GerarMetricaDurMedEmAnd` etc.
- 073 (eventos) e 071: NENHUMA SUB (073 é SET/LET desdobrado).
- RISCO: nomes repetidos entre arquivos (`GerarConjunto12Apre` em 074 e 075; `GerarListaCampo12` em 072, 074, 075, 076; `GerarPorEfet6` em 072 e 075; `GerarMetricaSomaCompleta` em 072 e 075; `ExecutarLoop*12` em 072 e 076). Em um mesmo script Qlik a segunda definição substitui/conflita com a primeira; o comportamento depende da ordem e de corpos diferentes. A CONFIRMAR (pergunta 9).

**app/08 (geradores de medidas mestras)**
- `GerarMedidasMestrasDeflagracao6(pAlias, pRadical)` (081 linha 69; a documentação e o dicionário dizem que está em 021, o que é FALSO). Gera 6 variáveis por alias: `vMedidaMestra<Alias>`, `...Tot`, `...SomAnter`, `vMedidaMestraKpi<Alias>`, `...KpiTot`, `...KpiSomAnter`. Cada uma é um `IF($(vTemSelecaoDatasContextoFato), PICK(@(vMostrarValAbsouRelaoEfetouPfEmNum)+1, $($(pRadical)DtMesAnoDefl), ...PorEfet, ...PfEmNum), PICK(... $($(pRadical)DtMesAno) ...))`, depois `CALL TratarExpansaoMacro`. Depende de 6 variáveis por radical criadas em 07 (`<radical>DtMesAno`, `DtMesAnoDefl`, `...PorEfet`, `...PorEfetTot`, `...PfEmNum...`, `SomAnter...`). Limitações: sem tratamento de alias inexistente; falha silenciosa se o radical não existir. Chamada 17+ vezes no fim do 081 (OperacoesHomologadas, OperacoesRelatadasAposDeflagradas, ...ComMajorantes, ...ComReRecuperacaoAtivos, Prisoes(Cumpridas|Expedidas|Preventivas|Temporarias)EmOperacoes, Buscas..., Vitimas...EmOperacoes) com o radical `vOperHom`, `vPrisCumprEmOper`, ...
- Auxiliares em 081: `GerarTitulosERodapesDeflagracao`, `GerarMedidasSoPfKpi`, `GerarBlocoPorOperacaoHomologada`, `GerarBlocoPorOperacaoHomologadaApre`, `GerarBlocoCadastradas`.
- 083: `GerarMedidasApreSomAnterMiBi`, `GerarMedidasApreSomAnterMiSemBiTot`, `GerarMedidasApreMiBiSemSomAnter`, `GerarMedidasPercentualApre`, `GerarMedidasKpiSoPfApreMiBi`, `GerarTitulosERodapesApre*`.
- 084: `GerarMedidasApreTotSomAnter`, `GerarTitulosERodapeApre`.
- 085: `GerarMedidasMestrasEpolProcData6`, `...Instauracao6`, `...SemRel4`, `...ProcData2`, `GerarMedidasDuracaoEpolSemRel2`, `GerarMedidaSoPfKpiEpolProcData`, `GerarTitulos*`.
- 086: sem SUB; loop `FOR i` sobre `TabelaMedidasMestrasEfetivo` (Peek de Sufixo/Título).
- 082: sem SUB (desdobramento manual, ver 4.4).

### 5.2 Variáveis principais

| Grupo | Onde | Conteúdo |
|---|---|---|
| Caminhos | ext 021, tra 021, app 022 (repetidas) | `vCaminhoTabelasCorpDicorNge`, `vCaminhoQvdEpol|Sigacrim|Palas|CorpDadosAuxiliares`, `vCaminhoExtraidosV2` (E2_), `vCaminhoTransformadosV3` (T3_) |
| Seleção de fonte | ext 021 | `vCarregaDados` ('Atuais' / 'IPO_2025') e `vCarrega<Tabela>` / `vFormato<Tabela>` (nomes de arquivo + formato) |
| Transformações reutilizáveis (texto de expressão) | ext 021, tra 021 | `vTransformaProcIdentificacaoEmCaso`, `vCorrigeIplsSigacrim`, `vCorrigeIplsPalas` |
| Blocos de campo | tra 021 | `vCarregaUnidAreaDirCoorGeralDaOperacao`, `...DoCaso`, `...DoEventoOperacional`, `...DoEventoExternoEstrangeiro`, `vCarregaDatasDaCasos`, `vCarregaDatasDaCasos_Data`; listas de fronteira `vUnidadeFronteiraSr|Dpf`, `vEstadosFronteiricos` |
| Modificadores de conjunto | app 071, 023 | `vConj...` (~180 em 023 para efetivo; ~18 `PfEmNumeros` em 071) |
| Seleções | app 071 | `vAnoSelecionado`, `vAnoEvenSelecionado`, ... |
| Modo de exibição | app 022 | `vMostrarValAbsouRelaoEfetouPfEmNum` (0/1/2), `vTitBotMostraMetricasPainel`, `vPaginacaoIndices*` |
| Listas de geração | app 07 | `vListaNomeVariavel`, `vListaConjunto` (listas separadas por '\|' consumidas por loops `ExecutarLoop*`) |
| Cronômetro | todas as camadas | `vReloadStart/End/Dur`, `v<Fase>LoadStart/End/Dur` e tabelas `ReloadLog`, `FatosLoadLog` etc. |

### 5.3 Padrões de incremental / QVD

- NÃO há carga incremental (sem filtro por data de última carga, sem `Exists`, sem QVD histórico). Todas as camadas são reprocessadas integralmente. O ganho de desempenho vem de: (a) QVD como camada entre apps; (b) preceding LOAD com `GROUP BY LastValue()` antes de converter valores monetários (ext 051 e 091 documentam o ganho em 3M e 8M linhas); (c) filtros de escopo hard-coded (`> 2021`, `> 2023`, `Homologada`).
- Snapshot por data: modo `vCarregaDados='IPO_2025'` lê QVDs `..._01_04_2026.qvd` gravados por blocos comentados (`NoConcatenate ... StoreCsv/StoreAndDrop` em ext 071/072/073 e outros). Sem rotina automatizada.
- Auditoria por CSV: tra 032/033/034 fazem `CALL StoreCsv(...)` de tabelas intermediárias em `lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/` (raiz) a cada carga.
- Nenhuma política de retenção de QVD encontrada.

---

## 6. Convenções observadas x padroes_qvs.md

### 6.1 Mapa de convenções de nomenclatura

| Elemento | Convenção observada (dominante) | Padrão do framework (skill) | Decisão sugerida (data-architect decide) |
|---|---|---|---|
| Scripts | `NNN_DESCRITIVO.qvs` MAIÚSCULAS, português | idem (numérico + descritivo) | ADOTAR padrão da plataforma; corrigir exceções (6.2) |
| Tabelas de negócio | `FATO_*`, `DIM_*`, `LINK_TABLE_...` MAIÚSCULAS (100% dos QVDs finais) | `Fact/Dim` singular PascalCase | ADOTAR plataforma (dominante clara) |
| Temporárias | `TEMP_`, `TEMP_TEMP_`, até `TEMP_TEMP_TEMP_TEMP_` (nível variável), `TMP_`, `TempMap*`, `MAP*`, `Map*`, `MAP_*` | `_` prefixo, `Map_` | FLAG: 4 grafias para mapping (`Map`, `MAP`, `TempMap`, `MAP_`), profundidade de TEMP inconsistente entre ext e tra |
| Campos ePol | `"Proc. Identificação"`, `"GestãoBens Item ID"` (prefixo de entidade com ponto/espaço, acentos) | `Entity.Attribute` | manter (origem) |
| Campos SIGACrim | `ID_OPERACAO`, `DT_DEFLAGRACAO`, `ETAPAOPERACAO` (UPPER_SNAKE) | idem acima | manter (origem), mas sem prefixo de entidade |
| Campos de eventos | `id_evento`, `dt_evento`, `qtd_presos` (lower_snake cru da fonte, sem prefixo) | prefixar `Event.*` | FLAG: campos de evento não foram renomeados na camada semântica (DIM/FATO carregam nomes crus) |
| Campos derivados/rótulos | `"Data do Evento Operacional"`, `"Ano da Apreensão"`, `"Tipo do Fato"` (frases em português) | `Entity.Attribute` | manter; dominante nos campos de exibição |
| Chaves de link | `%NOMEKEY` (`%CASOSKEY`) e `%NOME_KEY` (`%PROC_IDENTIFICACAO_KEY`) | `%` + `HidePrefix` | FLAG: dois estilos; par fato/dimensão duplicado |
| Variáveis | prefixo `v` + PascalCase (`vCaminho...`, `vConj...`, `vMedidaMestra...`, `vLoop_S`); listas em variáveis com '\|' | `v` prefixo | ADOTAR; FLAG `vLoop_*` (snake) |
| QVDs | `E2_<TABELA>.qvd` (ext), `T3_<TABELA>.qvd` (tra) | `Raw_/Transform_/Model_` | ADOTAR plataforma; prefixos E_/E2_/T_/T2_/T3_ herdados = FLAG |

### 6.2 Violações de padroes_qvs.md (nomes)

| Arquivo | Violação |
|---|---|
| `ext/05_casos_deduplicados/051 TEMP_TEMP_DIM_CASOS.qvs` | espaço no nome |
| `tra/07_dimensoes/074_DIM_RE_SEQUESTRO_CASO_DE_RE_DE_RECUPERAÇÃO_DE_ATIVOS.qvs` | acento (Ç, Ã) |
| `tra/03_.../0318_TEMP_Mun_Faixa_de_Fronteira_Cidades_Gemeas_2024.qvs`, `ext/14_unidade/146_TEMP_Mun_Faixa_...` | minúsculas |
| `tra/07_.../076_DIM_FILTROS_DESPIVOTADOS_Palas_Operacoes_Tratadas_2022_2023.qvs` | minúsculas |
| `tra/03_.../032|033|034_*_ATUAL_FUNCIONANDO.qvs`, `tra/05_.../051_*_ATUAL_FUNCIONANDO.qvs` | "versão" no nome (proibido) |
| `tra/03_.../037_TEMP_PALAS_OPERACOES_TRATADAS_2032_2033.qvs` | ano errado (2032_2033 x 2022_2023) |
| `tra/05_.../Untitled-1.js` | extensão e nome fora do padrão; rascunho rastreado |
| `app/00_orquestracao/000_Main.qvs` | caixa (padrão exige `000_MAIN.qvs`) |
| `qlik/planilha resultados operacionais para MJ EM NÚMEROS.qvs` | espaços, acentos, minúsculas, fora de camada |
| `tra/07_dimensoes/0710_DIM_CASOS_DIM_CASOS_.qvs` (e 0712, 0713, 0714, 077, 078, 079) | sufixo terminado em underscore, nome duplicando origem |
| Prefixos misturados 3 e 4 dígitos na mesma pasta (tra/03, tra/07) | permitido pelo padrão (3.4), mas ordena errado alfabeticamente |
| Mais de um arquivo com o mesmo número na mesma pasta (tra/03: 032 x2, 033 x2, 034 x2; tra/05: 051 x2) | quebra a unicidade do prefixo sequencial |
| Nomes de tabela `TEMP_TEMP_TEMP_TEMP_ARMAS...` (035 tra) x `TEMP_TEMP_TEMP_ARMAS...` (arquivo QVD e ext 151) | inconsistência de profundidade de TEMP |

### 6.3 Divergências entre README/docs/padroes e as pastas reais

1. `05_temp_casos` (padroes, README, arquitetura) x `05_casos_deduplicados` (real); `09_apreensoes` x `09_apreensoes_deduplicadas` (real).
2. padroes_qvs.md 2.3 lista `011_START_LOAD_TIME/` e `111_END_LOAD_TIME/` como PASTAS em app; na realidade são ARQUIVOS dentro de `01_...` e `11_...`.
3. Todas as fontes de verdade dizem "ordem por `$(Include=...)` no 000_MAIN"; os MAIN não têm Include.
4. README: "03_carregamento_qvds: 14 QVDs" (real: 18 arquivos únicos + 3 duplicatas); "07_dimensoes: 23 DIM" (real: 27 arquivos); "app 07/08: 6 arquivos" (correto).
5. README e arquitetura citam `scripts/` e `QVDs/` inexistentes; README não referencia `docs/link_table_relacionamentos.md`.
6. README cita `Eventos_Apreensoes.qvd` etc. corretamente, mas diz DIM_CASOS_TIPO_PENAL em `CORP_DADOS_AUXILIARES/qvd`; a variável usada é `vCaminhoQvdEpol` (`MD_EPOL`). Ver pergunta 16.
7. modelo_dimensional.md: `DIM_TNBIA` = script `0723_` (real: `0727_`; 0723 é DIM_CIRCUNSCRICAO_PF); `DIM_RE_SEQUESTRO` = 074 (o script grava `DIM_Caso_de_RE_de_Recuperação_de_Ativos`); "4 chaves principais" (real: 8 pares).
8. dicionario_indicadores.md e padroes_qvs.md situam `GerarMedidasMestrasDeflagracao6` em `app/02.../021_SUBROTINAS.qvs`; está em `app/08.../081_...OPERACIONAIS.qvs` linha 69.
9. Dicionário cita "Calendário canônico" e campos (`[Quantidade Prisões Cumpridas]`, `[ID_SERVIDOR]`) sem correspondência no código.
10. padroes_qvs.md 3.2 (marcadores de fase) x realidade: `031_START_FATOS_LOAD_TIME`, `041_START_LINKTABLE_LOAD_TIME`, etc. estão conformes; tra não tem marcadores por fase (só geral).
11. padroes_qvs.md seção 8 "Credenciais e paths sensíveis não devem estar no repositório" x os `lib://` e nomes de planilhas (com "Izel", "Baggio") no código. Sem credenciais, mas com nomes de pessoas.
12. `.gitignore` bloqueia `*key*`, `*.txt`, `*.json`, `*.csv`, `*.xlsx`, mas NÃO `*.js` (Untitled-1.js foi rastreado).

---

## 7. Section Access (resumo, sem credenciais)

- Presente nas 3 camadas, em script próprio (ext 161, tra 081, app 101), conforme o padrão; cada um faz `Section Access; LOAD "ACCESS","USERID" FROM [lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/SECTION_ACCESS_<EXT|TRA|(app)>_Estatísticas_Criminais_SIGACrim.xlsx] (ooxml, embedded labels, table is Planilha1); Section Application;`.
- Modelo: lista de autorização por `USERID` lida de planilha externa (identity provider/domínio não explícito; sem `NTNAME`, `GROUP`, `SERIAL`). Apenas 2 colunas: NÃO há campo de redução (`OMIT`, `UNIDADE`, `SR`, etc.), logo não há redução de dados por linha/unidade no repositório. Apesar de a documentação falar em "controle de acesso por linha/unidade", o script implementa só controle de acesso ao app.
- Posição: app 101 fica após as variáveis (10) e antes do cronômetro final (11); ext 161 termina sem `Section Application` (o `Section Application;` está no INÍCIO de 171); tra 081 fecha com `Section Application;`.
- Risco de manutenção: 3 planilhas distintas e independentes, uma por camada, caminho fixo no código, nome de planilha com acento.
- A CONFIRMAR: se há redução por unidade aplicada fora do repositório (ex.: segurança no Qmc/space) e se Section Access é necessário em ext/tra (apps geradores de QVD).

---

## 8. Qualidade de código

**8.1 Uso de sintaxe SQL em LOAD (regra do CLAUDE.md)**: NÃO foram encontrados `CASE WHEN`, `IS NULL`, `BETWEEN`, `IN (`, `HAVING`, `LIKE`, `SELECT`, aliases de tabela. `COALESCE`, `ISNULL()`, `GROUP BY`, `ORDER BY` e `LEFT KEEP` são funções/cláusulas válidas de Qlik. Único caso de sintaxe SQL indevida: `FROM <tabela residente>` em vez de `RESIDENT` (tra 051 versão A, 4.6). A regra parece cumprida no restante.

**8.2 Caminhos fixos (hardcoded)**
- `lib://MD_SIGACRIM/SIGACrimMaquinariosHom.qvd` (tra 041 linha 379), leitura direta da fonte na camada tra.
- `lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/T3_DIM_TB_MUNICIPIOS_BRASIL.qvd` (app 052 linha 539), ignora `vCaminhoTransformadosV3`.
- 3 caminhos de Section Access fixos.
- `SET vCaminho...` copiados em 3 arquivos (ext 021, tra 021, app 022) com risco de divergência; existem prefixos herdados (T_, T2_, E_) sem uso.
- Nomes de arquivo pessoais e com data no código: `armas_2026_2.xlsx`, `Drogas_2022_Izel_2.xlsx`, `descapitalizao_epol_31_03_2025.xlsx` (sic), `..._01_04_2026.qvd`, `*_baggio_09-09-2026.xlsx` (script avulso).
- Modo 'IPO_2025': o ramo `elseif` NÃO define `vCarregaDrogas2022..2025` (usa `vCarregadadosEntorpecentes2022a2025Final`, nunca consumida), nem `vCarregaDIM_CIRCUNSCRICAO_PF`, `vCarregaTB_MUNICIPIOS_BRASIL`, `vCarregaTB_UF_BRASIL`, `vCarregaMun_Faixa...`; usa DIM_CASOS_DATA_BENS_01_04_2026.qvd (nome estranho). Ext 041/143/144/145/146 quebrariam nesse modo. O `else` é cópia do ramo 'Atuais'.
- Filtros de escopo fixos no código: `Year(...) > 2021` (ext 091), `> 2023` (ext 071), `ds_etapa_evento='Homologada'` (duplicado em ext 071 e tra 032), `Year("GestãoBens Item Data Apreensão") < 2024`, `= 2024`, `> 2024` na descapitalização (061).
- `Timestamp(2944573)` como "infinito" nos IntervalMatch (052).

**8.3 Código morto e resíduos**
- Muitos blocos comentados (`// NoConcatenate [X_01_04_2026]: ... StoreCsv`), linhas `// DROP TABLE TEMP_TEMP_DIM_CASOS;` copiadas em 6 scripts; `FROM` comentado ao lado do atual em todo LOAD.
- `MapIdOrdemOriginalEventoIdOperacao` (041), tabela `TEMP_VALIDACAO`, `TEMP_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO` e `TEMP_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO` (versões ATUAL), variáveis `vEvenOper*` (073), 082 inteiro (clone de 081), `Untitled-1.js`, `vCaminhoTransformados/V2`, `vCarregadadosEntorpecentes2022a2025Final`, `DIM_OPERACOES_SEM_AREA`(a verificar uso).
- Comentários com trechos de outro contexto (ex.: "somente operações homologadas até o dia 5" em variáveis de eventos; título "Medidas Mestras Operacionais" em 082; "Carregando Subrotinas de Store dos csv e QVD" repetido).
- Erros de digitação em nomes/mensagens (ex.: "CArga", "sinconização", "descapitalizao").

**8.4 Riscos de desempenho**
- Scripts gigantes: 082 (940 KB, 19,6 mil linhas), 073 (205 KB), 023 (76 KB), 032 tra (98 KB), 061 (71 KB, IFs aninhados por ano). Risco de limite/lentidão do editor de script e da resolução de variáveis; a expansão recursiva `$($(...))` de listas com '\|' é pesada em reload e em cada gráfico.
- Repetição x6 do bloco de deduplicação em 032 (PF/externo/estrangeiro x prisão/apreensão) com `RESIDENT` e `JOIN` de auto-produto cartesiano (`TEMP_PRESOS_POR_EVENTOS_*` join `TEMP_INTERSECAO_*` com `id_evento_a <> id_evento_b`): custo O(n^2) por grupo de presos/apreensões; ainda sem medição.
- IntervalMatch em 051/052 sobre milhões de itens de apreensão x intervalos por IPL/RE_SEQUESTRO.
- `StoreCsv` de tabelas grandes (TEMP_TABELAOEVENTOS_ID_UNIFICADO com `descricao_evento`, 1963 caracteres) a cada carga, na pasta raiz compartilhada.
- Link table com colunas duplicadas (chave de fato e de dimensão) e fan-out (3.5) aumenta memória e tempo de associação.
- `SET CreateSearchIndexOnReload=1` em app com muitos campos texto.
- Dados sensíveis: tra 034 grava CSV com `no_preso` e `ds_cpf` (`StoreCsv('TEMP_EVENTOS_PRISOES_PF_EXTERNAS_ESTRANGEIRO', ...)`), se essas colunas NÃO já vierem anonimizadas do QVD de origem, há exposição de PII em pasta compartilhada. O comentário de 032 sugere que a anonimização acontece no próprio script (`Preso_000000`, `CPF_válido_000000`), o que indica que o QVD fonte contém dado real. A CONFIRMAR (pergunta 14).

**8.5 Consistência e robustez**
- Falhas silenciosas: nomes de campo inexistentes em set analysis/expressões retornam NULL sem erro; não há tela de validação pós-carga (só cronômetro).
- Nomes de campo sensíveis a caixa (`NOME_PRESO` x `no_preso`) e a acentuação (`Mês`, `Área`).
- Nenhum teste de contagem/reconciliação embutido (só `TEMP_VALIDACAO` isolada e um diagnóstico de conflitos RE em 052).

---

## 9. Registro de restrições da plataforma

| Item | Situação |
|---|---|
| Modelo de implantação | Qlik Sense Enterprise (cliente gerenciado) e/ou Desktop; SEM Qlik Cloud, SEM MCP (CLAUDE.md) |
| Segurança | Section Access só por USERID (7) |
| Volumes | ~3M linhas DIM_CASOS, ~8M linhas DIM_CASOS_APREENSAO_BENS brutas (comentários em ext 051/091); ~14 a 17 mil eventos distintos por tipo (comentários em 032) |
| Limites de desempenho | Sem limites documentados; tempo de reload não registrado no repositório (só `ReloadLog` no app) |
| Ambientes | Não há dev/test/prod nos scripts; seletor `vCarregaDados` |
| Sub-rotinas | Limitações em 5.1 (nomes repetidos; falha silenciosa; Store sem incremental) |
| Locale | pt-BR (DateFormat DD/MM/YYYY, moeda R$, FirstWeekDay=6); há pequena divergência de MonthNames (tra usa 'jan.' com ponto; ext/app 'jan') |
| Classificação da arquitetura upstream | Fontes em QVD corporativos (Lakehouse-like de QVDs) + planilhas xlsx auxiliares. Mistura de modelos: OLTP achatado (SIGACrim/TabelaoEventos com 1:N por unidade participante), dimensional (DIM_CASOS_* do ePol) e planilhas manuais. Confiança MÉDIA (sem documentação de fonte) |

---

## 10. Perguntas abertas para o desenvolvedor (Fase 1)

1. Como o app é montado hoje? Os 000_MAIN.qvs não têm `$(Include=...)`. Os .qvs são colados no editor de script? Em que ordem (numérica ou alfabética; `0310_` antes de `031_`)? Existe algum arquivo/script externo que os inclui?
2. Qual é a versão vigente de cada par: `032` (com ou sem `_ATUAL_FUNCIONANDO`), `033`, `034`, `051`? Posso considerar os sufixados como descartáveis (e o `Untitled-1.js`)? A cadeia atual (068/069/0610/0716/0717) só funciona com as versões sem sufixo `PF_EXTERNAS_ESTRANGEIRO`.
3. O 051 (versão sem sufixo) já foi executado com sucesso? Ele lê `IPL` de uma tabela que não tem esse campo e usa `FROM` no lugar de `RESIDENT`. Qual a regra de negócio desejada para ligar um evento PF a um item de apreensão ePol (IPL + subclasse, depois data)?
4. Qual é a definição de negócio, por métrica, para o escopo de eventos: (a) contar PRESOS: por evento unificado, por unidade participante, ou por pessoa distinta (`nome_cpf_preso`)? (b) contar EVENTOS: `id_evento` unificado? (c) somar apreensões `qt_item`: sem conversão de unidades? Preciso de exemplos de números conferidos (passo a passo do COP).
5. O que o painel deve mostrar de eventos PF, externos e estrangeiros? Os nomes "Externo/Estrangeiro" nas tabelas/campos devem ser renomeados agora que cobrem eventos PF? Qual o termo de negócio para eventos PF?
6. O filtro de escopo `ds_etapa_evento = 'Homologada'` e `Year(dt_evento) > 2023` (ext 071) é regra permanente? E a série histórica anterior a 2024 para eventos existe em outra fonte?
7. Eventos de apreensão e de prisão devem responder a filtros de Caso, Operação e Unidade da mesma forma que os demais fatos? Hoje só se ligam via `%EVENTOSKEY` (link de 068). Qual unidade é a "unidade do evento" para filtrar por SR/Descentralizada: a participante escolhida na deduplicação?
8. O conflito de `%UNIDADE_KEY` no link de 068 (unidade do evento x unidade do caso) é conhecido? Quais atributos de unidade/área/diretoria devem valer para um evento: os do evento (área de atribuição do evento) ou os do caso?
9. O app roda com as sub-rotinas de mesmo nome em 072, 074, 075, 076 (`GerarConjunto12Apre`, `GerarListaCampo12`, `GerarPorEfet6`, `GerarMetricaSomaCompleta`, `ExecutarLoop*`)? Os corpos são iguais ou divergem? A ordem de carga define qual vence?
10. O 073 (métricas) e o 082 (medidas mestras) de eventos são clones intencionais de placeholder? Posso considerar `vEvenOper*` e 082 como descartáveis e reescrever a partir de 0? 081 e 082 são ambos carregados (nomes `vMedidaMestra*` idênticos)?
11. Que indicadores de eventos/apreensões de eventos/prisões de eventos devem existir? Para cada um: fórmula, tabela/campo, exclusões, grão, escopo de tempo, tipo de data ('Evento Operacional', 'Evento Prisão...', 'Evento Apreensão...'), e formas de exibição (absoluto, por efetivo, PF em números, soma anterior/Pareto).
12. Como tratar eventos ligados a mais de uma operação (`tem_relacao_operacoes` guarda um único `ID_OPERACAO`)? E eventos sem operação e sem caso ("Proc. Identificação" nulo)?
13. Deve existir uma tabela de calendário mestre no app, ou a dimensão de tempo continua dentro da link table (`Data/Ano/Mês/Tipo da Data`)? Isso afeta comparativos "ano atual/anterior" das medidas.
14. `no_preso` e `ds_cpf` chegam anonimizados no QVD `Eventos_Prisoes.qvd` ou o script (032) faz a anonimização? Os CSVs de auditoria (`StoreCsv` em CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/) podem conter dado pessoal? Quem tem acesso a essa pasta?
15. Section Access: existe redução de dados por unidade/SR/diretoria fora do repositório? A planilha SECTION_ACCESS tem só ACCESS/USERID? Que provedor de identidade e formato de USERID (DOMINIO\usuario)? Ext e tra realmente precisam de Section Access?
16. Onde está de fato `DIM_CASOS_TIPO_PENAL.qvd`: `MD_EPOL` (variável `vCaminhoQvdEpol`) ou `CORP_DADOS_AUXILIARES` (README e comentário de ext 121)?
17. O modo `vCarregaDados = 'IPO_2025'` ainda é usado? Está incompleto (faltam variáveis de drogas 2022-2025, circunscrição, municípios, UF, fronteira). Pode ser removido ou deve ser corrigido?
18. Como e com que frequência é o reload (agenda, duração por camada, tamanho do app final, número de usuários)? Há limites do servidor (RAM, tempo máximo de reload)?
19. `qlik/planilha resultados operacionais para MJ EM NÚMEROS.qvs` (script avulso com fontes de 09-09-2026) é parte do projeto? Deve virar um script de camada, ser movido para outro repositório ou apagado?
20. Existe documentação/dicionário das fontes (TabelaoEventos, Eventos_Prisoes, Eventos_Apreensoes) para preencher `inputs/source-documentation/`? Em especial: cardinalidade de `id_evento`, unicidade de `id_evento_prisao` e `id_evento_apreensao`, significado de `cd_tipo_participacao`, `tem_relacao_operacao` x `tem_relacao_operacoes`, `st_selecionado`, `un_item`.
21. Posso propor a limpeza do repositório (renomear conforme padroes_qvs.md, apagar duplicados) como etapa separada, depois de concluída a modelagem dos eventos? Qual convenção de nome vale para campos de eventos (renomear `id_evento`, `qt_item`... para o padrão do painel)?
22. Os `README.md`/docs desatualizados (seção 6.3) devem ser corrigidos como parte do projeto ou só registrados?
