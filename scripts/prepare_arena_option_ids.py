#!/usr/bin/env python3
"""Prepare CloudArena overlays for language-independent option IDs.

Stable identity contract:

    <questionId>:option:<zero-based-index>

Migration rules:
- Legacy entries without optionId are resolved once from matchText.
- Entries that already have optionId are resolved from the ID, never from text.
- With --write, matchText is synchronized to the current canonical PT option text
  for human readability only. Runtime/validation identity remains optionId.
- The correct stage must point to the canonical `correct` option index.

This lets question wording evolve or be localized without breaking CloudArena.
"""

from __future__ import annotations

import argparse
import json
import re
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


def parse_option_id(question_id: str, value: str, option_count: int) -> int:
    if not isinstance(value, str):
        raise ValueError(f"{question_id}: optionId must be a string")
    match = re.fullmatch(re.escape(question_id) + r":option:(\d+)", value)
    if not match:
        raise ValueError(f"{question_id}: malformed optionId {value!r}")
    index = int(match.group(1))
    if index < 0 or index >= option_count:
        raise ValueError(
            f"{question_id}: optionId index {index} outside 0..{option_count - 1}"
        )
    return index


def resolve_option_index(options: list[str], match_text: str) -> int:
    indexes = [index for index, text in enumerate(options) if text == match_text]
    if len(indexes) != 1:
        raise ValueError(
            f"matchText must resolve exactly once, got {len(indexes)} matches for {match_text!r}"
        )
    return indexes[0]


def process_cert(cert_id: str, write: bool, require_ids: bool) -> tuple[int, int, int]:
    overlay_path = OVERLAYS_ROOT / f"{cert_id}.json"
    if not overlay_path.exists():
        return 0, 0, 0

    questions = load_questions(cert_id)
    document = json.loads(overlay_path.read_text(encoding="utf-8"))
    overlays = document.get("overlays", [])
    changed = False
    option_count = 0
    text_sync_count = 0

    for overlay in overlays:
        qid = overlay.get("questionId")
        question = questions.get(qid)
        if not question:
            raise ValueError(f"{cert_id}: overlay references unknown question {qid}")

        bank_options = question.get("options", [])
        if not isinstance(bank_options, list) or not bank_options:
            raise ValueError(f"{cert_id}:{qid}: question has no options")

        seen_ids: set[str] = set()
        correct_index = int(question.get("correct", -1))
        if correct_index < 0 or correct_index >= len(bank_options):
            raise ValueError(f"{cert_id}:{qid}: invalid canonical correct index {correct_index}")
        correct_option_id = option_id(qid, correct_index)
        correct_overlay_id = None

        overlay_options = overlay.get("options", [])
        if len(overlay_options) != len(bank_options):
            raise ValueError(
                f"{cert_id}:{qid}: overlay has {len(overlay_options)} options; "
                f"bank has {len(bank_options)}"
            )

        for overlay_option in overlay_options:
            option_count += 1
            current_id = overlay_option.get("optionId")
            match_text = overlay_option.get("matchText")

            if current_id:
                index = parse_option_id(qid, current_id, len(bank_options))
                expected_id = option_id(qid, index)
            else:
                if require_ids:
                    raise ValueError(f"{cert_id}:{qid}: missing optionId for legacy overlay option")
                if not isinstance(match_text, str):
                    raise ValueError(f"{cert_id}:{qid}: legacy overlay option missing matchText")
                index = resolve_option_index(bank_options, match_text)
                expected_id = option_id(qid, index)
                if write:
                    overlay_option["optionId"] = expected_id
                    current_id = expected_id
                    changed = True

            if expected_id in seen_ids:
                raise ValueError(f"{cert_id}:{qid}: duplicate overlay option {expected_id}")
            seen_ids.add(expected_id)

            # matchText is now documentation/readability only. Keep it synchronized
            # to the canonical PT option whenever writing, but never use it as identity.
            canonical_text = bank_options[index]
            if write and overlay_option.get("matchText") != canonical_text:
                overlay_option["matchText"] = canonical_text
                changed = True
                text_sync_count += 1

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

    return len(overlays), option_count, text_sync_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="add optionId and synchronize matchText")
    parser.add_argument(
        "--require-ids",
        action="store_true",
        help="fail if any overlay option has not been migrated yet",
    )
    args = parser.parse_args()

    cert_ids = sorted(path.stem for path in OVERLAYS_ROOT.glob("*.json"))
    total_overlays = 0
    total_options = 0
    total_text_sync = 0

    try:
        for cert_id in cert_ids:
            overlays, options, text_sync = process_cert(cert_id, args.write, args.require_ids)
            total_overlays += overlays
            total_options += options
            total_text_sync += text_sync
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"CloudArena option ID validation failed: {exc}")
        return 1

    action = "migrated/synchronized" if args.write else "validated"
    print(
        f"CloudArena option IDs {action}: {len(cert_ids)} certifications, "
        f"{total_overlays} overlays, {total_options} options, "
        f"{total_text_sync} matchText updates."
    )
    if not args.write and not args.require_ids:
        print("Run with --write to add optionId while keeping matchText as readable metadata.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
