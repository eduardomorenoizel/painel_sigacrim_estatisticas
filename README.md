# Painel SIGACrim Estatísticas

## Visão Geral

Este repositório contém o painel de Business Intelligence (BI) para Estatísticas Criminais do Núcleo de Gestão Estratégica (NGE) / Coordenação de Operações (COP) / Divisão de Coordenação e Controle (DICOR) da Polícia Federal.

O painel é desenvolvido em Qlik Sense e integra dados de múltiplas fontes (SIGACrim, ePol, Palas) para fornecer análises operacionais, de apreensões, efetivo e indicadores criminais.

## Arquitetura

Para detalhes sobre a arquitetura do sistema, consulte [arquitetura_bi.md](docs/arquitetura_bi.md).

## Modelo Dimensional

O modelo de dados segue uma abordagem dimensional com star schema e link table. Para mais informações, veja [modelo_dimensional.md](docs/modelo_dimensional.md).

## Dicionário de Indicadores

Lista completa dos KPIs e medidas utilizadas no painel. Disponível em [dicionario_indicadores.md](docs/dicionario_indicadores.md).

## Estrutura do Projeto

```
painel_sigacrim_estatisticas/
├── docs/                          # Documentação
│   ├── arquitetura_bi.md         # Arquitetura do sistema
│   ├── modelo_dimensional.md     # Modelo de dados
│   └── dicionario_indicadores.md # Indicadores e KPIs
├── scripts/                       # Scripts auxiliares
├── QVDs/                          # Arquivos QVD (dados processados)
├── BI SIGACrim Estatísticas v13 final com extracao, transformacao e painel/
│   ├── 9991 EXT_Estatísticas_Criminais_SIGACrim_v2/  # Scripts de Extração
│   ├── 9992 TRA_Estatísticas_Criminais_SIGACrim_v3/  # Scripts de Transformação
│   └── 9993 SIGACrim Estatísticas Criminais/         # Scripts do Painel
└── README.md                      # Este arquivo
```

## Pré-requisitos

- Qlik Sense Enterprise ou Desktop
- Acesso às fontes de dados:
  - SIGACrim
  - ePol
  - Palas
- Credenciais para Section Access

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd painel_sigacrim_estatisticas
   ```

2. **Configure as variáveis de ambiente:**
   - Edite os arquivos de variáveis (002 Variáveis extração.qvs, etc.)
   - Defina caminhos para fontes de dados
   - Configure conexões de banco de dados

3. **Execute a carga de dados:**
   - Execute primeiro os scripts de extração (EXT)
   - Depois os scripts de transformação (TRA)
   - Finalmente, carregue o painel principal

4. **Configure Section Access:**
   - Edite 181 SECTION ACCESS.qvs ou 061 SECTION ACCESS.qvs
   - Defina usuários e permissões

## Uso

### Carregamento de Dados

1. Abra o Qlik Sense Desktop ou acesse o Qlik Sense Hub
2. Execute os scripts na ordem:
   - Extração (9991 EXT_...)
   - Transformação (9992 TRA_...)
   - Painel (9993 SIGACrim...)

### Navegação no Painel

- **Página Inicial:** Visão geral dos principais KPIs
- **Operações:** Análise de operações deflagradas
- **Apreensões:** Detalhamento de bens apreendidos
- **ePol:** Indicadores de casos e processos
- **Efetivo:** Análise de recursos humanos

### Filtros Principais

- Período (Ano/Mês)
- Unidade da PF
- Tipo de operação/caso
- Status de homologação

## Desenvolvimento

### Convenções de Código

- Scripts numerados sequencialmente (001, 002, etc.)
- Prefixos para tipos de script:
  - TEMP_: Tabelas temporárias
  - FATO_: Tabelas de fatos
  - DIM_: Tabelas de dimensões
- Comentários em português brasileiro

### Versionamento

- v13: Versão atual
- Scripts versionados (v1, v2, etc.) para controle de mudanças

## Suporte e Contato

Para questões técnicas ou suporte:
- Contate a equipe do NGE/COP/DICOR
- Verifique logs de carregamento em caso de erros

## Licença

Este projeto é propriedade da Polícia Federal do Brasil. Uso interno autorizado apenas.
