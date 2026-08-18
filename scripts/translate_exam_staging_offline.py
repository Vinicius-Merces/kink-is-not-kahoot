#!/usr/bin/env python3
"""Generate faithful English exam staging locally with Marian MT.

All human-language fields in the selected range are collected first. Identical PT
strings are translated once and reused, then every assembled question is checked
against field-local semantic anchors before any staging batch is written.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from offline_mt import OfflineTranslator
from translation_integrity import question_anchor_errors

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FIELDS = {'text', 'options', 'explanation', 'hint', 'optionRationales'}


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def qnum(qid):
    match = re.search(r'(\d+)$', qid)
    if not match:
        raise ValueError(f'question id has no numeric suffix: {qid}')
    return int(match.group(1))


def existing(cert, level):
    directory = ROOT / 'translations' / 'en' / cert / level
    ids = set()
    if directory.exists():
        for path in directory.glob('*.json'):
            ids.update((load(path).get('questions') or {}).keys())
    return ids


def fields(question):
    result = {
        'text': question.get('text', ''),
        'options': question.get('options', []),
        'explanation': question.get('explanation', ''),
    }
    if 'hint' in question:
        result['hint'] = question.get('hint', '')
    if 'optionRationales' in question:
        result['optionRationales'] = question.get('optionRationales', [])
    return result


def collect_translation_jobs(questions):
    unique_sources = []
    source_index = {}
    jobs = []
    outputs = {}

    for question in questions:
        qid = question['id']
        source_fields = fields(question)
        outputs[qid] = {key: ([] if isinstance(value, list) else '') for key, value in source_fields.items()}
        for key, value in source_fields.items():
            if isinstance(value, list):
                for index, text in enumerate(value):
                    if text not in source_index:
                        source_index[text] = len(unique_sources)
                        unique_sources.append(text)
                    jobs.append((qid, key, index, source_index[text]))
            else:
                if value not in source_index:
                    source_index[value] = len(unique_sources)
                    unique_sources.append(value)
                jobs.append((qid, key, None, source_index[value]))
    return unique_sources, jobs, outputs


def assemble_and_validate(questions, unique_translations, jobs, outputs):
    for qid, key, index, source_idx in jobs:
        value = unique_translations[source_idx]
        if index is None:
            outputs[qid][key] = value
        else:
            outputs[qid][key].append(value)

    source_by_id = {q['id']: q for q in questions}
    for qid, item in outputs.items():
        if set(item) - ALLOWED_FIELDS:
            raise RuntimeError(f'{qid}: forbidden translated fields')
        issues = question_anchor_errors(source_by_id[qid], item)
        if issues:
            raise RuntimeError(f'{qid}: translation integrity failed: {issues}')
    return outputs


def write_batch(cert, level, source_path, questions, items):
    start, end = qnum(questions[0]['id']), qnum(questions[-1]['id'])
    directory = ROOT / 'translations' / 'en' / cert / level
    directory.mkdir(parents=True, exist_ok=True)
    name = f'{start:03d}-{end:03d}.json' if start != end else f'{start:03d}.json'
    target = directory / name
    if target.exists():
        raise FileExistsError(f'refusing to overwrite {target.relative_to(ROOT)}')
    payload = {
        '_batch': {
            'locale': 'en',
            'sourceLocale': 'pt-BR',
            'certId': cert,
            'level': level,
            'sourcePath': source_path,
            'range': f'{start:03d}-{end:03d}' if start != end else f'{start:03d}',
            'generator': 'offline-marian-faithful-v2',
        },
        'questions': {question['id']: items[question['id']] for question in questions},
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'wrote {target.relative_to(ROOT)} ({len(questions)} questions)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('request')
    args = parser.parse_args()

    request = load(ROOT / args.request)
    cert = request['certId']
    level = request['level']
    start = int(request.get('start', 1))
    end = int(request.get('end', 10**9))
    file_batch_size = max(1, min(int(request.get('batchSize', 8)), 12))

    source_rel = f'data/exams/{cert}/{level}.json'
    bank = load(ROOT / source_rel)
    done = existing(cert, level)
    selected = [
        q for q in bank.get('questions', [])
        if start <= qnum(q['id']) <= end and q['id'] not in done
    ]
    if not selected:
        print('No missing questions in requested range')
        return 0

    unique_sources, jobs, outputs = collect_translation_jobs(selected)
    print(
        f'offline EN staging {cert}/{level}: {len(selected)} question(s), '
        f'{len(jobs)} field occurrence(s), {len(unique_sources)} unique PT source string(s)'
    )

    translator = OfflineTranslator()
    unique_translations = translator.translate_many(unique_sources, batch_size=20)
    outputs = assemble_and_validate(selected, unique_translations, jobs, outputs)

    # No files are written until every selected question has passed integrity.
    for offset in range(0, len(selected), file_batch_size):
        batch = selected[offset:offset + file_batch_size]
        write_batch(cert, level, source_rel, batch, outputs)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
