#!/usr/bin/env python3
"""Valida overlays do CloudArena contra os bancos de questoes por optionId estavel.

Contrato atual:
  - options tem o mesmo numero de itens do banco (atualmente 4)
  - cada item possui optionId no formato <questionId>:option:<index>
  - IDs cobrem exatamente todos os indices da pergunta, sem duplicacao
  - exatamente 1 "correct", 2 "eliminate", 1 "trap"
  - o item "correct" aponta para o indice `correct` do banco
  - matchText e apenas metadado legivel; pode ser sincronizado pelo migrador
  - todo item nao-correct tem reasonWrong nao vazio
  - finalBlow.justifications tem exatamente 4 itens, exatamente 1 correct=true
  - questionId existe no banco daquela certificacao

A identidade nao depende mais da redacao em portugues, permitindo revisoes de texto
e bancos localizados sem quebrar o CloudArena.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CERTS = ["clf-c02", "saa-c03", "dva-c02", "dea-c01"]
LEVELS = ["iniciante", "medio", "avancado"]


def load_bank(cert):
    bank = {}
    for level in LEVELS:
        path = ROOT / "data" / "exams" / cert / f"{level}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for q in data.get("questions", []):
            bank[q["id"]] = {"question": q, "level": level}
    return bank


def parse_option_id(qid, value, option_count):
    if not isinstance(value, str):
        raise ValueError("optionId ausente ou nao textual")
    match = re.fullmatch(re.escape(qid) + r":option:(\d+)", value)
    if not match:
        raise ValueError(f"optionId malformado: {value!r}")
    index = int(match.group(1))
    if index < 0 or index >= option_count:
        raise ValueError(f"indice {index} fora do intervalo 0..{option_count - 1}")
    return index


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
    correct_index = question.get("correct")
    if not isinstance(correct_index, int) or not (0 <= correct_index < len(bank_options)):
        errors.append(f"{prefix} indice correct invalido no banco: {correct_index!r}")
        return

    options = entry.get("options", [])
    if len(options) != len(bank_options):
        errors.append(
            f"{prefix} options tem {len(options)} itens (banco tem {len(bank_options)})"
        )
        return

    stages = {"correct": 0, "eliminate": 0, "trap": 0}
    seen_ids = set()
    correct_overlay_index = None

    for opt in options:
        stage = opt.get("stage")
        if stage not in stages:
            errors.append(f"{prefix} stage invalido: {stage!r}")
            continue
        stages[stage] += 1

        try:
            index = parse_option_id(qid, opt.get("optionId"), len(bank_options))
        except ValueError as exc:
            errors.append(f"{prefix} {exc}")
            continue

        oid = f"{qid}:option:{index}"
        if oid in seen_ids:
            errors.append(f"{prefix} optionId duplicado: {oid}")
        seen_ids.add(oid)

        match_text = opt.get("matchText")
        if not isinstance(match_text, str) or not match_text.strip():
            errors.append(f"{prefix} {oid} sem matchText legivel")

        if stage != "correct" and not (opt.get("reasonWrong") or "").strip():
            errors.append(f"{prefix} item {stage!r} sem reasonWrong")
        if stage == "correct":
            correct_overlay_index = index

    expected_ids = {f"{qid}:option:{index}" for index in range(len(bank_options))}
    if seen_ids != expected_ids:
        errors.append(
            f"{prefix} cobertura de optionId invalida: "
            f"faltando={sorted(expected_ids - seen_ids)}, extras={sorted(seen_ids - expected_ids)}"
        )

    if stages != {"correct": 1, "eliminate": 2, "trap": 1}:
        errors.append(f"{prefix} distribuicao de stages invalida: {stages}")

    if correct_overlay_index != correct_index:
        errors.append(
            f"{prefix} DIVERGENCIA DE GABARITO: banco aponta indice {correct_index}, "
            f"overlay aponta {correct_overlay_index}"
        )

    fb = entry.get("finalBlow", {})
    justs = fb.get("justifications", [])
    if len(justs) != len(bank_options):
        errors.append(
            f"{prefix} finalBlow tem {len(justs)} justificativas "
            f"(esperado {len(bank_options)})"
        )
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
    print("CloudArena — validacao por optionId e relatorio de cobertura")
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
    print("OK: todos os overlays validos por optionId.")


if __name__ == "__main__":
    main()
