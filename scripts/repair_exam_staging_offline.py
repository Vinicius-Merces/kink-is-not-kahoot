#!/usr/bin/env python3
"""Repair field-local PT->EN translation drift with offline Marian MT.

Only human-language staging fields under translations/en/** are changed. The
canonical PT bank keeps IDs, domains, answer keys and option order. Fields that
already pass integrity checks are left untouched to preserve higher-quality prose.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from offline_mt import OfflineTranslator
from translation_integrity import question_anchor_errors

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "data" / "exams"
STAGING = ROOT / "translations" / "en"
LABEL_RE = re.compile(r"^(text|explanation|hint|option\[(\d+)\]|optionRationale\[(\d+)\]):")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_maps():
    result = {}
    for cert_dir in EXAMS.iterdir():
        if not cert_dir.is_dir():
            continue
        for path in cert_dir.glob("*.json"):
            payload = load_json(path)
            result[(cert_dir.name, path.stem)] = {q["id"]: q for q in payload.get("questions", [])}
    return result


def collect(request: dict):
    maps = source_maps()
    cert_filter = request.get("certId")
    level_filter = request.get("level")
    qid_filter = set(request.get("questionIds") or [])
    file_payloads = {}
    candidates = []
    for cert_dir in sorted(p for p in STAGING.iterdir() if p.is_dir()):
        if cert_filter and cert_dir.name != cert_filter:
            continue
        for level_dir in sorted(p for p in cert_dir.iterdir() if p.is_dir()):
            if level_filter and level_dir.name != level_filter:
                continue
            source = maps.get((cert_dir.name, level_dir.name), {})
            for path in sorted(level_dir.glob("*.json")):
                payload = load_json(path)
                file_payloads[path] = payload
                for qid, item in (payload.get("questions") or {}).items():
                    if qid_filter and qid not in qid_filter:
                        continue
                    src = source.get(qid)
                    if not src:
                        continue
                    issues = question_anchor_errors(src, item)
                    if issues:
                        candidates.append((path, qid, src, item, issues))
    return candidates, file_payloads


def field_specs(source: dict, issues: list[str]):
    specs = []
    seen = set()
    for issue in issues:
        match = LABEL_RE.match(issue)
        if not match:
            continue
        label = match.group(1)
        if label in seen:
            continue
        seen.add(label)
        if label.startswith("option["):
            idx = int(match.group(2))
            specs.append((label, source["options"][idx]))
        elif label.startswith("optionRationale["):
            idx = int(match.group(3))
            specs.append((label, source["optionRationales"][idx]))
        else:
            specs.append((label, source[label]))
    return specs


def apply_field(item: dict, label: str, value: str):
    if label.startswith("option["):
        idx = int(re.search(r"\d+", label).group())
        item["options"][idx] = value
    elif label.startswith("optionRationale["):
        idx = int(re.search(r"\d+", label).group())
        item["optionRationales"][idx] = value
    else:
        item[label] = value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    args = parser.parse_args()
    request_path = (ROOT / args.request).resolve()
    if ROOT not in request_path.parents:
        raise ValueError("request path escapes repository")
    request = load_json(request_path)

    candidates, file_payloads = collect(request)
    if not candidates:
        print("No field-local translation drift detected")
        return 0

    translation_sources = []
    jobs = []
    for path, qid, source, item, issues in candidates:
        for label, source_text in field_specs(source, issues):
            jobs.append((path, qid, source, item, label))
            translation_sources.append(source_text)

    print(f"Detected {len(candidates)} question(s) / {len(jobs)} field(s) requiring faithful retranslation")
    translator = OfflineTranslator()
    translated = translator.translate_many(translation_sources, batch_size=10)

    changed_paths = set()
    for job, value in zip(jobs, translated):
        path, qid, _source, item, label = job
        apply_field(item, label, value)
        changed_paths.add(path)

    # Validate the complete repaired question before any file is written.
    failures = []
    for path, qid, source, item, _issues in candidates:
        remaining = question_anchor_errors(source, item)
        if remaining:
            failures.append(f"{path.relative_to(ROOT)}::{qid}: {remaining}")
    if failures:
        raise RuntimeError("Offline repair still violates integrity:\n  " + "\n  ".join(failures[:100]))

    for path in sorted(changed_paths):
        path.write_text(json.dumps(file_payloads[path], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"repaired: {path.relative_to(ROOT)}")
    print(f"Repaired {len(jobs)} field(s) across {len(changed_paths)} staging file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
