#!/usr/bin/env python3
"""Generate English CloudArena pedagogical staging locally with Marian MT.

Structural metadata stays canonical in the PT overlay. Only reasonWrong and
final-blow justification prose is translated.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from offline_mt import OfflineTranslator
from translation_integrity import field_anchor_errors

ROOT=Path(__file__).resolve().parents[1]

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def qnum(qid):
    m=re.search(r'(\d+)$',qid); return int(m.group(1)) if m else 0

def ready_questions(cert):
    result={}
    for level in ('iniciante','medio','avancado'):
        path=ROOT/'data'/'exams-en'/cert/f'{level}.json'
        if not path.exists(): raise RuntimeError(f'Ready EN bank required: {path.relative_to(ROOT)}')
        payload=load(path)
        if (payload.get('_translation') or {}).get('status')!='ready': raise RuntimeError(f'EN bank not ready: {path.relative_to(ROOT)}')
        result.update({q['id']:q for q in payload.get('questions',[])})
    return result

def existing_ids(cert):
    d=ROOT/'translations'/'en'/'cloudarena'/cert; ids=set()
    if d.exists():
        for path in d.glob('*.json'): ids.update((load(path).get('questions') or {}).keys())
    return ids

def translate_batch(translator,overlays):
    strings=[]; slots=[]
    for ov in overlays:
        qid=ov['questionId']
        for option in ov.get('options',[]):
            source=option.get('reasonWrong','')
            if source.strip(): strings.append(source); slots.append((qid,'reason',option['optionId'],source))
        for idx,item in enumerate((ov.get('finalBlow') or {}).get('justifications',[])):
            source=item.get('text','')
            strings.append(source); slots.append((qid,'final',idx,source))
    translated=translator.translate_many(strings,batch_size=10) if strings else []
    output={ov['questionId']:{'optionReasons':{o['optionId']:'' for o in ov.get('options',[])},'finalJustifications':['']*len((ov.get('finalBlow') or {}).get('justifications',[]))} for ov in overlays}
    for slot,value in zip(slots,translated):
        qid,kind,key,source=slot
        issues=field_anchor_errors(source,value,f'{qid}:{kind}:{key}')
        if issues: raise RuntimeError(str(issues))
        if kind=='reason': output[qid]['optionReasons'][key]=value
        else: output[qid]['finalJustifications'][key]=value
    return output

def validate(overlays,translated):
    if set(translated)!={ov['questionId'] for ov in overlays}: raise ValueError('question IDs mismatch')
    for ov in overlays:
        qid=ov['questionId']; item=translated[qid]
        expected={o['optionId'] for o in ov.get('options',[])}
        if set(item['optionReasons'])!=expected: raise ValueError(f'{qid}: option IDs mismatch')
        for option in ov.get('options',[]):
            source=option.get('reasonWrong',''); value=item['optionReasons'][option['optionId']]
            if bool(source.strip())!=bool(value.strip()): raise ValueError(f'{qid}:{option["optionId"]}: empty parity changed')
        source_just=(ov.get('finalBlow') or {}).get('justifications',[])
        if len(item['finalJustifications'])!=len(source_just): raise ValueError(f'{qid}: justification count changed')
        if any(not str(v).strip() for v in item['finalJustifications']): raise ValueError(f'{qid}: empty final justification')
    return translated

def write_batch(cert,overlays,translated):
    start,end=qnum(overlays[0]['questionId']),qnum(overlays[-1]['questionId'])
    d=ROOT/'translations'/'en'/'cloudarena'/cert; d.mkdir(parents=True,exist_ok=True)
    target=d/(f'{start:03d}-{end:03d}.json' if start!=end else f'{start:03d}.json')
    if target.exists(): raise FileExistsError(f'Refusing to overwrite {target.relative_to(ROOT)}')
    target.write_text(json.dumps({'_batch':{'locale':'en','sourceLocale':'pt-BR','certId':cert,'range':f'{start:03d}-{end:03d}','generator':'offline-marian-faithful'},'questions':translated},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'wrote {target.relative_to(ROOT)}: {len(overlays)} overlays')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('request'); args=ap.parse_args(); req=load(ROOT/args.request)
    cert=req['certId']; batch_size=max(1,min(int(req.get('batchSize',8)),8)); questions=ready_questions(cert); done=existing_ids(cert)
    source=load(ROOT/'data'/'cloudarena'/'breakdowns'/f'{cert}.json'); overlays=[ov for ov in source.get('overlays',[]) if ov.get('questionId') not in done]
    if not overlays: print('No missing CloudArena overlays to translate'); return 0
    for ov in overlays:
        if ov['questionId'] not in questions: raise RuntimeError(f'Ready EN question missing: {ov["questionId"]}')
        if any(not x.get('optionId') for x in ov.get('options',[])): raise RuntimeError(f'optionId required: {ov["questionId"]}')
    translator=OfflineTranslator(); print(f'offline CloudArena staging {cert}: {len(overlays)} overlays')
    for off in range(0,len(overlays),batch_size):
        batch=overlays[off:off+batch_size]; translated=validate(batch,translate_batch(translator,batch)); write_batch(cert,batch,translated)
    return 0
if __name__=='__main__': raise SystemExit(main())
