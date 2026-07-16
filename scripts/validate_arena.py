#!/usr/bin/env python3
"""Valida os overlays do CloudArena contra os bancos de questoes.

Regras (CLOUDARENA-SPEC.md, secao 3):
  - options tem exatamente 4 itens
  - exatamente 1 "correct", 2 "eliminate", 1 "trap"
  - matchText de cada item bate com uma opcao da questao original (por TEXTO)
  - o matchText do "correct" bate com a alternativa correta do banco
  - todo item nao-correct tem reasonWrong nao vazio
  - finalBlow.justifications tem exatamente 4 itens, exatamente 1 correct=true
  - questionId existe no banco daquela certificacao

Emite relatorio de cobertura por certificacao e dificuldade.
Sai com codigo 1 se qualquer overlay estiver invalido.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CERTS = ["clf-c02", "saa-c03", "dva-c02", "dea-c01"]
LEVELS = ["iniciante", "medio", "avancado"]


def load_bank(cert):
    """Carrega todas as questoes do banco de uma cert, indexadas por id."""
    bank = {}
    for level in LEVELS:
        path = ROOT / "data" / "exams" / cert / f"{level}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for q in data.get("questions", []):
            bank[q["id"]] = {"question": q, "level": level}
    return bank


def validate_overlay(entry, bank, errors):
    qid = entry.get("questionId")
    prefix = f"[{qid}]"

    if not qid:
        errors.append("overlay sem questionId")
        return

    if qid not in bank:
        errors.append(f"{prefix} questionId nao existe no banco")
        return

    question = bank[qid]["question"]
    bank_options = question.get("options", [])
    correct_text = bank_options[question["correct"]] if 0 <= question.get("correct", -1) < len(bank_options) else None

    options = entry.get("options", [])
    if len(options) != 4:
        errors.append(f"{prefix} options tem {len(options)} itens (esperado 4)")
        return

    stages = {"correct": 0, "eliminate": 0, "trap": 0}
    seen_texts = set()
    for opt in options:
        stage = opt.get("stage")
        text = opt.get("matchText", "")
        if stage not in stages:
            errors.append(f"{prefix} stage invalido: {stage!r}")
            continue
        stages[stage] += 1
        if text in seen_texts:
            errors.append(f"{prefix} matchText duplicado: {text[:50]!r}")
        seen_texts.add(text)
        if text not in bank_options:
            errors.append(f"{prefix} matchText nao encontrado nas opcoes do banco: {text[:60]!r}")
        if stage != "correct" and not (opt.get("reasonWrong") or "").strip():
            errors.append(f"{prefix} item {stage!r} sem reasonWrong")
        if stage == "correct" and text != correct_text:
            errors.append(
                f"{prefix} DIVERGENCIA DE GABARITO: banco diz {correct_text[:50]!r}, "
                f"overlay diz {text[:50]!r}"
            )

    if stages != {"correct": 1, "eliminate": 2, "trap": 1}:
        errors.append(f"{prefix} distribuicao de stages invalida: {stages}")

    fb = entry.get("finalBlow", {})
    justs = fb.get("justifications", [])
    if len(justs) != 4:
        errors.append(f"{prefix} finalBlow tem {len(justs)} justificativas (esperado 4)")
    else:
        n_correct = sum(1 for j in justs if j.get("correct") is True)
        if n_correct != 1:
            errors.append(f"{prefix} finalBlow tem {n_correct} justificativas corretas (esperado 1)")
        for j in justs:
            if not (j.get("text") or "").strip():
                errors.append(f"{prefix} justificativa com texto vazio")


def main():
    total_errors = []
    print("=" * 72)
    print("CloudArena — validacao de overlays e relatorio de cobertura")
    print("=" * 72)

    for cert in CERTS:
        bank = load_bank(cert)
        overlay_path = ROOT / "data" / "cloudarena" / "breakdowns" / f"{cert}.json"

        overlays = []
        if overlay_path.exists():
            try:
                data = json.loads(overlay_path.read_text(encoding="utf-8"))
                overlays = data.get("overlays", [])
            except json.JSONDecodeError as e:
                total_errors.append(f"[{cert}] JSON invalido: {e}")

        errors = []
        seen_ids = set()
        for entry in overlays:
            qid = entry.get("questionId")
            if qid in seen_ids:
                errors.append(f"[{qid}] questionId duplicado no overlay")
            seen_ids.add(qid)
            validate_overlay(entry, bank, errors)

        # Cobertura por dificuldade
        per_level = {lvl: {"total": 0, "covered": 0} for lvl in LEVELS}
        for qid, info in bank.items():
            per_level[info["level"]]["total"] += 1
            if qid in seen_ids:
                per_level[info["level"]]["covered"] += 1

        print(f"\n{cert.upper()}  ({len(overlays)} overlays, {len(bank)} questoes no banco)")
        for lvl in LEVELS:
            t, c = per_level[lvl]["total"], per_level[lvl]["covered"]
            pct = (c / t * 100) if t else 0
            bar = "#" * int(pct // 5)
            print(f"  {lvl:<10} {c:>4}/{t:<4} ({pct:5.1f}%) {bar}")

        if errors:
            print(f"  ERROS ({len(errors)}):")
            for e in errors[:20]:
                print(f"    - {e}")
            if len(errors) > 20:
                print(f"    ... e mais {len(errors) - 20}")
            total_errors.extend(f"[{cert}] {e}" for e in errors)

    print("\n" + "=" * 72)
    if total_errors:
        print(f"FALHOU: {len(total_errors)} erro(s) encontrado(s).")
        sys.exit(1)
    print("OK: todos os overlays validos.")


if __name__ == "__main__":
    main()
