#!/usr/bin/env python3
"""Discover and promote every complete staged English exam translation.

A target is considered complete only when the set of staged question IDs exactly
matches the canonical PT bank. Partial targets are reported and skipped. Complete
targets are delegated to build_exam_translation.py with --require-complete and
--write, so all existing structural safeguards remain the source of truth.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING_ROOT = ROOT / "translations" / "en"
BUILDER = ROOT / "scripts" / "build_exam_translation.py"


def staged_ids(target_dir: Path) -> set[str]:
    ids: set[str] = set()
    for path in sorted(target_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        questions = payload.get("questions", {})
        if not isinstance(questions, dict):
            raise RuntimeError(f"{path.relative_to(ROOT)}: questions must be an object keyed by question ID")
        duplicates = ids.intersection(questions)
        if duplicates:
            raise RuntimeError(f"{path.relative_to(ROOT)}: duplicate staged IDs: {sorted(duplicates)}")
        ids.update(questions)
    return ids


def source_ids(cert: str, level: str) -> set[str]:
    source = ROOT / "data" / "exams" / cert / f"{level}.json"
    if not source.exists():
        raise RuntimeError(f"Canonical source missing for staged target: {cert}/{level}")
    payload = json.loads(source.read_text(encoding="utf-8"))
    return {q["id"] for q in payload.get("questions", [])}


def promote(cert: str, level: str) -> None:
    command = [sys.executable, str(BUILDER), cert, level]
    subprocess.run(command + ["--require-complete"], cwd=ROOT, check=True)
    subprocess.run(command + ["--write"], cwd=ROOT, check=True)


def main() -> int:
    promoted = []
    partial = []

    if not STAGING_ROOT.exists():
        print("No English staging root found; nothing to promote")
        return 0

    for cert_dir in sorted(p for p in STAGING_ROOT.iterdir() if p.is_dir()):
        for level_dir in sorted(p for p in cert_dir.iterdir() if p.is_dir()):
            cert = cert_dir.name
            level = level_dir.name
            expected = source_ids(cert, level)
            staged = staged_ids(level_dir)

            unknown = staged - expected
            if unknown:
                raise RuntimeError(f"{cert}/{level}: staged IDs not present in canonical bank: {sorted(unknown)}")

            missing = expected - staged
            if missing:
                partial.append((cert, level, len(staged), len(expected)))
                print(f"partial: {cert}/{level} {len(staged)}/{len(expected)}; promotion skipped")
                continue

            if staged != expected:
                raise RuntimeError(f"{cert}/{level}: staging coverage mismatch")

            promote(cert, level)
            promoted.append((cert, level, len(expected)))
            print(f"promoted: {cert}/{level} {len(expected)}/{len(expected)}")

    print(f"Promotion summary: {len(promoted)} ready target(s), {len(partial)} partial target(s)")
    for cert, level, count in promoted:
        print(f"  ready  {cert}/{level}: {count} questions")
    for cert, level, done, total in partial:
        print(f"  partial {cert}/{level}: {done}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
