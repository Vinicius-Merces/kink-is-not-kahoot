#!/usr/bin/env python3
"""Generate faithful English exam staging locally with Marian MT."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from offline_mt import OfflineTranslator
from translation_integrity import question_anchor_errors

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_FIELDS={'text','options','explanation','hint','optionRationales'}

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def qnum(qid):
    m=re.search(r'(\d+)$',qid)
    if not m: raise ValueError(f'question id has no numeric suffix: {qid}')
    return int(m.group(1))

def existing(cert,level):
    d=ROOT/'translations'/'en'/cert/level; ids=set()
    if d.exists():
        for p in d.glob('*.json'): ids.update((load(p).get('questions') or {}).keys())
    return ids

def fields(q):
    out={'text':q.get('text',''),'options':q.get('options',[]),'explanation':q.get('explanation','')}
    if 'hint' in q: out['hint']=q.get('hint','')
    if 'optionRationales' in q: out['optionRationales']=q.get('optionRationales',[])
    return out

def translate_question(translator,q):
    src=fields(q); values=[]; layout=[]
    for key,value in src.items():
        if isinstance(value,list):
            for i,text in enumerate(value): values.append(text); layout.append((key,i))
        else: values.append(value); layout.append((key,None))
    translated=translator.translate_many(values,batch_size=10)
    out={k:([] if isinstance(v,list) else '') for k,v in src.items()}
    for (key,index),value in zip(layout,translated):
        if index is None: out[key]=value
        else: out[key].append(value)
    if set(out)-ALLOWED_FIELDS: raise RuntimeError('forbidden translated fields')
    issues=question_anchor_errors(q,out)
    if issues: raise RuntimeError(f"{q['id']}: translation integrity failed: {issues}")
    return out

def write_batch(cert,level,source_path,questions,items):
    start,end=qnum(questions[0]['id']),qnum(questions[-1]['id'])
    d=ROOT/'translations'/'en'/cert/level; d.mkdir(parents=True,exist_ok=True)
    name=f'{start:03d}-{end:03d}.json' if start!=end else f'{start:03d}.json'; target=d/name
    if target.exists(): raise FileExistsError(f'refusing to overwrite {target.relative_to(ROOT)}')
    payload={'_batch':{'locale':'en','sourceLocale':'pt-BR','certId':cert,'level':level,'sourcePath':source_path,'range':f'{start:03d}-{end:03d}' if start!=end else f'{start:03d}','generator':'offline-marian-faithful'},'questions':items}
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'wrote {target.relative_to(ROOT)} ({len(questions)} questions)')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('request'); args=ap.parse_args()
    req=load(ROOT/args.request); cert=req['certId']; level=req['level']; start=int(req.get('start',1)); end=int(req.get('end',10**9)); batch_size=max(1,min(int(req.get('batchSize',5)),8))
    source_rel=f'data/exams/{cert}/{level}.json'; bank=load(ROOT/source_rel); done=existing(cert,level)
    selected=[q for q in bank.get('questions',[]) if start<=qnum(q['id'])<=end and q['id'] not in done]
    if not selected: print('No missing questions in requested range'); return 0
    translator=OfflineTranslator(); print(f'offline EN staging {cert}/{level}: {len(selected)} questions')
    for off in range(0,len(selected),batch_size):
        batch=selected[off:off+batch_size]; output={}
        for q in batch: output[q['id']]=translate_question(translator,q)
        write_batch(cert,level,source_rel,batch,output)
    return 0
if __name__=='__main__': raise SystemExit(main())
