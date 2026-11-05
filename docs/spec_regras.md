# Especificação das regras — HIERARQUIA_TECNICA_PF_V8.xlsx

Documento de trabalho para reimplementar em script Qlik as regras hoje calculadas na planilha
`S:\BI_NGE_ESTATISTICAS\HIERARQUIA_TECNICA_PF_V8.xlsx`. **As fórmulas descrevem o que a planilha faz hoje, não a regra correta.**
O desenvolvedor preenche os campos **Regra pretendida** e **Exemplos esperados**; só depois disso começa o script.

- Fonte: `docs/inventario_regras.csv` e `docs/inventario_formulas.csv` (gerados por `scripts/extrair_formulas_excel.py`, 2026-10-31).
  A fórmula completa, sem abreviação, está na coluna `formula_pt_exemplo` do `inventario_regras.csv`, pelo **ID**.
- Uso atual no Qlik: `ext/14_unidade/142` lê a aba `HIERARQUIA_TECNICA_PF` → `tra/07_dimensoes/0720` → `app/05_dimensoes/052`
  (e ~112 referências em `app/02_.../023_VARIAVEIS_DE_EFETIVO`).
- Notação abreviada nas fórmulas abaixo: `[Coluna]` = `Tabela1[[#This Row],[Coluna]]`;
  `UC` = `[Unidades Centrais]`, `UR` = `[Unidades Regionais]`, `B` = `[Bases]`, `UD` = `[Unidades Descentralizadas]`.
- "Valor hoje" nos exemplos foi calculado à mão a partir da fórmula; confira se bate com a planilha.

Sumário: [0. Entradas](#0-entradas-manuais) · [1. Ciclo extintas/novas](#1-ciclo-de-atualização-extintas--novas) ·
[2. Classificação](#2-classificação-central--regional--base--descentralizada) · [3. Campos derivados](#3-campos-derivados) ·
[4. Abas auxiliares](#4-abas-auxiliares) · [5. Perguntas gerais](#5-perguntas-gerais)

---

## 0. Entradas (manuais)

| Coluna | Campo | Preenchidas | O que é hoje |
|---|---|---|---|
| HIERARQUIA_TECNICA_PF!C | Unidade Sigla | 4.587 | copiada à mão da COM_HIERARQUIA_DIM_UNIDADE |
| HIERARQUIA_TECNICA_PF!N | Unidades Centrais | 770 | padrão com curinga, ex.: `*/GAB/PF`, `GAB/PF`, `PF`, `CTCG` (45 distintos) |
| HIERARQUIA_TECNICA_PF!O | Unidades Regionais | 2.168 | ex.: `SR/*`, `DREX/SR/*`, `*/DELEMIG/DREX/SR/*` (135 distintos) |
| HIERARQUIA_TECNICA_PF!P | Bases | 73 | ex.: `BABC/DRPJ/SR/*`, `FICCO/DPF/*`, `LAFIN-*/DRPJ/SR/*` (17 distintos) |
| HIERARQUIA_TECNICA_PF!Q | Unidades Descentralizadas | 1.576 | ex.: `ACOLHIDA/DPF/*`, `*CPD/DPF/*`, `*/NUPROC/DPF/*`, `DPF/*` (98 distintos) |
| HIERARQUIA_TECNICA_PF!AH | PJ/NPJ | 4.587 | `PJ` ou `NPJ` |
| HIERARQUIA_TECNICA_PF!AG | Hierarquia Técnica | ? | **sem fórmula e sem uso em nenhuma regra** — preenchida à mão |
| COM_HIERARQUIA_DIM_UNIDADE!A–L, AK | Sigla1..6, Superior, Descrição, Sigla, Nível | 4.705 | importada do CSV do `tra 0719` (conexão `DadosExternos_1`) |

Observações:
- 770 + 2.168 + 73 + 1.576 = 4.587: **cada linha tem exatamente uma das quatro colunas preenchida**.
- Na aba HIERARQUIA_TECNICA_PF, 4.585 das 4.588 linhas estão ocultas (filtro ativo) e a coluna A (`Unidade ID`) está oculta.

**Perguntas**
- 0.1 Uma unidade pode, de propósito, pertencer a duas categorias (ex.: Base **e** Regional)? Ou é sempre uma só?
- 0.2 O que é a coluna **Hierarquia Técnica** e como você a preenche? (Ela chega ao app pelo 0720/052.)
- 0.3 O padrão serve para dizer **quais unidades** entram na categoria (curinga sobre a `Unidade Sigla`), **qual rótulo** sai, ou as duas coisas?
  Hoje faz as duas: o rótulo é recortado do texto do padrão (ver seção 2).

---

## 1. Ciclo de atualização (extintas / novas)

### A6-AL.1 — Unidade Nova (COM_HIERARQUIA_DIM_UNIDADE!AL2:AL4706)
- **Colunas:** entrada `COM_HIERARQUIA_DIM_UNIDADE!L` (Unidade Sigla), `HIERARQUIA_TECNICA_PF!C` (Unidade Sigla).
- **Fórmula original:** `=PROCX([Unidade Sigla];Tabela1[Unidade Sigla];Tabela1[Unidade Sigla];"Nova";0;1)`
- **O que faz hoje:** procura a sigla da DIM_UNIDADE atual na HIERARQUIA_TECNICA_PF (correspondência exata). Se não achar, mostra `"Nova"`;
  se achar, repete a própria sigla.
- **Comportamentos suspeitos:**
  - Compara **só a sigla**. Você descreveu que compara "Descrição Unidade Sigla" **e** "Unidade Sigla": uma unidade que mudou de descrição
    mantendo a sigla não é marcada.
  - O resultado mistura dois tipos de informação na mesma coluna (a sigla ou a palavra "Nova").
- **Perguntas:**
  - 1.1 Mudança só de descrição (mesma sigla) deve ser tratada como unidade nova, como alteração, ou ignorada?
  - 1.2 Sigla que mudou (ex.: unidade renomeada) deve herdar a classificação da sigla antiga? Se sim, como identificar a mesma unidade — pelo `Unidade ID`?
- **Regra pretendida:** _____
- **Exemplos esperados:**

| Situação | Valor hoje | Esperado |
|---|---|---|
| Sigla existe nas duas abas | a própria sigla | |
| Sigla só na DIM_UNIDADE | `Nova` | |
| Mesma sigla, descrição mudou | a própria sigla | |

### A7-D.1 a A7-M.1 — Busca dos atributos atuais (HIERARQUIA_TECNICA_PF!D:M)
Dez regras iguais, mudando só a coluna devolvida:

| ID | Coluna | Campo devolvido da COM_HIERARQUIA_DIM_UNIDADE |
|---|---|---|
| A7-D.1 | D | Unidade Sigla Superior |
| A7-E.1 | E | Unidade Sigla1 |
| A7-F.1 | F | Unidade Sigla2 |
| A7-G.1 | G | Unidade Sigla3 |
| A7-H.1 | H | Unidade Sigla4 |
| A7-I.1 | I | Unidade Sigla5 |
| A7-J.1 | J | Unidade Sigla6 |
| A7-K.1 | K | Nível |
| A7-L.1 | L | Descrição Unidade Sigla NOVA |
| A7-M.1 | M | Unidade Sigla NOVA |

- **Fórmula original (ex. D):** `=PROCX([Unidade Sigla];COM_HIERARQUIA_DIM_UNIDADE[Unidade Sigla];COM_HIERARQUIA_DIM_UNIDADE[Unidade Sigla Superior];"Extinta";0;1)`
- **O que faz hoje:** busca a sigla da linha na DIM_UNIDADE atual (exata) e traz o atributo; se não achar, escreve `"Extinta"`.
- **Comportamentos suspeitos:**
  - `"Extinta"` cai também em **Nível** (campo numérico) e nas siglas: texto de controle misturado com dado.
  - **J824 tem o valor digitado `loikp`** no lugar da fórmula (parece digitação acidental).
  - Esses campos vão para o Qlik pelo `ext 142`, mas o `tra 0720` não os usa; o modelo já tem os mesmos campos na `DIM_UNIDADE`.
- **Perguntas:**
  - 1.3 No script, a base passa a ser a `DIM_UNIDADE` ativa (extintas somem sozinhas). Precisa de algum registro/histórico das unidades extintas?
  - 1.4 Pode apagar `loikp` em J824 (e considerar a célula como a fórmula da coluna)?
- **Regra pretendida:** _____
- **Exemplos esperados:** _____

---

## 2. Classificação (Central / Regional / Base / Descentralizada)

Cada regra recorta o **texto do padrão** digitado em N/O/P/Q para produzir a sigla da categoria.

### A7-V.1 — Unidade Central (V2:V3, V5:V4588)
- **Colunas:** entrada N (Unidades Centrais). Usada por: R, W, X, CRITERIO_UN_CENTRAIS, Planilha1.
- **Fórmula original:** `=SEERRO(SE(ESQUERDA(UC;1)="*";DIREITA(UC;NÚM.CARACT(UC)-2);SE(UC=0;"";UC));"")`
- **O que faz hoje:** se o padrão começa com `*`, tira os **2 primeiros caracteres** (`*/`); senão devolve o padrão como está; vazio → `""`.
- **Comportamentos suspeitos:**
  - Tira 2 caracteres fixos: um padrão `*X/PF` (sem barra depois do `*`) perderia uma letra.
  - `SE(UC=0;...)` é um jeito indireto de testar célula vazia.
  - `SEERRO` esconde qualquer erro.
  - **V4 tem `PF` digitado** no lugar da fórmula (a fórmula daria o mesmo se N4 = `PF`).
  - Siglas sem `/PF` (`UPAD`, `CTCG`, `CRI`, `CGPF`, `CGOVGP`, `CGIT`, `CDTIC`) viram Unidade Central.
- **Perguntas:**
  - 2.1 `UPAD`, `CTCG`, `CRI`, `CGPF`, `CGOVGP`, `CGIT`, `CDTIC` são unidades da PF? Devem ser Unidade Central, outra categoria ou ficar de fora?
  - 2.2 A sigla da Central deve ser sempre a unidade de 2º nível (`GAB/PF`, `DICOR/PF`...)? Ou pode ser outro nível?
- **Regra pretendida:** _____
- **Exemplos esperados:**

| Unidade Sigla | Padrão (N) | Valor hoje | Esperado |
|---|---|---|---|
| SESIN/DSEG/GAB/PF | `*/GAB/PF` | GAB/PF | |
| GAB/PF | `GAB/PF` | GAB/PF | |
| PF | `PF` (V4 digitado) | PF | |
| CTCG | `CTCG` | CTCG | |

### A7-Y.1 e A7-Y.2 — Unidade Regional (Y2:Y4567 e Y4568:Y4588)
- **Colunas:** entrada O (Unidades Regionais). Usada por: R, Z, AA, CRITERIO_UN_REGIONAIS, Planilha1.
- **Fórmula original:**
  - Y.1 (4.566 linhas): `=SEERRO(SE(ESQUERDA(UR;1)="*";EXT.TEXTO(UR;3;PROCURAR("/";UR;PROCURAR("/";UR)+1)-3);ESQUERDA(UR;PROCURAR("/";UR)-1));"")`
  - Y.2 (**últimas 21 linhas**): `=SEERRO(SE(ESQUERDA(UR;1)="*";EXT.TEXTO(UR;3;PROCURAR("/";UR;PROCURAR("/";UR;PROCURAR("/";UR)+1)+1)-3);SE(EXT.TEXTO(UR;PROCURAR("/";UR)+1;PROCURAR("/";UR;PROCURAR("/";UR)+1)-PROCURAR("/";UR)-1)="NUPROC";ESQUERDA(UR;PROCURAR("/";UR;PROCURAR("/";UR;PROCURAR("/";UR)+1)+1)-1);ESQUERDA(UR;PROCURAR("/";UR;PROCURAR("/";UR)+1)-1)));"")`
- **O que faz hoje:**
  - Y.1: devolve **o primeiro segmento** do padrão (ignorando o `*/` inicial).
  - Y.2: devolve **os dois primeiros segmentos**; se o 2º segmento for `NUPROC`, devolve **três**.
- **Comportamentos suspeitos:**
  - **A mesma coluna tem duas fórmulas**: o mesmo padrão dá rótulos diferentes dependendo da linha
    (`DELEMIG/DREX/SR/*` → `DELEMIG` nas primeiras linhas, `DELEMIG/DREX` nas 21 últimas).
  - Rótulo **sem a SR**: `DELEMIG` de todas as 27 SRs viram o mesmo valor.
  - Padrão sem segunda barra (ex.: `SR/*`) dá erro na Y.2 → `SEERRO` devolve `""` → a linha cai em **"ERRO"** na Raiz (A7-R.1).
  - `PA/*/SR/*` (curinga no meio) → rótulo `PA`.
- **Perguntas:**
  - 2.3 O rótulo da Regional deve ser genérico (`DELEMIG`, comparável entre SRs, com a SR em outro campo)
    ou completo (`DELEMIG/DREX/SR/PF/AP`)?
  - 2.4 Qual nível é o certo: 1 segmento (`DELEMIG`) ou 2 (`DELEMIG/DREX`)? E o caso `NUPROC` (`NUPROC/DRPJ`, `CP/NUPROC/DRPJ`)?
  - 2.5 O que é `PA/*/SR/*` e qual rótulo deve ter?
- **Regra pretendida:** _____
- **Exemplos esperados:**

| Unidade Sigla | Padrão (O) | Hoje Y.1 | Hoje Y.2 | Esperado |
|---|---|---|---|---|
| SR/PF/AP | `SR/*` | SR | (vazio → ERRO) | |
| DREX/SR/PF/SC | `DREX/SR/*` | DREX | DREX/SR | |
| UFTI/DELEMIG/DREX/SR/PF/AP | `*/DELEMIG/DREX/SR/*` | DELEMIG | DELEMIG/DREX | |
| NUPROC/DRPJ/SR/PF/RJ | `NUPROC/DRPJ/SR/*` | NUPROC | NUPROC/DRPJ | |
| CP/NUPROC/DRPJ/SR/PF/.. | `CP/NUPROC/DRPJ/SR/*` | CP | CP/NUPROC/DRPJ | |

### A7-AB.1 e A7-AB.2 — Base (AB2:AB4567 e AB4568:AB4588)
- **Colunas:** entrada P (Bases). Usada por: R, CRITERIO_BASES, Planilha1.
- **Fórmula original:**
  - AB.1: `=SEERRO(ESQUERDA(B;PROCURAR("/";B)-1);"")`
  - AB.2 (**últimas 21 linhas**): `=SEERRO(ESQUERDA(B;PROCURAR("/";B;PROCURAR("/";B)+1)-1);"")`
- **O que faz hoje:** AB.1 devolve o 1º segmento do padrão; AB.2 devolve os 2 primeiros.
- **Comportamentos suspeitos:**
  - Duas fórmulas na coluna (mesmo problema da Regional).
  - **`LAFIN-*/DRPJ/SR/*` → rótulo `LAFIN-*`**, com o asterisco literal (aparece assim na aba CRITERIO_BASES).
  - Rótulo sem SR/DPF: todas as `FICCO` (de várias SRs e DPFs) viram `FICCO`.
  - Não há regra para a Base que também casa com um padrão de Regional (ex.: `BABC/DRPJ/SR/*` também casa com `DRPJ/SR/*`): hoje
    depende de qual coluna você preencheu.
- **Perguntas:**
  - 2.6 Rótulo da Base: `FICCO` genérico ou `FICCO/DPF/XXX/UF` / `FICCO/DRPJ/SR/PF/UF`?
  - 2.7 Como deve ficar `LAFIN-*` (ex.: `LAFIN`, ou a sigla real `LAFIN-XX`)?
  - 2.8 Quando uma unidade casar com padrão de Base e de Regional, Base vence sempre?
- **Regra pretendida:** _____
- **Exemplos esperados:**

| Unidade Sigla | Padrão (P) | Hoje AB.1 | Hoje AB.2 | Esperado |
|---|---|---|---|---|
| BABC/DRPJ/SR/PF/.. | `BABC/DRPJ/SR/*` | BABC | BABC/DRPJ | |
| FICCO/DPF/../.. | `FICCO/DPF/*` | FICCO | FICCO/DPF | |
| GIASE/DMA/DRPJ/SR/PF/AM | `GIASE/DMA/DRPJ/SR/*` | GIASE | GIASE/DMA | |
| LAFIN-../DRPJ/SR/PF/.. | `LAFIN-*/DRPJ/SR/*` | LAFIN-* | LAFIN-*/DRPJ | |

### A7-AC.1 — Unidade Descentralizada (AC2:AC4588)
- **Colunas:** entrada Q (Unidades Descentralizadas). Usada por: R, AD, AE, CRITERIO_UN_DESCENTRALIZADAS, Planilha1.
- **Fórmula original:**
  `=SEERRO(SE(ESQUERDA(UD;2)="*/";EXT.TEXTO(UD;3;PROCURAR("/";UD;PROCURAR("/";UD;PROCURAR("/";UD)+1)+1)-3);SE(ESQUERDA(UD;1)="*";EXT.TEXTO(UD;2;PROCURAR("/";UD;PROCURAR("/";UD)+1)-2);SE(ESQUERDA(UD;3)="DPF";ESQUERDA(UD;PROCURAR("/";UD)-1);SE(EXT.TEXTO(UD;PROCURAR("/";UD)+1;PROCURAR("/";UD;PROCURAR("/";UD)+1)-PROCURAR("/";UD)-1)="NUPROC";ESQUERDA(UD;PROCURAR("/";UD;PROCURAR("/";UD;PROCURAR("/";UD)+1)+1)-1);ESQUERDA(UD;PROCURAR("/";UD;PROCURAR("/";UD)+1)-1)))));"")`
- **O que faz hoje** (na ordem):
  1. começa com `*/` → os 2 segmentos depois do `*/` (`*/NUPROC/DPF/*` → `NUPROC/DPF`);
  2. começa com `*` → do 2º caractere até a 2ª barra (`*CPD/DPF/*` → `CPD/DPF`);
  3. começa com `DPF` → 1º segmento (`DPF/*` → `DPF`);
  4. 2º segmento é `NUPROC` → 3 primeiros segmentos;
  5. senão → 2 primeiros segmentos (`ACOLHIDA/DPF/*` → `ACOLHIDA/DPF`).
- **Comportamentos suspeitos:**
  - Quando a subunidade fica dentro da DELEX, o rótulo **perde o `DPF`**: `CANIL/DELEX/DPF/*` → `CANIL/DELEX`,
    mas `CANIL/DPF/*` → `CANIL/DPF`. Assim o mesmo tipo de unidade sai com dois rótulos (`CANIL/DELEX` × `CANIL/DPF`,
    `UID/DELEX` × `UID/DPF`, `GCAP/DELEX` × `GCAP/DPF`).
  - Teste `ESQUERDA(UD;3)="DPF"` por posição fixa.
  - Padrão digitado com barra sobrando: `PLANTÃO/DELEX/DPF/*/`.
  - 4 níveis de SE aninhados + `SEERRO`: qualquer padrão fora desses formatos vira `""` e a linha cai em "ERRO" na Raiz.
- **Perguntas:**
  - 2.9 `CANIL/DELEX` e `CANIL/DPF` devem ser o mesmo rótulo (ex.: `CANIL/DPF`) ou rótulos diferentes?
  - 2.10 O rótulo deve ser genérico (`ACOLHIDA/DPF`, comparável entre delegacias) ou conter a delegacia (`ACOLHIDA/DPF/PAC/RR`)?
  - 2.11 `PLANTÃO/DELEX/DPF/*/` (barra no fim) é erro de digitação?
- **Regra pretendida:** _____
- **Exemplos esperados:**

| Unidade Sigla | Padrão (Q) | Valor hoje | Esperado |
|---|---|---|---|
| ACOLHIDA/DPF/PAC/RR | `ACOLHIDA/DPF/*` | ACOLHIDA/DPF | |
| CANIL/DELEX/DPF/FIG/PR | `CANIL/DELEX/DPF/*` | CANIL/DELEX | |
| 1ªCPD/DPF/../.. | `*CPD/DPF/*` | CPD/DPF | |
| UA/NUPROC/DPF/../.. | `*/NUPROC/DPF/*` | NUPROC/DPF | |
| DPF/JPN/RO | `DPF/*` | DPF | |
| NO/DPF/IJI/SC | `NO/DPF/*` | NO/DPF | |

### A7-S.1 — Unidade com Subunidades (S2:S4588)
- **Colunas:** C (Unidade Sigla), N, O, P, Q. Usada no 0720 para os campos `Unidade ... com Subunidades`.
- **Fórmula original:**
```
=LET(
 sigla; [Unidade Sigla];
 padrao; SE(UC<>"";UC;SE(UR<>"";UR;SE(B<>"";B;SE(UD<>"";UD;""))));
 col_desc; UD<>"";
 delex_pos; SEERRO(PROCURAR("/DELEX/";sigla);0);
 dpj_pos;   SEERRO(PROCURAR("/DPJ/";sigla);0);
 dpf_pos;   SEERRO(PROCURAR("/DPF/";sigla);0);
 nome_desc; SE(delex_pos>0; EXT.TEXTO(sigla;delex_pos+1;NÚM.CARACT(sigla));
            SE(dpj_pos>0;   EXT.TEXTO(sigla;dpj_pos+1;NÚM.CARACT(sigla));
            SE(dpf_pos>0;   EXT.TEXTO(sigla;dpf_pos+1;NÚM.CARACT(sigla)); sigla)));
 starts_star; ESQUERDA(padrao;1)="*";
 ends_star;   DIREITA(padrao;1)="*";
 ancora; SE(starts_star; EXT.TEXTO(padrao;3;SEERRO(PROCURAR("/";padrao;3);NÚM.CARACT(padrao)+1)-3);
                         ESQUERDA(padrao;SEERRO(PROCURAR("/";padrao);NÚM.CARACT(padrao)+1)-1));
 pos_ancora; SEERRO(PROCURAR(ancora;sigla);0);
 nome_geral; SE(padrao=""; nome_desc;
             SE(starts_star;
                SE(ends_star; SE(pos_ancora>0; EXT.TEXTO(sigla;pos_ancora;NÚM.CARACT(sigla)); sigla);
                              EXT.TEXTO(padrao;3;NÚM.CARACT(padrao)));
                SE(ends_star; SE(pos_ancora>0; EXT.TEXTO(sigla;pos_ancora;NÚM.CARACT(sigla)); sigla);
                              sigla)));
 SE(col_desc; nome_desc; nome_geral))
```
- **O que faz hoje:** devolve a **unidade "mãe"** (sigla completa, com SR/UF), ou seja, a unidade que contém as subunidades:
  - Descentralizadas: corta a sigla a partir do primeiro `/DELEX/`, senão do `/DPJ/`, senão do `/DPF/` (`NO/DPF/IJI/SC` → `DPF/IJI/SC`;
    `CANIL/DELEX/DPF/FIG/PR` → `DELEX/DPF/FIG/PR`).
  - Demais: pega a "âncora" (1º segmento do padrão, sem `*/`) e corta a sigla a partir dela
    (`*/DELEMIG/DREX/SR/*` em `UFTI/DELEMIG/DREX/SR/PF/AP` → `DELEMIG/DREX/SR/PF/AP`);
    padrão `*/X` sem `*` no fim → o texto do padrão sem `*/` (`*/GAB/PF` → `GAB/PF`); padrão sem curinga → a própria sigla.
- **Comportamentos suspeitos:**
  - A âncora é procurada como **pedaço de texto**, não como segmento entre barras: a âncora `COR` também é encontrada dentro de `DELECOR`,
    e `DRE` dentro de `DREX`. A sigla pode ser cortada no lugar errado.
  - **Âncora com curinga** (`LAFIN-*`) nunca é encontrada → devolve a sigla inteira.
  - Para Descentralizadas, a regra é diferente da usada no rótulo (A7-AC.1): aqui DELEX é a mãe de `CANIL/DELEX/...`; lá o rótulo é `CANIL/DELEX`.
  - Vários `SEERRO` escondem erros.
- **Perguntas:**
  - 2.12 A "Unidade com Subunidades" deve ser sempre a unidade **acima** na hierarquia real (um dos `Unidade Sigla1..6`), ou seja, a que o padrão
    agrupa? Se sim, o script pode usar a hierarquia da DIM_UNIDADE em vez de cortar texto.
  - 2.13 Nas descentralizadas, a mãe de uma subunidade da DELEX é a DELEX (`DELEX/DPF/FIG/PR`) ou a delegacia (`DPF/FIG/PR`)?
- **Regra pretendida:** _____
- **Exemplos esperados:**

| Unidade Sigla | Padrão | Valor hoje | Esperado |
|---|---|---|---|
| SESIN/DSEG/GAB/PF | `*/GAB/PF` | GAB/PF | |
| UFTI/DELEMIG/DREX/SR/PF/AP | `*/DELEMIG/DREX/SR/*` | DELEMIG/DREX/SR/PF/AP | |
| COR/SR/PF/AP | `COR/SR/*` | COR/SR/PF/AP | |
| NO/DPF/IJI/SC | `NO/DPF/*` | DPF/IJI/SC | |
| CANIL/DELEX/DPF/FIG/PR | `CANIL/DELEX/DPF/*` | DELEX/DPF/FIG/PR | |
| DPF/IJI/SC | `DPF/*` | DPF/IJI/SC | |

---

## 3. Campos derivados

### A7-R.1 — Unidade Sigla Raiz (R2:R3, R5:R4588)
- **Colunas:** V, Y, AB, AC. Usada por: T.
- **Fórmula original:** `=SE([Unidade Central]<>"";[Unidade Central];SE([Unidade Regional]<>"";[Unidade Regional];SE([Base]<>"";[Base];SE([Unidade Descentralizada]<>"";[Unidade Descentralizada];"ERRO"))))`
- **O que faz hoje:** o primeiro rótulo preenchido, na ordem Central → Regional → Base → Descentralizada; nenhum → `"ERRO"`.
- **Comportamentos suspeitos:**
  - `"ERRO"` vira valor de dimensão no app.
  - Uma Base que também tenha Regional preenchida sai como Regional (a ordem coloca Regional antes de Base).
  - **R4 tem `PF` digitado.**
- **Perguntas:**
  - 3.1 Quantas linhas mostram `ERRO` hoje? No script, unidade sem regra deve virar o quê: vazio, `Sem classificação`, ou só sair num relatório de exceções?
  - 3.2 A ordem de prioridade (Central > Regional > Base > Descentralizada) está certa?
- **Regra pretendida:** _____
- **Exemplos esperados:** _____

### A7-W.1, A7-X.1, A7-Z.1, A7-AA.1, A7-AD.1, A7-AE.1 — versões Investigativa / Não Investigativa
| ID | Coluna | Campo | Fórmula |
|---|---|---|---|
| A7-W.1 | W | Unidade Central Investigativa | `=SE([PJ/NPJ]="PJ";[Unidade Central];"")` |
| A7-X.1 | X | Unidade Central Não Investigativa | `=SE([PJ/NPJ]="NPJ";[Unidade Central];"")` |
| A7-Z.1 | Z | Unidade Regional Investigativa | `=SE([PJ/NPJ]="PJ";[Unidade Regional];"")` |
| A7-AA.1 | AA | Unidade Regional Não Investigativa | `=SE([PJ/NPJ]="NPJ";[Unidade Regional];"")` |
| A7-AD.1 | AD | Unidade Descentralizada Investigativa | `=SE([PJ/NPJ]="PJ";[Unidade Descentralizada];"")` — **só até AD4400** |
| A7-AE.1 | AE | Unidade Descentralizada Não Investigativa | `=SE([PJ/NPJ]="NPJ";[Unidade Descentralizada];"")` |

- **O que faz hoje:** copia o rótulo da categoria quando PJ/NPJ é o valor indicado.
- **Comportamentos suspeitos:**
  - **AD só tem fórmula até a linha 4400**; as linhas 4401–4588 (188 linhas) ficam sem "Descentralizada Investigativa", mesmo sendo PJ.
  - Não existe versão Investigativa/Não Investigativa para **Base** (no 0720 a Base aparece inteira em `Unidade PJ/NPJ`).
- **Perguntas:**
  - 3.3 PJ/NPJ é característica **da unidade** ou **do padrão**? (ver 5.1)
  - 3.4 Base precisa da divisão PJ/NPJ?
- **Regra pretendida:** _____
- **Exemplos esperados:** _____

### A7-T.1 — Unidade Sigla Unificada (T2:T3, T5:T4588)
- **Colunas:** R (Raiz), G (Unidade Sigla3). Usada por: U.
- **Fórmula original:** `=SE(OU(DIREITA([Unidade Sigla Raiz];4)="/DPF";DIREITA([Unidade Sigla Raiz];6)="/DELEX";DIREITA([Unidade Sigla Raiz];3)="DPF";DIREITA([Unidade Sigla Raiz];4)="/PRS";DIREITA([Unidade Sigla Raiz];4)="/DPJ");[Unidade Sigla3];[Unidade Sigla Raiz])`
- **O que faz hoje:** se a Raiz termina em `/DPF`, `/DELEX`, `DPF`, `/PRS` ou `/DPJ`, troca pela `Unidade Sigla3` (a delegacia, ex.: `DPF/FIG/PR`); senão mantém a Raiz.
  Na prática, toda Descentralizada vira a sua delegacia, e Centrais, Regionais e Bases ficam com o rótulo.
- **Comportamentos suspeitos:**
  - Depende de **como o rótulo terminou** (efeito do recorte da seção 2), não da categoria. Ex.: `NUPROC/DRPJ` (Regional) não é trocado; `CANIL/DELEX` é.
  - `DIREITA(...;3)="DPF"` já cobre `/DPF`; `/PRS` não aparece em nenhum rótulo conhecido.
  - Usa `Unidade Sigla3` fixo: só funciona se a delegacia estiver sempre no 3º nível.
  - Regionais ficam **sem SR** (`DELEMIG` de todas as SRs juntas); Bases sem SR/DPF (`FICCO`).
  - **T4 tem `GAB/PF` digitado** (linha da unidade `PF`?): a unidade PF unificada como GAB/PF.
- **Perguntas:**
  - 3.5 Para que serve a "Sigla Unificada"? A regra é "Descentralizada → sua delegacia; demais → rótulo"?
  - 3.6 Regionais e Bases deviam levar a SR/UF na Sigla Unificada?
  - 3.7 O que é `/PRS` e `/DPJ` aqui?
  - 3.8 `PF` → `GAB/PF` (T4) é intencional?
- **Regra pretendida:** _____
- **Exemplos esperados:**

| Unidade Sigla | Raiz hoje | Unificada hoje | Esperado |
|---|---|---|---|
| CANIL/DELEX/DPF/FIG/PR | CANIL/DELEX | DPF/FIG/PR | |
| NO/DPF/IJI/SC | NO/DPF | DPF/IJI/SC | |
| UFTI/DELEMIG/DREX/SR/PF/AP | DELEMIG | DELEMIG | |
| FICCO/DPF/../.. | FICCO | FICCO | |
| SESIN/DSEG/GAB/PF | GAB/PF | GAB/PF | |

### A7-U.1 — Unidade Sigla Abrangência Unificada (U2:U4588, com exceções)
- **Colunas:** T. 
- **Fórmula original:** `=SEERRO(SE(ESQUERDA([Unidade Sigla Unificada];4)="DPF/";"DPF";[Unidade Sigla Unificada]);"")`
- **O que faz hoje:** toda delegacia (`DPF/...`) vira `"DPF"`; o resto fica igual à Sigla Unificada.
- **Comportamentos suspeitos:**
  - **4 células com `DPF` digitado** (U1233, U1238, U1464, U1466) no lugar da fórmula.
  - Uma única coluna mistura Centrais (`GAB/PF`), Regionais genéricas (`DELEMIG`), Bases (`FICCO`) e `DPF`.
- **Perguntas:**
  - 3.9 Qual o uso no app? É para comparar "todas as delegacias" × cada Central/Regional/Base?
  - 3.10 As 4 células digitadas dariam outro valor pela fórmula? Qual está certo?
- **Regra pretendida:** _____
- **Exemplos esperados:** _____

### A7-AF.1 e A7-AF.2 — Hierarquia Administrativa (AF)
- **Colunas:** F (Unidade Sigla2) ou D (Unidade Sigla Superior).
- **Fórmula original:** AF.1 (3.695 células): `=[Unidade Sigla2]`; AF.2 (25 células): `=[Unidade Sigla Superior]`.
- **O que faz hoje:** quase sempre a unidade de 2º nível (a SR ou a Diretoria); em 25 linhas, a unidade imediatamente superior.
  **679 células têm valor digitado** (ex.: `GAB/PF`, `PF`, `DTI/PF`), e cerca de 188 ficam sem nada.
- **Perguntas:**
  - 3.11 Qual é a regra: "SR ou Diretoria da unidade" (= `Unidade Sigla2`)? Quais são as exceções e por quê (as 25 com Sigla Superior, as 679 digitadas)?
- **Regra pretendida:** _____
- **Exemplos esperados:** _____

### Hierarquia Técnica (AG) — sem regra
- Sem fórmula. Ver pergunta 0.2.
- **Regra pretendida:** _____

### Campos calculados no tra 0720 (para referência)
O 0720 calcula a partir da planilha: `É Unidade Central/Regional/Base/Descentralizada` (coluna de padrão preenchida?),
`Unidade ... com Subunidades` (S, por categoria), `PJ/NPJ` (vazio → `DESCONHECIDO`), `Unidade Abrangência` e `Unidade PJ/NPJ`
(primeiro rótulo não nulo, testado com `IsNull`).
- **Comportamento suspeito:** uma célula do Excel com fórmula que devolve `""` pode chegar ao Qlik como texto vazio, e não como nulo. Nesse caso
  `NOT IsNull([Unidade Central])` é verdadeiro em todas as linhas e `Unidade Abrangência` sai `Unidade Central` para todas.
- **Pergunta:** 3.12 No app, o campo `Unidade Abrangência` mostra só `Unidade Central`, ou mostra as quatro categorias?

---

## 4. Abas auxiliares

### A14-A.1 … A17-F.1 — abas WILDMATCH_* (listas de padrões)
- **O que fazem hoje:** `=ÚNICO(FILTRO(HIERARQUIA_TECNICA_PF!N2:N4149; ...<>""))` (e versões com `AH="PJ"`/`"NPJ"`). Listam os padrões distintos
  por categoria e PJ/NPJ. Ao lado, `=""''""&A2&""'',""` monta o texto `''padrão'',` para colar numa lista do `WildMatch` no Qlik.
- **Comportamentos suspeitos:**
  - **Intervalo fixo até a linha 4149**: a tabela vai até 4588, então **439 linhas (4150–4588) ficam de fora** das listas.
  - As colunas E/F/G têm tamanho fixo (ex.: E2:E141) e não acompanham o tamanho da lista: sobra linha com `''0'',` ou falta padrão novo.
  - Há **padrões nas duas listas, PJ e NPJ**, ao mesmo tempo: `DELEX/DPF/*` e `GCAP/DPF/*` (Descentralizadas).
- **Pergunta:** 4.1 Onde essas listas são coladas hoje? (No repositório só achei `WildMatch` com listas digitadas em `tra/07_dimensoes/0721_DIM_HIERARQUIA_UNIDADE_SIGLA_DO_CASO.qvs`.)

### A18-A.1 … A21-C.1 — abas CRITERIO_* (listas de rótulos)
- **O que fazem hoje:** `=ÚNICO(FILTRO(HIERARQUIA_TECNICA_PF!V2:V4149; ...))`: listam os rótulos calculados (V, Y, AB, AC) por PJ/NPJ.
- **Comportamentos suspeitos:**
  - Mesmo intervalo fixo até 4149.
  - Mostram as falhas da seção 2: o rótulo `LAFIN-*`; `NUPROC` e `NUPROC/DRPJ` lado a lado; `DELEX/DPF` e `GCAP/DPF` nas duas listas (PJ e NPJ);
    `CANIL/DELEX` × `CANIL/DPF`.
- **Pergunta:** 4.2 Essas abas são só conferência, ou alguma é usada em outro lugar?

### A13-C.1 (Planilha1), A8-B.1/A8-B.2 (Planilha5), A9-E.1 (Planilha6) — rascunhos
- Planilha1 (Tabela4): repete a fórmula da Raiz (A7-R.1) para 4.360 linhas (C56 com `PF` digitado).
- Planilha5: `=SEERRO(SUBSTITUIR(A2;"/PF/*";"/*");"")` (e `"/DPF/*/*"` → `"/DPF/*"` em 12 linhas) sobre a lista de Bases.
- Planilha6: `=SEERRO(SUBSTITUIR(D1;"/*/*";"/*");"")` sobre a lista de Descentralizadas.
- Parecem migração antiga de padrões (`.../SR/PF/*` → `.../SR/*`; `.../DPF/*/*` → `.../DPF/*`).
- Abas sem fórmula: `vUnidadesCentrais`, `vUnidadesRegionais`, `vBases`, `vUnidadesDescentralizadas`, `Testes`, `Planilha2` (Tabela3: lista de
  Sigla Unificada), `Planilha3` (Tabela2: `UNIDADE RAIS`), `Planilha4`.
- **Pergunta:** 4.3 Alguma dessas abas ainda é usada? Se não, podem ser ignoradas na reimplementação.

---

## 5. Perguntas gerais

- **5.1 PJ/NPJ:** a classificação é por unidade ou por padrão? Nas listas, quase todo padrão tem um só valor, mas `DELEX/DPF/*` e `GCAP/DPF/*`
  aparecem como PJ e como NPJ. Se for por padrão, esses dois precisam ser separados (ex.: `GCAP/DPF/*` PJ e `GCAP/DELEX/DPF/*` NPJ?).
  Se for por unidade, quais exceções existem?
- **5.2 Dois padrões que casam com a mesma unidade:** o script vai aplicar todos os padrões a todas as unidades. Quando mais de um casar
  (ex.: `DRPJ/SR/*` e `BABC/DRPJ/SR/*`), vence o **mais específico** (mais caracteres sem curinga)? Ou precisa de uma prioridade explícita?
- **5.3 Curinga no WildMatch:** no Qlik, `*` casa com qualquer texto, inclusive com barras (`*/GAB/PF` casa com `A/B/C/GAB/PF`). É isso que você quer?
- **5.4 Unidade nova sem padrão:** deve ficar visível no app (`Sem classificação`) ou só num CSV de exceções para você classificar?
- **5.5 Relação com o 0721:** o `tra 0721` classifica a **unidade do caso** com outras listas `WildMatch` (Órgãos Centrais/Regionais, Delegacias
  Especializadas/Descentralizadas, Base). As duas classificações devem usar a mesma tabela de regras?
- **5.6 Onde fica a tabela de regras:** numa aba nova da mesma planilha ou num arquivo novo?
- **5.7 Correção a uma hipótese anterior:** no plano, escrevi que o PJ/NPJ depende só do padrão. As listas WILDMATCH mostram duas exceções (5.1),
  e essas listas só cobrem até a linha 4149. A hipótese precisa ser confirmada com a aba inteira.
