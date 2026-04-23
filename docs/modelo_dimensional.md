# Modelo Dimensional - Estatísticas Criminais DICOR

## Visão Geral

O modelo dimensional do sistema de BI segue uma abordagem de star schema com link table para suportar múltiplas granularidades e chaves de ligação. Utiliza fatos (FATO_*) conectados a dimensões (DIM_*) através de uma tabela de ligação (Link Table) com 4 chaves principais, implementado na camada `app/02_fatos_e_dimensoes/`.

O modelo integra dados de SIGACrim, ePol, Palas e dados corporativos da PF, excluindo terceirizados e estagiários do efetivo policial.

## Chaves de Ligação (Link Keys)

- **%CASOSKEY**: Chave composta para casos/processos
- **%OPERACOESKEY**: Chave composta para operações
- **%APREENSOESKEY**: Chave composta para apreensões
- **%EVENTOSKEY**: Chave composta para eventos operacionais

## Tabelas de Fatos (Facts)

### FATO_APREENSOES
**Granularidade**: Itens individuais de apreensão

**Métricas Principais**:
- Quantidades apreendidas (armas, munições, drogas, etc.)
- Valores de descapitalização (níveis 1 e 2)
- Valores específicos por tipo de bem:
  - Bens imóveis e móveis
  - Criptoativos
  - Títulos e direitos
  - Valores monetários (espécie e bloqueados)
  - Itens destruídos no local

**Indicadores Específicos**:
- `[Valor Total Descapitalização]`
- `[1 Valor Bens Imóveis Apreendidos/Sequestrados LVL1]`
- `[2 Valor Bens Móveis e Semoventes Apreendidos/Sequestrados LVL1]`
- `[3 Valor Criptoativos apreendidos/sequestrados LVL1]`
- `[5 Valores Monetários Apreendidos/Sequestrados LVL1]`

**Flags de Classificação**:
- `[É Caso_de_RE_de_Recuperação_de_Ativos]`
- `[É Caso_de_Operação]`
- `[É Item Descapitalização]`
- `[É Item Destruição Ambiental]`

### FATO_OPERACOES
**Granularidade**: Operações deflagradas

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

### FATO_CASOS
**Granularidade**: Casos/processos

**Métricas**: Contagem e status de casos por unidade e período

### FATO_EVENTOS_OPERACIONAIS
**Granularidade**: Eventos individuais de operações

**Métricas**: Ações operacionais, prisões, apreensões contextuais

## Tabelas de Dimensões (Dimensions)

### DIM_OPERACOES
**Atributos Principais**:
- `[ID_OPERACAO]`, `[Caso_de_Operação]`
- `[NOME_OPERACAO]`, `[DS_OPERACAO]`
- `[UNIDADE_OPERACAO]`, `[UF_OPERACAO]`
- Datas: Deflagração, Cadastro, Início, Homologação
- `[ETAPAOPERACAO]`, `[DS_ATIVIDADE_ECONOMICA]`

### DIM_APREENSOES
**Atributos de Bens**:
- `[GestãoBens Item Unidade Material]`
- `[GestãoBens Item Valor Estimado]`
- `[DESCAP_CLASSE_LVL_1]`, `[DESCAP_CLASSE_LVL_2]`
- Dados de depósito: entrada, saída, quantidade

### DIM_CASOS
**Atributos Processuais**:
- `[Proc_Data Data Ano]`, `[Proc_Data Data Mês]`
- Status e andamento dos processos
- Classificação jurídica

### DIM_SERVIDORES
**Atributos do Efetivo**:
- Dados pessoais e funcionais
- Lotação e cargo
- Participação em operações

### DIM_UNIDADES
**Atributos Organizacionais**:
- Hierarquia da Polícia Federal
- `[ID_UNIDADE]`
- Localização geográfica

### DIM_HIERARQUIA_TECNICA
**Estrutura Técnica**:
- Organização por especialidades
- Níveis hierárquicos

### DIM_RE_SEQUESTRO
**Casos Especiais**:
- `[Caso_de_RE_de_Recuperação_de_Ativos]`
- Valores de sequestro e recuperação

## Calendário Canônico (Master Calendar)

- Tabela centralizada de datas em `app/02_fatos_e_dimensoes/`
- Atributos: Ano, mês, dia, trimestre, semana
- Suporte a múltiplas granularidades temporais

## Técnica de Link Table

### Implementação
- Utiliza `AutoNumberHash128()` para gerar chaves compostas
- Tabela de ligação em `021_TABELA_DE_LIGACAO.qvs`
- 4 chaves principais conectando fatos e dimensões

### Vantagens
- Permite associações flexíveis entre entidades
- Suporta drill-down e drill-across complexos
- Evita duplicação de dados
- Otimiza performance de consultas

## Fontes de Dados Integradas

### SIGACrim Homologadas
- Sistema de Gestão de Informações Criminais
- Operações com homologação oficial
- Dados validados e auditados

### SIGACrim Eventos Operacionais
- Eventos de prisões e apreensões
- Dados contextuais das operações

### ePol Casos
- Sistema Eletrônico de Polícia
- Processos e casos instaurados
- Classificação penal e andamento

### ePol Apreensões
- Bens apreendidos em processos
- Valores de descapitalização
- Itens específicos (armas, drogas, dinheiro)

### Palas Operações
- Sistema de Gestão de Operações
- Operações especiais e complementares
- Dados de 2022-2023 tratados

### Dados Corporativos PF
- Servidores ativos (excluindo terceirizados/estagiários)
- Estrutura organizacional por unidade
- Hierarquia técnica especializada

## Carregamento de Dados

### Ordem de Execução
1. Carregar fatos (`011_FATOS.qvs`)
2. Carregar tabela de ligação (`021_TABELA_DE_LIGACAO.qvs`)
3. Carregar dimensões (`031_DIMENSOES.qvs`)

### Localização dos Scripts
- Todos os componentes em `qlik/app/02_fatos_e_dimensoes/`
- Carregamento via `000_Main.qvs` na orquestração