#!/usr/bin/env python3
"""Valida vínculos e cobertura da revisão individual SAA-C03 avançado.

--require-complete exige as 235 questões no registro de auditoria.
Não substitui revisão pedagógica nem validação técnica do conteúdo.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    bank = json.loads((ROOT / 'data/exams/saa-c03/avancado.json').read_text())
    entries = json.loads((ROOT / 'data/cloudarena/breakdowns/saa-c03.json').read_text())['overlays']
    reviewed = json.loads((ROOT / 'docs/auditoria-saa-avancado-registro.json').read_text())
    questions = bank['questions']
    indexed = {q['id']: q for q in questions}
    overlays = {o['questionId']: o for o in entries}
    expected = {f'saa-avc-{n:03}' for n in range(1, 237) if n != 4}
    errors = []
    if len(questions) != 235 or set(indexed) != expected:
        errors.append('Quantidade ou conjunto de IDs do avançado alterado.')
    if len({q['text'].strip() for q in questions}) != len(questions):
        errors.append('Enunciados duplicados.')
    for q in questions:
        if len(set(q['options'])) != len(q['options']):
            errors.append(f"{q['id']}: alternativas duplicadas.")
    for qid in reviewed:
        q = indexed.get(qid)
        if q is None:
            errors.append(f'{qid}: registro sem questão correspondente.')
            continue
        reasons = q.get('optionRationales', [])
        if len(reasons) != len(q['options']) or not all(isinstance(r, str) and r.strip() for r in reasons):
            errors.append(f'{qid}: justificativas incompletas.')
            continue
        if not q.get('hint', '').strip():
            errors.append(f'{qid}: dica ausente.')
        if q['explanation'] != ' '.join(reasons):
            errors.append(f'{qid}: explicação diverge das justificativas revisadas.')
        if isinstance(q['correct'], int):
            overlay = overlays.get(qid)
            if overlay is None:
                errors.append(f'{qid}: overlay ausente.')
                continue
            if {o['matchText'] for o in overlay['options']} != set(q['options']):
                errors.append(f'{qid}: referências de alternativas divergentes.')
            for option in overlay['options']:
                if option['matchText'] not in q['options']:
                    continue
                index = q['options'].index(option['matchText'])
                if (option['stage'] == 'correct') != (index == q['correct']):
                    errors.append(f'{qid}: gabarito divergente na Arena.')
                if option['stage'] != 'correct' and option.get('reasonWrong') != reasons[index]:
                    errors.append(f'{qid}: reasonWrong divergente do rationale.')
            justifications = overlay['finalBlow']['justifications']
            if len(justifications) != 4 or sum(j.get('correct') is True for j in justifications) != 1:
                errors.append(f'{qid}: finalBlow inválido.')
            if len({j['text'] for j in justifications}) != 4:
                errors.append(f'{qid}: justificativas duplicadas na Arena.')
    missing = sorted(expected - set(reviewed))
    print(f'Revisadas: {len(reviewed)}/235. Pendentes: {len(missing)}.')
    for error in errors:
        print('ERRO:', error)
    if errors:
        return 1
    print('OK: vínculos das questões revisadas consistentes.')
    if missing and args.require_complete:
        print('INCOMPLETA: a branch ainda não atende à cobertura final de 235 questões.')
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
