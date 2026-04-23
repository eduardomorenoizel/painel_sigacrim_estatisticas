# Arquitetura BI - Estatísticas Criminais DICOR

## Visão Geral

Este documento descreve a arquitetura do sistema de Business Intelligence (BI) para as Estatísticas Criminais do Núcleo de Gestão Estratégica (NGE) / Coordenação de Operações (COP) / Divisão de Coordenação e Controle (DICOR) da Polícia Federal.

O sistema utiliza Qlik Sense como plataforma de BI, com uma arquitetura em camadas para extração, transformação e apresentação de dados criminais de fontes como SIGACrim, ePol e Palas.

## Camadas da Arquitetura

### 1. Camada de Fontes de Dados (Data Sources)

- **SIGACrim**: Sistema de Gestão de Informações e Conhecimento em Atividades de Repressão ao Crime Organizado.
- **ePol**: Sistema Eletrônico de Polícia.
- **Palas**: Sistema de Gestão de Operações.
- **Outros**: Dados de apreensões, operações, casos, etc.

### 2. Camada de Extração (Extraction Layer)

- Scripts Qlik para extração incremental de dados das fontes.
- Geração de arquivos temporários (TEMP_*) para processamento inicial.
- Tratamento de dados brutos, limpeza e padronização.

### 3. Camada de Transformação (Transformation Layer)

- Integração de dados de múltiplas fontes.
- Criação de tabelas de fatos (FATO_*) e dimensões (DIM_*).
- Aplicação de regras de negócio, mapeamentos e cálculos.
- Geração de QVDs (Qlik Data Files) para armazenamento otimizado.

### 4. Camada de Apresentação (Presentation Layer)

- Aplicação Qlik Sense com dashboards interativos.
- Medidas mestras (Master Measures) parametrizadas.
- Visualizações de KPIs operacionais, apreensões, efetivo, etc.
- Section Access para controle de acesso.

## Fluxo de Dados

1. **Extração**: Dados são extraídos das fontes e armazenados em tabelas temporárias.
2. **Transformação**: Dados são integrados, transformados e modelados em fatos e dimensões.
3. **Carregamento**: Dados são carregados na aplicação Qlik Sense.
4. **Apresentação**: Usuários interagem com dashboards para análise.

## Tecnologias Utilizadas

- **Qlik Sense**: Plataforma de BI.
- **Qlik Script**: Linguagem para ETL.
- **QVD**: Formato de armazenamento de dados Qlik.
- **Link Table**: Técnica para modelagem dimensional com múltiplas chaves.

## Considerações de Segurança

- Controle de acesso via Section Access.
- Dados sensíveis criptografados e protegidos.
- Auditoria de acessos e alterações.