#!/usr/bin/env python3
"""Verificador de re-grafia: LE cada entrada do RESPELL com as regras de
leitura do portugues e compara com o som que a gente QUERIA produzir.

Por que isso existe
-------------------
Nao da pra ouvir o audio daqui (a Azure nao e alcancavel do ambiente onde este
script foi escrito). Mas nao precisa ouvir para pegar a maior classe de erro:
"escrevi a re-grafia aplicando errado uma regra do portugues".

As regras de letra->som do PT-BR sao fatos da ortografia, nao opiniao. Entao
este script implementa um LEITOR de portugues (independente do transdutor
IPA->grafia do glossary.py) e mostra o que a voz vai realmente falar.

Se o leitor devolver algo diferente do alvo em ingles, a re-grafia esta errada.

Uso:
    python3 check_respell.py            # so os problemas
    python3 check_respell.py --all      # todas as entradas
"""
import re
import sys

from glossary import RESPELL

# ---------------------------------------------------------------------------
# Leitor de portugues (grafema -> fonema). Regras do PT-BR padrao.
# ---------------------------------------------------------------------------

VOWELS = "aeiouáéíóúâêôãõà"


def _e_vogal(ch: str) -> bool:
    """Cuidado: "" in VOWELS devolve True em Python. Guarda contra isso."""
    return bool(ch) and ch in VOWELS


def ler_em_portugues(texto: str) -> str:
    """Devolve a leitura aproximada (IPA) que uma voz pt-BR faria do texto."""
    s = texto.lower()
    out = []
    i = 0
    apos_digrafo = False   # o "u" de "gu"/"qu" e mudo: nao forma ditongo depois
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        nxt2 = s[i + 2] if i + 2 < len(s) else ""
        prev = s[i - 1] if i > 0 else ""

        # dígrafos primeiro
        if c == "t" and nxt == "c" and nxt2 == "h":
            out.append("tʃ"); i += 3; continue
        if c == "c" and nxt == "h":
            out.append("ʃ"); i += 2; continue
        if c == "l" and nxt == "h":
            out.append("ʎ"); i += 2; continue
        if c == "n" and nxt == "h":
            out.append("ɲ"); i += 2; continue
        if c == "r" and nxt == "r":
            out.append("h"); i += 2; continue      # "rr" = /h/ no PT-BR
        if c == "s" and nxt == "s":
            out.append("s"); i += 2; continue      # "ss" = /s/
        if c == "q" and nxt == "u":
            # "qu" + e/i = /k/ (u mudo) ; "qu" + a/o = /kw/
            if nxt2 in "eiéêí":
                out.append("k"); i += 2; apos_digrafo = True; continue
            out.append("kw"); i += 2; continue
        if c == "g" and nxt == "u" and nxt2 in "eiéêí":
            out.append("g"); i += 2; apos_digrafo = True; continue   # "gu" = /g/ duro
        if c == "d" and nxt == "j":
            out.append("dʒ"); i += 2; continue

        # consoantes sensíveis ao contexto
        if c == "c":
            out.append("s" if nxt in "eiéêí" else "k"); i += 1; continue
        if c == "g":
            out.append("ʒ" if nxt in "eiéêí" else "g"); i += 1; continue
        if c == "s":
            # "s" entre vogais = /z/
            if prev in VOWELS and nxt in VOWELS:
                out.append("z")
            else:
                out.append("s")
            i += 1; continue
        if c == "r":
            # "r" inicial de palavra = /h/ aspirado; entre vogais = tap
            if i == 0 or prev == " ":
                out.append("h")
            elif prev in VOWELS and nxt in VOWELS:
                out.append("ɾ")
            else:
                out.append("ɾ")
            i += 1; continue
        if c == "h":
            i += 1; continue                        # "h" é MUDO em português
        if c == "x":
            out.append("ʃ"); i += 1; continue
        if c == "j":
            out.append("ʒ"); i += 1; continue
        if c == "z":
            out.append("z"); i += 1; continue
        if c == "l":
            # "l" final de sílaba vira /w/ no PT-BR
            out.append("w" if (nxt == "" or nxt not in VOWELS) else "l")
            i += 1; continue

        # vogais (acento = tônica)
        VMAP = {
            "a": "a", "á": "ˈa", "â": "ˈɐ", "ã": "ɐ̃",
            "e": "e", "é": "ˈɛ", "ê": "ˈe",
            "i": "i", "í": "ˈi",
            "o": "o", "ó": "ˈɔ", "ô": "ˈo", "õ": "õ",
            "u": "u", "ú": "ˈu",
        }
        if c in VMAP:
            # "u"/"i" atonos ao lado de vogal formam ditongo (semivogal),
            # MAS nao quando vem logo apos o "u" mudo de "gu"/"qu".
            vizinho_vogal = _e_vogal(nxt) or (_e_vogal(prev) and not apos_digrafo)
            apos_digrafo = False
            if c == "u" and vizinho_vogal:
                out.append("w"); i += 1; continue
            if c == "i" and vizinho_vogal:
                out.append("j"); i += 1; continue
            out.append(VMAP[c]); i += 1; continue
        apos_digrafo = False

        if c == " ":
            out.append(" "); i += 1; continue

        out.append(c); i += 1

    return "".join(out)


# ---------------------------------------------------------------------------
# Alvos: o som que cada termo DEVE ter (inglês, aproximado ao que o PT alcança)
# Só listo os que importam checar. Marcador simples: sons que NÃO podem sumir.
# ---------------------------------------------------------------------------
DEVE_CONTER = {
    "gateway":    ["g", "ˈe", "w"],     # /g/ duro (não /ʒ/), tônica no "guêi", glide /w/
    "deny":       ["d", "ˈa", "j"],     # tônica no "nái" (i vira semivogal /j/)
    "allow":      ["ˈa", "w"],          # tônica no "láu" (u vira semivogal /w/)
    "bucket":     ["b", "k"],           # /k/ (não /s/)
    "throughput": ["t", "ˈu"],
    "role":       ["h", "w"],           # r inicial = /h/ ; "ou" -> /ow/
    "spot":       ["s", "p", "t"],
    "health check": ["tʃ", "k"],        # tch + k (não /s/)
    "auto scaling": ["s", "k"],         # "isk..." tem /s/ E /k/ (scaling)
    "github":     ["g", "h"],           # /g/ duro + /h/ do "Rábi"
    "ram":        ["h", "ˈa"],          # "Rám"
    "quicksight": ["k", "ˈa", "j"],
}

PROIBIDO = {
    "gateway": ["ʒ"],        # /ʒ/ = o "g" foi lido como "jê" -> ERRO
    "bucket": ["s"],         # /s/ = o "c" foi lido como cê -> ERRO
    "auto scaling": ["ʒ"],
}


def main():
    mostrar_tudo = "--all" in sys.argv
    problemas = 0

    print(f"{'TERMO':<24} {'RE-GRAFIA':<22} {'COMO O PT VAI LER':<26} STATUS")
    print("-" * 92)

    for termo, respell in sorted(RESPELL.items()):
        leitura = ler_em_portugues(respell)

        erros = []
        for som in DEVE_CONTER.get(termo, []):
            if som not in leitura:
                erros.append(f"falta {som}")
        for som in PROIBIDO.get(termo, []):
            if som in leitura:
                erros.append(f"PROIBIDO {som}")

        if erros:
            problemas += 1
            status = "❌ " + ", ".join(erros)
        elif termo in DEVE_CONTER:
            status = "✅ confere"
        else:
            status = "·  (sem alvo definido)"

        if erros or mostrar_tudo or termo in DEVE_CONTER:
            print(f"{termo[:23]:<24} {respell[:21]:<22} {leitura[:25]:<26} {status}")

    print("-" * 92)
    print(f"{len(RESPELL)} re-grafias | {problemas} com problema")
    if problemas:
        print("\nCorrija no dict RESPELL do glossary.py e rode de novo.")
        sys.exit(1)
    print("\nTodas as re-grafias com alvo definido são lidas corretamente pelo português.")


if __name__ == "__main__":
    main()
