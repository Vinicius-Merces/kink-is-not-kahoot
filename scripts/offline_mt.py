#!/usr/bin/env python3
"""Offline PT-BR -> EN translation helper for CI.

Uses the Apache-2.0 Helsinki-NLP/opus-mt-roa-en Marian checkpoint locally on the
GitHub Actions runner. No hosted inference API or project secret is required.
Technical/numeric anchors are protected and verified so AWS names, acronyms,
prices, percentages and durations cannot silently disappear.
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


def _protected_spans(text: str):
    spans = []
    for regex in (EXTRA_PROTECTED_RE, TECHNICAL_RE, NUMBER_RE):
        for match in regex.finditer(text or ""):
            spans.append((match.start(), match.end(), match.group(0)))
    spans.sort(key=lambda row: (row[0], -(row[1] - row[0])))
    result = []
    last_end = -1
    for start, end, value in spans:
        if start < last_end:
            continue
        result.append((start, end, value))
        last_end = end
    return result


def _protect(text: str):
    spans = _protected_spans(text)
    if not spans:
        return text, {}
    parts = []
    cursor = 0
    mapping = {}
    for idx, (start, end, value) in enumerate(spans):
        token = f"CPXQ{idx:03d}QXPC"
        parts.append(text[cursor:start])
        parts.append(token)
        mapping[token] = value
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts), mapping


def _restore(text: str, mapping: dict[str, str]):
    restored = text
    for token, value in mapping.items():
        # Marian normally copies these opaque ASCII tokens. Be tolerant of spaces
        # the tokenizer may insert inside the sentinel.
        pattern = r"\s*".join(re.escape(ch) for ch in token)
        restored, count = re.subn(pattern, lambda _m, v=value: v, restored, count=1, flags=re.I)
        if count == 0:
            return None
    return restored


def _chunk(text: str, max_chars: int = 1050):
    text = (text or "").strip()
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
            # Last-resort clause split while retaining all source text.
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
class _ChunkTask:
    owner: int
    protected: str
    mapping: dict[str, str]


class OfflineTranslator:
    def __init__(self, model_id: str = MODEL_ID):
        # Imports are lazy so validators that import this module don't need ML deps.
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

    def _segmented_fallback(self, source: str) -> str:
        spans = _protected_spans(source)
        if not spans:
            return self._generate_batch([source])[0].strip()
        parts = []
        cursor = 0
        natural = []
        layout = []
        for start, end, value in spans:
            before = source[cursor:start]
            if before:
                natural.append(before)
                layout.append(("natural", len(natural) - 1))
            layout.append(("anchor", value))
            cursor = end
        if cursor < len(source):
            natural.append(source[cursor:])
            layout.append(("natural", len(natural) - 1))
        translated_natural = []
        for value in natural:
            if re.search(r"[A-Za-zÀ-ÿ]", value):
                translated_natural.append(self._generate_batch([value])[0])
            else:
                translated_natural.append(value)
        for kind, value in layout:
            parts.append(translated_natural[value] if kind == "natural" else value)
        return "".join(parts).strip()

    def translate_many(self, sources: list[str], batch_size: int = 12) -> list[str]:
        results = [""] * len(sources)
        tasks: list[_ChunkTask] = []
        owner_chunks: list[list[int]] = [[] for _ in sources]
        for owner, source in enumerate(sources):
            for chunk in _chunk(source):
                protected, mapping = _protect(chunk)
                task_idx = len(tasks)
                tasks.append(_ChunkTask(owner, protected, mapping))
                owner_chunks[owner].append(task_idx)

        translated_chunks = [""] * len(tasks)
        for offset in range(0, len(tasks), batch_size):
            batch = tasks[offset:offset + batch_size]
            outputs = self._generate_batch([task.protected for task in batch])
            if len(outputs) != len(batch):
                raise RuntimeError("offline MT output cardinality mismatch")
            for local_idx, (task, output) in enumerate(zip(batch, outputs)):
                restored = _restore(output, task.mapping)
                if restored is None:
                    restored = self._segmented_fallback(_restore(task.protected, task.mapping) or task.protected)
                translated_chunks[offset + local_idx] = restored.strip()

        for owner, source in enumerate(sources):
            candidate = " ".join(translated_chunks[idx] for idx in owner_chunks[owner]).strip()
            issues = field_anchor_errors(source, candidate, "translation")
            if issues:
                candidate = self._segmented_fallback(source)
                issues = field_anchor_errors(source, candidate, "translation")
            if issues:
                raise RuntimeError(f"offline translation lost protected anchors: {issues}; source={source[:160]!r}")
            if not candidate:
                raise RuntimeError(f"offline translation returned empty text for {source[:160]!r}")
            results[owner] = candidate
        return results

    def translate(self, source: str) -> str:
        return self.translate_many([source])[0]
