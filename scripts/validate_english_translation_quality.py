#!/usr/bin/env python3
"""Mechanical quality gates for staged English exam translations.

This validator intentionally checks invariants rather than prose style:
- translated human-language fields must be present and non-empty;
- obvious PT prose must not leak into EN;
- option/rationale cardinality must match the canonical PT bank;
- every field preserves its own AWS/technical and numeric anchors.

The field-local rule is important: a service that appears in PT option 3 must still
appear in EN option 3. Merely mentioning it elsewhere in the question is not enough.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from translation_integrity import norm, question_anchor_errors

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "data" / "exams"
STAGING = ROOT / "translations" / "en"

PT_MARKERS = re.compile(
    r"\b(?:qual|quais|uma|um|empresa|servi[cç]o|usu[aá]rio|equipe|dados|nuvem|"
    r"armazenamento|seguran[cç]a|gerenciado|gerenciada|permite|deve|possui|"
    r"precisa|deseja|utiliza|utilizar|aplica[cç][aã]o|inst[aâ]ncia|regi[aã]o|"
    r"disponibilidade|faturamento|custo|custos|acesso|recurso|recursos)\b",
    re.I,
)


def source_map(cert: str, level: str) -> dict[str, dict]:
    path = EXAMS / cert / f"{level}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {q["id"]: q for q in payload.get("questions", [])}


def staged_targets():
    if not STAGING.exists():
        return
    for cert_dir in sorted(p for p in STAGING.iterdir() if p.is_dir()):
        for level_dir in sorted(p for p in cert_dir.iterdir() if p.is_dir()):
            yield cert_dir.name, level_dir.name, level_dir


def _check_text_field(qid: str, source: dict, item: dict, field: str, errors: list[str], location: str):
    if field not in source:
        return
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{location}::{qid}: empty {field}")
        return
    src = source.get(field, "")
    if len(src) >= 24 and norm(value) == norm(src):
        errors.append(f"{location}::{qid}: {field} copied unchanged from PT source")
    markers = PT_MARKERS.findall(value)
    if len(markers) >= 3:
        errors.append(f"{location}::{qid}: probable Portuguese residue in {field}: {markers[:5]}")


def validate_item(qid: str, source: dict, item: dict, errors: list[str], location: str):
    for field in ("text", "explanation", "hint"):
        _check_text_field(qid, source, item, field, errors, location)

    options = item.get("options")
    src_options = source.get("options") or []
    if not isinstance(options, list) or len(options) != len(src_options):
        errors.append(f"{location}::{qid}: option cardinality mismatch")
    else:
        for index, (src, translated) in enumerate(zip(src_options, options)):
            if not isinstance(translated, str) or not translated.strip():
                errors.append(f"{location}::{qid}: empty option {index}")
            elif len(src) >= 28 and norm(src) == norm(translated) and PT_MARKERS.search(src):
                errors.append(f"{location}::{qid}: option {index} copied unchanged from PT")

    if "optionRationales" in source:
        rationales = item.get("optionRationales")
        src_rationales = source.get("optionRationales") or []
        if not isinstance(rationales, list) or len(rationales) != len(src_rationales):
            errors.append(f"{location}::{qid}: optionRationales cardinality mismatch")
        else:
            for index, (src, translated) in enumerate(zip(src_rationales, rationales)):
                if not isinstance(translated, str) or not translated.strip():
                    errors.append(f"{location}::{qid}: empty optionRationale {index}")
                elif len(src) >= 32 and norm(src) == norm(translated) and PT_MARKERS.search(src):
                    errors.append(f"{location}::{qid}: optionRationale {index} copied unchanged from PT")

    for detail in question_anchor_errors(source, item):
        errors.append(f"{location}::{qid}: {detail}")


def main() -> int:
    errors: list[str] = []
    checked = 0

    for cert, level, directory in staged_targets() or []:
        source = source_map(cert, level)
        for path in sorted(directory.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for qid, item in (payload.get("questions") or {}).items():
                if qid not in source:
                    continue
                validate_item(qid, source[qid], item, errors, str(path.relative_to(ROOT)))
                checked += 1

    if errors:
        print(f"English translation quality validation failed: {len(errors)} issue(s)")
        for error in errors[:250]:
            print(f"  - {error}")
        if len(errors) > 250:
            print(f"  ... and {len(errors) - 250} more")
        return 1

    print(f"English translation quality validation passed: {checked} staged questions checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
