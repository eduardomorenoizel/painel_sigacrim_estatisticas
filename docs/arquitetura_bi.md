# Arquitetura BI - Estatísticas Criminais DICOR

## Visão Geral

Este documento descreve a arquitetura do sistema de Business Intelligence (BI) para as Estatísticas Criminais do Núcleo de Gestão Estratégica e Inovação (NGE) da Coordenação de Supervisão de Operações e Pesquisas (COP) da Diretoria de Investigação e Combate ao Crime Organizado (DICOR) da Polícia Federal.

O sistema integra dados de múltiplas fontes (SIGACrim Operações, SIGACrim Eventos Operacionais, ePol Casos, ePol Apreensões, Palas Operações, Servidores e Unidades da PF) para fornecer análises operacionais, de apreensões, de desempenho investigativo, de efetivo policial e administrativo da PF (excluindo terceirizados e estagiários).

## Estrutura do Projeto

```
painel_sigacrim_estatisticas/
├── docs/                          # Documentação técnica
│   ├── arquitetura_bi.md         # Arquitetura do sistema
│   ├── modelo_dimensional.md     # Modelo de dados
│   └── dicionario_indicadores.md # Indicadores e KPIs
├── qlik/                          # Scripts Qlik Sense
│   ├── app/                       # Camada de Apresentação
│   ├── ext/                       # Camada de Extração
│   └── tra/                       # Camada de Transformação
├── scripts/                       # Scripts auxiliares
├── QVDs/                          # Dados processados (QVD)
├── .gitignore                     # Controle de versionamento
├── padroes_qvs.md                 # Padrões de desenvolvimento
└── README.md                      # Documentação geral
```

## Camadas da Arquitetura

### 1. Camada de Extração (ext/)

**Propósito**: Extrair dados brutos das fontes originais e prepará-los para transformação, salvando como QVDs intermediários.

**Estrutura**:
- `00_orquestracao/`: Controle da execução (`000_MAIN.qvs`) — configura locale brasileiro
- `01_inicio_contagem_tempo_carga/`: Marcador de início do tempo de carga
- `02_subrotinas_e_variaveis/`: Variáveis de caminhos e sub-rotinas auxiliares
- `03_dados_corporativos/`: Classificação de materiais TNBIA
- `04_armas_municoes_drogas/`: Dados de armas, munições e drogas (CGPRE)
- `05_temp_casos/`: Dados temporários de casos (com marcadores groupby)
- `06_caso_area_diretoria/`: Mapeamento caso → área → diretoria → CG
- `07_eventos_operacionais/`: Eventos da tabela de eventos (prisões e apreensões)
- `08_operacoes/`: Operações SIGACrim homologadas e Palas 2022-2023
- `09_apreensoes/`: Itens apreendidos — casos e bens (com marcadores groupby)
- `10_casos_data/`: Casos com informações de data
- `11_casos/`: Dimensão principal de casos
- `12_casos_tipo_penal/`: Classificação caso × tipo penal
- `13_servidor_ativo/`: Efetivo ativo da PF
- `14_unidade/`: Unidades e hierarquia técnica
- `15_output/`: Gravação de todos os QVDs extraídos (`151_GRAVA_QVD.qvs`)
- `16_section_access/`: Controle de acesso por linha
- `17_final_contagem_tempo_carga/`: Marcador de fim do tempo de carga

**Fontes de Dados Principais**:
- **SIGACrim**: Sistema de Gestão de Informações Criminais
  - Operações homologadas (`SIGACRIMHOMOLOGADAS`)
  - Eventos operacionais: prisões, apreensões (`TabelaoEventos`)
- **ePol**: Sistema Eletrônico de Polícia
  - Casos, processos e classificação penal
  - Apreensões de bens (`DIM_CASOS_APREENSAO_BENS`)
- **Palas**: Sistema de Gestão de Operações
  - Operações tratadas 2022-2023 (`PALAS_OPERACOES_TRATADAS_2022_2023`)
- **Dados Corporativos PF**:
  - Servidores ativos (excluindo terceirizados/estagiários)
  - Estrutura organizacional e hierarquia técnica
  - Classificação de materiais TNBIA

---

### 2. Camada de Transformação (tra/)

**Propósito**: Integrar, limpar e modelar os QVDs extraídos em tabelas de fatos e dimensões prontas para consumo.

**Estrutura**:
- `00_orquestracao/`: Controle da transformação (`000_MAIN.qvs`)
- `01_inicio_contagem_tempo_carga/`: Marcador de início do tempo de carga
- `02_subrotinas_e_variaveis/`: Variáveis de caminhos, unidades, áreas, diretorias e CGS; sub-rotinas
- `03_carregamento_qvds/`: Carregamento dos QVDs extraídos (14 arquivos)
  - TNBIA, TabelaoEventos (ID unificado), eventos externos/estrangeiro (apreensões e prisões)
  - Armas/munições/drogas, SIGACrim homologadas, Palas 2022-2023
  - Casos e bens, casos com data, casos, tipo penal, servidor ativo, unidade, hierarquia técnica
- `04_mapeamentos/`: Tabelas de mapeamento (interesse do item, capitalização, classes de descapitalização LVL1/LVL2, RE-Sequestro)
- `05_ajustes_qvds_originais/`: Ajustes sobre os QVDs carregados
  - Adição de EventoPF ao item de apreensão
  - Adição do ID de operação ao item de apreensão
  - Correção de erro de sincronização no SIGACrim homologadas
- `06_fatos/`: Criação das tabelas de fatos (10 arquivos)
- `07_dimensoes/`: Criação das tabelas de dimensões (23 arquivos)
- `08_section_access/`: Controle de acesso por linha
- `09_final_contagem_tempo_carga/`: Marcador de fim do tempo de carga

**Processos**:
- Integração de dados de múltiplas fontes em um modelo unificado
- Aplicação de regras de negócio e ajustes de qualidade
- Criação de chaves de ligação (`%CASOSKEY`, `%OPERACOESKEY`, `%APREENSOESKEY`, `%EVENTOSKEY`)
- Geração das tabelas `FATO_*` e `DIM_*` prontas para a camada de apresentação

---

### 3. Camada de Apresentação (app/)

**Propósito**: Carregar os dados modelados, definir métricas, medidas mestras e configurar a lógica de apresentação para o Qlik Sense.

**Estrutura**:
- `00_orquestracao/`: Controle da aplicação (`000_MAIN.qvs`) — configura locale brasileiro
- `011_START_LOAD_TIME/`: Marcador de início do tempo de carga geral
- `01_inicio_contagem_tempo_carga/`: Marcador de início (alternativo)
- `02_subrotinas_variaveis_de_ambiente_e_efetivo/`: Sub-rotinas de criação de variáveis, variáveis de ambiente e de efetivo
- `03_fatos/`: Carregamento das tabelas de fatos (com marcadores de tempo)
- `04_tabela_de_ligacao/`: Carregamento da tabela de ligação (com marcadores de tempo)
- `05_dimensoes/`: Carregamento das tabelas de dimensões (com marcadores de tempo)
- `06_inicio_contagem_tempo_carga_variaveis/`: Marcador de início de carga de variáveis
- `07_variaveis_de_metricas/`: Variáveis de cálculo de métricas (6 arquivos):
  - Controle, operacionais, eventos operacionais, apreensões, drogas/armas/munições, ePol
- `08_variaveis_de_medidas_mestras/`: Medidas mestras parametrizadas (6 arquivos):
  - Operacionais, eventos operacionais, apreensões, drogas/armas/munições, ePol, efetivo
- `09_final_contagem_tempo_carga_variaveis/`: Marcador de fim de carga de variáveis
- `10_section_access/`: Controle de acesso final
- `111_END_LOAD_TIME/`: Marcador de fim do tempo de carga geral

**Componentes**:
- Medidas mestras (Master Measures) parametrizadas via sub-rotinas
- Variáveis de métricas por categoria temática
- Controle de tempo de carga por fase
- Section Access

---

## Fluxo de Dados

```
Fontes (ePol, SIGACrim, Palas, Corporativo)
        │
        ▼
[ext/] Extração → QVDs intermediários (TEMP_*)
        │
        ▼
[tra/] Transformação → FATO_* + DIM_* (QVDs modelados)
        │
        ▼
[app/] Apresentação → Variáveis de métricas + Medidas mestras → Qlik Sense
```

1. **Extração (ext/)**: Dados extraídos das fontes e salvos como QVDs temporários em `15_output/`
2. **Transformação (tra/)**: QVDs carregados, ajustados e modelados em fatos e dimensões
3. **Apresentação (app/)**: Fatos e dimensões carregados com métricas e medidas para visualização

---

## Modelo de Dados

### Técnica de Link Table
- Utiliza 4 chaves principais: `%CASOSKEY`, `%OPERACOESKEY`, `%APREENSOESKEY`, `%EVENTOSKEY`
- Chaves compostas geradas via `AutoNumberHash128()`
- Permite associações flexíveis entre múltiplas entidades
- Suporta análises complexas com drill-down/across

### Tabelas de Fatos
- `FATO_APREENSOES`: Itens apreendidos com valores de descapitalização (ePol, SIGACrim, Palas)
- `FATO_OPERACOES`: Operações deflagradas (SIGACrim homologadas e Palas)
- `FATO_CASOS`: Processos/casos com status e classificação
- `FATO_CASOS_DATA`: Casos com granularidade temporal
- `FATO_EVENTOS_OPERACIONAIS`: Ações operacionais da tabela de eventos
- `FATO_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO`: Apreensões externas/estrangeiro
- `FATO_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO`: Prisões externas/estrangeiro

### Tabelas de Dimensões
- `DIM_OPERACOES`: Detalhes das operações (SIGACrim e Palas)
- `DIM_ATRIBUTOS`: Atributos adicionais das operações SIGACrim
- `DIM_APREENSOES`: Características dos bens apreendidos (ePol, SIGACrim, Palas)
- `DIM_CASOS`: Informações dos processos
- `DIM_CASOS_DATA`: Casos com dimensão temporal detalhada
- `DIM_CASOS_TIPO_PENAL`: Classificação dos casos por tipo penal
- `DIM_FILTROS_DESPIVOTADOS`: Filtros despivotados (SIGACrim e Palas)
- `DIM_RE_SEQUESTRO`: Casos de recuperação de ativos (RE/Sequestro)
- `DIM_MATERIA_RE`: Matérias de RE/Sequestro
- `DIM_EVENTOS_OPERACIONAIS`: Eventos de operações
- `DIM_EVENTOS_APREENSOES_EXTERNAS_ESTRANGEIRO`: Apreensões externas
- `DIM_EVENTOS_PRISOES_EXTERNAS_ESTRANGEIRO`: Prisões externas
- `DIM_SERVIDORES_ATIVOS`: Dados do efetivo ativo
- `DIM_UNIDADES`: Estrutura organizacional
- `DIM_HIERARQUIA_TECNICA`: Hierarquia técnica especializada
- `DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO`: Hierarquia de unidades pelo caso
- `DIM_UNIDADE_SUBUNIDADE`: Relação unidade × subunidade
- `DIM_TNBIA`: Classificação de materiais (taxonomia de bens)

---

## Tecnologias Utilizadas

- **Qlik Sense Enterprise**: Plataforma de BI
- **Qlik Script**: Linguagem de ETL e modelagem
- **QVD**: Formato otimizado para armazenamento de dados
- **Git**: Controle de versão
- **Section Access**: Controle de segurança por usuário/unidade

---

## Conexões de Dados

### Data Connections Necessárias
- `lib://CORP_DICOR_COP/`: Dados operacionais
- `lib://MD_SIGACRIM/`: Dados do SIGACrim
- `lib://CORP_DICOR_NGE/`: Dados específicos do NGE
- `lib://MD_EPOL/`: Dados do ePol
- `lib://CORP_DADOS_AUXILIARES/`: Dados auxiliares

---

## Considerações de Segurança

- Section Access implementado nas três camadas (ext, tra, app)
- Dados sensíveis protegidos
- Auditoria de acessos
- Controle de versão com `.gitignore`

---

## Padrões de Desenvolvimento

Para padrões específicos de desenvolvimento Qlik, consulte [padroes_qvs.md](../padroes_qvs.md).
