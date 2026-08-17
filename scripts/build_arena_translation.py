#!/usr/bin/env python3
"""Build a complete English CloudArena overlay from validated staging.

Canonical structural metadata always comes from data/cloudarena/breakdowns/<cert>.json.
English staging can replace only pedagogical prose. optionId is the stable join key.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def en_questions(cert):
    result={}
    for level in ('iniciante','medio','avancado'):
        path=ROOT/'data'/'exams-en'/cert/f'{level}.json'
        payload=load(path)
        if (payload.get('_translation') or {}).get('status')!='ready':
            raise RuntimeError(f'EN exam bank not ready: {path.relative_to(ROOT)}')
        result.update({q['id']:q for q in payload.get('questions',[])})
    return result

def stage_map(cert):
    directory=ROOT/'translations'/'en'/'cloudarena'/cert
    result={}
    if not directory.exists(): return result
    for path in sorted(directory.glob('*.json')):
        for qid,item in (load(path).get('questions') or {}).items():
            if qid in result: raise RuntimeError(f'duplicate staged arena question {qid}')
            result[qid]=item
    return result

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('cert'); parser.add_argument('--write',action='store_true'); args=parser.parse_args()
    cert=args.cert
    source_path=ROOT/'data'/'cloudarena'/'breakdowns'/f'{cert}.json'
    source=load(source_path); overlays=source.get('overlays',[]); staged=stage_map(cert); enq=en_questions(cert)
    ids={ov['questionId'] for ov in overlays}
    unknown=set(staged)-ids
    if unknown: raise RuntimeError(f'unknown staged arena IDs: {sorted(unknown)}')
    missing=ids-set(staged)
    if missing:
        print(f'{cert}: CloudArena staging {len(staged)}/{len(ids)}; missing {len(missing)}')
        return 2
    output=json.loads(json.dumps(source,ensure_ascii=False))
    output['_translation']={'locale':'en','sourceLocale':'pt-BR','status':'ready'}
    for ov in output.get('overlays',[]):
        qid=ov['questionId']; tr=staged[qid]; question=enq[qid]
        option_text={f'{qid}:option:{i}':text for i,text in enumerate(question.get('options',[]))}
        for opt in ov.get('options',[]):
            oid=opt['optionId']
            if oid not in option_text: raise RuntimeError(f'{qid}: EN option missing for {oid}')
            opt['matchText']=option_text[oid]
            opt['reasonWrong']=tr['optionReasons'][oid]
        just=(ov.get('finalBlow') or {}).get('justifications',[])
        texts=tr['finalJustifications']
        if len(just)!=len(texts): raise RuntimeError(f'{qid}: justification count mismatch')
        for item,text in zip(just,texts): item['text']=text
    if args.write:
        target=ROOT/'data'/'cloudarena'/'breakdowns-en'/f'{cert}.json'; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {target.relative_to(ROOT)}: {len(overlays)} overlays')
    else: print(f'{cert}: CloudArena EN complete {len(overlays)}/{len(overlays)}')
    return 0
if __name__=='__main__': raise SystemExit(main())
