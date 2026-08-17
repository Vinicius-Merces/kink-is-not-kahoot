#!/usr/bin/env python3
"""Shared mechanical integrity checks for PT-BR -> EN translations.

The goal is not to judge prose style. It protects semantic anchors that must not
silently change during translation: distinctive AWS/service names, technical
acronyms and numeric facts. Checks are field-local, so a service mentioned in
source option 3 must remain in translated option 3 rather than merely appearing
elsewhere.
"""
from __future__ import annotations

import re
import unicodedata

TECHNICAL_PATTERNS = [
    r"AWS", r"Amazon", r"EC2", r"S3", r"RDS", r"VPC", r"IAM", r"EBS", r"EFS",
    r"SQS", r"SNS", r"ECS", r"EKS", r"KMS", r"MFA", r"API", r"CDN", r"DNS",
    r"TCP", r"UDP", r"HTTP", r"HTTPS", r"SQL", r"NoSQL", r"DynamoDB", r"Lambda",
    r"CloudFront", r"CloudTrail", r"CloudWatch", r"Route\s*53", r"Fargate",
    r"Redshift", r"Aurora", r"GuardDuty", r"Macie", r"Artifact", r"Organizations",
    r"Auto\s*Scaling", r"Direct\s*Connect", r"Trusted\s*Advisor", r"Cost\s*Explorer",
    r"Budgets?", r"Savings\s*Plans?", r"Reserved\s*Instances?", r"Spot(?:\s*Instances?)?",
    r"Security\s*Groups?", r"Network\s*ACLs?", r"NACLs?", r"Load\s*Balancer",
    r"Application\s*Load\s*Balancer", r"ALB", r"Elastic\s*Beanstalk", r"Outposts?",
    r"Local\s*Zones?", r"Edge\s*Locations?", r"Identity\s*Center", r"WAF", r"Shield",
    r"Secrets\s*Manager", r"Systems\s*Manager", r"Parameter\s*Store", r"CloudHSM",
    r"Certificate\s*Manager", r"ACM", r"AWS\s*Config", r"Audit\s*Manager", r"Inspector",
    r"Control\s*Tower", r"Service\s*Control\s*Polic(?:y|ies)", r"SCPs?", r"Free\s*Tier",
    r"Well-Architected", r"Cloud\s*Adoption\s*Framework", r"CAF", r"CloudFormation",
    r"API\s*Gateway", r"Cognito", r"Step\s*Functions", r"EventBridge", r"Kinesis",
    r"Glue", r"Athena", r"EMR", r"QuickSight", r"SageMaker", r"Bedrock", r"Snowball",
    r"Snow\s*Family", r"Storage\s*Gateway", r"DataSync", r"Transfer\s*Family",
    r"Global\s*Accelerator", r"Transit\s*Gateway", r"Internet\s*Gateway", r"NAT\s*Gateway",
    r"CloudShell", r"CodePipeline", r"CodeBuild", r"CodeDeploy", r"SAM", r"Cloud9",
]

TECHNICAL_RE = re.compile(r"\b(?:" + "|".join(TECHNICAL_PATTERNS) + r")\b", re.I)
GENERIC_TECHNICAL_ANCHORS = {"aws", "amazon", "api"}

# Immutable numeric spans used by the offline translator. Human-language units are
# deliberately NOT included here: only the value is frozen, so `9 anos` can become
# `9 years`. Locale-neutral technical units/symbols remain attached to the number.
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9])(?P<number>\d+(?:[.,]\d+)?)(?P<suffix>\s*%|\s*(?:GB|TB|PB))?",
    re.I,
)

# Richer matcher used only for cross-locale QA. It consumes translated duration
# units but normalizes them back to the numeric value.
NUMERIC_FACT_RE = re.compile(
    r"(?<![A-Za-z0-9])(?P<number>\d+(?:[.,]\d+)?)"
    r"(?P<suffix>\s*%|\s*(?:ms|s|sec|seconds?|segundos?|minutes?|minutos?|hours?|horas?|days?|dias?|months?|meses?|years?|anos?|GB|TB|PB))?",
    re.I,
)


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"\s+", " ", value.strip()).casefold()


def technical_anchors(text: str) -> set[str]:
    anchors = set()
    for match in TECHNICAL_RE.finditer(text or ""):
        token = re.sub(r"\s+", "", match.group(0)).casefold()
        token = token.replace("instances", "instance")
        # Generic vendor prefixes and the generic word API can be omitted in an
        # otherwise faithful English sentence without changing the proposition.
        # Distinctive service/product/protocol anchors remain mandatory.
        if token in GENERIC_TECHNICAL_ANCHORS:
            continue
        anchors.add(token)
    return anchors


def numeric_anchors(text: str) -> set[str]:
    anchors = set()
    for match in NUMERIC_FACT_RE.finditer(text or ""):
        number = match.group("number").replace(",", ".").casefold()
        suffix = re.sub(r"\s+", "", match.group("suffix") or "").casefold()
        if "%" in suffix:
            anchors.add(number + "%")
        elif suffix in {"gb", "tb", "pb"}:
            anchors.add(number + suffix)
        else:
            anchors.add(number)
    return anchors


def field_anchor_errors(source: str, translated: str, label: str) -> list[str]:
    errors: list[str] = []
    src_tech = technical_anchors(source)
    dst_tech = technical_anchors(translated)
    missing_tech = sorted(src_tech - dst_tech)
    if missing_tech:
        errors.append(f"{label}: technical anchors lost: {missing_tech}")

    src_numbers = numeric_anchors(source)
    dst_numbers = numeric_anchors(translated)
    missing_numbers = sorted(src_numbers - dst_numbers)
    if missing_numbers:
        errors.append(f"{label}: numeric anchors lost: {missing_numbers}")
    return errors


def question_anchor_errors(source: dict, item: dict) -> list[str]:
    errors: list[str] = []
    for field in ("text", "explanation", "hint"):
        if field in source and field in item and isinstance(source.get(field), str) and isinstance(item.get(field), str):
            errors.extend(field_anchor_errors(source[field], item[field], field))

    src_options = source.get("options") or []
    options = item.get("options") or []
    if len(src_options) == len(options):
        for index, (src, dst) in enumerate(zip(src_options, options)):
            if isinstance(src, str) and isinstance(dst, str):
                errors.extend(field_anchor_errors(src, dst, f"option[{index}]"))

    src_rationales = source.get("optionRationales") or []
    rationales = item.get("optionRationales") or []
    if src_rationales and len(src_rationales) == len(rationales):
        for index, (src, dst) in enumerate(zip(src_rationales, rationales)):
            if isinstance(src, str) and isinstance(dst, str):
                errors.extend(field_anchor_errors(src, dst, f"optionRationale[{index}]"))
    return errors


def norm(value: str) -> str:
    return _norm(value)
