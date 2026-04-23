# Modelo Dimensional - Estatísticas Criminais DICOR

## Visão Geral

O modelo dimensional do sistema de BI segue uma abordagem de star schema com link table para suportar múltiplas granularidades e chaves de ligação. Utiliza fatos (FATO_*) conectados a dimensões (DIM_*) através de uma tabela de ligação (Link Table) com 4 chaves principais.

## Chaves de Ligação (Link Keys)

- **%CASOSKEY**: Chave para casos/processos.
- **%OPERACOESKEY**: Chave para operações.
- **%APREENSOESKEY**: Chave para apreensões.
- **%EVENTOSKEY**: Chave para eventos operacionais.

## Tabelas de Fatos (Facts)

### FATO APREENSOES
- Granularidade: Itens de apreensão.
- Métricas: Valores de descapitalização, quantidades de bens apreendidos (armas, drogas, dinheiro, etc.).
- Conectado via %APREENSOESKEY.

### FATO OPERACOES
- Granularidade: Operações deflagradas.
- Métricas: Número de operações, valores apreendidos, efetivo envolvido.
- Conectado via %OPERACOESKEY.

### FATO CASOS
- Granularidade: Casos/processos.
- Métricas: Número de casos, tipos penais, status.
- Conectado via %CASOSKEY.

### FATO CASOS DATA
- Granularidade: Casos por data.
- Métricas: Evolução temporal de casos.
- Conectado via %CASOSKEY.

### FATO EVENTOS OPERACIONAIS
- Granularidade: Eventos de operações.
- Métricas: Ações operacionais, prisões, apreensões.
- Conectado via %EVENTOSKEY.

## Tabelas de Dimensões (Dimensions)

### DIM OPERACOES
- Atributos: Nome da operação, data de deflagração, unidade responsável, etc.

### DIM APREENSOES
- Atributos: Tipo de bem apreendido, valor, data de apreensão, etc.

### DIM CASOS
- Atributos: Número do processo, tipo penal, status, etc.

### DIM CASOS DATA
- Atributos: Datas relacionadas aos casos (instauração, relatório, etc.).

### DIM EVENTOS OPERACIONAIS
- Atributos: Tipo de evento, data, localização, etc.

### DIM SERVIDORES
- Atributos: Dados dos servidores envolvidos.

### DIM UNIDADES
- Atributos: Unidades da PF, hierarquia.

### DIM HIERARQUIA TÉCNICA
- Atributos: Estrutura organizacional.

### DIM RE_SEQUESTRO
- Atributos: Casos de recuperação de ativos.

## Calendário Canônico (Master Calendar)

- Tabela de datas centralizada para todas as análises temporais.
- Atributos: Ano, mês, dia, trimestre, etc.

## Técnica de Link Table

- Utiliza AutoNumberHash128 para gerar chaves compostas.
- Permite associações flexíveis entre fatos e dimensões.
- Suporta drill-down e drill-across em múltiplas granularidades.

## Fontes de Dados Integradas

- **SIGACrim Homologadas**: Operações homologadas.
- **Palas Operações**: Dados de operações especiais.
- **DIM CASOS APREENSAO BENS**: Apreensões de bens.
- **Eventos Externos**: Prisões e apreensões externas.