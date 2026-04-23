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

**Propósito**: Extrair dados brutos das fontes originais e prepará-los para transformação.

**Estrutura**:
- `00_orquestracao/`: Controle da execução (000_MAIN.qvs)
- `01_configuracoes/`: Variáveis de ambiente e caminhos
- `02_dados_corporativos/`: Extração de dados corporativos
- `03_armas_municoes_drogas/`: Dados de apreensões específicas
- `04_eventos_operacionais/`: Eventos de operações
- `05_operacoes/`: Dados de operações
- `06_apreensoes/`: Itens apreendidos
- `07_casos/`: Processos/casos
- `08_output/`: Geração de QVDs intermediários
- `09_section_access/`: Controle de acesso

**Fontes de Dados Principais**:
- **SIGACrim**: Sistema de Gestão de Informações Criminais
  - Operações homologadas
  - Eventos operacionais (prisões, apreensões)
- **ePol**: Sistema Eletrônico de Polícia
  - Casos e processos
  - Apreensões de bens
- **Palas**: Sistema de Gestão de Operações
  - Operações especiais
  - Dados complementares
- **Dados Corporativos PF**:
  - Servidores ativos (excluindo terceirizados/estagiários)
  - Estrutura organizacional
  - Hierarquia técnica

### 2. Camada de Transformação (tra/)

**Propósito**: Integrar, limpar e modelar os dados extraídos em estruturas analíticas.

**Estrutura**:
- `00_orquestracao/`: Controle da transformação
- `01_configuracoes/`: Mapeamentos e configurações
- `02_dimensoes/`: Criação de tabelas de dimensões
- `03_fatos/`: Criação de tabelas de fatos
- `04_ajustes/`: Regras de negócio e ajustes
- `05_section_access/`: Controle de acesso

**Processos**:
- Integração de dados de múltiplas fontes
- Aplicação de regras de negócio
- Criação de chaves de ligação (Link Keys)
- Geração de tabelas FATO_* e DIM_*

### 3. Camada de Apresentação (app/)

**Propósito**: Preparar dados para consumo no Qlik Sense e definir a lógica de apresentação.

**Estrutura**:
- `00_orquestracao/`: Controle da aplicação (000_Main.qvs)
- `01_variaveis_ambiente/`: Subrotinas e variáveis globais
- `02_fatos_e_dimensoes/`: Carregamento de fatos e dimensões
- `03_metricas/`: Definição de variáveis de cálculo
- `04_medidas_mestras/`: Medidas parametrizadas para front-end
- `05_section_access/`: Controle de acesso final

**Componentes**:
- Medidas mestras (Master Measures)
- Variáveis de métricas
- Lógica de apresentação
- Section Access

## Fluxo de Dados

1. **Extração (ext/)**: Dados são extraídos das fontes e salvos como QVDs intermediários
2. **Transformação (tra/)**: QVDs são integrados, transformados e modelados em fatos/dimensões
3. **Apresentação (app/)**: Dados modelados são carregados com lógica de negócio e medidas

## Modelo de Dados

### Técnica de Link Table
- Utiliza 4 chaves principais: %CASOSKEY, %OPERACOESKEY, %APREENSOESKEY, %EVENTOSKEY
- Permite associações flexíveis entre múltiplas entidades
- Suporta análises complexas com drill-down/across

### Tabelas de Fatos
- FATO_APREENSOES: Itens apreendidos com valores de descapitalização
- FATO_OPERACOES: Operações deflagradas com características
- FATO_CASOS: Processos/casos com status
- FATO_EVENTOS_OPERACIONAIS: Ações operacionais

### Tabelas de Dimensões
- DIM_OPERACOES: Detalhes das operações
- DIM_APREENSOES: Características dos bens apreendidos
- DIM_CASOS: Informações dos processos
- DIM_SERVIDORES: Dados do efetivo
- DIM_UNIDADES: Estrutura organizacional

## Tecnologias Utilizadas

- **Qlik Sense Enterprise**: Plataforma de BI
- **Qlik Script**: Linguagem de ETL e modelagem
- **QVD**: Formato otimizado para armazenamento de dados
- **Git**: Controle de versão
- **Section Access**: Controle de segurança por usuário/unidade

## Conexões de Dados

### Data Connections Necessárias
- `lib://CORP_DICOR_COP/`: Dados operacionais
- `lib://MD_SIGACRIM/`: Dados do SIGACrim
- `lib://CORP_DICOR_NGE/`: Dados específicos do NGE
- `lib://MD_EPOL/`: Dados do ePol
- `lib://CORP_DADOS_AUXILIARES/`: Dados auxiliares

## Considerações de Segurança

- Section Access implementado em cada camada
- Dados sensíveis protegidos
- Auditoria de acessos
- Controle de versão com .gitignore

## Padrões de Desenvolvimento

Para padrões específicos de desenvolvimento Qlik, consulte [padroes_qvs.md](../padroes_qvs.md).