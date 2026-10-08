# Painel SIGACrim Estatísticas

## Visão Geral

Este repositório contém o painel de Business Intelligence (BI) SIGACrim Estatísticas Criminais do Núcleo de Gestão Estratégica e Inovação (NGE) da Coordenação de Supervisão de Operações e Pesquisas (COP) da Diretoria de Investigação e Combate ao Crime Organizado (DICOR) da Polícia Federal.

O painel é desenvolvido em Qlik Sense e integra dados de múltiplas fontes (SIGACrim Operações, SIGACrim Eventos Operacionais com prisões e apreensões de eventos, ePol Casos, ePol Apreensões, Palas Operações, planilhas CGPRE, Servidores e Unidades da PF) para fornecer análises operacionais, de apreensões e descapitalização, de desempenho investigativo e de efetivo policial e administrativo da PF (sem terceirizados e estagiários). O objetivo é responder num só app perguntas que antes exigiam cruzar vários painéis no Excel, como "todas as apreensões, prisões e buscas de um caso".

Contexto, decisões e problemas conhecidos estão em [CLAUDE.md](CLAUDE.md). O plano de otimização da link table está em
[artifacts/03-plano-otimizacao-link-table.md](artifacts/03-plano-otimizacao-link-table.md).

## Arquitetura

Para detalhes sobre a arquitetura do sistema, consulte [docs/arquitetura_bi.md](docs/arquitetura_bi.md).

## Modelo Dimensional

O modelo de dados segue uma abordagem dimensional com star schema e link table. Para mais informações, veja [docs/modelo_dimensional.md](docs/modelo_dimensional.md).

## Dicionário de Indicadores

Lista completa dos KPIs e medidas utilizadas no painel. Disponível em [docs/dicionario_indicadores.md](docs/dicionario_indicadores.md).

## Estrutura do Projeto

```
painel_sigacrim_estatisticas/
├── CLAUDE.md                                         # Memória do projeto (contexto, decisões, problemas conhecidos)
├── padroes_qvs.md                                    # Padrões de desenvolvimento Qlik (fonte oficial)
├── docs/
│   ├── arquitetura_bi.md                             # Camadas, fluxo e conexões
│   ├── modelo_dimensional.md                         # Fatos, dimensões, datas e unidade comum
│   ├── link_table_relacionamentos.md                 # Link table: colunas e blocos por fato
│   └── dicionario_indicadores.md                     # Organização das métricas e medidas mestras
├── artifacts/                                        # Análises e propostas (aplicadas em qlik/ só após aprovação)
├── inputs/                                           # Ponteiros para os materiais de entrada
└── qlik/
    ├── ext/                                          # Extração → QVDs E2_TEMP_*
    │   ├── 00_orquestracao/                          # 000_MAIN.qvs
    │   ├── 01_inicio_contagem_tempo_carga/
    │   ├── 02_subrotinas_e_variaveis/
    │   ├── 03_dados_corporativos/                    # TNBIA
    │   ├── 04_armas_municoes_drogas/                 # CGPRE
    │   ├── 05_casos_deduplicados/                    # DIM_CASOS deduplicado
    │   ├── 06_caso_area_diretoria/                   # Área → diretoria → CG
    │   ├── 07_eventos_operacionais/                  # TabelaoEventos, prisões e apreensões de eventos
    │   ├── 08_operacoes/                             # SIGACrim e Palas
    │   ├── 09_apreensoes_deduplicadas/               # DIM_CASOS_APREENSAO_BENS deduplicado
    │   ├── 10_casos_data/
    │   ├── 11_casos/
    │   ├── 12_casos_tipo_penal/
    │   ├── 13_servidor_ativo/
    │   ├── 14_unidade/                               # Unidade, hierarquia técnica, circunscrição, municípios, UF, fronteira
    │   ├── 15_output/                                # Gravação dos QVDs extraídos
    │   ├── 16_section_access/
    │   └── 17_final_contagem_tempo_carga/
    ├── tra/                                          # Transformação → QVDs T3_FATO_*, T3_DIM_*, T3_LINK_TABLE_*
    │   ├── 00_orquestracao/
    │   ├── 01_inicio_contagem_tempo_carga/
    │   ├── 02_subrotinas_e_variaveis/
    │   ├── 03_carregamento_qvds/                     # 18 QVDs extraídos; deduplicação de eventos
    │   ├── 04_mapeamentos/
    │   ├── 05_ajustes_qvds_originais/                # Evento e operação de cada item apreendido
    │   ├── 06_fatos/                                 # 7 fatos em 10 scripts + blocos da link table
    │   ├── 07_dimensoes/                             # 27 scripts de dimensões; 0722 grava a link table
    │   ├── 08_section_access/
    │   └── 09_final_contagem_tempo_carga/
    └── app/                                          # Camada semântica
        ├── 00_orquestracao/
        ├── 01_inicio_contagem_tempo_carga/
        ├── 02_subrotinas_variaveis_de_ambiente_e_efetivo/
        ├── 03_fatos/
        ├── 04_tabela_de_ligacao/
        ├── 05_dimensoes/
        ├── 06_inicio_contagem_tempo_carga_variaveis/
        ├── 07_variaveis_de_metricas/                 # 071 a 076
        ├── 08_variaveis_de_medidas_mestras/          # 081 a 086
        ├── 09_final_contagem_tempo_carga_variaveis/
        ├── 10_section_access/
        └── 11_final_contagem_tempo_carga/
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
   - Extração (`qlik/ext/`) — grava os QVDs `E2_TEMP_*` (`15_output/151_GRAVA_QVD.qvs`)
   - Transformação (`qlik/tra/`) — grava `T3_FATO_*`, `T3_DIM_*` e a link table
   - Apresentação (`qlik/app/`) — carrega modelo final com métricas e medidas

### Tipos de página

- **Painéis:** comparações históricas, visualizações rápidas e leitura rápida dos indicadores essenciais.
- **Análises:** comparações por UF, SR, Descentralizadas, Bases e Efetivos, com filtros e detalhamentos para responder ao "por quê".
- **Relatórios:** dados na maior granularidade, interação com detalhes de tabelas e linhas, exportação.

### Datas

Os filtros de data comuns (`Data`, `Ano`, `Mês`) mostram cada indicador pelo seu próprio período: apreensões pela data da
apreensão, operações pela deflagração, eventos pela data do evento, casos pela instauração e as movimentações dos casos (`Casos_Data`) pela data do
Proc_Data. As datas específicas de cada
fato ficam nas dimensões (ex.: `Ano da Deflagração`).

### Observação sobre a ordem de carga

Os `000_MAIN.qvs` do repositório não têm `$(Include=...)`; a ordem das seções está no editor de script de cada app no Qlik.

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
