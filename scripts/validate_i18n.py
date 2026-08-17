#!/usr/bin/env python3
"""Validate CloudPath locale catalogs and referenced i18n keys.

This validator intentionally covers UI catalogs only. Narration assets and the
large certification content banks are migrated in later phases.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "locales"
BASE_LOCALE = "pt-BR"
SUPPORTED_LOCALES = ("pt-BR", "en")

REFERENCE_PATTERN = re.compile(
    r"data-i18n(?:-placeholder|-aria-label|-title)?=[\"']([^\"']+)[\"']"
)


def load_catalog(locale: str) -> dict:
    path = LOCALES_DIR / locale / "ui.json"
    if not path.exists():
        raise ValueError(f"missing locale catalog: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def flatten(value: object, prefix: str = "") -> dict[str, object]:
    result: dict[str, object] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{prefix}.{key}" if prefix else key
            result.update(flatten(child, current))
    else:
        result[prefix] = value
    return result


def referenced_keys() -> set[str]:
    keys: set[str] = set()
    candidates = list(ROOT.glob("*.html")) + list((ROOT / "js").glob("*.js"))
    for path in candidates:
        text = path.read_text(encoding="utf-8", errors="replace")
        keys.update(REFERENCE_PATTERN.findall(text))
    return keys


def main() -> int:
    errors: list[str] = []
    flattened: dict[str, dict[str, object]] = {}

    for locale in SUPPORTED_LOCALES:
        try:
            catalog = load_catalog(locale)
            flattened[locale] = flatten(catalog)
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    base_keys = set(flattened[BASE_LOCALE])

    for locale in SUPPORTED_LOCALES:
        keys = set(flattened[locale])
        missing = sorted(base_keys - keys)
        extra = sorted(keys - base_keys)
        if missing:
            errors.append(f"{locale}: missing keys: {', '.join(missing)}")
        if extra:
            errors.append(f"{locale}: extra keys: {', '.join(extra)}")

        for key, value in flattened[locale].items():
            if not isinstance(value, str):
                errors.append(f"{locale}:{key}: leaf value must be a string")
            elif not value.strip():
                errors.append(f"{locale}:{key}: translation must not be empty")

    refs = referenced_keys()
    unknown_refs = sorted(refs - base_keys)
    if unknown_refs:
        errors.append("unknown data-i18n keys referenced by frontend: " + ", ".join(unknown_refs))

    if errors:
        print("CloudPath i18n validation failed:\n")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"CloudPath i18n OK: {len(SUPPORTED_LOCALES)} locales, "
        f"{len(base_keys)} catalog keys, {len(refs)} frontend references."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
