#!/usr/bin/env python3
"""Create safe English translation scaffolds from canonical PT exam banks.

The scaffold intentionally keeps source-language copy in place and marks the
file as `draft`. Translators edit only human-language fields while IDs, answer
order, correct indexes, domains and topics remain structurally frozen.

Examples:
  python3 scripts/scaffold_exam_translation.py clf-c02
  python3 scripts/scaffold_exam_translation.py clf-c02 --level iniciante
  python3 scripts/scaffold_exam_translation.py clf-c02 --force
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "data" / "exams"
OUTPUT_ROOT = ROOT / "data" / "exams-en"
LEVELS = ("iniciante", "medio", "avancado")


def read_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"source bank not found: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"bank root must be an object: {path.relative_to(ROOT)}")
    return payload


def scaffold_payload(source: dict, source_path: Path) -> dict:
    payload = copy.deepcopy(source)
    payload["_translation"] = {
        "locale": "en",
        "sourceLocale": "pt-BR",
        "sourcePath": str(source_path.relative_to(ROOT)).replace("\\", "/"),
        "status": "draft",
        "instructions": "Translate text/options/explanation/domain names only. Preserve IDs, option order, correct indexes, domains and topics."
    }
    return payload


def write_scaffold(cert_id: str, level: str, force: bool) -> Path:
    source_path = SOURCE_ROOT / cert_id / f"{level}.json"
    target_path = OUTPUT_ROOT / cert_id / f"{level}.json"
    if target_path.exists() and not force:
        raise ValueError(
            f"refusing to overwrite {target_path.relative_to(ROOT)}; use --force only if you intentionally want to reset translated copy"
        )

    source = read_json(source_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(scaffold_payload(source, source_path), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cert_id", help="certification id, e.g. clf-c02")
    parser.add_argument("--level", choices=LEVELS, help="generate only one level; default generates all three")
    parser.add_argument("--force", action="store_true", help="overwrite an existing EN scaffold")
    args = parser.parse_args()

    cert_id = args.cert_id.strip().lower()
    cert_dir = SOURCE_ROOT / cert_id
    if not cert_dir.exists():
        print(f"ERROR: unknown certification source directory: {cert_dir.relative_to(ROOT)}")
        return 1

    levels = (args.level,) if args.level else LEVELS
    created: list[Path] = []
    try:
        for level in levels:
            created.append(write_scaffold(cert_id, level, args.force))
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    print("English translation scaffold created:")
    for path in created:
        print(f"  - {path.relative_to(ROOT)}")
    print("\nNext: translate human-language fields, set _translation.status to 'ready' only after review, then run:")
    print("  python3 scripts/validate_exam_locale_parity.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
