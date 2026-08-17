#!/usr/bin/env python3
"""Validate staged exam translations and build a complete EN bank when ready.

Staging lives under:
  translations/en/<cert>/<level>/*.json

A batch contains human-language fields only, keyed by stable question id. The
builder always takes structural fields from the canonical PT source, so a
translator cannot accidentally alter answer indexes, domains, topics or IDs.

Examples:
  # Validate current staged coverage (partial coverage is allowed)
  python3 scripts/build_exam_translation.py clf-c02 iniciante --check

  # Require 100% coverage without writing output
  python3 scripts/build_exam_translation.py clf-c02 iniciante --require-complete

  # Build data/exams-en/... only when 100% complete and valid
  python3 scripts/build_exam_translation.py clf-c02 iniciante --write
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "data" / "exams"
STAGING_ROOT = ROOT / "translations" / "en"
OUTPUT_ROOT = ROOT / "data" / "exams-en"
TRANSLATABLE_FIELDS = ("text", "options", "explanation", "hint", "optionRationales")


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return payload


def source_questions(payload: dict, path: Path) -> tuple[list[str], dict[str, dict]]:
    questions = payload.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError(f"{path.relative_to(ROOT)}: missing non-empty questions list")
    order: list[str] = []
    mapping: dict[str, dict] = {}
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            raise ValueError(f"{path.relative_to(ROOT)}: question #{index + 1} is not an object")
        qid = question.get("id")
        if not isinstance(qid, str) or not qid:
            raise ValueError(f"{path.relative_to(ROOT)}: question #{index + 1} has no stable id")
        if qid in mapping:
            raise ValueError(f"{path.relative_to(ROOT)}: duplicate question id {qid}")
        order.append(qid)
        mapping[qid] = question
    return order, mapping


def load_domain_labels(cert_id: str, source: dict) -> dict[str, str]:
    path = STAGING_ROOT / cert_id / "domains.json"
    payload = load_json(path)
    meta = payload.get("_meta") or {}
    if meta.get("locale") != "en" or meta.get("certId") != cert_id or meta.get("sourceLocale") != "pt-BR":
        raise ValueError(f"{path.relative_to(ROOT)}: invalid translation metadata")
    labels = payload.get("domains")
    if not isinstance(labels, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: domains must be an object")

    source_ids = {
        d.get("id") for d in (source.get("domains") or [])
        if isinstance(d, dict) and isinstance(d.get("id"), str)
    }
    label_ids = set(labels)
    if source_ids != label_ids:
        missing = sorted(source_ids - label_ids)
        extra = sorted(label_ids - source_ids)
        details = []
        if missing:
            details.append("missing=" + ", ".join(missing))
        if extra:
            details.append("extra=" + ", ".join(extra))
        raise ValueError(f"{path.relative_to(ROOT)}: domain id mismatch ({'; '.join(details)})")
    for domain_id, label in labels.items():
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"{path.relative_to(ROOT)}: empty English label for domain {domain_id}")
    return labels


def batch_files(cert_id: str, level: str) -> list[Path]:
    directory = STAGING_ROOT / cert_id / level
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def validate_batch_meta(path: Path, payload: dict, cert_id: str, level: str) -> None:
    meta = payload.get("_batch")
    if not isinstance(meta, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: missing _batch metadata")
    expected = {
        "locale": "en",
        "sourceLocale": "pt-BR",
        "certId": cert_id,
        "level": level,
        "sourcePath": f"data/exams/{cert_id}/{level}.json",
    }
    for key, value in expected.items():
        if meta.get(key) != value:
            raise ValueError(f"{path.relative_to(ROOT)}: _batch.{key} must be {value!r}")


def require_nonempty_string(value: object, context: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: translation must be a non-empty string")


def validate_translation_entry(qid: str, source: dict, translated: dict, path: Path) -> None:
    if not isinstance(translated, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: {qid} translation must be an object")

    forbidden = sorted(set(translated) - set(TRANSLATABLE_FIELDS))
    if forbidden:
        raise ValueError(
            f"{path.relative_to(ROOT)}: {qid} contains non-translatable/structural fields: {', '.join(forbidden)}"
        )

    required = [field for field in TRANSLATABLE_FIELDS if field in source]
    missing = [field for field in required if field not in translated]
    extra_human = [field for field in translated if field not in source]
    if missing:
        raise ValueError(f"{path.relative_to(ROOT)}: {qid} missing translated fields: {', '.join(missing)}")
    if extra_human:
        raise ValueError(f"{path.relative_to(ROOT)}: {qid} translates fields not present in source: {', '.join(extra_human)}")

    for field in required:
        src = source[field]
        dst = translated[field]
        if isinstance(src, str):
            require_nonempty_string(dst, f"{path.relative_to(ROOT)}:{qid}.{field}")
        elif isinstance(src, list):
            if not isinstance(dst, list):
                raise ValueError(f"{path.relative_to(ROOT)}: {qid}.{field} must remain a list")
            if len(src) != len(dst):
                raise ValueError(
                    f"{path.relative_to(ROOT)}: {qid}.{field} length changed ({len(src)} -> {len(dst)})"
                )
            for index, value in enumerate(dst):
                require_nonempty_string(value, f"{path.relative_to(ROOT)}:{qid}.{field}[{index}]")
        else:
            raise ValueError(f"{path.relative_to(ROOT)}: unsupported translatable field type {qid}.{field}")


def load_staged_translations(cert_id: str, level: str, source_map: dict[str, dict]) -> tuple[dict[str, dict], list[Path]]:
    staged: dict[str, dict] = {}
    files = batch_files(cert_id, level)
    for path in files:
        payload = load_json(path)
        validate_batch_meta(path, payload, cert_id, level)
        questions = payload.get("questions")
        if not isinstance(questions, dict) or not questions:
            raise ValueError(f"{path.relative_to(ROOT)}: questions must be a non-empty object")
        for qid, translated in questions.items():
            if qid not in source_map:
                raise ValueError(f"{path.relative_to(ROOT)}: unknown question id {qid}")
            if qid in staged:
                raise ValueError(f"{path.relative_to(ROOT)}: duplicate staged translation for {qid}")
            validate_translation_entry(qid, source_map[qid], translated, path)
            staged[qid] = translated
    return staged, files


def build_payload(source: dict, source_order: list[str], staged: dict[str, dict], domain_labels: dict[str, str], cert_id: str, level: str) -> dict:
    payload = copy.deepcopy(source)
    for domain in payload.get("domains") or []:
        if isinstance(domain, dict) and domain.get("id") in domain_labels:
            domain["name"] = domain_labels[domain["id"]]

    by_id = {q["id"]: q for q in payload.get("questions") or []}
    for qid in source_order:
        target = by_id[qid]
        for field, value in staged[qid].items():
            target[field] = copy.deepcopy(value)

    payload["_translation"] = {
        "locale": "en",
        "sourceLocale": "pt-BR",
        "sourcePath": f"data/exams/{cert_id}/{level}.json",
        "status": "ready",
        "buildMode": "staged-overlays",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cert_id", help="certification id, e.g. clf-c02")
    parser.add_argument("level", choices=("iniciante", "medio", "avancado"))
    parser.add_argument("--check", action="store_true", help="validate staged batches; partial coverage is allowed")
    parser.add_argument("--require-complete", action="store_true", help="fail unless every source question has a staged translation")
    parser.add_argument("--write", action="store_true", help="build data/exams-en only when coverage is complete")
    args = parser.parse_args()

    cert_id = args.cert_id.strip().lower()
    level = args.level
    source_path = SOURCE_ROOT / cert_id / f"{level}.json"

    try:
        source = load_json(source_path)
        order, source_map = source_questions(source, source_path)
        domain_labels = load_domain_labels(cert_id, source)
        staged, files = load_staged_translations(cert_id, level, source_map)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    missing = [qid for qid in order if qid not in staged]
    coverage = len(staged) / len(order) * 100
    print(
        f"EN staging {cert_id}/{level}: {len(staged)}/{len(order)} questions "
        f"({coverage:.1f}%) across {len(files)} batch file(s)."
    )

    require_complete = args.require_complete or args.write
    if missing:
        preview = ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else "")
        print(f"Missing: {preview}")
        if require_complete:
            print("ERROR: complete coverage is required for this operation")
            return 1
        print("Staged translations are structurally valid; output bank was not generated.")
        return 0

    print("Coverage complete: every source question has a valid English overlay.")
    if args.write:
        output_path = OUTPUT_ROOT / cert_id / f"{level}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output = build_payload(source, order, staged, domain_labels, cert_id, level)
        output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Built: {output_path.relative_to(ROOT)}")
    elif not args.check:
        print("Use --write to build the ready EN bank.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
