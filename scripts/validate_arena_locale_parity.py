#!/usr/bin/env python3
"""Validate structural parity between canonical PT and ready EN CloudArena overlays."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PT=ROOT/'data'/'cloudarena'/'breakdowns'; EN=ROOT/'data'/'cloudarena'/'breakdowns-en'

def load(path): return json.loads(path.read_text(encoding='utf-8'))
def signature(ov):
    return {
        'questionId':ov.get('questionId'),
        'options':[(o.get('optionId'),o.get('stage')) for o in ov.get('options',[])],
        'finalCorrect':[j.get('correct') for j in (ov.get('finalBlow') or {}).get('justifications',[])],
    }
def main():
    errors=[]; checked=0
    for pt_path in sorted(PT.glob('*.json')):
        en_path=EN/pt_path.name
        if not en_path.exists(): continue
        pt=load(pt_path); en=load(en_path)
        meta=en.get('_translation') or {}
        if meta.get('locale')!='en' or meta.get('sourceLocale')!='pt-BR' or meta.get('status')!='ready':
            errors.append(f'{en_path.relative_to(ROOT)}: invalid _translation metadata')
            continue
        pt_by={o['questionId']:o for o in pt.get('overlays',[])}; en_by={o['questionId']:o for o in en.get('overlays',[])}
        if set(pt_by)!=set(en_by): errors.append(f'{pt_path.stem}: questionId coverage differs'); continue
        for qid in pt_by:
            if signature(pt_by[qid])!=signature(en_by[qid]): errors.append(f'{pt_path.stem}:{qid}: structural metadata changed')
            checked+=1
    if errors:
        print(f'CloudArena locale parity failed: {len(errors)} issue(s)')
        for e in errors[:100]: print('  -',e)
        return 1
    print(f'CloudArena locale parity passed: {checked} translated overlays checked')
    return 0
if __name__=='__main__': sys.exit(main())
