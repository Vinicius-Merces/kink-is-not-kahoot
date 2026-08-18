#!/usr/bin/env python3
"""Discover and validate every staged English exam translation target."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING_ROOT = ROOT / "translations" / "en"
BUILDER = ROOT / "scripts" / "build_exam_translation.py"
LEVELS = {"iniciante", "medio", "avancado"}


def targets() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if not STAGING_ROOT.exists():
        return found
    for cert_dir in sorted(path for path in STAGING_ROOT.iterdir() if path.is_dir()):
        for level_dir in sorted(path for path in cert_dir.iterdir() if path.is_dir()):
            if level_dir.name not in LEVELS:
                continue
            if any(level_dir.glob("*.json")):
                found.append((cert_dir.name, level_dir.name))
    return found


def main() -> int:
    discovered = targets()
    if not discovered:
        print("Exam translation staging OK: no staged question batches yet.")
        return 0

    failures = 0
    for cert_id, level in discovered:
        print(f"\n== {cert_id}/{level} ==")
        result = subprocess.run(
            [sys.executable, str(BUILDER), cert_id, level, "--check"],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            failures += 1

    if failures:
        print(f"\nERROR: {failures} staged translation target(s) failed validation.")
        return 1

    print(f"\nExam translation staging OK: {len(discovered)} target(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
