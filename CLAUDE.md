# CLAUDE.md — Painel SIGACrim Estatísticas Criminais

Memória persistente do projeto. Lida automaticamente pelo Claude Code em toda sessão.
**Idioma de trabalho: português brasileiro.**
Contexto refeito do zero em 2026-10-08, a partir do estado atual do repositório (commit `a4325df`).

## 1. Contexto

Aplicativo de BI em Qlik Sense do NGE/COP/DICOR da Polícia Federal. Reúne num único app os dados que antes exigiam
abrir vários painéis e cruzar planilhas no Excel (PROCV/PROCX). Exemplo de pergunta-alvo: "todas as apreensões, prisões e
buscas de um caso".

Domínios integrados:
- Operações: SIGACrim Homologadas (2024 em diante) e Palas Operações Tratadas (2022–2023)
- Eventos operacionais: TabelaoEventos, com eventos de apreensões (Eventos_Apreensoes) e de prisões (Eventos_Prisoes)
- Apreensões e descapitalização, em três granularidades:
  - até 2023: Palas, só valores totais por operação
  - 2024: ePol `DIM_CASOS_APREENSAO_BENS` (por item) + SIGACrim (totais por operação, para o que o ePol não capturava)
  - 2025 em diante: só ePol `DIM_CASOS_APREENSAO_BENS` (por item)
- Drogas, armas e munições: planilhas CGPRE
- Procedimentos investigativos: ePol `DIM_CASOS`, `DIM_CASOS_DATA`, `DIM_CASOS_TIPO_PENAL`
- Unidades: `DIM_UNIDADE`, hierarquia técnica, circunscrição, municípios/UF, faixa de fronteira
- Efetivo: `DIM_SERVIDOR_ATIVO` (sem terceirizados e estagiários)

## 2. Objetivos atuais (em ordem de prioridade)

1. **Otimizar o app.** A link table chegou a 61 milhões de linhas e hoje tem cerca de 12 milhões, o que deixa o app quase
   inviável. Plano em [artifacts/03-plano-otimizacao-link-table.md](artifacts/03-plano-otimizacao-link-table.md).
2. Escrever as métricas e medidas mestras de eventos (prisões e apreensões de eventos), que ainda são clones das de operações.
3. Refatorar o repositório (nomes fora do padrão, `000_MAIN.qvs` sem `$(Include=...)`, documentação).

A modelagem dos eventos de prisões e de apreensões (fatos, dimensões e entradas na link table) foi **concluída pelo Eduardo**
antes de 2026-10-08.

## 3. Tipos de página do app (requisito de UX)

- **Painéis** — comparações históricas, visualizações rápidas, informações essenciais, leitura rápida.
- **Análises** — comparações por UF, SR, Descentralizadas, Bases e Efetivos; exploração em profundidade;
  insights; responder ao "por quê"; filtros e detalhamentos.
- **Relatórios** — maior granularidade, informações granulares, exportação, interação com detalhes de tabelas e linhas.

## 4. Arquitetura (resumo)

Três camadas, cada uma com `00_orquestracao/000_MAIN.qvs` como ponto de entrada:
- `qlik/ext/` — extração das fontes → QVDs `E2_TEMP_*`
- `qlik/tra/` — transformação → QVDs `T3_FATO_*`, `T3_DIM_*` e `T3_LINK_TABLE_APREENSOES_OPERACOES_CASOS`
- `qlik/app/` — camada semântica: carrega fatos, link table e dimensões; variáveis de métricas (07x) e medidas mestras (08x);
  section access

Modelo: 7 fatos + 1 link table (`LINK_TABLE_APREENSOES_OPERACOES_CASOS`) + dimensões. A link table é montada **na `tra`**,
um bloco por fato (`tra/06_fatos/061` a `0610`), e gravada em `tra/07_dimensoes/0722`. Todas as métricas filtram o próprio
fato com `[Tipo do Fato]`. Documentação:
- [docs/arquitetura_bi.md](docs/arquitetura_bi.md)
- [docs/modelo_dimensional.md](docs/modelo_dimensional.md)
- [docs/link_table_relacionamentos.md](docs/link_table_relacionamentos.md)
- [docs/dicionario_indicadores.md](docs/dicionario_indicadores.md)
- [artifacts/00-platform-context.md](artifacts/00-platform-context.md) (inventário e achados)

## 5. Regras obrigatórias

Seguir **[padroes_qvs.md](padroes_qvs.md)** (fonte oficial). Destaques:
- Nomes de scripts `NNN_DESCRITIVO.qvs`, MAIÚSCULAS, português, sem acentos/espaços, sem versão no nome.
- Toda métrica e medida mestra em script (nada criado manualmente no front-end).
- Section access em script separado, ao final de cada camada.
- Nunca versionar dados (`.qvd`, `.csv`, `.xlsx`) nem credenciais.
- Commits semânticos (`feat:`, `fix:`, `refactor:`, `docs:`).
- Nunca usar sintaxe SQL em LOAD do Qlik (CASE WHEN, IS NULL, BETWEEN, IN, HAVING, aliases de tabela etc.).
- Não alterar os scripts de `qlik/` sem aprovação: as propostas são geradas em `artifacts/` e aplicadas após validação.

## 6. Como trabalhamos

- Validação de carga é manual: o ambiente é Qlik Sense Enterprise/Desktop, sem MCP do Qlik Cloud. O Eduardo recarrega e
  reporta os resultados.
- As planilhas (sheets) do front-end não estão no repositório. Mudanças que renomeiam ou removem campos usados em telas
  precisam de um inventário dos objetos antes.
- Projeto brownfield: `inputs/` aponta para os scripts e docs existentes (não foram copiados — ver `inputs/README.md`).
- O pipeline Qlik Agents (fases 0 a 8) foi usado no início; `.pipeline-state.json` não existe no repositório. Artefatos em
  `artifacts/`.

## 7. Problemas conhecidos (verificados em 2026-10-08)

Detalhes em [artifacts/00-platform-context.md](artifacts/00-platform-context.md).
- **Explosão da link table:** os blocos 061 a 068 fazem `LEFT JOIN` 1:N entre fatos (itens, Proc_Data, operações,
  participações de eventos), multiplicando linhas. Ver plano.
- Os `000_MAIN.qvs` não têm `$(Include=...)`; a ordem real de carga não está no repositório.
- Nomes de tabela divergentes: `tra/03/033` e `034` criam `TEMP_EVENTOS_*_PF_EXTERNAS_ESTRANGEIRO`, mas 068, 069, 0610,
  0716 e 0717 leem `TEMP_EVENTOS_*_EXTERNAS_ESTRANGEIRO`. A confirmar com o app real.
- Métricas 073 e medidas 082 de eventos ainda são clones das de operações.
- `qtd_presos`, `houve_prisao` e `houve_apreensao` ficam no grão de participação (evento × unidade): risco de somar o mesmo
  evento várias vezes.
- Nomes fora do padrão: `tra/03/037_..._2032_2033` (deveria ser 2022_2023), acento em `tra/07/074_..._RECUPERAÇÃO_...`,
  minúsculas em `0318_..._Mun_Faixa_de_Fronteira...`, `ext/14/146_..._Mun_Faixa...` e `tra/07/076_..._Palas_...`, espaço em
  `ext/05/051 TEMP_TEMP_DIM_CASOS.qvs`, sublinhado final em `0710`, `0712`, `0713`, `0714`, `077`, `078`, `079`, e o
  arquivo solto `qlik/planilha resultados operacionais para MJ EM NÚMEROS.qvs`.

## 8. Decisões tomadas

Registrar aqui toda decisão relevante (data — decisão — motivo).

- 2026-09-30 — Usar CLAUDE.md como memória do projeto — evitar repetir contexto entre sessões.
- 2026-09-30 — `inputs/` referencia os arquivos existentes em vez de copiá-los — evitar duplicação e divergência.
- 2026-10-08 — Recomeçar a análise do zero a partir do repositório atual; a análise e o plano anteriores ficam obsoletos.
- 2026-10-08 — **Só datas comuns.** A alta administração só usa `Data`/`Ano`/`Mês` comuns: cada indicador mostra os seus
  próprios registros do período. O cruzamento por datas específicas entre fatos (ex.: flagrantes pela data da apreensão)
  não é necessário e pode ser eliminado da link table.
