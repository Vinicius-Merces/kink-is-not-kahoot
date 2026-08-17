#!/usr/bin/env python3
"""Prepare CloudArena overlays for language-independent option IDs.

Current overlays bind metadata to the Portuguese option text through matchText.
That is safe only while the question bank is Portuguese. This tool defines the
stable migration contract without breaking the current runtime:

    <questionId>:option:<zero-based-index>

During the migration, overlays can carry BOTH fields:

    {
      "optionId": "clf-ini-001:option:2",
      "matchText": "...",
      "stage": "correct"
    }

`matchText` remains for backwards compatibility until server.js switches to
optionId/index resolution. English banks must preserve the same question IDs,
correct index and option ordering during this transition.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMS_ROOT = ROOT / "data" / "exams"
OVERLAYS_ROOT = ROOT / "data" / "cloudarena" / "breakdowns"
LEVELS = ("iniciante", "medio", "avancado")


def load_questions(cert_id: str) -> dict[str, dict]:
    questions: dict[str, dict] = {}
    cert_root = EXAMS_ROOT / cert_id
    for level in LEVELS:
        path = cert_root / f"{level}.json"
        if not path.exists():
            continue
        bank = json.loads(path.read_text(encoding="utf-8"))
        for question in bank.get("questions", []):
            qid = question.get("id")
            if not qid:
                raise ValueError(f"{path}: question without id")
            if qid in questions:
                raise ValueError(f"duplicate question id {qid} in {cert_id}")
            questions[qid] = question
    return questions


def option_id(question_id: str, index: int) -> str:
    return f"{question_id}:option:{index}"


def resolve_option_index(options: list[str], match_text: str) -> int:
    indexes = [index for index, text in enumerate(options) if text == match_text]
    if len(indexes) != 1:
        raise ValueError(
            f"matchText must resolve exactly once, got {len(indexes)} matches for {match_text!r}"
        )
    return indexes[0]


def process_cert(cert_id: str, write: bool, require_ids: bool) -> tuple[int, int]:
    overlay_path = OVERLAYS_ROOT / f"{cert_id}.json"
    if not overlay_path.exists():
        return 0, 0

    questions = load_questions(cert_id)
    document = json.loads(overlay_path.read_text(encoding="utf-8"))
    overlays = document.get("overlays", [])
    changed = False
    option_count = 0

    for overlay in overlays:
        qid = overlay.get("questionId")
        question = questions.get(qid)
        if not question:
            raise ValueError(f"{cert_id}: overlay references unknown question {qid}")

        bank_options = question.get("options", [])
        if not isinstance(bank_options, list) or not bank_options:
            raise ValueError(f"{cert_id}:{qid}: question has no options")

        seen_ids: set[str] = set()
        correct_option_id = option_id(qid, int(question.get("correct", -1)))
        correct_overlay_id = None

        for overlay_option in overlay.get("options", []):
            option_count += 1
            match_text = overlay_option.get("matchText")
            if not isinstance(match_text, str):
                raise ValueError(f"{cert_id}:{qid}: overlay option missing matchText")

            index = resolve_option_index(bank_options, match_text)
            expected_id = option_id(qid, index)
            current_id = overlay_option.get("optionId")

            if current_id and current_id != expected_id:
                raise ValueError(
                    f"{cert_id}:{qid}: optionId {current_id!r} does not match {expected_id!r}"
                )
            if require_ids and not current_id:
                raise ValueError(f"{cert_id}:{qid}: missing optionId for {match_text!r}")
            if write and current_id != expected_id:
                overlay_option["optionId"] = expected_id
                changed = True

            if expected_id in seen_ids:
                raise ValueError(f"{cert_id}:{qid}: duplicate overlay option {expected_id}")
            seen_ids.add(expected_id)

            if overlay_option.get("stage") == "correct":
                if correct_overlay_id is not None:
                    raise ValueError(f"{cert_id}:{qid}: multiple correct overlay options")
                correct_overlay_id = expected_id

        expected_ids = {option_id(qid, index) for index in range(len(bank_options))}
        if seen_ids != expected_ids:
            missing = sorted(expected_ids - seen_ids)
            extra = sorted(seen_ids - expected_ids)
            raise ValueError(
                f"{cert_id}:{qid}: overlay option coverage mismatch; missing={missing}, extra={extra}"
            )
        if correct_overlay_id != correct_option_id:
            raise ValueError(
                f"{cert_id}:{qid}: overlay correct option {correct_overlay_id} != bank {correct_option_id}"
            )

    if write and changed:
        overlay_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return len(overlays), option_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="enrich overlays with optionId")
    parser.add_argument(
        "--require-ids",
        action="store_true",
        help="fail if any overlay option has not been migrated yet",
    )
    args = parser.parse_args()

    cert_ids = sorted(path.stem for path in OVERLAYS_ROOT.glob("*.json"))
    total_overlays = 0
    total_options = 0

    try:
        for cert_id in cert_ids:
            overlays, options = process_cert(cert_id, args.write, args.require_ids)
            total_overlays += overlays
            total_options += options
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"CloudArena option ID validation failed: {exc}")
        return 1

    action = "migrated" if args.write else "validated"
    print(
        f"CloudArena option IDs {action}: {len(cert_ids)} certifications, "
        f"{total_overlays} overlays, {total_options} options."
    )
    if not args.write and not args.require_ids:
        print("Run with --write to add optionId while keeping matchText compatibility.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
