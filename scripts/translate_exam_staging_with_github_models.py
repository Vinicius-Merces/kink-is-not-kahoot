#!/usr/bin/env python3
"""Generate English exam staging drafts with GitHub Models.

This tool is intentionally *not* a publisher. It writes only human-language staging
fields under translations/en/**. Structural truth remains in the canonical PT bank
and the existing builder/parity pipeline remains the only path to `ready` banks.

Security / quality boundaries:
- authentication comes only from GITHUB_TOKEN in CI;
- source content is public repository content;
- the model may return human-language fields only;
- option cardinality/order is validated against the canonical bank;
- IDs, domain, correct, selectCount and topics never come from the model;
- existing staged IDs are skipped unless explicitly requested otherwise;
- any malformed or partial model response fails closed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://models.github.ai/inference/chat/completions"
ALLOWED_FIELDS = {"text", "options", "explanation", "hint", "optionRationales"}
FORBIDDEN_FIELDS = {"id", "domain", "correct", "selectCount", "topics", "certCode", "level"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_glossary() -> str:
    path = ROOT / "translations" / "en" / "GLOSSARY.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def staged_ids(cert: str, level: str) -> set[str]:
    target = ROOT / "translations" / "en" / cert / level
    result: set[str] = set()
    if not target.exists():
        return result
    for path in target.glob("*.json"):
        payload = load_json(path)
        result.update((payload.get("questions") or {}).keys())
    return result


def numeric_suffix(question_id: str) -> int:
    match = re.search(r"(\d+)$", question_id)
    if not match:
        raise ValueError(f"Question ID has no numeric suffix: {question_id}")
    return int(match.group(1))


def source_human_fields(question: dict) -> dict:
    fields = {
        "text": question.get("text", ""),
        "options": question.get("options", []),
        "explanation": question.get("explanation", ""),
    }
    if "hint" in question:
        fields["hint"] = question.get("hint", "")
    if "optionRationales" in question:
        fields["optionRationales"] = question.get("optionRationales", [])
    return fields


def expected_fields(question: dict) -> set[str]:
    result = {"text", "options", "explanation"}
    if "hint" in question:
        result.add("hint")
    if "optionRationales" in question:
        result.add("optionRationales")
    return result


def compact_source(batch: list[dict]) -> dict:
    return {q["id"]: source_human_fields(q) for q in batch}


def model_request(token: str, model: str, source: dict, glossary: str, retries: int = 4) -> dict:
    system = """You are translating AWS certification study questions from Brazilian Portuguese to professional US English for CloudPath.

Translate faithfully. Do not solve, rewrite, reorder, simplify, correct, or change the meaning of questions. Preserve the order and count of answer options exactly. Preserve AWS official service/product names and common official English terminology. Translate pedagogical explanations, hints and option rationales naturally. Do not add factual claims that do not exist in the source. Return JSON only.

The JSON root must be an object keyed by the exact question IDs supplied. Each value may contain ONLY: text, options, explanation, hint, optionRationales. Include hint and optionRationales exactly when they exist in the source. Never output id, domain, correct, selectCount, topics, certCode, level, or any answer-key metadata.
"""
    if glossary:
        system += "\nCloudPath terminology guide:\n" + glossary[:12000]

    user = "Translate this batch. Preserve every option position exactly:\n" + json.dumps(
        source, ensure_ascii=False, separators=(",", ":")
    )
    body = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    encoded = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    last_error = None
    for attempt in range(retries):
        req = urllib.request.Request(API_URL, data=encoded, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
            content = payload["choices"][0]["message"]["content"]
            return json.loads(content)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in {408, 429, 500, 502, 503, 504}:
                detail = exc.read().decode("utf-8", errors="replace")[:2000]
                raise RuntimeError(f"GitHub Models request failed HTTP {exc.code}: {detail}") from exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"GitHub Models request failed after {retries} attempts: {last_error}")


def validate_translation(source_questions: list[dict], translated: dict) -> dict:
    expected_ids = [q["id"] for q in source_questions]
    if set(translated) != set(expected_ids):
        raise ValueError(
            f"Model response IDs mismatch. expected={expected_ids}, got={sorted(translated)}"
        )

    output = {}
    for source in source_questions:
        qid = source["id"]
        item = translated[qid]
        if not isinstance(item, dict):
            raise ValueError(f"{qid}: translation must be an object")
        forbidden = set(item) & FORBIDDEN_FIELDS
        unknown = set(item) - ALLOWED_FIELDS
        if forbidden or unknown:
            raise ValueError(f"{qid}: forbidden/unknown fields: {sorted(forbidden | unknown)}")
        if set(item) != expected_fields(source):
            raise ValueError(
                f"{qid}: field parity mismatch. expected={sorted(expected_fields(source))}, got={sorted(item)}"
            )

        if not isinstance(item["text"], str) or not item["text"].strip():
            raise ValueError(f"{qid}: empty text")
        if not isinstance(item["explanation"], str) or not item["explanation"].strip():
            raise ValueError(f"{qid}: empty explanation")
        if not isinstance(item["options"], list) or len(item["options"]) != len(source.get("options", [])):
            raise ValueError(f"{qid}: option count changed")
        if any(not isinstance(value, str) or not value.strip() for value in item["options"]):
            raise ValueError(f"{qid}: invalid/empty option")

        if "hint" in item and (not isinstance(item["hint"], str) or not item["hint"].strip()):
            raise ValueError(f"{qid}: invalid/empty hint")
        if "optionRationales" in item:
            rationales = item["optionRationales"]
            source_rationales = source.get("optionRationales", [])
            if not isinstance(rationales, list) or len(rationales) != len(source_rationales):
                raise ValueError(f"{qid}: optionRationales count changed")
            if any(not isinstance(value, str) or not value.strip() for value in rationales):
                raise ValueError(f"{qid}: invalid/empty optionRationale")
        output[qid] = item
    return output


def write_batch(cert: str, level: str, source_path: str, questions: list[dict], translated: dict) -> Path:
    start = numeric_suffix(questions[0]["id"])
    end = numeric_suffix(questions[-1]["id"])
    target_dir = ROOT / "translations" / "en" / cert / level
    target_dir.mkdir(parents=True, exist_ok=True)
    name = f"{start:03d}-{end:03d}.json" if start != end else f"{start:03d}.json"
    target = target_dir / name
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite staged batch: {target.relative_to(ROOT)}")
    payload = {
        "_batch": {
            "locale": "en",
            "sourceLocale": "pt-BR",
            "certId": cert,
            "level": level,
            "sourcePath": source_path,
            "range": f"{start:03d}-{end:03d}" if start != end else f"{start:03d}",
            "generator": "github-models-assisted-draft",
        },
        "questions": translated,
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote: {target.relative_to(ROOT)} ({len(questions)} questions)")
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", help="JSON request file")
    args = parser.parse_args()

    request_path = (ROOT / args.request).resolve()
    if ROOT not in request_path.parents:
        raise ValueError("request path escapes repository")
    request = load_json(request_path)
    cert = request["certId"]
    level = request["level"]
    start = int(request.get("start", 1))
    end = int(request.get("end", 10**9))
    batch_size = max(1, min(int(request.get("batchSize", 5)), 8))
    model = request.get("model", "openai/gpt-4.1-mini")

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required; no unauthenticated fallback is allowed")

    source_rel = f"data/exams/{cert}/{level}.json"
    source = load_json(ROOT / source_rel)
    all_questions = source.get("questions", [])
    existing = staged_ids(cert, level)
    selected = [
        q for q in all_questions
        if start <= numeric_suffix(q["id"]) <= end and q["id"] not in existing
    ]
    if not selected:
        print("No missing questions in requested range; nothing to translate")
        return 0

    glossary = load_glossary()
    print(f"Generating assisted EN staging for {cert}/{level}: {len(selected)} missing questions using {model}")
    for offset in range(0, len(selected), batch_size):
        batch = selected[offset:offset + batch_size]
        translated = model_request(token, model, compact_source(batch), glossary)
        validated = validate_translation(batch, translated)
        write_batch(cert, level, source_rel, batch, validated)
        time.sleep(0.5)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
