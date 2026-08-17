#!/usr/bin/env python3
"""Generate English CloudArena pedagogical-text staging with GitHub Models.

Stable questionId/optionId/stage/correct metadata never comes from the model. The
model translates only reasonWrong and finalBlow justification text. It receives the
ready English exam question/options/explanation as context so revised canonical facts
win over stale wording that may still exist in legacy overlay prose.
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


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def qnum(qid: str) -> int:
    match = re.search(r"(\d+)$", qid)
    return int(match.group(1)) if match else 0


def ready_questions(cert: str) -> dict[str, dict]:
    result = {}
    for level in ("iniciante", "medio", "avancado"):
        path = ROOT / "data" / "exams-en" / cert / f"{level}.json"
        if not path.exists():
            raise RuntimeError(f"Ready EN bank required before Arena translation: {path.relative_to(ROOT)}")
        payload = load(path)
        if (payload.get("_translation") or {}).get("status") != "ready":
            raise RuntimeError(f"EN bank is not ready: {path.relative_to(ROOT)}")
        result.update({q["id"]: q for q in payload.get("questions", [])})
    return result


def existing_ids(cert: str) -> set[str]:
    directory = ROOT / "translations" / "en" / "cloudarena" / cert
    ids = set()
    if directory.exists():
        for path in directory.glob("*.json"):
            ids.update((load(path).get("questions") or {}).keys())
    return ids


def request_model(token: str, model: str, payload: dict) -> dict:
    system = """Translate CloudArena pedagogical feedback from Brazilian Portuguese to professional US English.
Return JSON only, keyed by the exact question IDs supplied.

For each question return exactly:
- optionReasons: object keyed by the exact optionId values supplied; translate each reason string faithfully. Empty source reason stays empty.
- finalJustifications: array of translated strings in exactly the supplied order.

Never output or change questionId, optionId, stage, correct flags, answer indexes, domains, or any structural metadata.
Preserve official AWS product names and terminology.
The supplied canonical English question/options/explanation are the current source of truth. If legacy Portuguese feedback conflicts with that current canonical wording or facts, align the English feedback to the canonical English question rather than preserving an obsolete claim.
"""
    body = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))},
        ],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
            return json.loads(result["choices"][0]["message"]["content"])
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in {408,429,500,502,503,504}:
                detail = exc.read().decode("utf-8", errors="replace")[:1500]
                raise RuntimeError(f"GitHub Models HTTP {exc.code}: {detail}") from exc
            if attempt < 4:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"GitHub Models failed after retries: {last}")


def model_input(overlays: list[dict], questions: dict[str, dict]) -> dict:
    output = {}
    for ov in overlays:
        qid = ov["questionId"]
        q = questions[qid]
        output[qid] = {
            "canonicalEnglish": {
                "text": q.get("text", ""),
                "options": q.get("options", []),
                "explanation": q.get("explanation", ""),
            },
            "optionReasons": {
                item["optionId"]: item.get("reasonWrong", "")
                for item in ov.get("options", [])
            },
            "finalJustifications": [
                item.get("text", "") for item in (ov.get("finalBlow") or {}).get("justifications", [])
            ],
        }
    return output


def validate(overlays: list[dict], translated: dict) -> dict:
    expected_ids = {ov["questionId"] for ov in overlays}
    if set(translated) != expected_ids:
        raise ValueError("CloudArena model response question IDs mismatch")
    clean = {}
    for ov in overlays:
        qid = ov["questionId"]
        item = translated[qid]
        if set(item) != {"optionReasons", "finalJustifications"}:
            raise ValueError(f"{qid}: unexpected translation fields")
        expected_option_ids = {o["optionId"] for o in ov.get("options", [])}
        reasons = item["optionReasons"]
        if not isinstance(reasons, dict) or set(reasons) != expected_option_ids:
            raise ValueError(f"{qid}: optionReason IDs mismatch")
        for option in ov.get("options", []):
            oid = option["optionId"]
            source_reason = option.get("reasonWrong", "")
            value = reasons[oid]
            if not isinstance(value, str):
                raise ValueError(f"{qid}:{oid}: reason must be string")
            if source_reason.strip() and not value.strip():
                raise ValueError(f"{qid}:{oid}: translated reason is empty")
            if not source_reason.strip() and value.strip():
                raise ValueError(f"{qid}:{oid}: empty source reason must stay empty")
        source_just = (ov.get("finalBlow") or {}).get("justifications", [])
        just = item["finalJustifications"]
        if not isinstance(just, list) or len(just) != len(source_just):
            raise ValueError(f"{qid}: finalJustifications cardinality changed")
        if any(not isinstance(v, str) or not v.strip() for v in just):
            raise ValueError(f"{qid}: empty final justification")
        clean[qid] = item
    return clean


def write_batch(cert: str, overlays: list[dict], translated: dict):
    start, end = qnum(overlays[0]["questionId"]), qnum(overlays[-1]["questionId"])
    target_dir = ROOT / "translations" / "en" / "cloudarena" / cert
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / (f"{start:03d}-{end:03d}.json" if start != end else f"{start:03d}.json")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target.relative_to(ROOT)}")
    target.write_text(json.dumps({
        "_batch": {"locale":"en","sourceLocale":"pt-BR","certId":cert,"range":f"{start:03d}-{end:03d}","generator":"github-models-assisted-draft"},
        "questions": translated,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}: {len(overlays)} overlays")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    args = parser.parse_args()
    request = load(ROOT / args.request)
    cert = request["certId"]
    batch_size = max(1, min(int(request.get("batchSize", 8)), 8))
    model = request.get("model", "openai/gpt-4.1-mini")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN required; no unauthenticated fallback")

    source = load(ROOT / "data" / "cloudarena" / "breakdowns" / f"{cert}.json")
    questions = ready_questions(cert)
    done = existing_ids(cert)
    overlays = [ov for ov in source.get("overlays", []) if ov.get("questionId") not in done]
    if not overlays:
        print("No missing CloudArena overlays to translate")
        return 0
    for ov in overlays:
        qid = ov.get("questionId")
        if qid not in questions:
            raise RuntimeError(f"Ready EN exam question missing for overlay {qid}")
        if any(not item.get("optionId") for item in ov.get("options", [])):
            raise RuntimeError(f"Stable optionId required before translating overlay {qid}")

    print(f"Generating EN CloudArena staging for {cert}: {len(overlays)} overlays")
    for offset in range(0, len(overlays), batch_size):
        batch = overlays[offset:offset+batch_size]
        translated = request_model(token, model, model_input(batch, questions))
        write_batch(cert, batch, validate(batch, translated))
        time.sleep(0.5)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
