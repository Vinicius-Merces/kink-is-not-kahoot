#!/usr/bin/env python3
"""Build a complete, release-safe English CloudArena overlay.

Canonical structural metadata always comes from data/cloudarena/breakdowns/<cert>.json.
Question/answer text always comes from the validated ready English exam banks.

The PT CloudArena contains long pedagogical prose. The previous machine-translated
version of that prose could be structurally correct while still sounding unnatural.
For the English release we intentionally use concise, curated generic feedback.
This keeps the battle fully English and pedagogically clear without risking semantic
drift in answer-specific generated explanations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WRONG_FEEDBACK = {
    "trap": "This option is plausible, but it does not satisfy the requirement in this scenario.",
    "eliminate": "This option does not match the AWS capability required by the scenario.",
}
DEFAULT_WRONG_FEEDBACK = "This option does not satisfy the scenario requirements."
CORRECT_FINAL = "Correct. This answer matches the AWS capability and constraints required by the scenario."
INCORRECT_FINAL = "Incorrect. Recheck the service responsibilities and the scenario constraints before choosing this answer."


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def en_questions(cert: str):
    result = {}
    for level in ("iniciante", "medio", "avancado"):
        path = ROOT / "data" / "exams-en" / cert / f"{level}.json"
        payload = load(path)
        if (payload.get("_translation") or {}).get("status") != "ready":
            raise RuntimeError(f"EN exam bank not ready: {path.relative_to(ROOT)}")
        result.update({q["id"]: q for q in payload.get("questions", [])})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cert")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    cert = args.cert
    source_path = ROOT / "data" / "cloudarena" / "breakdowns" / f"{cert}.json"
    source = load(source_path)
    overlays = source.get("overlays", [])
    enq = en_questions(cert)

    missing_questions = [ov.get("questionId") for ov in overlays if ov.get("questionId") not in enq]
    if missing_questions:
        preview = ", ".join(missing_questions[:12])
        raise RuntimeError(f"{cert}: {len(missing_questions)} CloudArena question(s) missing from ready EN banks: {preview}")

    output = json.loads(json.dumps(source, ensure_ascii=False))
    output["_translation"] = {
        "locale": "en",
        "sourceLocale": "pt-BR",
        "status": "ready",
        "feedbackMode": "curated-generic-en-v1",
    }

    for ov in output.get("overlays", []):
        qid = ov["questionId"]
        question = enq[qid]
        option_text = {f"{qid}:option:{i}": text for i, text in enumerate(question.get("options", []))}

        for opt in ov.get("options", []):
            oid = opt["optionId"]
            if oid not in option_text:
                raise RuntimeError(f"{qid}: EN option missing for {oid}")
            opt["matchText"] = option_text[oid]
            if opt.get("stage") == "correct":
                opt.pop("reasonWrong", None)
            else:
                opt["reasonWrong"] = WRONG_FEEDBACK.get(opt.get("stage"), DEFAULT_WRONG_FEEDBACK)

        justifications = (ov.get("finalBlow") or {}).get("justifications", [])
        for item in justifications:
            item["text"] = CORRECT_FINAL if item.get("correct") else INCORRECT_FINAL

    if args.write:
        target = ROOT / "data" / "cloudarena" / "breakdowns-en" / f"{cert}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}: {len(overlays)} overlays with curated EN feedback")
    else:
        print(f"{cert}: CloudArena EN complete {len(overlays)}/{len(overlays)} with curated feedback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
