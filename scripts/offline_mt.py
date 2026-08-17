#!/usr/bin/env python3
"""Offline PT-BR -> EN translation helper for CI.

Uses the Apache-2.0 Helsinki-NLP/opus-mt-roa-en Marian checkpoint locally on the
GitHub Actions runner. No hosted inference API or project secret is required.

AWS/service names, acronyms, URLs, placeholders and numeric facts are never sent
through the translation model. They are cut out as immutable literal spans, only the
natural-language text between them is translated, and the original anchors are then
reassembled byte-for-byte into the result. A post-translation integrity check remains
as a second line of defense.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

from translation_integrity import NUMBER_RE, TECHNICAL_RE, field_anchor_errors

MODEL_ID = os.environ.get("CLOUDPATH_MT_MODEL", "Helsinki-NLP/opus-mt-roa-en")

EXTRA_PROTECTED_RE = re.compile(
    r"https?://\S+|www\.\S+|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|"
    r"\$\{[^}]+\}|\{\{[^}]+\}\}|\{[A-Za-z0-9_.:-]+\}|%[sdif]|"
    r"\b[A-Z][A-Z0-9_-]{2,}\b"
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?;:])\s+(?=[A-ZÀ-Ý0-9(\[\"'])")
LETTER_RE = re.compile(r"[A-Za-zÀ-ÿ]")


def _protected_spans(text: str):
    """Return immutable source intervals covering every protected anchor.

    Matches from different detectors can overlap. Never discard a later overlap:
    merge the intervals and preserve the exact original source slice. This guarantees
    that a numeric fact cannot disappear merely because another technical pattern
    overlaps the same source region.
    """
    source = text or ""
    intervals: list[tuple[int, int]] = []
    for regex in (EXTRA_PROTECTED_RE, TECHNICAL_RE, NUMBER_RE):
        for match in regex.finditer(source):
            intervals.append((match.start(), match.end()))
    if not intervals:
        return []

    intervals.sort(key=lambda row: (row[0], row[1]))
    merged: list[list[int]] = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end, source[start:end]) for start, end in merged]


def _chunk(text: str, max_chars: int = 1050):
    """Split natural prose into model-safe chunks without changing its semantics."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    sentences = SENTENCE_SPLIT_RE.split(text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            clauses = re.split(r"(?<=[,;])\s+", sentence)
            buf = ""
            for clause in clauses:
                if buf and len(buf) + 1 + len(clause) > max_chars:
                    chunks.append(buf.strip())
                    buf = clause
                else:
                    buf = f"{buf} {clause}".strip()
            if buf:
                chunks.append(buf.strip())
            continue
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current.strip())
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current.strip())
    return chunks


@dataclass
class _TranslationTask:
    source: str


def _append_natural(layout: list[tuple[str, object]], tasks: list[_TranslationTask], value: str):
    """Add natural prose to a layout while preserving surrounding whitespace exactly."""
    if not value:
        return
    if not LETTER_RE.search(value):
        layout.append(("literal", value))
        return

    leading = re.match(r"^\s*", value).group(0)
    trailing = re.search(r"\s*$", value).group(0)
    core_end = len(value) - len(trailing) if trailing else len(value)
    core = value[len(leading):core_end]

    if leading:
        layout.append(("literal", leading))
    chunks = _chunk(core)
    if not chunks:
        layout.append(("literal", core))
    else:
        for index, chunk in enumerate(chunks):
            if index:
                layout.append(("literal", " "))
            task_index = len(tasks)
            tasks.append(_TranslationTask(chunk))
            layout.append(("task", task_index))
    if trailing:
        layout.append(("literal", trailing))


def _build_layout(source: str, tasks: list[_TranslationTask]):
    """Represent a source as immutable anchors plus translatable prose tasks."""
    layout: list[tuple[str, object]] = []
    spans = _protected_spans(source)
    cursor = 0
    for start, end, anchor in spans:
        _append_natural(layout, tasks, source[cursor:start])
        layout.append(("literal", anchor))
        cursor = end
    _append_natural(layout, tasks, source[cursor:])
    return layout


class OfflineTranslator:
    def __init__(self, model_id: str = MODEL_ID):
        # Imports are lazy so validators that import this module do not require ML deps.
        from transformers import MarianMTModel, MarianTokenizer
        import torch

        self.torch = torch
        self.tokenizer = MarianTokenizer.from_pretrained(model_id)
        self.model = MarianMTModel.from_pretrained(model_id)
        self.model.eval()
        torch.set_num_threads(max(1, min(4, os.cpu_count() or 2)))

    def _generate_batch(self, values: list[str]) -> list[str]:
        if not values:
            return []
        encoded = self.tokenizer(
            values,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )
        with self.torch.inference_mode():
            generated = self.model.generate(
                **encoded,
                num_beams=4,
                max_new_tokens=512,
                early_stopping=True,
            )
        return self.tokenizer.batch_decode(generated, skip_special_tokens=True)

    def translate_many(self, sources: list[str], batch_size: int = 12) -> list[str]:
        tasks: list[_TranslationTask] = []
        layouts = [_build_layout(source, tasks) for source in sources]

        translated_tasks = [""] * len(tasks)
        for offset in range(0, len(tasks), batch_size):
            batch = tasks[offset:offset + batch_size]
            outputs = self._generate_batch([task.source for task in batch])
            if len(outputs) != len(batch):
                raise RuntimeError("offline MT output cardinality mismatch")
            for index, output in enumerate(outputs):
                if not output.strip():
                    raise RuntimeError(f"offline MT returned empty prose for {batch[index].source[:160]!r}")
                translated_tasks[offset + index] = output.strip()

        results = []
        for source, layout in zip(sources, layouts):
            parts = []
            for kind, value in layout:
                parts.append(str(value) if kind == "literal" else translated_tasks[int(value)])
            candidate = "".join(parts).strip()
            issues = field_anchor_errors(source, candidate, "translation")
            if issues:
                raise RuntimeError(
                    f"offline translation lost immutable anchors despite segmented assembly: {issues}; "
                    f"source={source[:160]!r}"
                )
            if not candidate:
                raise RuntimeError(f"offline translation returned empty text for {source[:160]!r}")
            results.append(candidate)
        return results

    def translate(self, source: str) -> str:
        return self.translate_many([source])[0]
