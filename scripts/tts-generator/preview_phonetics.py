#!/usr/bin/env python3
"""Tabela de revisao da pronuncia: mostra COMO cada termo em ingles sera falado.

Varre todos os roteiros, extrai as chamadas PHON("ipa", "texto") e mostra a
re-grafia que sera enviada a Azure. Use para revisar a olho e afinar o que
soar estranho -- basta editar o dict RESPELL no glossary.py.

Uso:
    python3 preview_phonetics.py            # tabela completa
    python3 preview_phonetics.py --auto      # so os termos SEM revisao manual
    python3 preview_phonetics.py > revisao.txt
"""
import glob
import re
import sys

from glossary import RESPELL, ipa_to_ptbr

PATTERN = re.compile(r'PHON\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)')


def collect():
    terms = {}  # texto -> (ipa, arquivos)
    for path in sorted(glob.glob("cap*_script.py")) + ["glossary.py"]:
        try:
            src = open(path, encoding="utf-8").read()
        except OSError:
            continue
        for ipa, text in PATTERN.findall(src):
            key = text.strip()
            if key not in terms:
                terms[key] = [ipa, set()]
            terms[key][1].add(path.replace("_script.py", "").replace(".py", ""))
    return terms


def main():
    only_auto = "--auto" in sys.argv
    terms = collect()

    manual, auto = [], []
    for text, (ipa, files) in sorted(terms.items(), key=lambda x: x[0].lower()):
        override = RESPELL.get(text.strip().lower())
        row = (text, ipa, override or ipa_to_ptbr(ipa), len(files))
        (manual if override else auto).append(row)

    def dump(title, rows):
        print(f"\n{'=' * 78}\n{title} ({len(rows)} termos)\n{'=' * 78}")
        print(f"{'TERMO (ingles)':<28} {'SERA FALADO COMO':<28} caps")
        print("-" * 78)
        for text, ipa, spoken, n in rows:
            print(f"{text[:27]:<28} {spoken[:27]:<28} {n}")

    if not only_auto:
        dump("REVISADOS A MAO (dict RESPELL -- prioridade)", manual)
    dump("AUTOMATICOS (transdutor IPA->PT) -- revise e promova ao RESPELL se soar mal", auto)

    print(f"\n{'=' * 78}")
    print(f"TOTAL: {len(manual) + len(auto)} termos distintos "
          f"({len(manual)} revisados a mao, {len(auto)} automaticos)")
    print("Para corrigir um termo: adicione ao dict RESPELL em glossary.py")
    print("   ex.:  \"health check\": \"Rélf Tchéque\",")


if __name__ == "__main__":
    main()
