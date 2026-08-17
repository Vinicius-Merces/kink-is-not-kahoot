#!/usr/bin/env python3
"""Validate CloudPath modular locale catalogs and referenced translation keys."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "locales"
BASE_LOCALE = "pt-BR"
SUPPORTED_LOCALES = ("pt-BR", "en")

MARKUP_REFERENCE_PATTERN = re.compile(
    r"data-i18n(?:-placeholder|-aria-label|-title)?=[\"']([^\"']+)[\"']"
)
KEY_LITERAL_PATTERN = re.compile(
    r"[\"']((?:meta|brand|language|common|nav|auth|home|quiz|study|exam|arena|progress|errors)\.[A-Za-z0-9_.]+)[\"']"
)


def deep_merge(target: dict, source: dict) -> dict:
    for key, value in source.items():
        if isinstance(value, dict):
            current = target.get(key)
            if current is not None and not isinstance(current, dict):
                raise ValueError(f"catalog namespace collision at {key}")
            target[key] = deep_merge(current or {}, value)
        else:
            if key in target and isinstance(target[key], dict):
                raise ValueError(f"catalog namespace collision at {key}")
            target[key] = value
    return target


def catalog_files(locale: str) -> list[Path]:
    directory = LOCALES_DIR / locale
    if not directory.exists():
        raise ValueError(f"missing locale directory: {directory.relative_to(ROOT)}")
    files = sorted(directory.glob("*.json"))
    if not files:
        raise ValueError(f"no locale catalogs in {directory.relative_to(ROOT)}")
    return files


def load_catalog(locale: str) -> dict:
    merged: dict = {}
    for path in catalog_files(locale):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"catalog root must be an object: {path.relative_to(ROOT)}")
        deep_merge(merged, payload)
    return merged


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
        keys.update(MARKUP_REFERENCE_PATTERN.findall(text))
        keys.update(KEY_LITERAL_PATTERN.findall(text))
    return keys


def main() -> int:
    errors: list[str] = []
    flattened: dict[str, dict[str, object]] = {}

    try:
        base_files = {p.name for p in catalog_files(BASE_LOCALE)}
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    for locale in SUPPORTED_LOCALES:
        try:
            locale_files = {p.name for p in catalog_files(locale)}
            missing_files = sorted(base_files - locale_files)
            extra_files = sorted(locale_files - base_files)
            if missing_files:
                errors.append(f"{locale}: missing catalog files: {', '.join(missing_files)}")
            if extra_files:
                errors.append(f"{locale}: extra catalog files: {', '.join(extra_files)}")
            flattened[locale] = flatten(load_catalog(locale))
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
        errors.append("unknown i18n keys referenced by frontend: " + ", ".join(unknown_refs))

    if errors:
        print("CloudPath i18n validation failed:\n")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"CloudPath i18n OK: {len(SUPPORTED_LOCALES)} locales, "
        f"{len(base_files)} catalog files/locale, {len(base_keys)} keys, "
        f"{len(refs)} frontend references."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
