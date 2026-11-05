#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrair_formulas_excel.py
-------------------------
Inventario das regras de negocio de uma planilha Excel (ex.: HIERARQUIA_TECNICA_PF_v8.xlsx),
para reimplementa-las em script de carga Qlik.

Gera em docs/ (separador ';', UTF-8 com BOM, abre direto no Excel PT-BR):

  inventario_formulas.csv  -> uma linha por item:
        ABA, ABA_OCULTA, NOME_DEFINIDO, TABELA, VALIDACAO_DADOS, FORMATACAO_CONDICIONAL,
        COLUNAS_OCULTAS, LINHAS_OCULTAS, LINK_EXTERNO e FORMULA (uma por celula).
  inventario_regras.csv    -> formulas repetidas agrupadas em regras unicas
        (mesma aba + mesma coluna + mesma formula em notacao R1C1), colunas de entrada
        (sem formula) usadas pelas regras, dependencias e ordem de calculo.

Alertas automaticos (coluna "alertas"):
  PROCV_APROXIMADO, PROC_APROXIMADO, CORRESP_APROXIMADO, PROCX_APROXIMADO, PROCX_CURINGA,
  PROCX_SE_NAO_ENCONTRADO, SEERRO, TESTE_DE_ERRO, DATA_DO_DIA, VOLATIL, INTERVALO_FIXO,
  INTERVALO_INCOMPLETO, INTERVALO_DESLIZANTE, COLUNA_INTEIRA, INDICE_COLUNA_FIXO,
  POSICAO_FIXA, OCORRENCIA_FIXA, TEXTO_DIGITADO, NUMERO_DIGITADO, CURINGA_LITERAL,
  SE_ANINHADO, REF_OUTRA_ABA, AUTORREFERENCIA_COLUNA, REFERENCIA_EXTERNA, ERRO_REF,
  MATRICIAL, MATRIZ_DINAMICA, NAO_TOKENIZADA.
  Nas regras: VARIANTES_NA_COLUNA, CONSTANTES_NA_COLUNA, RESULTADO_COM_ERRO, CICLO.

Uso:
  python -m pip install openpyxl
  python scripts/extrair_formulas_excel.py "S:\\BI_NGE_ESTATISTICAS\\HIERARQUIA_TECNICA_PF_v8.xlsx"
  python scripts/extrair_formulas_excel.py ARQUIVO.xlsx --saida docs --linha-cabecalho 1

Somente leitura: o arquivo Excel nao e alterado.
"""

import argparse
import csv
import datetime as dt
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from openpyxl import load_workbook
    from openpyxl.formula.tokenizer import Token, Tokenizer
    from openpyxl.utils import column_index_from_string, get_column_letter
except ImportError:
    sys.exit("openpyxl nao encontrado. Instale com:  python -m pip install openpyxl")

try:
    from openpyxl.worksheet.formula import ArrayFormula
except ImportError:  # versoes antigas do openpyxl
    ArrayFormula = None


# --------------------------------------------------------------------------------------
# Nomes das funcoes em portugues (Excel PT-BR), so para leitura
# --------------------------------------------------------------------------------------
PT = {
    "IF": "SE", "IFS": "SES", "IFERROR": "SEERRO", "IFNA": "SENÃODISP", "AND": "E", "OR": "OU",
    "NOT": "NÃO", "XOR": "OUEXCL", "SWITCH": "PARÂMETRO", "CHOOSE": "ESCOLHER",
    "VLOOKUP": "PROCV", "HLOOKUP": "PROCH", "LOOKUP": "PROC", "XLOOKUP": "PROCX",
    "MATCH": "CORRESP", "XMATCH": "CORRESPX", "INDEX": "ÍNDICE", "INDIRECT": "INDIRETO",
    "OFFSET": "DESLOC", "ROW": "LIN", "COLUMN": "COL", "ROWS": "LINS", "COLUMNS": "COLS",
    "MID": "EXT.TEXTO", "LEFT": "ESQUERDA", "RIGHT": "DIREITA", "LEN": "NÚM.CARACT",
    "FIND": "PROCURAR", "SEARCH": "LOCALIZAR", "SUBSTITUTE": "SUBSTITUIR", "REPLACE": "MUDAR",
    "TRIM": "ARRUMAR", "CLEAN": "TIRAR", "UPPER": "MAIÚSCULA", "LOWER": "MINÚSCULA",
    "PROPER": "PRI.MAIÚSCULA", "CONCATENATE": "CONCATENAR", "CONCAT": "CONCAT",
    "TEXTJOIN": "UNIRTEXTO", "TEXTBEFORE": "TEXTOANTES", "TEXTAFTER": "TEXTODEPOIS",
    "TEXTSPLIT": "DIVIDIRTEXTO", "REPT": "REPT", "EXACT": "EXATO", "TEXT": "TEXTO",
    "VALUE": "VALOR", "CHAR": "CARACT", "CODE": "CÓDIGO",
    "ISERROR": "ÉERROS", "ISERR": "ÉERRO", "ISNA": "É.NÃO.DISP", "ISBLANK": "ÉCÉL.VAZIA",
    "ISNUMBER": "ÉNÚM", "ISTEXT": "ÉTEXTO", "ISLOGICAL": "ÉLÓGICO",
    "COUNTIF": "CONT.SE", "COUNTIFS": "CONT.SES", "COUNTA": "CONT.VALORES", "COUNT": "CONT.NÚM",
    "COUNTBLANK": "CONTAR.VAZIO", "SUMIF": "SOMASE", "SUMIFS": "SOMASES", "SUM": "SOMA",
    "SUMPRODUCT": "SOMARPRODUTO", "MAX": "MÁXIMO", "MIN": "MÍNIMO", "MAXIFS": "MÁXIMOSES",
    "MINIFS": "MÍNIMOSES", "LARGE": "MAIOR", "SMALL": "MENOR", "AGGREGATE": "AGREGAR",
    "TODAY": "HOJE", "NOW": "AGORA", "RAND": "ALEATÓRIO", "RANDBETWEEN": "ALEATÓRIOENTRE",
    "CELL": "CÉL", "INFO": "INFORMAÇÃO", "FILTER": "FILTRO", "UNIQUE": "ÚNICO",
    "SORT": "CLASSIFICAR", "SORTBY": "CLASSIFICARPOR", "SEQUENCE": "SEQUÊNCIA",
    "TAKE": "PEGAR", "DROP": "DESCARTAR", "CHOOSECOLS": "ESCOLHERCOLS",
    "CHOOSEROWS": "ESCOLHERLINS", "LET": "LET", "LAMBDA": "LAMBDA", "MAP": "MAP",
    "REDUCE": "REDUCE", "BYROW": "BYROW",
}
LOGICO_PT = {"TRUE": "VERDADEIRO", "FALSE": "FALSO"}
ERRO_PT = {"#N/A": "#N/D", "#VALUE!": "#VALOR!", "#NAME?": "#NOME?", "#REF!": "#REF!",
           "#DIV/0!": "#DIV/0!", "#NUM!": "#NÚM!", "#NULL!": "#NULO!", "#SPILL!": "#DESPEJAR!",
           "#CALC!": "#CALC!"}
ERROS_EXCEL = set(ERRO_PT) | {"#GETTING_DATA"}

FUNCOES_VOLATEIS = {"INDIRECT", "OFFSET", "CELL", "INFO", "RAND", "RANDBETWEEN"}
FUNCOES_MATRIZ_DINAMICA = {"FILTER", "UNIQUE", "SORT", "SORTBY", "SEQUENCE", "TEXTSPLIT",
                           "TAKE", "DROP", "CHOOSECOLS", "CHOOSEROWS", "MAP", "BYROW"}

RE_CEL = re.compile(r"^(\$?)([A-Za-z]{1,3})(\$?)(\d+)$")
RE_COL = re.compile(r"^(\$?)([A-Za-z]{1,3})$")
RE_LIN = re.compile(r"^(\$?)(\d+)$")
MAX_COLUNAS_EXPANDIDAS = 200


# --------------------------------------------------------------------------------------
# Utilitarios
# --------------------------------------------------------------------------------------
def texto(v):
    if v is None:
        return ""
    if isinstance(v, (dt.datetime, dt.date, dt.time)):
        return v.isoformat()
    return str(v)


def nome_funcao(valor_token):
    v = valor_token[:-1] if valor_token.endswith("(") else valor_token
    for prefixo in ("_xlfn._xlws.", "_xlfn.", "_xlws."):
        if v.lower().startswith(prefixo.lower()):
            v = v[len(prefixo):]
    return v.upper()


def nome_pt(nome):
    return PT.get(nome, nome)


def comprimir_linhas(linhas, letra, limite=12):
    """[2,3,4,7,8] -> 'R2:R4, R7:R8'."""
    if not linhas:
        return ""
    linhas = sorted(set(linhas))
    blocos, ini, ant = [], linhas[0], linhas[0]
    for l in linhas[1:]:
        if l == ant + 1:
            ant = l
            continue
        blocos.append((ini, ant))
        ini = ant = l
    blocos.append((ini, ant))
    partes = [f"{letra}{a}" if a == b else f"{letra}{a}:{letra}{b}" for a, b in blocos]
    if len(partes) > limite:
        return ", ".join(partes[:limite]) + f", ... (+{len(partes) - limite} blocos)"
    return ", ".join(partes)


def celulas(ws):
    """Itera so as celulas existentes (evita varrer 1 milhao de linhas formatadas)."""
    mapa = getattr(ws, "_cells", None)
    if mapa is not None:
        for (_, _), c in sorted(mapa.items()):
            yield c
    else:
        for linha in ws.iter_rows():
            for c in linha:
                yield c


def texto_formula(cel):
    """Devolve (texto da formula, eh_matricial, ref_matricial) ou (None, False, '')."""
    v = cel.value
    if ArrayFormula is not None and isinstance(v, ArrayFormula):
        return (v.text or ""), True, getattr(v, "ref", "") or ""
    if isinstance(v, str) and v.startswith("=") and cel.data_type == "f":
        return v, False, ""
    return None, False, ""


# --------------------------------------------------------------------------------------
# Referencias
# --------------------------------------------------------------------------------------
def separar_aba(valor):
    """"'Aba X'!$A$1" -> ("'Aba X'", "Aba X", "$A$1")."""
    if "!" in valor:
        i = valor.rfind("!")
        bruto, endereco = valor[:i], valor[i + 1:]
        limpo = bruto
        if limpo.startswith("'") and limpo.endswith("'"):
            limpo = limpo[1:-1].replace("''", "'")
        return bruto, limpo, endereco
    return "", None, valor


def _cel_r1c1(m, lin0, col0):
    cabs, col, labs, lin = m.groups()
    c, l = column_index_from_string(col.upper()), int(lin)
    rs = f"R{l}" if labs else f"R[{l - lin0}]"
    cs = f"C{c}" if cabs else f"C[{c - col0}]"
    return rs + cs, c, l, bool(labs)


def converter_ref(valor, lin0, col0, aba_atual, ctx):
    """Converte uma referencia A1 para R1C1 relativa a (lin0, col0) e descreve o que ela aponta."""
    bruto, aba, end = separar_aba(valor)
    prefixo = (bruto + "!") if bruto else ""
    info = {"original": valor, "aba": ctx["abas_canon"].get((aba or aba_atual).upper(), aba or aba_atual),
            "tipo": "nome", "c1": None, "c2": None, "l1": None, "l2": None,
            "abs_linhas": False, "externo": False, "nome": None, "tabela": None, "colunas_tab": []}
    if valor.startswith("[") and re.match(r"^\[\d+\]", valor) or (aba and aba.startswith("[")):
        info["externo"] = True
        info["tipo"] = "externa"
        return valor, info

    if "[" in end:  # referencia estruturada de tabela: Tabela1[Coluna], [@Coluna]
        info["tipo"] = "estruturada"
        info["tabela"] = end.split("[", 1)[0] or None
        cols = [c.lstrip("@") for c in re.findall(r"\[([^\[\]]+)\]", end)]
        info["colunas_tab"] = [c for c in cols if c and not c.startswith("#")]
        return valor, info

    partes = end.split(":")
    if len(partes) == 1:
        m = RE_CEL.match(end)
        if m:
            r, c, l, la = _cel_r1c1(m, lin0, col0)
            info.update(tipo="celula", c1=c, c2=c, l1=l, l2=l, abs_linhas=la)
            return prefixo + r, info
    elif len(partes) == 2:
        m1, m2 = RE_CEL.match(partes[0]), RE_CEL.match(partes[1])
        if m1 and m2:
            r1, c1, l1, a1 = _cel_r1c1(m1, lin0, col0)
            r2, c2, l2, a2 = _cel_r1c1(m2, lin0, col0)
            info.update(tipo="intervalo", c1=min(c1, c2), c2=max(c1, c2), l1=min(l1, l2),
                        l2=max(l1, l2), abs_linhas=(a1 and a2))
            return f"{prefixo}{r1}:{r2}", info
        k1, k2 = RE_COL.match(partes[0]), RE_COL.match(partes[1])
        if k1 and k2:
            c1 = column_index_from_string(k1.group(2).upper())
            c2 = column_index_from_string(k2.group(2).upper())
            s1 = f"C{c1}" if k1.group(1) else f"C[{c1 - col0}]"
            s2 = f"C{c2}" if k2.group(1) else f"C[{c2 - col0}]"
            info.update(tipo="colunas", c1=min(c1, c2), c2=max(c1, c2))
            return f"{prefixo}{s1}:{s2}", info
        j1, j2 = RE_LIN.match(partes[0]), RE_LIN.match(partes[1])
        if j1 and j2:
            l1, l2 = int(j1.group(2)), int(j2.group(2))
            s1 = f"R{l1}" if j1.group(1) else f"R[{l1 - lin0}]"
            s2 = f"R{l2}" if j2.group(1) else f"R[{l2 - lin0}]"
            info.update(tipo="linhas", l1=min(l1, l2), l2=max(l1, l2))
            return f"{prefixo}{s1}:{s2}", info

    info["nome"] = end.replace("_xlpm.", "")
    return valor.replace("_xlpm.", ""), info


def colunas_de(info, ctx, profundidade=0):
    """Lista de (aba, indice_coluna) apontados por uma referencia."""
    if profundidade > 5:
        return []
    t = info["tipo"]
    if t in ("celula", "intervalo", "colunas"):
        c2 = min(info["c2"], info["c1"] + MAX_COLUNAS_EXPANDIDAS - 1)
        return [(info["aba"], c) for c in range(info["c1"], c2 + 1)]
    if t == "nome" and info["nome"]:
        saida = []
        for aba_dest, ref in ctx["nomes_dest"].get(info["nome"].upper(), []):
            _, sub = converter_ref(f"'{aba_dest}'!{ref}", 1, 1, aba_dest, ctx)
            saida += colunas_de(sub, ctx, profundidade + 1)
        return saida
    if t == "estruturada":
        tab = None
        if info["tabela"]:
            tab = ctx["tabelas"].get(info["tabela"].upper())
        else:
            tab = ctx["tabela_da_celula"]
        if not tab:
            return []
        saida = []
        for nome_col in info["colunas_tab"]:
            if nome_col.upper() in tab["colunas"]:
                saida.append((tab["aba"], tab["col_ini"] + tab["colunas"][nome_col.upper()]))
        return saida
    return []


# --------------------------------------------------------------------------------------
# Analise de uma formula
# --------------------------------------------------------------------------------------
def tokens_da_formula(formula):
    try:
        return Tokenizer(formula if formula.startswith("=") else "=" + formula).items, None
    except Exception as e:  # noqa: BLE001
        return [], str(e)


def chamadas_de_funcao(tokens):
    """Lista de chamadas {nome, args[str], prof_se} com os argumentos como texto."""
    pilha, chamadas = [], []
    abre = (Token.FUNC, Token.ARRAY, Token.PAREN)
    for t in tokens:
        if t.type in abre and t.subtype == Token.OPEN:
            for f in pilha:
                f["args"][-1].append(t.value)
            nome = nome_funcao(t.value) if t.type == Token.FUNC else t.type
            prof_se = sum(1 for f in pilha if f["nome"] in ("IF", "IFS")) + (1 if nome in ("IF", "IFS") else 0)
            pilha.append({"nome": nome, "func": t.type == Token.FUNC, "args": [[]], "prof_se": prof_se})
        elif t.type in abre and t.subtype == Token.CLOSE:
            if pilha:
                f = pilha.pop()
                if f["func"]:
                    chamadas.append({"nome": f["nome"], "args": ["".join(a).strip() for a in f["args"]],
                                     "prof_se": f["prof_se"]})
            for f in pilha:
                f["args"][-1].append(t.value)
        elif t.type == Token.SEP and t.subtype == Token.ARG and pilha:
            pilha[-1]["args"].append([])
            for f in pilha[:-1]:
                f["args"][-1].append(t.value)
        else:
            for f in pilha:
                f["args"][-1].append(t.value)
    return chamadas


def analisar_formula(formula, lin0, col0, aba_atual, ctx):
    tokens, erro = tokens_da_formula(formula)
    res = {"pt": formula, "r1c1": formula, "refs": [], "alertas": [], "chamadas": []}
    if erro:
        res["alertas"].append(("NAO_TOKENIZADA", erro))
        return res

    r1c1, pt, pilha = [], [], []
    for t in tokens:
        if t.type == Token.OPERAND and t.subtype == Token.RANGE:
            r, info = converter_ref(t.value, lin0, col0, aba_atual, ctx)
            r1c1.append(r)
            pt.append(t.value.replace("_xlpm.", ""))
            res["refs"].append(info)
        elif t.type == Token.FUNC and t.subtype == Token.OPEN:
            n = nome_funcao(t.value)
            r1c1.append(n + "(")
            pt.append(nome_pt(n) + "(")
            pilha.append("F")
        elif t.type in (Token.ARRAY, Token.PAREN) and t.subtype == Token.OPEN:
            r1c1.append(t.value)
            pt.append(t.value)
            pilha.append("A" if t.type == Token.ARRAY else "P")
        elif t.subtype == Token.CLOSE:
            if pilha:
                pilha.pop()
            r1c1.append(t.value)
            pt.append(t.value)
        elif t.type == Token.SEP and t.subtype == Token.ARG:
            r1c1.append(",")
            pt.append(t.value if (pilha and pilha[-1] == "A") else ";")
        elif t.type == Token.OPERAND and t.subtype == Token.LOGICAL:
            r1c1.append(t.value)
            pt.append(LOGICO_PT.get(t.value.upper(), t.value))
        elif t.type == Token.OPERAND and t.subtype == Token.NUMBER:
            r1c1.append(t.value)
            pt.append(t.value.replace(".", ","))
        elif t.type == Token.OPERAND and t.subtype == Token.ERROR:
            r1c1.append(t.value)
            pt.append(ERRO_PT.get(t.value.upper(), t.value))
        else:
            r1c1.append(t.value)
            pt.append(t.value)
    res["r1c1"] = "=" + "".join(r1c1)
    res["pt"] = "=" + "".join(pt)

    chamadas = chamadas_de_funcao(tokens)
    res["chamadas"] = chamadas
    alertas = res["alertas"]

    def add(codigo, detalhe):
        if (codigo, detalhe) not in alertas:
            alertas.append((codigo, detalhe))

    def fmt(ch):
        return f"{nome_pt(ch['nome'])}({'; '.join(ch['args'])})"

    for ch in chamadas:
        n, a = ch["nome"], ch["args"]
        if n in ("VLOOKUP", "HLOOKUP"):
            if len(a) < 4 or a[3].strip().upper() in ("TRUE", "VERDADEIRO", "1"):
                add("PROCV_APROXIMADO", f"{fmt(ch)} sem 4º argumento FALSO/0: correspondência aproximada (exige lista ordenada e devolve o 'mais próximo')")
            if len(a) >= 3 and re.fullmatch(r"\d+", a[2].strip()):
                add("INDICE_COLUNA_FIXO", f"{nome_pt(n)} devolve a coluna nº {a[2].strip()} de {a[1]} (quebra se inserirem/removerem colunas)")
        elif n == "LOOKUP":
            add("PROC_APROXIMADO", f"{fmt(ch)}: PROC sempre é aproximado")
        elif n == "MATCH":
            if len(a) < 3 or a[2].strip().upper() in ("1", "-1", "TRUE"):
                add("CORRESP_APROXIMADO", f"{fmt(ch)} sem tipo 0: correspondência aproximada")
        elif n == "XMATCH":
            if len(a) >= 3 and a[2].strip() in ("-1", "1"):
                add("CORRESP_APROXIMADO", f"{fmt(ch)} modo aproximado")
        elif n == "XLOOKUP":
            if len(a) >= 5 and a[4].strip() in ("-1", "1"):
                add("PROCX_APROXIMADO", f"{fmt(ch)} modo aproximado")
            if len(a) >= 5 and a[4].strip() == "2":
                add("PROCX_CURINGA", f"{fmt(ch)} com curingas")
            if len(a) >= 4 and a[3].strip():
                add("PROCX_SE_NAO_ENCONTRADO", f"se não encontrar devolve {a[3].strip()}")
        elif n in ("IFERROR", "IFNA"):
            fallback = a[-1] if len(a) >= 2 else ""
            add("SEERRO", f"{nome_pt(n)}(...; {fallback or 'vazio'}) esconde qualquer erro de: {a[0][:150]}")
        elif n in ("ISERROR", "ISERR", "ISNA"):
            add("TESTE_DE_ERRO", f"{nome_pt(n)}({a[0][:150]})")
        elif n in ("TODAY", "NOW"):
            add("DATA_DO_DIA", f"{nome_pt(n)}(): resultado muda conforme o dia em que a planilha é aberta")
        elif n in FUNCOES_VOLATEIS:
            add("VOLATIL", f"{fmt(ch)[:200]}")
        elif n == "INDEX" and len(a) >= 3 and re.fullmatch(r"\d+", a[2].strip()):
            add("INDICE_COLUNA_FIXO", f"ÍNDICE devolve a coluna nº {a[2].strip()} de {a[0]}")
        elif n in ("MID", "LEFT", "RIGHT"):
            nums = [x.strip() for x in a[1:] if re.fullmatch(r"\d+", x.strip())]
            if nums:
                add("POSICAO_FIXA", f"{fmt(ch)[:200]}: posição/tamanho digitado ({', '.join(nums)})")
        elif n == "SUBSTITUTE" and len(a) >= 4 and re.fullmatch(r"\d+", a[3].strip()):
            add("OCORRENCIA_FIXA", f"{fmt(ch)[:200]}: troca só a {a[3].strip()}ª ocorrência")
        if n in FUNCOES_MATRIZ_DINAMICA:
            add("MATRIZ_DINAMICA", f"{nome_pt(n)}: resultado se espalha (spill); células vizinhas aparecem como valores")

    prof = max([c["prof_se"] for c in chamadas if c["nome"] in ("IF", "IFS")] or [0])
    if prof >= 4:
        add("SE_ANINHADO", f"{prof} níveis de SE aninhados")

    textos = []
    for t in tokens:
        if t.type == Token.OPERAND and t.subtype == Token.TEXT:
            s = t.value[1:-1].replace('""', '"') if t.value.startswith('"') else t.value
            if s != "" and s not in textos:
                textos.append(s)
    if textos:
        add("TEXTO_DIGITADO", " | ".join(f'"{s}"' for s in textos))
    curingas = [s for s in textos if any(ch in s for ch in "*?~")]
    if curingas:
        add("CURINGA_LITERAL", " | ".join(f'"{s}"' for s in curingas))
    numeros = []
    for t in tokens:
        if t.type == Token.OPERAND and t.subtype == Token.NUMBER and t.value not in ("0", "1", "-1") \
                and t.value not in numeros:
            numeros.append(t.value)
    if numeros:
        add("NUMERO_DIGITADO", ", ".join(numeros))

    outras_abas = []
    for info in res["refs"]:
        if info["externo"]:
            add("REFERENCIA_EXTERNA", info["original"])
            continue
        destino = info["aba"]
        if destino != aba_atual and destino not in outras_abas:
            outras_abas.append(destino)
        if info["tipo"] == "intervalo" and info["l2"] > info["l1"]:
            if info["abs_linhas"]:
                add("INTERVALO_FIXO", f"{info['original']} (linhas {info['l1']} a {info['l2']})")
                ultima = ctx["ultima_linha"].get(destino)
                if ultima and info["l2"] < ultima:
                    add("INTERVALO_INCOMPLETO", f"{info['original']} termina na linha {info['l2']}, mas '{destino}' tem dados até a linha {ultima}")
            else:
                add("INTERVALO_DESLIZANTE", f"{info['original']}: intervalo relativo, se desloca ao arrastar a fórmula")
        if info["tipo"] == "colunas":
            add("COLUNA_INTEIRA", info["original"])
        if destino == aba_atual and info["c1"] is not None and info["c1"] <= col0 <= info["c2"]:
            add("AUTORREFERENCIA_COLUNA", f"{info['original']} inclui a própria coluna")
    if outras_abas:
        add("REF_OUTRA_ABA", ", ".join(outras_abas))
    if "#REF!" in formula.upper():
        add("ERRO_REF", "fórmula contém #REF! (referência apagada)")
    return res


# --------------------------------------------------------------------------------------
# Principal
# --------------------------------------------------------------------------------------
CAMPOS_INVENTARIO = ["tipo_item", "aba", "visibilidade_aba", "celula", "linha", "coluna",
                     "cabecalho_coluna", "id_regra", "formula_original", "formula_pt", "formula_r1c1",
                     "valor_em_cache", "alertas", "detalhe_alertas", "observacao"]

CAMPOS_REGRAS = ["ordem_calculo", "nivel_dependencia", "id_regra", "id_coluna", "tipo", "aba", "coluna",
                 "cabecalho_coluna", "variante", "qtd_variantes_na_coluna", "qtd_celulas", "celulas",
                 "formula_original_exemplo", "formula_pt_exemplo", "formula_r1c1",
                 "qtd_resultado_erro", "amostra_resultado_erro", "qtd_resultado_vazio",
                 "qtd_constantes_na_coluna", "amostra_constantes", "depende_de", "depende_de_regras",
                 "usada_por", "alertas", "detalhe_alertas", "qtd_valores_preenchidos",
                 "amostra_valores_distintos"]


def linha_vazia_inventario(**kw):
    d = {k: "" for k in CAMPOS_INVENTARIO}
    d.update({k: texto(v) for k, v in kw.items()})
    return d


def gravar_csv(caminho, campos, linhas):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for l in linhas:
            w.writerow(l)


def nomes_definidos(wb):
    """Lista (escopo, DefinedName) para openpyxl 3.0 e 3.1."""
    saida = []
    dn = wb.defined_names
    if hasattr(dn, "definedName"):  # 3.0.x
        for d in dn.definedName:
            escopo = "(pasta de trabalho)"
            if d.localSheetId is not None:
                try:
                    escopo = wb.worksheets[int(d.localSheetId)].title
                except (IndexError, ValueError):
                    escopo = f"(aba {d.localSheetId})"
            saida.append((escopo, d))
    else:  # 3.1+
        for _, d in dn.items():
            saida.append(("(pasta de trabalho)", d))
        for ws in wb.worksheets:
            for _, d in getattr(ws, "defined_names", {}).items():
                saida.append((ws.title, d))
    return saida


def main():
    padrao_saida = Path(__file__).resolve().parent.parent / "docs"
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo", nargs="?", default=r"S:\BI_NGE_ESTATISTICAS\HIERARQUIA_TECNICA_PF_v8.xlsx")
    ap.add_argument("--saida", default=str(padrao_saida), help="pasta de saída (padrão: docs/ do repositório)")
    ap.add_argument("--linha-cabecalho", type=int, default=1)
    args = ap.parse_args()

    origem = Path(args.arquivo)
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    hdr = args.linha_cabecalho

    print(f"Lendo fórmulas de {origem} ...")
    wb = load_workbook(origem, data_only=False)
    print("Lendo valores calculados (cache do Excel) ...")
    wbv = load_workbook(origem, data_only=True)

    # ---------- contexto ----------
    ctx = {"abas_canon": {ws.title.upper(): ws.title for ws in wb.worksheets},
           "ultima_linha": {}, "nomes_dest": defaultdict(list), "tabelas": {}, "tabela_da_celula": None}
    cabecalhos = {}
    for ws in wb.worksheets:
        ultima = 0
        for c in celulas(ws):
            if c.value is not None and texto(c.value).strip() != "":
                ultima = max(ultima, c.row)
        ctx["ultima_linha"][ws.title] = ultima
        cabecalhos[ws.title] = {c: texto(ws.cell(row=hdr, column=c).value).strip()
                                for c in range(1, (ws.max_column or 0) + 1)}
        for nome_tab in list(ws.tables):
            tab = ws.tables[nome_tab]
            ini, _ = tab.ref.split(":") if ":" in tab.ref else (tab.ref, tab.ref)
            m = RE_CEL.match(ini.replace("$", ""))
            cols = [tc.name for tc in tab.tableColumns]
            ctx["tabelas"][nome_tab.upper()] = {
                "aba": ws.title, "ref": tab.ref, "nome": nome_tab,
                "col_ini": column_index_from_string(m.group(2)) if m else 1,
                "colunas": {n.upper(): i for i, n in enumerate(cols)}, "lista": cols}

    lista_nomes = nomes_definidos(wb)
    for escopo, d in lista_nomes:
        try:
            for aba_dest, ref in d.destinations:
                ctx["nomes_dest"][d.name.upper()].append((aba_dest, ref.replace("$", "")))
        except Exception:  # noqa: BLE001 - nomes com constantes/fórmulas não têm destino
            pass

    def cab(aba, c):
        return cabecalhos.get(aba, {}).get(c, "")

    def rotulo(aba, c):
        h = cab(aba, c)
        return f"{aba}!{get_column_letter(c)}" + (f" ({h})" if h else "")

    def tabela_da(aba, lin, col):
        for t in ctx["tabelas"].values():
            if t["aba"] != aba:
                continue
            a, _, b = t["ref"].partition(":")
            ma, mb = RE_CEL.match(a.replace("$", "")), RE_CEL.match((b or a).replace("$", ""))
            if ma and mb:
                c1, l1 = column_index_from_string(ma.group(2)), int(ma.group(4))
                c2, l2 = column_index_from_string(mb.group(2)), int(mb.group(4))
                if l1 <= lin <= l2 and c1 <= col <= c2:
                    return t
        return None

    inventario = []

    # ---------- abas, colunas/linhas ocultas, tabelas, validações, formatação condicional ----------
    for i, ws in enumerate(wb.worksheets, start=1):
        estado = ws.sheet_state
        qtd_f = sum(1 for c in celulas(ws) if texto_formula(c)[0] is not None)
        cols_ocultas = []
        for chave, dim in ws.column_dimensions.items():
            if dim.hidden:
                a = get_column_letter(dim.min) if dim.min else chave
                b = get_column_letter(dim.max) if dim.max else chave
                cols_ocultas.append(a if a == b else f"{a}:{b}")
        linhas_ocultas = [r for r, dim in ws.row_dimensions.items() if dim.hidden]
        inventario.append(linha_vazia_inventario(
            tipo_item="ABA_OCULTA" if estado != "visible" else "ABA", aba=ws.title, visibilidade_aba=estado,
            celula=ws.dimensions, observacao=(f"aba nº {i}; {qtd_f} células com fórmula; dados até a linha "
                                              f"{ctx['ultima_linha'][ws.title]}; colunas ocultas: "
                                              f"{', '.join(cols_ocultas) or 'nenhuma'}; linhas ocultas: {len(linhas_ocultas)}")))
        if cols_ocultas:
            inventario.append(linha_vazia_inventario(tipo_item="COLUNAS_OCULTAS", aba=ws.title, visibilidade_aba=estado,
                                                     celula=", ".join(cols_ocultas),
                                                     observacao="; ".join(f"{x}: {cab(ws.title, column_index_from_string(x.split(':')[0]))}" for x in cols_ocultas)))
        if linhas_ocultas:
            inventario.append(linha_vazia_inventario(tipo_item="LINHAS_OCULTAS", aba=ws.title, visibilidade_aba=estado,
                                                     celula=comprimir_linhas(linhas_ocultas, "", 30),
                                                     observacao=f"{len(linhas_ocultas)} linhas ocultas"))
        for t in ctx["tabelas"].values():
            if t["aba"] == ws.title:
                inventario.append(linha_vazia_inventario(tipo_item="TABELA", aba=ws.title, visibilidade_aba=estado,
                                                         celula=t["ref"], cabecalho_coluna=t["nome"],
                                                         observacao="colunas: " + " | ".join(t["lista"])))
        try:
            for dv in ws.data_validations.dataValidation:
                f = " | ".join(x for x in (dv.formula1, dv.formula2) if x)
                inventario.append(linha_vazia_inventario(tipo_item="VALIDACAO_DADOS", aba=ws.title, visibilidade_aba=estado,
                                                         celula=str(dv.sqref), formula_original=f,
                                                         observacao=f"tipo={dv.type}; operador={dv.operator}; permite vazio={dv.allow_blank}"))
        except AttributeError:
            pass
        try:
            for fc in ws.conditional_formatting:
                for regra in fc.rules:
                    inventario.append(linha_vazia_inventario(
                        tipo_item="FORMATACAO_CONDICIONAL", aba=ws.title, visibilidade_aba=estado, celula=str(fc.sqref),
                        formula_original=" | ".join(regra.formula or []),
                        observacao=f"tipo={regra.type}; operador={regra.operator}; texto={regra.text}; prioridade={regra.priority}"))
        except (AttributeError, TypeError):
            pass

    for escopo, d in lista_nomes:
        valor = d.attr_text if hasattr(d, "attr_text") else getattr(d, "value", "")
        al = []
        if "#REF!" in (valor or "").upper():
            al.append("ERRO_REF")
        if re.search(r"\[\d+\]", valor or ""):
            al.append("REFERENCIA_EXTERNA")
        inventario.append(linha_vazia_inventario(
            tipo_item="NOME_DEFINIDO", aba=escopo, celula=d.name, formula_original=valor, alertas=", ".join(al),
            observacao=("oculto; " if getattr(d, "hidden", False) else "") + (d.comment or "")))

    for lk in getattr(wb, "_external_links", []) or []:
        alvo = ""
        try:
            alvo = lk.file_link.Target
        except AttributeError:
            pass
        inventario.append(linha_vazia_inventario(tipo_item="LINK_EXTERNO", formula_original=alvo,
                                                 alertas="REFERENCIA_EXTERNA"))

    # ---------- fórmulas ----------
    grupos = {}            # (aba, col, r1c1) -> dados do grupo
    analise_cache = {}     # (aba, col, r1c1) -> alertas
    linhas_formula = []
    colunas_com_formula = defaultdict(set)   # aba -> {col}
    for ws in wb.worksheets:
        wsv = wbv[ws.title]
        for c in celulas(ws):
            f, matricial, ref_mat = texto_formula(c)
            if f is None:
                continue
            ctx["tabela_da_celula"] = tabela_da(ws.title, c.row, c.column)
            an = analisar_formula(f, c.row, c.column, ws.title, ctx)
            if matricial:
                an["alertas"].append(("MATRICIAL", f"fórmula matricial (CSE) em {ref_mat}"))
            chave = (ws.title, c.column, an["r1c1"])
            cache = texto(wsv.cell(row=c.row, column=c.column).value)
            g = grupos.get(chave)
            if g is None:
                deps = set()
                for info in an["refs"]:
                    for aba_d, col_d in colunas_de(info, ctx):
                        deps.add((aba_d, col_d))
                g = grupos[chave] = {"aba": ws.title, "col": c.column, "r1c1": an["r1c1"], "linhas": [],
                                     "exemplo": f, "exemplo_pt": an["pt"], "primeira": c.coordinate,
                                     "alertas": an["alertas"], "deps": deps, "erros": [], "vazios": 0}
            g["linhas"].append(c.row)
            if cache.strip().upper() in ERROS_EXCEL:
                g["erros"].append(f"{c.coordinate}={cache}")
            elif cache.strip() == "":
                g["vazios"] += 1
            colunas_com_formula[ws.title].add(c.column)
            linhas_formula.append((ws, c, f, an, cache, chave))

    # ids de coluna e de variante
    ordem_abas = {ws.title: i for i, ws in enumerate(wb.worksheets, start=1)}
    id_coluna = {}
    for aba, cols in colunas_com_formula.items():
        for col in cols:
            id_coluna[(aba, col)] = f"A{ordem_abas[aba]}-{get_column_letter(col)}"
    por_coluna = defaultdict(list)
    for chave, g in grupos.items():
        por_coluna[(g["aba"], g["col"])].append(g)
    for (aba, col), lista in por_coluna.items():
        lista.sort(key=lambda g: min(g["linhas"]))
        for n, g in enumerate(lista, start=1):
            g["variante"] = n
            g["id"] = f"{id_coluna[(aba, col)]}.{n}"
            g["qtd_variantes"] = len(lista)

    # constantes digitadas em colunas que têm fórmula
    constantes = defaultdict(list)
    for ws in wb.worksheets:
        cols = colunas_com_formula.get(ws.title, set())
        if not cols:
            continue
        for c in celulas(ws):
            if c.row <= hdr or c.column not in cols:
                continue
            if texto_formula(c)[0] is None and c.value is not None and texto(c.value).strip() != "":
                constantes[(ws.title, c.column)].append(f"{c.coordinate}={texto(c.value)[:60]}")

    # ---------- dependências entre colunas ----------
    nos = set(id_coluna)
    deps_col = defaultdict(set)
    for g in grupos.values():
        no = (g["aba"], g["col"])
        deps_col[no] |= {d for d in g["deps"] if d != no}
    usada_por = defaultdict(set)
    for no, ds in deps_col.items():
        for d in ds:
            usada_por[d].add(no)

    nivel, em_visita, ciclos = {}, set(), set()

    def calc_nivel(no):
        if no not in nos:
            return 0
        if no in nivel:
            return nivel[no]
        if no in em_visita:
            ciclos.add(no)
            return 0
        em_visita.add(no)
        n = 1 + max([calc_nivel(d) for d in deps_col[no]] or [0])
        em_visita.discard(no)
        nivel[no] = n
        return n

    for no in nos:
        calc_nivel(no)
    ordem_nos = sorted(nos, key=lambda x: (nivel[x], ordem_abas[x[0]], x[1]))
    ordem_de = {no: i for i, no in enumerate(ordem_nos, start=1)}

    # ---------- inventário: linhas de fórmula ----------
    for ws, c, f, an, cache, chave in sorted(linhas_formula, key=lambda x: (ordem_abas[x[0].title], x[1].column, x[1].row)):
        g = grupos[chave]
        inventario.append(linha_vazia_inventario(
            tipo_item="FORMULA", aba=ws.title, visibilidade_aba=ws.sheet_state, celula=c.coordinate, linha=c.row,
            coluna=get_column_letter(c.column), cabecalho_coluna=cab(ws.title, c.column), id_regra=g["id"],
            formula_original=f, formula_pt=an["pt"], formula_r1c1=an["r1c1"], valor_em_cache=cache,
            alertas=", ".join(dict.fromkeys(a for a, _ in an["alertas"])),
            detalhe_alertas=" || ".join(f"{a}: {d}" for a, d in an["alertas"])))

    # ---------- regras ----------
    regras = []
    for no in ordem_nos:
        aba, col = no
        for g in por_coluna[no]:
            al = list(g["alertas"])
            if g["qtd_variantes"] > 1:
                al.append(("VARIANTES_NA_COLUNA", f"a coluna tem {g['qtd_variantes']} fórmulas diferentes"))
            if constantes[no]:
                al.append(("CONSTANTES_NA_COLUNA", f"{len(constantes[no])} células com valor digitado no lugar da fórmula"))
            if g["erros"]:
                al.append(("RESULTADO_COM_ERRO", f"{len(g['erros'])} células com erro no valor calculado"))
            if no in ciclos:
                al.append(("CICLO", "dependência circular entre colunas"))
            regras.append({
                "ordem_calculo": ordem_de[no], "nivel_dependencia": nivel[no], "id_regra": g["id"],
                "id_coluna": id_coluna[no], "tipo": "FORMULA", "aba": aba, "coluna": get_column_letter(col),
                "cabecalho_coluna": cab(aba, col), "variante": g["variante"],
                "qtd_variantes_na_coluna": g["qtd_variantes"], "qtd_celulas": len(g["linhas"]),
                "celulas": comprimir_linhas(g["linhas"], get_column_letter(col)),
                "formula_original_exemplo": f"{g['primeira']}: {g['exemplo']}",
                "formula_pt_exemplo": g["exemplo_pt"], "formula_r1c1": g["r1c1"],
                "qtd_resultado_erro": len(g["erros"]), "amostra_resultado_erro": " | ".join(g["erros"][:15]),
                "qtd_resultado_vazio": g["vazios"], "qtd_constantes_na_coluna": len(constantes[no]),
                "amostra_constantes": " | ".join(constantes[no][:20]),
                "depende_de": " | ".join(rotulo(a, c) for a, c in sorted(g["deps"], key=lambda x: (ordem_abas.get(x[0], 99), x[1]))),
                "depende_de_regras": ", ".join(sorted({id_coluna[d] for d in g["deps"] if d in nos and d != no},
                                                      key=lambda x: ordem_de[next(k for k, v in id_coluna.items() if v == x)])),
                "usada_por": ", ".join(sorted(id_coluna[u] for u in usada_por[no] if u in nos)),
                "alertas": ", ".join(dict.fromkeys(a for a, _ in al)),
                "detalhe_alertas": " || ".join(f"{a}: {d}" for a, d in al),
                "qtd_valores_preenchidos": "", "amostra_valores_distintos": ""})

    # colunas de entrada (sem fórmula) usadas pelas regras
    entradas = sorted({d for ds in deps_col.values() for d in ds if d not in nos},
                      key=lambda x: (ordem_abas.get(x[0], 99), x[1]))
    for aba, col in entradas:
        valores = []
        if aba in wb.sheetnames:
            ws = wb[aba]
            for c in celulas(ws):
                if c.column == col and c.row > hdr and c.value is not None and texto(c.value).strip() != "":
                    valores.append(texto(c.value))
        distintos = list(dict.fromkeys(valores))
        regras.append({k: "" for k in CAMPOS_REGRAS} | {
            "ordem_calculo": 0, "nivel_dependencia": 0, "id_regra": f"E{ordem_abas.get(aba, 0)}-{get_column_letter(col)}",
            "id_coluna": f"E{ordem_abas.get(aba, 0)}-{get_column_letter(col)}", "tipo": "ENTRADA", "aba": aba,
            "coluna": get_column_letter(col), "cabecalho_coluna": cab(aba, col),
            "usada_por": ", ".join(sorted(id_coluna[u] for u in usada_por[(aba, col)] if u in nos)),
            "qtd_valores_preenchidos": len(valores),
            "amostra_valores_distintos": f"{len(distintos)} distintos: " + " | ".join(distintos[:40])})
    regras.sort(key=lambda r: (int(r["ordem_calculo"]), r["id_regra"]))

    arq_inv = saida / "inventario_formulas.csv"
    arq_reg = saida / "inventario_regras.csv"
    gravar_csv(arq_inv, CAMPOS_INVENTARIO, inventario)
    gravar_csv(arq_reg, CAMPOS_REGRAS, regras)

    # ---------- resumo no console ----------
    print("\n=== Abas ===")
    for ws in wb.worksheets:
        print(f"  [{ws.sheet_state:10}] {ws.title}: {len([1 for x in linhas_formula if x[0] is ws])} fórmulas")
    print(f"\nNomes definidos: {len(lista_nomes)} | Tabelas: {len(ctx['tabelas'])}")
    print(f"Células com fórmula: {len(linhas_formula)} | Regras únicas (variantes): {len(grupos)} | "
          f"Colunas com fórmula: {len(nos)} | Colunas de entrada: {len(entradas)}")
    print("\n=== Ordem de cálculo (coluna -> depende de) ===")
    for no in ordem_nos:
        ds = ", ".join(id_coluna[d] for d in sorted(deps_col[no], key=lambda x: ordem_de.get(x, 0)) if d in nos)
        print(f"  {ordem_de[no]:>3}. nível {nivel[no]}  {id_coluna[no]:<8} {cab(*no)[:45]:<45} "
              f"variantes={len(por_coluna[no])}  <- {ds or '(só entradas)'}")
    if ciclos:
        print(f"\nATENÇÃO: dependência circular em {', '.join(id_coluna[c] for c in ciclos)}")
    print(f"\nGerados:\n  {arq_inv}\n  {arq_reg}")


if __name__ == "__main__":
    main()
