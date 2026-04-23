# Painel SIGACrim Estatísticas

## Visão Geral

Este repositório contém o painel de Business Intelligence (BI) SIGACrim Estatísticas Criminais do Núcleo de Gestão Estratégica e Inovação (NGE) da Coordenação de Supervisão de Operações e Pesquisas (COP) da Diretoria de Investigação e Combate ao Crime Organizado (DICOR) da Polícia Federal.

O painel é desenvolvido em Qlik Sense e integra dados de múltiplas fontes (SIGACrim Operações, SIGACrim Eventos Operacionais, ePol Casos, ePol Apreensões, Palas Operações, Servidores e Unidades da PF) para fornecer análises operacionais, de apreensões, de desempenho investigativo, de efetivo policial e administrativo da PF (sem terceirizados e estagiários).

## Arquitetura

Para detalhes sobre a arquitetura do sistema, consulte [docs/arquitetura_bi.md](docs/arquitetura_bi.md).

## Modelo Dimensional

O modelo de dados segue uma abordagem dimensional com star schema e link table. Para mais informações, veja [docs/modelo_dimensional.md](docs/modelo_dimensional.md).

## Dicionário de Indicadores

Lista completa dos KPIs e medidas utilizadas no painel. Disponível em [docs/dicionario_indicadores.md](docs/dicionario_indicadores.md).

## Estrutura do Projeto

```
painel_sigacrim_estatisticas/
├── docs/                          # Documentação
│   ├── arquitetura_bi.md         # Arquitetura do sistema
│   ├── modelo_dimensional.md     # Modelo de dados
│   └── dicionario_indicadores.md # Indicadores e KPIs
├── qlik/                          # Scripts Qlik Sense
│   ├── app/                       # Scripts do aplicativo/painel principal
│   │   ├── 00_orquestracao/       # Scripts de orquestração e controle
│   │   ├── 01_variaveis_ambiente/ # Variáveis de ambiente e subrotinas
│   │   ├── 02_fatos_e_dimensoes/  # Definição de fatos e dimensões
│   │   ├── 03_metricas/           # Variáveis de métricas
│   │   ├── 04_medidas_mestras/    # Medidas mestras parametrizadas
│   │   └── 05_section_access/     # Controle de acesso
│   ├── ext/                       # Scripts de extração de dados
│   │   ├── 00_orquestracao/       # Controle da extração
│   │   ├── 01_configuracoes/      # Configurações de extração
│   │   ├── 02_dados_corporativos/ # Dados corporativos
│   │   ├── 03_armas_municoes_drogas/ # Extração de apreensões
│   │   ├── 04_eventos_operacionais/ # Eventos operacionais
│   │   ├── 05_operacoes/          # Operações
│   │   ├── 06_apreensoes/         # Apreensões
│   │   ├── 07_casos/              # Casos/processos
│   │   ├── 08_output/             # Saídas/QVDs
│   │   └── 09_section_access/     # Controle de acesso
│   └── tra/                       # Scripts de transformação
│       ├── 00_orquestracao/       # Controle da transformação
│       ├── 01_configuracoes/      # Configurações
│       ├── 02_dimensoes/          # Criação de dimensões
│       ├── 03_fatos/              # Criação de fatos
│       ├── 04_ajustes/            # Ajustes e mapeamentos
│       └── 05_section_access/     # Controle de acesso
├── scripts/                       # Scripts auxiliares
├── QVDs/                          # Arquivos QVD (dados processados)
├── .gitignore                     # Arquivos ignorados pelo Git
├── padroes_qvs.md                 # Padrões de desenvolvimento Qlik
└── README.md                      # Este arquivo
```

## Pré-requisitos

- Qlik Sense Enterprise ou Desktop
- Acesso às fontes de dados (lib://dataconnection/arquivo):
  - lib://CORP_DICOR_COP/TabelaoEventos.qvd
  - lib://CORP_DICOR_COP/Eventos_Prisoes.qvd
  - lib://CORP_DICOR_COP/Eventos_Apreensoes.qvd
  - lib://CORP_DICOR_COP/SIGACrim.qvd
  - lib://MD_SIGACRIM/Palas_Operacoes_Tratadas_2022_2023.qvd
  - lib://MD_SIGACRIM/SIGACrimMaquinariosHom.qvd
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/armas_final.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/municoes_final.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/dados_entorpecentes_2022a 2025_final.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/Area_Diretoria_CG.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/HIERARQUIA_TECNICA_PF_v8.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/CONSOLIDADA - Bens Interesse e Descapitalização Izel.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/descapitalizao_epol_31_03_2025.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/Ops Argus Izel.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/DPF-CAC-PR.xlsx
  - lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/RECURSO_HUMANOS_BRUTOS_ARGOS.xlsx
  - lib://MD_EPOL/DIM_CASOS.qvd
  - lib://CORP_DADOS_AUXILIARES/qvd/DIM_CASOS_TIPO_PENAL.qvd
  - lib://MD_EPOL/DIM_CASOS_DATA.qvd
  - lib://MD_EPOL/DIM_CASOS_APREENSAO_BENS.qvd
  - lib://CORP_DADOS_AUXILIARES/qvd/DIM_SERVIDOR_ATIVO.qvd
  - lib://CORP_DADOS_AUXILIARES/qvd/DIM_UNIDADE.qvd
- Credenciais para Section Access

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd painel_sigacrim_estatisticas
   ```

2. **Configure as variáveis de ambiente:**
   - Edite os arquivos em `qlik/ext/01_configuracoes/` e `qlik/app/01_variaveis_ambiente/`
   - Defina caminhos para fontes de dados
   - Configure conexões de banco de dados

3. **Execute a carga de dados:**
   - Execute primeiro os scripts de extração (`qlik/ext/`)
   - Depois os scripts de transformação (`qlik/tra/`)
   - Finalmente, carregue o painel principal (`qlik/app/`)

4. **Configure Section Access:**
   - Edite arquivos em `qlik/*/05_section_access/` ou `qlik/*/09_section_access/`
   - Defina usuários e permissões

## Uso

### Carregamento de Dados

1. Abra o Qlik Sense Desktop ou acesse o Qlik Sense Hub
2. Execute os scripts na ordem:
   - Extração (`qlik/ext/`)
   - Transformação (`qlik/tra/`)
   - Painel (`qlik/app/`)

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

Para padrões de desenvolvimento Qlik, consulte [padroes_qvs.md](padroes_qvs.md).

- Scripts organizados por camadas (ext, tra, app)
- Numeração sequencial dentro de cada pasta
- Prefixos padronizados para tipos de script
- Comentários em português brasileiro

### Versionamento

- Scripts versionados para controle de mudanças
- Controle via Git com .gitignore configurado

## Suporte e Contato

Para questões técnicas ou suporte:
- Contate a equipe do NGE/COP/DICOR
- Verifique logs de carregamento em caso de erros

## Licença

Este projeto é propriedade da Polícia Federal do Brasil. Uso interno autorizado apenas.
