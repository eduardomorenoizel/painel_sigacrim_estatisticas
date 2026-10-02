# inputs/ — Materiais de entrada (somente leitura)

Projeto brownfield. Os materiais NÃO foram copiados para cá; os agentes devem ler diretamente dos caminhos abaixo.
Nenhum agente deve alterar esses arquivos.

## existing-apps/
Scripts do app atual (3 camadas):
- `../qlik/ext/` — extração (000_MAIN.qvs em 00_orquestracao)
- `../qlik/tra/` — transformação (FATO_* e DIM_*)
- `../qlik/app/` — camada semântica (fatos, link table, dimensões, métricas, medidas mestras)

## platform-libraries/
Sub-rotinas e variáveis compartilhadas:
- `../qlik/ext/02_subrotinas_e_variaveis/`
- `../qlik/tra/02_subrotinas_e_variaveis/`
- `../qlik/app/02_subrotinas_variaveis_de_ambiente_e_efetivo/`
- Padrões oficiais: `../padroes_qvs.md`

## upstream-architecture/
- `../docs/arquitetura_bi.md`
- `../docs/modelo_dimensional.md`
- `../docs/link_table_relacionamentos.md`
- `../docs/dicionario_indicadores.md`
- `../README.md` (lista de fontes/conexões lib://)

## source-documentation/
(vazio — adicionar aqui layouts/dicionários das fontes: TabelaoEventos, Eventos_Prisoes, Eventos_Apreensoes, SIGACrim, Palas, ePol)
