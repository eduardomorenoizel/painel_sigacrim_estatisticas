# Padrões Institucionais – Scripts Qlik Sense (.qvs)

Este documento define os padrões oficiais para desenvolvimento,
organização e versionamento de scripts Qlik Sense utilizados
no Painel SIGACrim – Estatísticas Criminais.

## 1. Princípios Gerais

- Todo script Qlik deve ser versionado em Git
- Nenhuma regra de negócio deve existir apenas no front-end
- Versionamento ocorre pelo Git, nunca no nome do arquivo
- A ordem de carga é controlada exclusivamente pelo arquivo principal (`000_MAIN.qvs`)

## 2. Estrutura de Pastas

- Pastas devem ser nomeadas em minúsculas com underscores
- Sem acentos, espaços ou caracteres especiais
- Separação obrigatória por camada:
  - `ext/` — extração de dados das fontes originais
  - `tra/` — transformação, modelagem e geração de fatos/dimensões
  - `app/` — camada semântica, métricas e apresentação

### 2.1 Pastas da Camada ext/

```
ext/
├── 00_orquestracao/
├── 01_inicio_contagem_tempo_carga/
├── 02_subrotinas_e_variaveis/
├── 03_dados_corporativos/
├── 04_armas_municoes_drogas/
├── 05_temp_casos/
├── 06_caso_area_diretoria/
├── 07_eventos_operacionais/
├── 08_operacoes/
├── 09_apreensoes/
├── 10_casos_data/
├── 11_casos/
├── 12_casos_tipo_penal/
├── 13_servidor_ativo/
├── 14_unidade/
├── 15_output/
├── 16_section_access/
└── 17_final_contagem_tempo_carga/
```

### 2.2 Pastas da Camada tra/

```
tra/
├── 00_orquestracao/
├── 01_inicio_contagem_tempo_carga/
├── 02_subrotinas_e_variaveis/
├── 03_carregamento_qvds/
├── 04_mapeamentos/
├── 05_ajustes_qvds_originais/
├── 06_fatos/
├── 07_dimensoes/
├── 08_section_access/
└── 09_final_contagem_tempo_carga/
```

### 2.3 Pastas da Camada app/

```
app/
├── 00_orquestracao/
├── 011_START_LOAD_TIME/
├── 01_inicio_contagem_tempo_carga/
├── 02_subrotinas_variaveis_de_ambiente_e_efetivo/
├── 03_fatos/
├── 04_tabela_de_ligacao/
├── 05_dimensoes/
├── 06_inicio_contagem_tempo_carga_variaveis/
├── 07_variaveis_de_metricas/
├── 08_variaveis_de_medidas_mestras/
├── 09_final_contagem_tempo_carga_variaveis/
├── 10_section_access/
└── 111_END_LOAD_TIME/
```

## 3. Nomenclatura de Scripts (.qvs)

### 3.1 Padrão Geral

```
NNN_DESCRITIVO_DETALHADO.qvs
```

- `NNN` — prefixo numérico sequencial de três dígitos (ou mais, quando necessário)
- `DESCRITIVO_DETALHADO` — nome em MAIÚSCULAS e português brasileiro, separado por underscores

### 3.2 Scripts de Orquestração e Controle de Tempo

- `000_MAIN.qvs` — arquivo principal de cada módulo (único ponto de entrada)
- Marcadores de tempo de carga geral:
  - `011_START_LOAD_TIME.qvs` — início geral
  - `171_END_LOAD_TIME.qvs` (ext) / `091_END_LOAD_TIME.qvs` (tra) / `111_END_LOAD_TIME.qvs` (app)
- Marcadores de tempo por fase (padrão `NNN0_START_` / `NN9_END_`):
  - `050_START_CASOS_GROUPBY_LOAD.qvs` / `059_END_CASOS_GROUPBY_LOAD.qvs`
  - `090_START_APREENSOES_GROUPBY_LOAD.qvs` / `099_END_APREENSOES_GROUPBY_LOAD.qvs`
  - `031_START_FATOS_LOAD_TIME.qvs` / `033_END_FATOS_LOAD_TIME.qvs`
  - `041_START_LINKTABLE_LOAD_TIME.qvs` / `043_END_LINKTABLE_LOAD_TIME.qvs`
  - `051_START_DIMENSOES_LOAD_TIME.qvs` / `053_END_DIMENSOES_LOAD_TIME.qvs`

### 3.3 Scripts Funcionais — Exemplos por Camada

**ext/**
```
021_VARIAVEIS_EXTRACAO.qvs
022_SUBROTINAS.qvs
031_TEMP_TNBIA.qvs
041_TEMP_ARMAS_MUNICOES_DROGAS_FINAL_CGPRE.qvs
051_TEMP_TEMP_DIM_CASOS.qvs
061_AREA_DIRETORIA_CG.qvs
071_TEMP_TABELAOEVENTOS.qvs
081_TEMP_TEMP_SIGACRIMHOMOLOGADAS.qvs
091_TEMP_DIM_CASOS_APREENSAO_BENS.qvs
151_GRAVA_QVD.qvs
161_SECTION_ACCESS.qvs
```

**tra/**
```
021_VARIAVEIS_CAMINHOS_UNIDADES_AREAS_DIRETORIAS_CGS.qvs
022_SUBROTINAS.qvs
031_TEMP_TNBIA.qvs
041_MAPPING_LOADS.qvs
051_ADICIONA_EVENTOPF_AO_ITEM_APREENSAO.qvs
061_FATO_APREENSOES_DIM_CASOS_APREENSAO_BENS.qvs
064_FATO_OPERACOES_SIGACRIMHOMOLOGADAS.qvs
066_FATO_CASOS_DIM_CASOS.qvs
071_DIM_OPERACOES_SIGACRIMHOMOLOGADAS.qvs
077_DIM_APREENSOES_DIM_CASOS_APREENSAO_BENS_.qvs
081_SECTION_ACCESS.qvs
```

**app/**
```
021_SUBROTINAS.qvs
022_VARIAVEIS_DE_AMBIENTE.qvs
023_VARIAVEIS_DE_EFETIVO.qvs
032_FATOS.qvs
042_TABELA_DE_LIGACAO.qvs
052_DIMENSOES.qvs
071_VARIAVEIS_DE_METRICAS_DE_CONTROLE.qvs
072_VARIAVEIS_DE_METRICAS_OPERACIONAIS.qvs
081_VARIAVEIS_DE_MEDIDAS_MESTRAS_OPERACIONAIS.qvs
101_SECTION_ACCESS.qvs
```

### 3.4 Regras

- Scripts sempre em MAIÚSCULAS
- Uso obrigatório de prefixo numérico sequencial
- Uso de underscore (`_`) como separador
- Nomes descritivos em português brasileiro
- Proibido usar:
  - espaços
  - acentos
  - versões no nome (v2, v3, final)
- Prefixos de quatro dígitos (`0310`, `0311`…) são permitidos quando há mais de 9 scripts em uma mesma fase
- Alguns arquivos de controle de tempo podem não ter extensão `.qvs`

## 4. Orquestração de Carga

- Todo módulo deve conter um arquivo principal (`000_MAIN.qvs`)
- Nenhum script pode ser executado fora do arquivo principal
- A ordem de execução deve ser explícita através de `$(Include=...)`
- Scripts de START/END delimitam seções do processo para medição de tempo
- Cada camada (ext, tra, app) possui seus próprios marcadores de tempo geral e por fase

## 5. Versionamento e Commits

- Toda alteração relevante deve gerar um commit
- Commits devem ser semânticos, por exemplo:
  - `feat: nova métrica operacional`
  - `fix: correção cálculo apreensões`
  - `refactor: reorganização scripts sem impacto estatístico`
  - `docs: atualização padrões desenvolvimento`

## 6. Métricas e Medidas Mestras

- Nenhuma métrica deve ser criada manualmente no Qlik Sense
- Todas as métricas e medidas mestras devem estar em script
- Separação clara por pasta na camada `app/`:
  - `07_variaveis_de_metricas/`: Variáveis de cálculo por categoria temática
  - `08_variaveis_de_medidas_mestras/`: Medidas parametrizadas para o front-end
- Categorias de métricas cobertas (071–076 e 081–086):
  - Controle, operacionais, eventos operacionais, apreensões, drogas/armas/munições, ePol, efetivo
- Medidas mestras geradas via sub-rotina parametrizada (`GerarMedidasMestrasDeflagracao6`)

## 7. Section Access

- Deve existir em script separado dentro da pasta `*_section_access/` de cada camada:
  - `ext/16_section_access/161_SECTION_ACCESS.qvs`
  - `tra/08_section_access/081_SECTION_ACCESS.qvs`
  - `app/10_section_access/101_SECTION_ACCESS.qvs`
- Deve ser incluído ao final do fluxo de carga de cada camada
- Nunca misturado com regras de negócio

## 8. Dados e Segurança

- É proibido versionar dados (`.qvd`, `.csv`, `.xlsx`)
- Credenciais e paths sensíveis não devem estar no repositório
- Arquivo `.gitignore` deve excluir arquivos de dados

---

Documento aplicável a todos os scripts Qlik do projeto Painel SIGACrim.
