#!/usr/bin/env python3
"""Repair mechanically detected PT->EN semantic drift using GitHub Models.

This script only rewrites staging under translations/en/**. It never writes ready
banks or answer-key metadata. Candidate questions are selected by field-local
technical/numeric anchor failures against the canonical PT bank. A repaired item
must pass the same anchor checks before any file is written.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from translation_integrity import question_anchor_errors

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "data" / "exams"
STAGING = ROOT / "translations" / "en"
API_URL = "https://models.github.ai/inference/chat/completions"
ALLOWED_FIELDS = {"text", "options", "explanation", "hint", "optionRationales"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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


def source_maps() -> dict[tuple[str, str], dict[str, dict]]:
    result = {}
    for cert_dir in EXAMS.iterdir():
        if not cert_dir.is_dir():
            continue
        for path in cert_dir.glob("*.json"):
            payload = load_json(path)
            result[(cert_dir.name, path.stem)] = {q["id"]: q for q in payload.get("questions", [])}
    return result


def collect_candidates(request: dict):
    maps = source_maps()
    cert_filter = request.get("certId")
    level_filter = request.get("level")
    qid_filter = set(request.get("questionIds") or [])
    candidates = []
    file_payloads: dict[Path, dict] = {}

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
                        candidates.append({
                            "path": path,
                            "qid": qid,
                            "source": src,
                            "current": item,
                            "issues": issues,
                        })
    return candidates, file_payloads


def model_request(token: str, model: str, batch: list[dict], retries: int = 4) -> dict:
    source = {
        row["qid"]: {
            "source": source_human_fields(row["source"]),
            "currentEnglish": row["current"],
            "detectedIntegrityIssues": row["issues"],
        }
        for row in batch
    }
    system = """You are repairing English translations of AWS certification questions.

The Brazilian Portuguese source is canonical. Produce a faithful US-English translation ONLY. Do not solve, rewrite, simplify, modernize, improve, replace, invent, or remove any question concept or answer option. Every answer option must remain the same proposition as the source option at the same array index, including deliberately wrong distractors. Preserve every AWS product/service name, technical acronym, number, percentage, duration, protocol, pricing model, and negation from its corresponding source field. If the current English differs from the source, ignore the current wording and retranslate from the source.

Return JSON only. Root keys must be the exact supplied question IDs. Values may contain ONLY text, options, explanation, hint, optionRationales. Do not return id, domain, correct, selectCount, topics or any answer-key metadata. Preserve option and rationale order/count exactly.
"""
    body = {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(source, ensure_ascii=False, separators=(",", ":"))},
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
            return json.loads(payload["choices"][0]["message"]["content"])
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in {408, 429, 500, 502, 503, 504}:
                detail = exc.read().decode("utf-8", errors="replace")[:2000]
                raise RuntimeError(f"GitHub Models request failed HTTP {exc.code}: {detail}") from exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"GitHub Models request failed after {retries} attempts: {last_error}")


def validate_repair(source: dict, item: dict, qid: str) -> dict:
    if not isinstance(item, dict):
        raise ValueError(f"{qid}: repair must be an object")
    if set(item) != expected_fields(source):
        raise ValueError(f"{qid}: field parity mismatch: {sorted(item)}")
    if set(item) - ALLOWED_FIELDS:
        raise ValueError(f"{qid}: forbidden fields returned")
    if not isinstance(item.get("text"), str) or not item["text"].strip():
        raise ValueError(f"{qid}: empty text")
    if not isinstance(item.get("explanation"), str) or not item["explanation"].strip():
        raise ValueError(f"{qid}: empty explanation")
    options = item.get("options")
    if not isinstance(options, list) or len(options) != len(source.get("options") or []):
        raise ValueError(f"{qid}: option count changed")
    if any(not isinstance(x, str) or not x.strip() for x in options):
        raise ValueError(f"{qid}: empty option")
    if "hint" in source and (not isinstance(item.get("hint"), str) or not item["hint"].strip()):
        raise ValueError(f"{qid}: empty hint")
    if "optionRationales" in source:
        values = item.get("optionRationales")
        if not isinstance(values, list) or len(values) != len(source.get("optionRationales") or []):
            raise ValueError(f"{qid}: rationale count changed")
        if any(not isinstance(x, str) or not x.strip() for x in values):
            raise ValueError(f"{qid}: empty rationale")
    issues = question_anchor_errors(source, item)
    if issues:
        raise ValueError(f"{qid}: repaired translation still violates anchors: {issues}")
    return item


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", help="JSON repair request inside repository")
    args = parser.parse_args()

    request_path = (ROOT / args.request).resolve()
    if ROOT not in request_path.parents:
        raise ValueError("request path escapes repository")
    request = load_json(request_path)
    model = request.get("model", "openai/gpt-4.1")
    batch_size = max(1, min(int(request.get("batchSize", 4)), 6))
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")

    candidates, file_payloads = collect_candidates(request)
    if not candidates:
        print("No field-anchor translation drift detected; nothing to repair")
        return 0

    print(f"Repairing {len(candidates)} staged question(s) with {model}")
    repaired: dict[tuple[Path, str], dict] = {}
    for offset in range(0, len(candidates), batch_size):
        batch = candidates[offset:offset + batch_size]
        response = model_request(token, model, batch)
        expected_ids = {row["qid"] for row in batch}
        if set(response) != expected_ids:
            raise ValueError(f"Model IDs mismatch: expected={sorted(expected_ids)} got={sorted(response)}")
        for row in batch:
            qid = row["qid"]
            repaired[(row["path"], qid)] = validate_repair(row["source"], response[qid], qid)
        time.sleep(0.4)

    changed_paths = set()
    for (path, qid), item in repaired.items():
        file_payloads[path]["questions"][qid] = item
        changed_paths.add(path)

    # Transaction-style: write only after all model batches passed validation.
    for path in sorted(changed_paths):
        path.write_text(json.dumps(file_payloads[path], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"repaired: {path.relative_to(ROOT)}")

    print(f"Repaired {len(repaired)} question(s) across {len(changed_paths)} staging file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
