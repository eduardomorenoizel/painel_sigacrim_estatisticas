# Arquitetura BI — Estatísticas Criminais DICOR

Painel SIGACrim Estatísticas Criminais do NGE/COP/DICOR/PF, em Qlik Sense Enterprise. Estado do repositório em 2026-10-08.

O objetivo do app é reunir num só lugar dados que antes exigiam abrir vários painéis e cruzar planilhas: operações,
eventos operacionais (com prisões e apreensões de eventos), apreensões e descapitalização, procedimentos investigativos
(ePol), unidades e efetivo.

## 1. Fluxo

```
Fontes (lib://CORP_DICOR_COP, MD_SIGACRIM, MD_EPOL, CORP_DADOS_AUXILIARES, CORP_DICOR_NGE)
        │
        ▼
[qlik/ext] extração, deduplicação de casos e itens  →  QVDs  E2_TEMP_*
        │
        ▼
[qlik/tra] limpeza, inferências, fatos, dimensões e link table  →  QVDs  T3_FATO_*, T3_DIM_*, T3_LINK_TABLE_*
        │
        ▼
[qlik/app] carga do modelo, variáveis de métricas (07x) e medidas mestras (08x), section access  →  app Qlik Sense
```

Cada camada é um script de carga separado, com `00_orquestracao/000_MAIN.qvs` como entrada. Os `000_MAIN.qvs` do
repositório só definem o locale; não há `$(Include=...)`, então a ordem real das seções está no editor de script do Qlik.

## 2. Camada `ext` (31 scripts)

| Pasta | Conteúdo |
|---|---|
| `02_subrotinas_e_variaveis` | caminhos das fontes (`vCarrega*`), modo de carga, sub-rotinas de gravação |
| `03_dados_corporativos` | TNBIA (taxonomia de materiais), a partir de `DIM_CASOS_APREENSAO_BENS` |
| `04_armas_municoes_drogas` | planilhas CGPRE de armas, munições e drogas (2022 a 2026) |
| `05_casos_deduplicados` | `DIM_CASOS` do ePol deduplicado (`GROUP BY`) |
| `06_caso_area_diretoria` | `Area_Diretoria_CG.xlsx` (área → diretoria → CG) |
| `07_eventos_operacionais` | `TabelaoEventos`, `Eventos_Prisoes`, `Eventos_Apreensoes` |
| `08_operacoes` | `SIGACrim.qvd` (homologadas) e `Palas_Operacoes_Tratadas_2022_2023.qvd` |
| `09_apreensoes_deduplicadas` | `DIM_CASOS_APREENSAO_BENS` deduplicado por item |
| `10_casos_data`, `11_casos`, `12_casos_tipo_penal` | demais tabelas do ePol |
| `13_servidor_ativo`, `14_unidade` | efetivo, unidades, hierarquia técnica, circunscrição, municípios, UF, faixa de fronteira |
| `15_output` | grava todos os QVDs `E2_TEMP_*` |
| `16_section_access` | section access |

## 3. Camada `tra` (66 scripts)

| Pasta | Conteúdo |
|---|---|
| `02_subrotinas_e_variaveis` | caminhos (`vCaminhoExtraidosV2` = `E2_`, `vCaminhoTransformadosV3` = `T3_`), listas de unidades de fronteira, variáveis de correção de IPL e de unidade/área/diretoria/CG (`vCarregaUnidAreaDirCoorGeral*`) |
| `03_carregamento_qvds` | carrega os 18 QVDs `E2_TEMP_*`. Destaques: `032` deduplica o TabelaoEventos e cria `id_ordem_original_evento` (participação de unidade em evento); `033`/`034` atribuem cada apreensão e prisão de evento à unidade participante prioritária; `035` corrige a subclasse dos itens CGPRE; `038` carrega o ePol sem as subclasses `3.*` e `11.*` e concatena os itens CGPRE no lugar delas |
| `04_mapeamentos` | mapas de item de interesse/descapitalização, RE, operação por caso, evento PF por caso, migração, fatores de normalização |
| `05_ajustes_qvds_originais` | `051` vincula apreensões de eventos PF a itens do ePol (matching hierárquico); `052` atribui operação ao item por intervalos de deflagração (IPL e RE_SEQUESTRO); `053` escolhe a operação final do item; `054` corrige erro de sincronização ePol/SIGACrim |
| `06_fatos` | 10 scripts: cada um grava um `FATO_*` e monta um bloco da link table |
| `07_dimensoes` | 27 scripts de `DIM_*`; `0722` grava também a link table |
| `08_section_access` | section access |

## 4. Camada `app` (30 scripts)

| Pasta | Conteúdo |
|---|---|
| `02_subrotinas_variaveis_de_ambiente_e_efetivo` | sub-rotinas `CriarVariavel*` (contagem, soma, relativa, anteriores, Mi/Bi/Reais), variáveis de ambiente, modificadores de efetivo |
| `03_fatos` | carga dos 7 `FATO_*` |
| `04_tabela_de_ligacao` | carga da link table |
| `05_dimensoes` | carga das dimensões |
| `07_variaveis_de_metricas` | 071 controle, 072 operações, 073 eventos, 074 apreensões, 075 drogas/armas/munições, 076 ePol |
| `08_variaveis_de_medidas_mestras` | 081 operações, 082 eventos, 083 apreensões, 084 drogas/armas/munições, 085 ePol, 086 efetivo |
| `10_section_access` | section access |
| `01`, `06`, `09`, `11` | marcadores de tempo de carga |

## 5. Modelo

Link table com 7 fatos e dimensões compartilhadas. Ver [modelo_dimensional.md](modelo_dimensional.md) e
[link_table_relacionamentos.md](link_table_relacionamentos.md).

Pontos de projeto:
- **Data comum:** cada linha da link tem `Data`/`Ano`/`Mês` do próprio fato, e `Tipo do Fato` identifica o fato. Toda
  métrica filtra o próprio `Tipo do Fato`, então os indicadores são independentes por período.
- **Unidade comum:** `%UNIDADE_KEY` em toda linha (unidade do caso, unidade Palas ou unidade participante do evento).
- **Granularidades diferentes de apreensões:** Palas (até 2023, totais por operação), ePol + SIGACrim (2024), só ePol
  (2025 em diante). No `FATO_APREENSOES`, o SIGACrim e o Palas entram com a operação no lugar do item.
- **Problema atual:** os blocos da link fazem `LEFT JOIN` 1:N entre fatos, o que leva a ~12 milhões de linhas (já foram 61).
  Plano em [../artifacts/03-plano-otimizacao-link-table.md](../artifacts/03-plano-otimizacao-link-table.md).

## 6. Conexões de dados

| Conexão | Conteúdo |
|---|---|
| `lib://CORP_DICOR_COP/` | `TabelaoEventos.qvd`, `Eventos_Prisoes.qvd`, `Eventos_Apreensoes.qvd`, `SIGACrim.qvd` |
| `lib://MD_SIGACRIM/` | `Palas_Operacoes_Tratadas_2022_2023.qvd` |
| `lib://MD_EPOL/` | `DIM_CASOS.qvd`, `DIM_CASOS_DATA.qvd`, `DIM_CASOS_APREENSAO_BENS.qvd` |
| `lib://CORP_DADOS_AUXILIARES/qvd/` | `DIM_CASOS_TIPO_PENAL.qvd`, `DIM_SERVIDOR_ATIVO.qvd`, `DIM_UNIDADE.qvd`, `DIM_CIRCUNSCRICAO_PF.qvd`, `TB_MUNICIPIOS_BRASIL.QVD`, `TB_UF_BRASIL.QVD` |
| `lib://CORP_DICOR_NGE/BI_NGE_ESTATISTICAS/` | planilhas de apoio (CGPRE, `Area_Diretoria_CG.xlsx`, `HIERARQUIA_TECNICA_PF_v8.xlsx`, `CONSOLIDADA - Bens Interesse e Descapitalização Izel.xlsx`, `descapitalizao_epol_31_03_2025.xlsx`, faixa de fronteira, section access) e os QVDs `E2_`/`T3_` |

## 7. Segurança

Section access em script separado no fim de cada camada (`ext/16/161`, `tra/08/081`, `app/10/101`), lendo planilhas da
conexão `CORP_DICOR_NGE`. Credenciais não são versionadas. Nomes e CPFs de presos são anonimizados na `tra` (`032`, `034`).

## 8. Padrões

Ver [../padroes_qvs.md](../padroes_qvs.md).
