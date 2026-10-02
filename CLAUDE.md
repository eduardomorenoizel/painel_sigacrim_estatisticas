# CLAUDE.md — Painel SIGACrim Estatísticas Criminais

Memória persistente do projeto. Lida automaticamente pelo Claude Code em toda sessão.
**Idioma de trabalho: português brasileiro.**

## 1. Contexto

Aplicativo de BI em Qlik Sense do NGE/COP/DICOR da Polícia Federal. Integra, num único painel,
dados de vários outros painéis/fontes para atender às demandas de gestão estratégica das
Diretorias, das Unidades Regionais (SR) e das Descentralizadas.

Domínios integrados:
- Operações (SIGACrim Homologadas, Palas Operações Tratadas 2022–2023)
- Eventos operacionais (TabelaoEventos)
- Apreensões, incluindo valores de descapitalização (ePol DIM_CASOS_APREENSAO_BENS, SIGACrim, Palas, CGPRE drogas/armas/munições)
- Prisões (Eventos_Prisoes)
- Procedimentos investigativos (ePol DIM_CASOS, DIM_CASOS_DATA, DIM_CASOS_TIPO_PENAL)
- Unidades (DIM_UNIDADE, hierarquia técnica, circunscrição, municípios/UF, faixa de fronteira)
- Efetivo de servidores (DIM_SERVIDOR_ATIVO — sem terceirizados e estagiários)

## 2. Objetivos atuais (em ordem de prioridade)

1. **Concluir a modelagem dos eventos operacionais, dos eventos de apreensões e dos eventos de prisões**
   (fatos, dimensões, integração à link table, métricas e medidas mestras).
2. Refatorar o repositório (limpeza de duplicados, padronização de nomes, organização das camadas).
3. Outras melhorias de desempenho, qualidade de dados e usabilidade.

## 3. Tipos de página do app (requisito de UX)

- **Painéis** — comparações históricas, visualizações rápidas, informações essenciais, leitura rápida.
- **Análises** — comparações por UF, SR, Descentralizadas, Bases e Efetivos; exploração em profundidade;
  insights; responder ao "por quê"; filtros e detalhamentos.
- **Relatórios** — maior granularidade, informações granulares, exportação, interação com detalhes de tabelas e linhas.

## 4. Arquitetura existente (resumo)

Três camadas, cada uma com `00_orquestracao/000_MAIN.qvs` como único ponto de entrada:
- `qlik/ext/` — extração das fontes → QVDs intermediários
- `qlik/tra/` — transformação → tabelas `FATO_*` e `DIM_*`
- `qlik/app/` — camada semântica: fatos, **link table**, dimensões, variáveis de métricas (07x) e medidas mestras (08x), section access

Modelo: star schema com link table. Documentação em `docs/`:
- [docs/arquitetura_bi.md](docs/arquitetura_bi.md)
- [docs/modelo_dimensional.md](docs/modelo_dimensional.md)
- [docs/link_table_relacionamentos.md](docs/link_table_relacionamentos.md)
- [docs/dicionario_indicadores.md](docs/dicionario_indicadores.md)

## 5. Regras obrigatórias

Seguir **[padroes_qvs.md](padroes_qvs.md)** (fonte oficial). Destaques:
- Nomes de scripts `NNN_DESCRITIVO.qvs`, MAIÚSCULAS, português, sem acentos/espaços, sem versão no nome.
- Toda métrica e medida mestra em script (nada criado manualmente no front-end).
- Section access em script separado, ao final de cada camada.
- Nunca versionar dados (`.qvd`, `.csv`, `.xlsx`) nem credenciais.
- Commits semânticos (`feat:`, `fix:`, `refactor:`, `docs:`).
- Nunca usar sintaxe SQL em LOAD do Qlik (CASE WHEN, IS NULL, BETWEEN, IN, HAVING, aliases de tabela etc.).
- Não alterar os scripts de `qlik/` sem aprovação: as propostas são geradas em `artifacts/` e aplicadas após validação.

## 6. Como trabalhamos (Qlik Agents)

- Uso o plugin **Qlik Agents** em pipeline de fases (0 a 8). Estado oficial em **`.pipeline-state.json`** — sempre ler antes de continuar.
- Projeto brownfield: `inputs/` aponta para os scripts e docs existentes (não foram copiados — ver `inputs/README.md`).
- MCP do Qlik Cloud: não disponível (ambiente Qlik Sense Enterprise/Desktop). Validação de carga é feita por mim manualmente, e eu reporto os resultados.
- Para retomar: "Continue o pipeline do SIGACrim".

## 7. Problemas conhecidos (levantados em 2026-09-30, a confirmar na Fase 0)

- Arquivos duplicados em `qlik/tra/` com sufixo `_ATUAL_FUNCIONANDO` (032, 033, 034, 051) — definir qual versão é a vigente.
- `qlik/tra/05_ajustes_qvds_originais/Untitled-1.js` solto no repositório.
- `037_TEMP_PALAS_OPERACOES_TRATADAS_2032_2033.qvs` — provável erro de digitação (2022_2023).
- Nomes fora do padrão: acento em `074_..._RECUPERAÇÃO_...`, minúsculas em `0318_..._Mun_Faixa_de_Fronteira...`, `076_..._Palas_...`, espaço em `ext/05_casos_deduplicados/051 TEMP_TEMP_DIM_CASOS.qvs`.
- README e padroes_qvs.md divergem das pastas reais (ex.: `05_temp_casos` vs `05_casos_deduplicados`, `09_apreensoes` vs `09_apreensoes_deduplicadas`).

Achados da Fase 0 (detalhes em `artifacts/00-platform-context.md`):
- Os `000_MAIN.qvs` não têm `$(Include=...)`, então a ordem de carga real não está no repositório.
- As métricas 073 e as medidas 082 de eventos são clones das de operações. Ainda não há métricas de prisões nem de apreensões de eventos.
- A link table de 068 faz 3 LEFT JOIN encadeados, com risco de multiplicar linhas. `qtd_presos` se repete por unidade participante, com risco de inflar somas.

## 8. Decisões tomadas

Registrar aqui toda decisão relevante (data — decisão — motivo).

- 2026-09-30 — Usar o pipeline Qlik Agents com CLAUDE.md como memória do projeto — evitar repetir contexto entre sessões.
- 2026-09-30 — `inputs/` referencia os arquivos existentes em vez de copiá-los — evitar duplicação e divergência.
