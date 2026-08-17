#!/usr/bin/env python3
"""Validate structural parity between canonical PT exam banks and EN translations.

Portuguese banks remain in data/exams/<cert>/<level>.json.
English translations are added incrementally under data/exams-en/<cert>/<level>.json.

The translated bank may change human-language fields (question text, options,
explanations and domain display names), but it must never change assessment
semantics such as IDs, domain membership, correct indexes or option counts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "data" / "exams"
EN_ROOT = ROOT / "data" / "exams-en"
LEVELS = {"iniciante", "medio", "avancado"}
TRANSLATION_STATUSES = {"draft", "ready"}


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"root must be an object: {path.relative_to(ROOT)}")
    return value


def question_map(payload: dict, path: Path) -> tuple[list[str], dict[str, dict]]:
    questions = payload.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError(f"{path.relative_to(ROOT)}: missing non-empty questions list")
    ids: list[str] = []
    mapped: dict[str, dict] = {}
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            raise ValueError(f"{path.relative_to(ROOT)}: question #{index + 1} is not an object")
        qid = question.get("id")
        if not isinstance(qid, str) or not qid:
            raise ValueError(f"{path.relative_to(ROOT)}: question #{index + 1} has no stable id")
        if qid in mapped:
            raise ValueError(f"{path.relative_to(ROOT)}: duplicate question id {qid}")
        ids.append(qid)
        mapped[qid] = question
    return ids, mapped


def domain_map(payload: dict) -> dict[str, dict]:
    domains = payload.get("domains") or []
    result: dict[str, dict] = {}
    for domain in domains:
        if isinstance(domain, dict) and isinstance(domain.get("id"), str):
            result[domain["id"]] = domain
    return result


def validate_translation_meta(payload: dict, path: Path, require_ready: bool) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    meta = payload.get("_translation")
    if not isinstance(meta, dict):
        return [f"{rel}: missing _translation metadata; generate the file with scaffold_exam_translation.py"]

    if meta.get("locale") != "en":
        errors.append(f"{rel}: _translation.locale must be 'en'")
    if meta.get("sourceLocale") != "pt-BR":
        errors.append(f"{rel}: _translation.sourceLocale must be 'pt-BR'")

    status = meta.get("status")
    if status not in TRANSLATION_STATUSES:
        errors.append(f"{rel}: _translation.status must be one of {sorted(TRANSLATION_STATUSES)}")
    elif require_ready and status != "ready":
        errors.append(f"{rel}: translation is required to be ready but status is {status!r}")

    expected_source = str((SOURCE_ROOT / path.parent.name / path.name).relative_to(ROOT)).replace("\\", "/")
    if meta.get("sourcePath") != expected_source:
        errors.append(f"{rel}: _translation.sourcePath must be '{expected_source}'")
    return errors


def same_value(left, right) -> bool:
    return left == right


def validate_pair(source_path: Path, translated_path: Path, require_ready: bool = False) -> list[str]:
    errors: list[str] = []
    source = read_json(source_path)
    translated = read_json(translated_path)
    rel = translated_path.relative_to(ROOT)

    errors.extend(validate_translation_meta(translated, translated_path, require_ready))

    source_ids, source_questions = question_map(source, source_path)
    translated_ids, translated_questions = question_map(translated, translated_path)

    source_set = set(source_ids)
    translated_set = set(translated_ids)
    missing = sorted(source_set - translated_set)
    extra = sorted(translated_set - source_set)
    if missing:
        errors.append(f"{rel}: missing question IDs: {', '.join(missing[:12])}" + (" ..." if len(missing) > 12 else ""))
    if extra:
        errors.append(f"{rel}: unknown question IDs: {', '.join(extra[:12])}" + (" ..." if len(extra) > 12 else ""))
    if len(source_ids) != len(translated_ids):
        errors.append(f"{rel}: question count changed ({len(source_ids)} -> {len(translated_ids)})")

    source_domains = domain_map(source)
    translated_domains = domain_map(translated)
    if set(source_domains) != set(translated_domains):
        errors.append(
            f"{rel}: domain IDs changed (source={sorted(source_domains)}, en={sorted(translated_domains)})"
        )
    for domain_id in sorted(set(source_domains) & set(translated_domains)):
        src = source_domains[domain_id]
        dst = translated_domains[domain_id]
        # Domain names are localizable. Every other metadata field is structural.
        for key in sorted((set(src) | set(dst)) - {"name"}):
            if not same_value(src.get(key), dst.get(key)):
                errors.append(f"{rel}: domain {domain_id} changed structural field '{key}'")

    for qid in sorted(source_set & translated_set):
        src = source_questions[qid]
        dst = translated_questions[qid]

        for field in ("domain", "correct", "selectCount", "topics"):
            if not same_value(src.get(field), dst.get(field)):
                errors.append(f"{rel}: {qid} changed '{field}' ({src.get(field)!r} -> {dst.get(field)!r})")

        src_options = src.get("options")
        dst_options = dst.get("options")
        if not isinstance(src_options, list) or not isinstance(dst_options, list):
            errors.append(f"{rel}: {qid} must keep an options list in both locales")
        elif len(src_options) != len(dst_options):
            errors.append(f"{rel}: {qid} option count changed ({len(src_options)} -> {len(dst_options)})")

    return errors


def translated_files() -> list[Path]:
    if not EN_ROOT.exists():
        return []
    return sorted(EN_ROOT.glob("*/*.json"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-cert",
        action="append",
        default=[],
        help="require all three EN level files for the certification and require status=ready; may be repeated",
    )
    args = parser.parse_args()

    errors: list[str] = []
    files = translated_files()
    required = {cert.strip().lower() for cert in args.require_cert if cert.strip()}

    for cert_id in required:
        for level in sorted(LEVELS):
            expected = EN_ROOT / cert_id / f"{level}.json"
            if not expected.exists():
                errors.append(f"missing required translated bank: {expected.relative_to(ROOT)}")

    for translated_path in files:
        cert_id = translated_path.parent.name
        level = translated_path.stem
        if level not in LEVELS:
            errors.append(f"{translated_path.relative_to(ROOT)}: unsupported level filename '{level}.json'")
            continue
        source_path = SOURCE_ROOT / cert_id / translated_path.name
        if not source_path.exists():
            errors.append(f"{translated_path.relative_to(ROOT)}: no canonical PT source bank exists")
            continue
        try:
            errors.extend(validate_pair(source_path, translated_path, require_ready=cert_id in required))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        print("Exam locale parity validation failed:\n")
        for error in errors:
            print(f"  - {error}")
        return 1

    if not files:
        print("Exam locale parity OK: EN bank directory has no translated JSON files yet; contract is ready.")
    else:
        ready_count = 0
        for path in files:
            try:
                if read_json(path).get("_translation", {}).get("status") == "ready":
                    ready_count += 1
            except ValueError:
                pass
        print(
            f"Exam locale parity OK: {len(files)} translated bank file(s) match canonical PT structure "
            f"({ready_count} ready, {len(files) - ready_count} draft)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
