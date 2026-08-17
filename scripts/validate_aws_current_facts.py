#!/usr/bin/env python3
"""Guard a small set of time-sensitive AWS facts in exam content.

This validator intentionally targets claims we have verified against current AWS
primary documentation. It is narrow by design: broader certification-content
fact review should add explicit rules as facts are verified rather than guessing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "data" / "exams"

LEGACY_FREE_TIER_PATTERNS = [
    re.compile(r"free tier.{0,120}12\s+mes", re.I | re.S),
    re.compile(r"12\s+mes.{0,120}free tier", re.I | re.S),
    re.compile(r"servi[cç]os gratuitos.{0,80}12\s+mes", re.I | re.S),
    re.compile(r"12-month.{0,80}free tier", re.I | re.S),
]


def iter_human_text(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_human_text(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {"id", "domain", "correct", "selectCount", "topics"}:
                continue
            yield from iter_human_text(item)


def main() -> int:
    errors = []
    for path in sorted(EXAMS.glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for question in data.get("questions", []):
            combined = " ".join(iter_human_text(question))
            for pattern in LEGACY_FREE_TIER_PATTERNS:
                if pattern.search(combined):
                    errors.append(
                        f"{path.relative_to(ROOT)}::{question.get('id')}: legacy 12-month AWS Free Tier claim detected"
                    )
                    break

    if errors:
        print("AWS current-fact validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("AWS current-fact validation passed: no legacy 12-month Free Tier claims detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
