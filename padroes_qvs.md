# Padrões Institucionais – Scripts Qlik Sense (.qvs)

Este documento define os padrões oficiais para desenvolvimento,
organização e versionamento de scripts Qlik Sense utilizados
no Painel SIGACrim – Estatísticas Criminais.

## 1. Princípios Gerais

- Todo script Qlik deve ser versionado em Git
- Nenhuma regra de negócio deve existir apenas no front-end
- Versionamento ocorre pelo Git, nunca no nome do arquivo
- A ordem de carga é controlada exclusivamente pelo MAIN.qvs

## 2. Estrutura de Pastas

- Pastas devem ser nomeadas em minúsculas
- Sem acentos, espaços ou caracteres especiais
- Separação obrigatória por camada:
  - ext (extração)
  - tra (transformação)
  - app (camada semântica)

## 3. Nomenclatura de Scripts (.qvs)

### 3.1 Padrão Obrigatório

NNN_<TIPO>_<OBJETO>[_DETALHE].qvs

Exemplos:
- 031_TEMP_DIM_CASOS.qvs
- 151_FATO_APREENSOES.qvs
- 052_MEDIDAS_APREENSAO.qvs

### 3.2 Regras

- Scripts sempre em MAIÚSCULAS
- Uso obrigatório de prefixo numérico
- Uso de underscore (_) como separador
- Proibido usar:
  - espaços
  - acentos
  - versões no nome (v2, v3, final)

## 4. Orquestração de Carga

- Todo módulo deve conter um 000_MAIN.qvs
- Nenhum script pode ser executado fora do MAIN
- A ordem de execução deve ser explícita através de $(Include=...)

## 5. Versionamento e Commits

- Toda alteração relevante deve gerar um commit
- Commits devem ser semânticos, por exemplo:
  - feat: nova métrica
  - fix: correção de regra
  - refactor: reorganização sem impacto estatístico
  - docs: ajuste de documentação

## 6. Métricas e Medidas Mestras

- Nenhuma métrica deve ser criada manualmente no Qlik Sense
- Todas as métricas e medidas mestras devem estar em script
- Arquivos específicos para:
  - métricas
  - medidas mestras

## 7. Section Access

- Deve existir em script separado
- Deve ser incluído ao final do fluxo
- Nunca misturado com regras de negócio

## 8. Dados e Segurança

- É proibido versionar dados (.qvd, .csv, .xlsx)
- Credenciais e paths sensíveis não devem estar no repositório

---

Documento aplicável a todos os scripts Qlik do projeto.