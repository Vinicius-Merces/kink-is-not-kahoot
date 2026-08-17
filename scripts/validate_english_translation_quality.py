#!/usr/bin/env python3
"""Mechanical quality gates for ready/staged English exam translations.

This is deliberately conservative. It catches obvious localization failures rather
than pretending to replace subject-matter review:
- Portuguese source text copied unchanged into EN fields;
- common Portuguese prose markers left in translated question/explanation text;
- empty human-language fields;
- loss of important AWS acronyms/product tokens from the translated question;
- translated option/rationale cardinality drift.

Structural correctness remains enforced by the existing staging/parity validators.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "data" / "exams"
STAGING = ROOT / "translations" / "en"

PT_MARKERS = re.compile(
    r"\b(?:qual|quais|uma|um|empresa|servi[cç]o|usu[aá]rio|equipe|dados|nuvem|"
    r"armazenamento|seguran[cç]a|gerenciado|gerenciada|permite|deve|possui|"
    r"precisa|deseja|utiliza|utilizar|aplica[cç][aã]o|inst[aâ]ncia|regi[aã]o|"
    r"disponibilidade|faturamento|custo|custos|acesso|recurso|recursos)\b",
    re.I,
)

IMPORTANT_TOKENS = re.compile(
    r"\b(?:AWS|Amazon|EC2|S3|RDS|VPC|IAM|EBS|EFS|SQS|SNS|ECS|EKS|KMS|MFA|"
    r"API|CDN|DNS|TCP|UDP|HTTP|HTTPS|SQL|NoSQL|DynamoDB|Lambda|CloudFront|"
    r"CloudTrail|CloudWatch|Route\s*53|Fargate|Redshift|Aurora|GuardDuty|"
    r"Macie|Artifact|Organizations|Auto\s*Scaling|Direct\s*Connect)\b",
    re.I,
)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"\s+", " ", value.strip()).casefold()


def source_map(cert: str, level: str) -> dict[str, dict]:
    path = EXAMS / cert / f"{level}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {q["id"]: q for q in payload.get("questions", [])}


def staged_targets():
    for cert_dir in sorted(p for p in STAGING.iterdir() if p.is_dir()):
        for level_dir in sorted(p for p in cert_dir.iterdir() if p.is_dir()):
            yield cert_dir.name, level_dir.name, level_dir


def meaningful_tokens(text: str) -> set[str]:
    return {match.group(0).lower().replace(" ", "") for match in IMPORTANT_TOKENS.finditer(text or "")}


def validate_item(qid: str, source: dict, item: dict, errors: list[str], location: str):
    for field in ("text", "explanation"):
        value = item.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{location}::{qid}: empty {field}")
            continue
        if len(source.get(field, "")) >= 24 and norm(value) == norm(source.get(field, "")):
            errors.append(f"{location}::{qid}: {field} copied unchanged from PT source")
        # Question/explanation prose should not contain obvious PT residue. Product
        # names and abbreviations are not matched by this detector.
        markers = PT_MARKERS.findall(value)
        if len(markers) >= 3:
            errors.append(
                f"{location}::{qid}: probable Portuguese residue in {field}: {markers[:5]}"
            )

    options = item.get("options")
    src_options = source.get("options") or []
    if not isinstance(options, list) or len(options) != len(src_options):
        errors.append(f"{location}::{qid}: option cardinality mismatch")
    else:
        for index, (src, translated) in enumerate(zip(src_options, options)):
            if not isinstance(translated, str) or not translated.strip():
                errors.append(f"{location}::{qid}: empty option {index}")
            elif len(src) >= 28 and norm(src) == norm(translated) and PT_MARKERS.search(src):
                errors.append(f"{location}::{qid}: option {index} copied unchanged from PT")

    if "optionRationales" in source:
        rationales = item.get("optionRationales")
        src_rationales = source.get("optionRationales") or []
        if not isinstance(rationales, list) or len(rationales) != len(src_rationales):
            errors.append(f"{location}::{qid}: optionRationales cardinality mismatch")

    source_tokens = meaningful_tokens(source.get("text", "") + " " + " ".join(src_options))
    translated_tokens = meaningful_tokens(
        (item.get("text") or "") + " " + " ".join(item.get("options") or [])
    )
    lost = sorted(token for token in source_tokens if token not in translated_tokens)
    # A small number of tokens may legitimately disappear when the source repeats a
    # service in explanatory phrasing. Multiple losses are a stronger mechanical signal.
    if len(lost) >= 2:
        errors.append(f"{location}::{qid}: important AWS tokens lost in EN: {lost}")


def main() -> int:
    errors: list[str] = []
    checked = 0

    for cert, level, directory in staged_targets():
        source = source_map(cert, level)
        for path in sorted(directory.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for qid, item in (payload.get("questions") or {}).items():
                if qid not in source:
                    continue  # unknown IDs are caught by staging validation
                validate_item(qid, source[qid], item, errors, str(path.relative_to(ROOT)))
                checked += 1

    if errors:
        print(f"English translation quality validation failed: {len(errors)} issue(s)")
        for error in errors[:100]:
            print(f"  - {error}")
        if len(errors) > 100:
            print(f"  ... and {len(errors) - 100} more")
        return 1

    print(f"English translation quality validation passed: {checked} staged questions checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
