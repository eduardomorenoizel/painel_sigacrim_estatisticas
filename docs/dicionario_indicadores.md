# Dicionário de Indicadores - Estatísticas Criminais DICOR

## Visão Geral

Este dicionário descreve os principais indicadores (KPIs) utilizados no painel de BI, organizados por categoria. Os indicadores são implementados como medidas mestras (Master Measures) em Qlik Sense, com parametrização para diferentes contextos de data e filtros.

## 1. Indicadores Operacionais

### Número de Operações
- **Definição**: Contagem de operações deflagradas.
- **Fórmula**: Count distinct de operações por período.
- **Unidade**: Quantidade.
- **Dimensões**: Unidade, data de deflagração, tipo de operação.

### Valor Total de Descapitalização
- **Definição**: Soma dos valores de bens apreendidos/sequestrados.
- **Fórmula**: Sum de valores monetários, imóveis, móveis, criptoativos, etc.
- **Unidade**: R$ (Reais).
- **Dimensões**: Tipo de bem, data de apreensão, unidade.

### Efetivo Envolvido
- **Definição**: Número de servidores participantes em operações.
- **Fórmula**: Count distinct de servidores por operação.
- **Unidade**: Quantidade de pessoas.
- **Dimensões**: Unidade, cargo, data.

## 2. Indicadores de Apreensões

### Quantidade de Drogas Apreendidas
- **Definição**: Volume/peso de drogas apreendidas.
- **Fórmula**: Sum de quantidades por tipo de droga.
- **Unidade**: kg, g, etc.
- **Dimensões**: Tipo de droga, data, unidade.

### Quantidade de Armas Apreendidas
- **Definição**: Número de armas de fogo apreendidas.
- **Fórmula**: Count de itens de armas.
- **Unidade**: Quantidade.
- **Dimensões**: Tipo de arma, calibre, data.

### Quantidade de Munições Apreendidas
- **Definição**: Número de munições apreendidas.
- **Fórmula**: Sum de quantidades.
- **Unidade**: Quantidade.
- **Dimensões**: Calibre, tipo, data.

### Valor de Dinheiro Apreendido
- **Definição**: Soma de valores monetários apreendidos.
- **Fórmula**: Sum de valores em espécie e bloqueados.
- **Unidade**: R$.
- **Dimensões**: Tipo (espécie/bloqueado), data.

## 3. Indicadores do ePol

### Número de Casos
- **Definição**: Contagem de casos instaurados.
- **Fórmula**: Count distinct de processos.
- **Unidade**: Quantidade.
- **Dimensões**: Tipo penal, unidade, data.

### Número de Prisões
- **Definição**: Contagem de prisões efetuadas.
- **Fórmula**: Count de eventos de prisão.
- **Unidade**: Quantidade.
- **Dimensões**: Tipo de prisão, data, unidade.

### Número de Autos de Apreensão
- **Definição**: Contagem de autos de apreensão.
- **Fórmula**: Count distinct de autos.
- **Unidade**: Quantidade.
- **Dimensões**: Tipo de bem, data.

## 4. Indicadores de Efetivo

### Efetivo Total
- **Definição**: Número total de servidores ativos.
- **Fórmula**: Count distinct de servidores.
- **Unidade**: Quantidade.
- **Dimensões**: Unidade, cargo, lotação.

### Efetivo por Operação
- **Definição**: Média de servidores por operação.
- **Fórmula**: Efetivo total / Número de operações.
- **Unidade**: Quantidade.
- **Dimensões**: Unidade, período.

## Parametrização das Medidas

### Contextos de Data
- **DtMesAno**: Usa data de deflagração/apreensão quando não há seleção específica.
- **DtMesAnoDefl**: Sempre usa data de deflagração.
- **AnoAtual**: Dados do ano corrente.

### Modos de Apresentação
- **Absoluto**: Valores brutos.
- **Relativo ao Efetivo**: Valores por servidor.
- **Em Números**: Contagens simples.

### Filtros de Controle
- Operações homologadas até o dia 5 do mês corrente.
- Exclusão de dados migrados do SINPRO.
- Ajustes para anos específicos (2022-2025).

## Notas Técnicas

- Indicadores implementados como variáveis Qlik com lógica condicional.
- Utilizam subrotinas para geração parametrizada.
- Suportam drill-down por dimensões hierárquicas.
- Valores ajustados para conformidade com regras de negócio.