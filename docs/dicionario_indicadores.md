# Dicionário de Indicadores - Estatísticas Criminais DICOR

## Visão Geral

Este dicionário cataloga os indicadores e medidas mestras do painel de Estatísticas Criminais do NGE/DICOR/PF. Os indicadores são parametrizados por data (mês/ano), unidade policial e tipo de operação, implementados na camada `app/08_variaveis_de_medidas_mestras/` com scripts numerados (081–086) por categoria temática.

Os indicadores abrangem análises operacionais, de eventos operacionais, de apreensões (inclusive drogas, armas e munições), de efetivo policial e do sistema ePol (excluindo terceirizados e estagiários).

---

## Arquitetura das Medidas Mestras

### Parametrização Automática
- **Sub-rotina Principal**: `GerarMedidasMestrasDeflagracao6(pAlias, pRadical)`
- **Variantes geradas**: `[Alias]`, `[Alias]Tot`, `[Alias]SomAnter`, `Kpi[Alias]`, `Kpi[Alias]Tot`, `Kpi[Alias]SomAnter`

### Contextos de Data
- **DtMesAno**: Usa data de deflagração quando não há seleção específica
- **DtMesAnoDefl**: Sempre usa data de deflagração
- **AnoAtual**: Dados do ano corrente

### Modos de Apresentação
- **Absoluto**: Valores brutos (padrão)
- **Por Efetivo**: Valores por servidor (`PorEfet`)
- **Em Números**: Contagens simples (`PfEmNum`)

---

## Variáveis de Métricas

As variáveis de métricas são calculadas antes das medidas mestras e ficam em `app/07_variaveis_de_metricas/`. Cada arquivo cobre uma categoria:

| Arquivo | Categoria |
|---|---|
| `071_VARIAVEIS_DE_METRICAS_DE_CONTROLE.qvs` | Métricas de controle e filtragem |
| `072_VARIAVEIS_DE_METRICAS_OPERACIONAIS.qvs` | Métricas de operações |
| `073_VARIAVEIS_DE_METRICAS_DE_EVENTOS_OPERACIONAIS.qvs` | Métricas de eventos operacionais |
| `074_VARIAVEIS_DE_METRICAS_DE_APREENSOES.qvs` | Métricas de apreensões |
| `075_VARIAVEIS_DE_METRICAS_DE_APREENSOES_DE_DROGAS_E_ARMAS_E_MUNICOES.qvs` | Métricas de drogas, armas e munições |
| `076_VARIAVEIS_DE_METRICAS_DO_EPOL.qvs` | Métricas do sistema ePol |

---

## Categorias de Indicadores

### Análises Operacionais
- Operações homologadas por unidade e período
- Efetividade das operações (prisões, apreensões, vítimas resgatadas)
- Distribuição por tipo de crime e região
- Recuperação de ativos (RE/Sequestro)

### Análises de Eventos Operacionais
- Prisões cumpridas e expedidas em operações
- Vítimas resgatadas (trabalho escravo, tráfico de pessoas, migração ilegal, grupos de extermínio)
- Erradicação de drogas
- Eventos externos/estrangeiro

### Análises de Apreensões
- Valores de descapitalização por operação (LVL1 e LVL2)
- Tipos de bens apreendidos (imóveis, móveis, criptoativos, valores monetários)
- Drogas apreendidas (cocaína, maconha, sintéticas)
- Armas e munições apreendidas

### Desempenho Investigativo (ePol)
- Casos e processos instaurados
- Produtividade por servidor
- Eficiência por unidade

### Efetivo Policial
- Distribuição de servidores por unidade e especialidade
- Capacidade operacional por região

---

## 1. Indicadores Operacionais

### Operações Homologadas
- **Medidas**: `vMedidaMestraOperacoesHomologadas*`
- **Definição**: Contagem de operações com homologação oficial
- **Fórmula**: `Count(DISTINCT [%OPERACOESKEY])` com filtros de homologação
- **Unidade**: Quantidade
- **Dimensões**: Unidade, data de deflagração, tipo de operação

### Operações Relatadas Após Deflagração
- **Medidas**: `vMedidaMestraOperacoesRelatadasAposDeflagradas*`
- **Definição**: Operações com relatório posterior à deflagração
- **Fórmula**: Contagem com condição de relatório posterior
- **Unidade**: Quantidade

### Operações com Majorantes
- **Medidas**: `vMedidaMestraOperacoesHomologadasComMajorantes*`
- **Definição**: Operações que envolvem crimes com majorantes
- **Fórmula**: Contagem com flag de majorantes criminais

### Operações de Recuperação de Ativos
- **Medidas**: `vMedidaMestraOperacoesHomologadasComReRecuperacaoAtivos*`
- **Definição**: Operações relacionadas à recuperação de ativos (RE/Sequestro)
- **Fórmula**: Contagem com `[É Caso_de_RE_de_Recuperação_de_Ativos] = 'Sim'`

---

## 2. Indicadores de Eventos Operacionais

### Prisões Cumpridas em Operações
- **Medidas**: `vMedidaMestraPrisoesCumpridasEmOperacoes*`
- **Definição**: Número de prisões efetivamente cumpridas durante operações
- **Fórmula**: `Sum([Quantidade Prisões Cumpridas])`
- **Unidade**: Quantidade
- **Dimensões**: Tipo de prisão, unidade, data

### Prisões Expedidas em Operações
- **Medidas**: `vMedidaMestraPrisoesExpedidasEmOperacoes*`
- **Definição**: Número de mandados de prisão expedidos em operações
- **Fórmula**: `Sum([Quantidade Prisões Expedidas])`
- **Unidade**: Quantidade

### Prisões Preventivas Cumpridas
- **Medidas**: `vMedidaMestraPrisoesPreventivasCumpridasEmOperacoes*`
- **Definição**: Prisões preventivas efetivamente cumpridas
- **Fórmula**: Subconjunto de prisões cumpridas com tipo preventivo

### Prisões Temporárias Cumpridas
- **Medidas**: `vMedidaMestraPrisoesTemporariasCumpridasEmOperacoes*`
- **Definição**: Prisões temporárias efetivamente cumpridas
- **Fórmula**: Subconjunto com tipo temporário

### Vítimas de Trabalho Escravo
- **Medidas**: `vMedidaMestraVitimasTrabalhoEscravoEmOperacoes*`
- **Definição**: Pessoas resgatadas de trabalho escravo em operações
- **Fórmula**: `Sum([Quantidade Vítimas Trabalho Escravo])`
- **Unidade**: Quantidade de pessoas

### Vítimas de Tráfico de Pessoas
- **Medidas**: `vMedidaMestraVitimasTraficoPessoasEmOperacoes*`
- **Definição**: Vítimas de tráfico humano resgatadas
- **Fórmula**: `Sum([Quantidade Vítimas Tráfico Pessoas])`

### Vítimas de Migração Ilegal
- **Medidas**: `vMedidaMestraVitimasMigracaoIlegalEmOperacoes*`
- **Definição**: Imigrantes em situação irregular resgatados
- **Fórmula**: `Sum([Quantidade Vítimas Migração Ilegal])`

### Vítimas de Grupos de Extermínio
- **Medidas**: `vMedidaMestraVitimasGrupoExterminioEmOperacoes*`
- **Definição**: Vítimas de milícias e grupos de extermínio
- **Fórmula**: `Sum([Quantidade Vítimas Grupo Extermínio])`

### Erradicação de Maconha
- **Medidas**: `vMedidaMestraErradicacoesMaconha*`
- **Definição**: Quantidade de maconha erradicada em operações
- **Fórmula**: `Sum([Quantidade Maconha Erradicada])`
- **Unidade**: kg (quilogramas)
- **Dimensões**: Unidade, região, data

---

## 3. Indicadores de Apreensões

### Valor Total de Descapitalização
- **Fonte**: `FATO_APREENSOES.[Valor Total Descapitalização]`
- **Definição**: Soma total de valores dos bens apreendidos/sequestrados
- **Fórmula**: `Sum([Valor Total Descapitalização])`
- **Unidade**: R$ (Reais)
- **Componentes**:
  - Bens imóveis (LVL1 e LVL2)
  - Bens móveis e semoventes
  - Criptoativos
  - Títulos e valores mobiliários
  - Valores monetários (espécie e bloqueados)
  - Itens destruídos no local

### Quantidade de Drogas Apreendidas
- **Fonte**: `FATO_APREENSOES`
- **Definição**: Volume de drogas apreendidas por tipo
- **Métricas Específicas**:
  - `[Item Quantidade Apreendida Cocaína (kg)]`
  - `[Item Quantidade Apreendida Maconha (kg)]`
  - `[Item Quantidade Apreendida Drogas Sintéticas (un)]`
- **Unidade**: kg para maconha/cocaína, unidades para sintéticas

### Quantidade de Armas e Munições
- **Fonte**: `FATO_APREENSOES`
- **Métricas**:
  - `[Item Quantidade Apreendida Armas (un)]`
  - `[Item Quantidade Apreendida Munições (un)]`
- **Unidade**: Quantidade (unidades)

---

## 4. Indicadores do ePol

### Casos e Processos
- **Fonte**: `FATO_CASOS`
- **Definição**: Contagem de processos instaurados
- **Fórmula**: `Count(DISTINCT [%CASOSKEY])`
- **Dimensões**: Tipo penal, unidade, fase processual

### Prisões Externas
- **Fonte**: `FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO`
- **Definição**: Prisões realizadas fora do contexto operacional padrão
- **Fórmula**: Contagem de eventos prisionais externos

### Apreensões Externas
- **Fonte**: `FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO`
- **Definição**: Apreensões realizadas fora do contexto operacional padrão
- **Fórmula**: Contagem de eventos de apreensão externos

---

## 5. Indicadores de Efetivo

### Efetivo Total
- **Fonte**: `DIM_SERVIDORES_ATIVOS`
- **Definição**: Número total de servidores ativos
- **Fórmula**: `Count(DISTINCT [ID_SERVIDOR])`
- **Dimensões**: Unidade, cargo, lotação

### Efetivo por Operação
- **Fonte**: Relacionamento entre `DIM_SERVIDORES_ATIVOS` e `FATO_OPERACOES`
- **Definição**: Média de servidores por operação
- **Fórmula**: `Count(DISTINCT [ID_SERVIDOR]) / Count(DISTINCT [%OPERACOESKEY])`

---

## Parametrização das Medidas

### Variáveis de Controle
- `vMostrarValAbsouRelaoEfetouPfEmNum`: Define modo de apresentação (0=Absoluto, 1=Por Efetivo, 2=Em Números)
- `vTemSelecaoDatasContextoFato`: Detecta seleções de datas contextuais
- `vTemSelecaoDatasCalendario`: Detecta seleções no calendário canônico

### Filtros Automáticos
- Operações homologadas até o dia 5 do mês corrente
- Exclusão de dados migrados do SINPRO
- Ajustes específicos para anos 2022-2025

---

## Localização dos Scripts

### Medidas Mestras — por categoria

| Categoria | Arquivo |
|---|---|
| Operacionais | `app/08_variaveis_de_medidas_mestras/081_VARIAVEIS_DE_MEDIDAS_MESTRAS_OPERACIONAIS.qvs` |
| Eventos Operacionais | `app/08_variaveis_de_medidas_mestras/082_VARIAVEIS_DE_MEDIDAS_MESTRAS_DE_EVENTOS_OPERACIONAIS.qvs` |
| Apreensões | `app/08_variaveis_de_medidas_mestras/083_VARIAVEIS_DE_MEDIDAS_MESTRAS_DE_APREENSOES.qvs` |
| Drogas, Armas e Munições | `app/08_variaveis_de_medidas_mestras/084_VARIAVEIS_DE_MEDIDAS_MESTRAS_DE_APREENSOES_DE_DROGAS_E_ARMAS_E_MUNICOES.qvs` |
| ePol | `app/08_variaveis_de_medidas_mestras/085_VARIAVEIS_DE_MEDIDAS_MESTRAS_DO_EPOL.qvs` |
| Efetivo | `app/08_variaveis_de_medidas_mestras/086_VARIAVEIS_DE_MEDIDAS_MESTRAS_DE_EFETIVO.qvs` |

### Sub-rotinas de Geração
- Arquivo: `app/02_subrotinas_variaveis_de_ambiente_e_efetivo/021_SUBROTINAS.qvs`
- Sub-rotina: `GerarMedidasMestrasDeflagracao6`

---

## Notas Técnicas

- Todas as medidas são geradas parametricamente via sub-rotinas Qlik Script
- Suportam drill-down por dimensões hierárquicas
- Valores ajustados conforme regras de negócio específicas por período
- Implementadas como variáveis Qlik com lógica condicional
- Utilizam `$(Include=...)` para carregamento sequencial
- Tempo de carga das variáveis monitorado pelos marcadores `06_inicio_contagem_tempo_carga_variaveis/` e `09_final_contagem_tempo_carga_variaveis/`
