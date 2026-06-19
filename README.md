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
├── docs/                                              # Documentação
│   ├── arquitetura_bi.md                             # Arquitetura do sistema
│   ├── modelo_dimensional.md                         # Modelo de dados
│   └── dicionario_indicadores.md                     # Indicadores e KPIs
├── qlik/                                              # Scripts Qlik Sense
│   ├── ext/                                           # Extração de dados
│   │   ├── 00_orquestracao/                           # 000_MAIN.qvs
│   │   ├── 01_inicio_contagem_tempo_carga/
│   │   ├── 02_subrotinas_e_variaveis/
│   │   ├── 03_dados_corporativos/                     # TNBIA
│   │   ├── 04_armas_municoes_drogas/                  # CGPRE
│   │   ├── 05_temp_casos/                             # Casos temporários
│   │   ├── 06_caso_area_diretoria/                    # Mapeamento área/diretoria
│   │   ├── 07_eventos_operacionais/                   # TabelaoEventos, prisões, apreensões
│   │   ├── 08_operacoes/                              # SIGACrim e Palas
│   │   ├── 09_apreensoes/                             # Bens e casos
│   │   ├── 10_casos_data/
│   │   ├── 11_casos/
│   │   ├── 12_casos_tipo_penal/
│   │   ├── 13_servidor_ativo/
│   │   ├── 14_unidade/                                # Unidade e hierarquia técnica
│   │   ├── 15_output/                                 # Gravação dos QVDs extraídos
│   │   ├── 16_section_access/
│   │   └── 17_final_contagem_tempo_carga/
│   ├── tra/                                           # Transformação e modelagem
│   │   ├── 00_orquestracao/                           # 000_MAIN.qvs
│   │   ├── 01_inicio_contagem_tempo_carga/
│   │   ├── 02_subrotinas_e_variaveis/
│   │   ├── 03_carregamento_qvds/                      # 14 QVDs extraídos
│   │   ├── 04_mapeamentos/                            # Lookup tables
│   │   ├── 05_ajustes_qvds_originais/                 # Correções e enriquecimentos
│   │   ├── 06_fatos/                                  # 10 tabelas FATO_*
│   │   ├── 07_dimensoes/                              # 23 tabelas DIM_*
│   │   ├── 08_section_access/
│   │   └── 09_final_contagem_tempo_carga/
│   └── app/                                           # Camada semântica e apresentação
│       ├── 00_orquestracao/                           # 000_MAIN.qvs
│       ├── 011_START_LOAD_TIME/
│       ├── 01_inicio_contagem_tempo_carga/
│       ├── 02_subrotinas_variaveis_de_ambiente_e_efetivo/
│       ├── 03_fatos/                                  # Carregamento FATO_*
│       ├── 04_tabela_de_ligacao/                      # Link table
│       ├── 05_dimensoes/                              # Carregamento DIM_*
│       ├── 06_inicio_contagem_tempo_carga_variaveis/
│       ├── 07_variaveis_de_metricas/                  # 6 arquivos por categoria
│       ├── 08_variaveis_de_medidas_mestras/           # 6 arquivos por categoria
│       ├── 09_final_contagem_tempo_carga_variaveis/
│       ├── 10_section_access/
│       └── 111_END_LOAD_TIME/
├── scripts/                                           # Scripts auxiliares
├── QVDs/                                              # Arquivos QVD (dados processados)
├── .gitignore                                         # Arquivos ignorados pelo Git
├── padroes_qvs.md                                     # Padrões de desenvolvimento Qlik
└── README.md                                          # Este arquivo
```

## Pré-requisitos

- Qlik Sense Enterprise ou Desktop
- Acesso às seguintes fontes de dados:

**lib://CORP_DICOR_COP/**
- `TabelaoEventos.qvd`
- `Eventos_Prisoes.qvd`
- `Eventos_Apreensoes.qvd`
- `SIGACrim.qvd`

**lib://MD_SIGACRIM/**
- `Palas_Operacoes_Tratadas_2022_2023.qvd`
- `SIGACrimMaquinariosHom.qvd`

**lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/**
- `armas_final.xlsx`
- `municoes_final.xlsx`
- `dados_entorpecentes_2022a2025_final.xlsx`
- `Area_Diretoria_CG.xlsx`
- `HIERARQUIA_TECNICA_PF_v8.xlsx`
- `CONSOLIDADA - Bens Interesse e Descapitalização Izel.xlsx`
- `descapitalizao_epol_31_03_2025.xlsx`
- `Ops Argus Izel.xlsx`
- `DPF-CAC-PR.xlsx`
- `RECURSO_HUMANOS_BRUTOS_ARGOS.xlsx`

**lib://MD_EPOL/**
- `DIM_CASOS.qvd`
- `DIM_CASOS_DATA.qvd`
- `DIM_CASOS_APREENSAO_BENS.qvd`

**lib://CORP_DADOS_AUXILIARES/qvd/**
- `DIM_CASOS_TIPO_PENAL.qvd`
- `DIM_SERVIDOR_ATIVO.qvd`
- `DIM_UNIDADE.qvd`

- Credenciais para Section Access

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd painel_sigacrim_estatisticas
   ```

2. **Configure as variáveis de extração:**
   - Edite `qlik/ext/02_subrotinas_e_variaveis/021_VARIAVEIS_EXTRACAO.qvs`
   - Defina os caminhos para as fontes de dados e o modo de carga

3. **Configure as variáveis de transformação:**
   - Edite `qlik/tra/02_subrotinas_e_variaveis/021_VARIAVEIS_CAMINHOS_UNIDADES_AREAS_DIRETORIAS_CGS.qvs`
   - Defina caminhos, unidades, áreas e diretorias

4. **Configure as variáveis de ambiente da aplicação:**
   - Edite `qlik/app/02_subrotinas_variaveis_de_ambiente_e_efetivo/022_VARIAVEIS_DE_AMBIENTE.qvs`

5. **Execute a carga de dados na ordem:**
   - Extração: `qlik/ext/00_orquestracao/000_MAIN.qvs`
   - Transformação: `qlik/tra/00_orquestracao/000_MAIN.qvs`
   - Apresentação: `qlik/app/00_orquestracao/000_MAIN.qvs`

6. **Configure Section Access:**
   - `qlik/ext/16_section_access/161_SECTION_ACCESS.qvs`
   - `qlik/tra/08_section_access/081_SECTION_ACCESS.qvs`
   - `qlik/app/10_section_access/101_SECTION_ACCESS.qvs`

## Uso

### Carregamento de Dados

1. Abra o Qlik Sense Desktop ou acesse o Qlik Sense Hub
2. Execute os scripts na ordem:
   - Extração (`qlik/ext/`) — gera QVDs intermediários em `15_output/`
   - Transformação (`qlik/tra/`) — gera tabelas FATO_* e DIM_*
   - Apresentação (`qlik/app/`) — carrega modelo final com métricas e medidas

### Navegação no Painel

- **Página Inicial:** Visão geral dos principais KPIs
- **Operações:** Análise de operações deflagradas
- **Apreensões:** Detalhamento de bens apreendidos e valores de descapitalização
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
- Nomes em MAIÚSCULAS, português brasileiro, sem acentos

### Versionamento

- Scripts versionados via Git
- Commits semânticos (`feat:`, `fix:`, `refactor:`, `docs:`)
- Dados (`.qvd`, `.csv`, `.xlsx`) excluídos pelo `.gitignore`

## Suporte e Contato

Para questões técnicas ou suporte:
- Contate a equipe do NGE/COP/DICOR
- Verifique os logs de tempo de carga gerados pelos marcadores START/END em cada camada

## Licença

Este projeto é propriedade da Polícia Federal do Brasil. Uso interno autorizado apenas.
