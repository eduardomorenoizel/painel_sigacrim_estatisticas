# Modelo Dimensional - Estatísticas Criminais DICOR

## Visão Geral

O modelo dimensional do sistema de BI segue uma abordagem de star schema com link table para suportar múltiplas granularidades e chaves de ligação. Utiliza fatos (`FATO_*`) conectados a dimensões (`DIM_*`) através de uma tabela de ligação (`LINK_TABLE_APREENSOES_OPERACOES_CASOS`). O modelo, inclusive a link table, é construído na camada `tra/` e apenas carregado pela camada `app/`.

O modelo integra dados de SIGACrim, ePol, Palas e dados corporativos da PF, excluindo terceirizados e estagiários do efetivo policial.

---

## Chaves de Ligação (Link Keys)

- **%CASOSKEY** / **%PROC_IDENTIFICACAO_KEY**: casos, a partir do Caso (`IPL`, formato `AAAA.NNNNNNN`)
- **%CASOSDATAKEY** / **%PROC_DATA_ID_KEY**: linhas de Casos_Data (`Proc_Data ID`)
- **%OPERACOESKEY** / **%ID_OPERACAO_KEY**: operações (`ID_OPERACAO`)
- **%APREENSOESKEY** / **%GESTAO_BENS_ITEM_ID_KEY**: apreensões (item ePol; `'SIGACrim_'&ID_OPERACAO`; `ID_OPERACAO` Palas)
- **%SUBCLASSESKEY** / **%ITEM_SUBCLASSE_KEY**: subclasse do item (DIM_TNBIA liga pela segunda)
- **%EVENTOSKEY** / **%ID_EVENTOS_KEY**: eventos operacionais (`id_ordem_original_evento`)
- **%EVENTOSAPREENSOESKEY** / **%ID_EVENTOS_APREENSOES_KEY**: eventos de apreensões (`id_evento_apreensao`)
- **%EVENTOSPRISOESKEY** / **%ID_EVENTOS_PRISOES_KEY**: eventos de prisões (`id_evento_prisao`)
- **%UNIDADE_KEY**: unidade comum da linha (caso, operação Palas ou unidade participante do evento)

A primeira chave de cada par liga ao `FATO_*` e a segunda às `DIM_*`. Todas são geradas via `AutoNumberHash128()` na camada `tra/`. As chaves de caso usam o `IPL` (e não o `"Proc. Identificação"`), porque o tipo do procedimento muda durante a tramitação; a DIM_CASOS mantém o `Proc. Identificação` atual.

---

## Tabelas de Fatos

### FATO_APREENSOES
**Granularidade**: Itens individuais de apreensão
**Fontes**: ePol (`DIM_CASOS_APREENSAO_BENS`), SIGACrim homologadas, Palas 2022-2023
**Scripts**: `tra/06_fatos/061_`, `062_`, `063_`

**Métricas Principais**:
- Quantidades apreendidas (armas, munições, drogas)
- Valores de descapitalização (LVL1 e LVL2):
  - `[1 Valor Bens Imóveis Apreendidos/Sequestrados LVL1]`
  - `[2 Valor Bens Móveis e Semoventes Apreendidos/Sequestrados LVL1]`
  - `[3 Valor Criptoativos apreendidos/sequestrados LVL1]`
  - `[5 Valores Monetários Apreendidos/Sequestrados LVL1]`
  - `[Valor Total Descapitalização]`

**Flags de Classificação**:
- `[É Caso_de_RE_de_Recuperação_de_Ativos]`
- `[É Caso_de_Operação]`
- `[É Item Descapitalização]`
- `[É Item Destruição Ambiental]`

---

### FATO_OPERACOES
**Granularidade**: Operações deflagradas
**Fontes**: SIGACrim homologadas, Palas 2022-2023
**Scripts**: `tra/06_fatos/064_`, `065_`

**Características Operacionais**:
- `[HOUVE_FASE_OPERACAO_ANTERIOR]`
- `[HOUVE_COOPERACAO_POLICIAL]`
- `[HOUVE_COOPERACAO_JURIDICA]`
- `[UTILIZACAO_RIF]`
- `[GEOPROCESSAMENTO]`
- `[AGENTE_INFILTRADO]`
- `[ACAO_CONTROLADA]`

**Características Criminais**:
- `[CRIME_LAVAGEM_DINHEIRO]`
- `[CRIME_TRANSNACIONAL]`
- `[FACCAO_CRIMINOSA]`
- `[GRUPO_EXTERMINIO_MILICIA]`
- `[AREA_FRONTEIRA]`

---

### FATO_CASOS
**Granularidade**: Casos/processos
**Fonte**: ePol (`DIM_CASOS`)
**Script**: `tra/06_fatos/066_`

**Métricas**: Contagem e status de casos por unidade, período e classificação penal

---

### FATO_CASOS_DATA
**Granularidade**: Casos com dimensão temporal detalhada
**Fonte**: ePol (`DIM_CASOS_DATA`)
**Script**: `tra/06_fatos/067_`

**Métricas**: Distribuição temporal dos casos (ano, mês, fase processual)

---

### FATO_EVENTOS_OPERACIONAIS
**Granularidade**: Eventos individuais de operações
**Fonte**: SIGACrim (`TabelaoEventos`)
**Script**: `tra/06_fatos/068_`

**Métricas**: Ações operacionais, prisões e apreensões contextuais dentro de operações

---

### FATO_EVENTOS_APREENSOES
**Granularidade**: Apreensões de eventos (`id_evento_apreensao`) PF, externos e estrangeiros, atribuídas a uma unidade participante
**Fonte**: `TEMP_EVENTOS_APREENSOES_UNIFICADOS` (tra 033)
**Script**: `tra/06_fatos/069_`

**Métricas**: Quantidade apreendida em eventos (`qt_item`); métricas ainda não escritas

---

### FATO_EVENTOS_PRISOES
**Granularidade**: Prisões de eventos (`id_evento_prisao`) PF, externos e estrangeiros, atribuídas a uma unidade participante
**Fonte**: `TEMP_EVENTOS_PRISOES_UNIFICADOS` (tra 034)
**Script**: `tra/06_fatos/0610_`

**Métricas**: Presos em eventos (`nome_cpf_preso`, `cd_tipo_prisao`); métricas ainda não escritas

---

## Tabelas de Dimensões

### DIM_OPERACOES
**Fontes**: SIGACrim homologadas e Palas 2022-2023
**Scripts**: `tra/07_dimensoes/071_`, `073_`

**Atributos Principais**:
- `[ID_OPERACAO]`, `[Caso_de_Operação]`
- `[NOME_OPERACAO]`, `[DS_OPERACAO]`
- `[UNIDADE_OPERACAO]`, `[UF_OPERACAO]`
- Datas: Deflagração, Cadastro, Início, Homologação
- `[ETAPAOPERACAO]`, `[DS_ATIVIDADE_ECONOMICA]`

---

### DIM_ATRIBUTOS
**Fonte**: SIGACrim homologadas
**Script**: `tra/07_dimensoes/072_`

**Atributos**: Atributos adicionais das operações SIGACrim (características de inteligência e investigação)

---

### DIM_FILTROS_DESPIVOTADOS
**Fontes**: SIGACrim homologadas e Palas 2022-2023
**Scripts**: `tra/07_dimensoes/075_`, `076_`

**Atributos**: Filtros despivotados para análises dimensionais flexíveis por tipo de crime, região e característica operacional

---

### DIM_APREENSOES
**Fontes**: ePol (`DIM_CASOS_APREENSAO_BENS`), SIGACrim homologadas, Palas 2022-2023
**Scripts**: `tra/07_dimensoes/077_`, `078_`, `079_`

**Atributos de Bens**:
- `[GestãoBens Item Unidade Material]`
- `[GestãoBens Item Valor Estimado]`
- `[DESCAP_CLASSE_LVL_1]`, `[DESCAP_CLASSE_LVL_2]`
- Dados de depósito: entrada, saída, quantidade

---

### DIM_RE_SEQUESTRO
**Fonte**: Mapeamento de recuperação de ativos
**Script**: `tra/07_dimensoes/074_`

**Atributos**:
- `[Caso_de_RE_de_Recuperação_de_Ativos]`
- Valores de sequestro e recuperação

---

### DIM_MATERIA_RE
**Fonte**: Matérias de RE/Sequestro
**Script**: `tra/07_dimensoes/0713_`

**Atributos**: Classificação temática das matérias de recuperação de ativos

---

### DIM_CASOS
**Fonte**: ePol (`DIM_CASOS`)
**Script**: `tra/07_dimensoes/0710_`

**Atributos Processuais**:
- `[Proc_Data Data Ano]`, `[Proc_Data Data Mês]`
- Status e andamento dos processos
- Classificação jurídica e criminal

---

### DIM_CASOS_DATA
**Fonte**: ePol (`DIM_CASOS_DATA`)
**Script**: `tra/07_dimensoes/0714_`

**Atributos**: Dimensão temporal detalhada dos casos (ano, mês, dia, fase)

---

### DIM_CASOS_TIPO_PENAL
**Fonte**: ePol (`DIM_CASOS_TIPO_PENAL`)
**Script**: `tra/07_dimensoes/0712_`

**Atributos**: Classificação penal por tipo de crime associado a cada caso

---

### DIM_FILTROS_DESPIVOTADOS_CASOS
**Fonte**: ePol (`DIM_CASOS`)
**Script**: `tra/07_dimensoes/0711_`

**Atributos**: Filtros despivotados dos casos para análises dimensionais

---

### DIM_EVENTOS_OPERACIONAIS
**Fonte**: SIGACrim (`TabelaoEventos`)
**Script**: `tra/07_dimensoes/0715_`

**Atributos**: Tipo de evento, data, unidade e características das ações operacionais

---

### DIM_EVENTOS_APREENSOES
**Script**: `tra/07_dimensoes/0716_`

**Atributos**: Item, categoria, local e unidade das apreensões de eventos (PF, externos e estrangeiros)

---

### DIM_EVENTOS_PRISOES
**Script**: `tra/07_dimensoes/0717_`

**Atributos**: Preso (anonimizado), documento e local das prisões de eventos (PF, externos e estrangeiros)

---

### DIM_SERVIDORES_ATIVOS
**Fonte**: Dados corporativos PF
**Script**: `tra/07_dimensoes/0718_`

**Atributos do Efetivo**:
- Dados pessoais e funcionais
- Lotação e cargo
- Participação em operações

---

### DIM_UNIDADES
**Fonte**: Dados corporativos PF
**Script**: `tra/07_dimensoes/0719_`

**Atributos Organizacionais**:
- Hierarquia da Polícia Federal
- `[ID_UNIDADE]`
- Localização geográfica

---

### DIM_HIERARQUIA_TECNICA
**Fonte**: Dados corporativos PF
**Script**: `tra/07_dimensoes/0720_`

**Estrutura Técnica**:
- Organização por especialidades
- Níveis hierárquicos

---

### DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO
**Fonte**: Cruzamento caso × unidade
**Script**: `tra/07_dimensoes/0721_`

**Atributos**: Hierarquia das unidades identificadas pela sigla do caso instaurado

---

### DIM_UNIDADE_SUBUNIDADE
**Fonte**: Dados corporativos PF
**Script**: `tra/07_dimensoes/0722_`

**Atributos**: Relação hierárquica entre unidades e suas subunidades. Este script também grava a link table (`StoreAndDrop('LINK_TABLE_APREENSOES_OPERACOES_CASOS', ...)`)

---

### DIM_TNBIA
**Fonte**: Dados corporativos (taxonomia de bens TNBIA)
**Script**: `tra/07_dimensoes/0727_`

**Atributos**: Classificação oficial de materiais e bens apreendidos

---

## Técnica de Link Table

### Implementação
- Chaves geradas via `AutoNumberHash128()` (pares fato/dimensão, ver "Chaves de Ligação")
- Montada em `tra/06_fatos/` (061 cria; 062 a 0610 concatenam) e gravada em `tra/07_dimensoes/0722_`
- Carregada no app por `app/04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs`
- Campos de data comum (`Data`, `Ano`, `Mês`, `Mês (Num)`, `Tipo da Data`) e `Tipo do Fato` / `Fonte` em cada linha
- Volume atual: ~61 milhões de linhas por LEFT JOINs entre fatos; ver o diagnóstico e o desenho enxuto em `docs/link_table_relacionamentos.md`

### Vantagens
- Permite associações flexíveis entre entidades de diferentes granularidades
- Suporta drill-down e drill-across complexos
- Evita duplicação de dados
- Otimiza performance de consultas

---

## Calendário Canônico (Master Calendar)

- Ainda **não existe** tabela de calendário no código. A data comum fica na própria link table (`Data`, `Ano`, `Mês`, `Mês (Num)`, `Tipo da Data`) e cada DIM tem suas datas específicas.
- Proposta (2026-10-09): `DIM_CALENDARIO` ligada por uma chave de data comum, como parte do enxugamento da link table.

---

## Fontes de Dados Integradas

### SIGACrim Homologadas
- Operações com homologação oficial
- Dados de prisões e apreensões contextuais
- Dados validados e auditados

### SIGACrim Eventos Operacionais
- Eventos de prisões e apreensões (TabelaoEventos)
- Dados contextuais das operações

### ePol Casos
- Processos e casos instaurados
- Classificação penal e andamento
- Dimensão temporal dos casos

### ePol Apreensões
- Bens apreendidos em processos (`DIM_CASOS_APREENSAO_BENS`)
- Valores de descapitalização
- Itens específicos (armas, drogas, dinheiro, criptoativos)

### Palas Operações
- Operações tratadas 2022-2023
- Dados complementares de apreensões e operações

### Dados Corporativos PF
- Servidores ativos (excluindo terceirizados/estagiários)
- Estrutura organizacional por unidade
- Hierarquia técnica especializada
- Classificação TNBIA de materiais

---

## Ordem de Carregamento

### Extração (ext/)
1. TNBIA e dados corporativos
2. Armas, munições e drogas
3. Casos temporários e mapeamento área/diretoria
4. Eventos operacionais (TabelaoEventos, prisões, apreensões)
5. Operações (SIGACrim e Palas)
6. Apreensões (bens e casos)
7. Casos com data, casos e tipo penal
8. Servidor ativo, unidade e hierarquia
9. Gravação dos QVDs (`15_output/151_GRAVA_QVD.qvs`)

### Transformação (tra/)
1. Carregamento dos QVDs extraídos (`03_carregamento_qvds/`)
2. Mapeamentos de lookup (`04_mapeamentos/041_MAPPING_LOADS.qvs`)
3. Ajustes sobre os QVDs originais (`05_ajustes_qvds_originais/`)
4. Criação das tabelas de fatos (`06_fatos/`)
5. Criação das tabelas de dimensões (`07_dimensoes/`)

### Apresentação (app/)
1. Fatos (`03_fatos/032_FATOS.qvs`)
2. Tabela de ligação (`04_tabela_de_ligacao/042_TABELA_DE_LIGACAO.qvs`)
3. Dimensões (`05_dimensoes/052_DIMENSOES.qvs`)
