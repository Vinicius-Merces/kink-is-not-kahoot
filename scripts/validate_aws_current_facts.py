#!/usr/bin/env python3
"""Guard verified time-sensitive AWS facts in truth-bearing exam fields.

Distractors are intentionally allowed to contain false statements, so this check
scans only the question prompt, explanation and the option(s) marked correct.
Broader fact rules should be added only after verification against AWS primary docs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "data" / "exams"

LEGACY_FREE_TIER_PATTERNS = [
    re.compile(r"free tier.{0,140}12\s+mes", re.I | re.S),
    re.compile(r"12\s+mes.{0,140}free tier", re.I | re.S),
    re.compile(r"12-month.{0,100}free tier", re.I | re.S),
    re.compile(r"free tier.{0,100}12-month", re.I | re.S),
]


def correct_option_text(question: dict) -> list[str]:
    options = question.get("options") or []
    correct = question.get("correct")
    indexes = correct if isinstance(correct, list) else [correct]
    result = []
    for index in indexes:
        if isinstance(index, int) and 0 <= index < len(options):
            result.append(str(options[index]))
    return result


def truth_text(question: dict) -> str:
    parts = [str(question.get("text") or ""), str(question.get("explanation") or "")]
    parts.extend(correct_option_text(question))
    return " ".join(parts)


def main() -> int:
    errors = []
    for path in sorted(EXAMS.glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for question in data.get("questions", []):
            combined = truth_text(question)
            if any(pattern.search(combined) for pattern in LEGACY_FREE_TIER_PATTERNS):
                errors.append(
                    f"{path.relative_to(ROOT)}::{question.get('id')}: legacy 12-month AWS Free Tier claim is presented as truth"
                )

    if errors:
        print("AWS current-fact validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("AWS current-fact validation passed: no legacy 12-month Free Tier claim is taught as current truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
