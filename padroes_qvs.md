# Padrões Institucionais – Scripts Qlik Sense (.qvs)

Este documento define os padrões oficiais para desenvolvimento,
organização e versionamento de scripts Qlik Sense utilizados
no Painel SIGACrim – Estatísticas Criminais.

## 1. Princípios Gerais

- Todo script Qlik deve ser versionado em Git
- Nenhuma regra de negócio deve existir apenas no front-end
- Versionamento ocorre pelo Git, nunca no nome do arquivo
- A ordem de carga é controlada exclusivamente pelo arquivo principal (000_Main.qvs ou 000_MAIN.qvs)

## 2. Estrutura de Pastas

- Pastas devem ser nomeadas em minúsculas
- Sem acentos, espaços ou caracteres especiais
- Separação obrigatória por camada:
  - `ext` (extração de dados das fontes)
  - `tra` (transformação e modelagem)
  - `app` (camada semântica e apresentação)

## 3. Nomenclatura de Scripts (.qvs)

### 3.1 Padrão Geral

NNN_DESCRITIVO_DETALHADO.qvs

### 3.2 Scripts de Orquestração

- `000_Main.qvs` ou `000_MAIN.qvs`: Arquivo principal de cada módulo
- `001_START_LOAD_TIME.qvs`: Início do carregamento com timestamp
- `999_END_LOAD_TIME.qvs`: Fim do carregamento com timestamp
- Scripts de controle: `010_START_*_LOAD_TIME.qvs`, `019_END_*_LOAD_TIME.qvs`

### 3.3 Scripts Funcionais

Exemplos baseados na estrutura atual:
- `002_SUBROTINAS.qvs`
- `003_VARIAVEIS_DE_AMBIENTE.qvs`
- `011_FATOS.qvs`
- `021_TABELA_DE_LIGACAO.qvs`
- `031_DIMENSOES.qvs`
- `041_VARIAVEIS_DE_METRICAS_DE_CONTROLE.qvs`
- `042_VARIAVEIS_DE_METRICAS_OPERACIONAIS.qvs`
- `051_VARIAVEIS_DE_MEDIDAS_MESTRAS_OPERACIONAIS.qvs`
- `061_SECTION_ACCESS.qvs`

### 3.4 Regras

- Scripts sempre em MAIÚSCULAS
- Uso obrigatório de prefixo numérico sequencial
- Uso de underscore (_) como separador
- Nomes descritivos em português brasileiro
- Proibido usar:
  - espaços
  - acentos
  - versões no nome (v2, v3, final)
- Alguns arquivos de controle podem não ter extensão `.qvs`

## 4. Orquestração de Carga

- Todo módulo deve conter um arquivo principal (`000_Main.qvs` ou `000_MAIN.qvs`)
- Nenhum script pode ser executado fora do arquivo principal
- A ordem de execução deve ser explícita através de `$(Include=...)`
- Scripts de START/END delimitam seções do processo

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
- Separação clara entre:
  - `03_metricas/`: Definição de variáveis de cálculo
  - `04_medidas_mestras/`: Medidas parametrizadas para o front-end

## 7. Section Access

- Deve existir em script separado (`061_SECTION_ACCESS.qvs`)
- Deve ser incluído ao final do fluxo de carga
- Nunca misturado com regras de negócio

## 8. Dados e Segurança

- É proibido versionar dados (.qvd, .csv, .xlsx)
- Credenciais e paths sensíveis não devem estar no repositório
- Arquivo `.gitignore` deve excluir arquivos de dados

---

Documento aplicável a todos os scripts Qlik do projeto Painel SIGACrim.