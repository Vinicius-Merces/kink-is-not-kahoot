#!/usr/bin/env python3
"""Diagnóstico heurístico de pistas de comprimento no SAA-C03 avançado."""
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data/exams/saa-c03/avancado.json"
questions = json.loads(path.read_text(encoding="utf-8"))["questions"]
longest = []
imbalanced = []
for q in questions:
    options = q["options"]
    answer = q["correct"]
    if not isinstance(answer, int) or not (0 <= answer < len(options)):
        continue  # questões multirresposta devem ser revisadas separadamente
    sizes = [len(s.strip()) for s in options]
    others = [n for i, n in enumerate(sizes) if i != answer]
    ratio = sizes[answer] / (sum(others) / len(others) or 1)
    if sizes[answer] == max(sizes):
        longest.append(q["id"])
    if ratio >= 2:
        imbalanced.append((ratio, q["id"], sizes))
print(f"Questões: {len(questions)}")
print(f"Correta (empatada como) mais longa: {len(longest)}")
print(f"Correta >= 2x média das demais: {len(imbalanced)}")
for ratio, qid, sizes in sorted(imbalanced, reverse=True):
    print(f"{qid}: razão={ratio:.2f}; caracteres={sizes}")
