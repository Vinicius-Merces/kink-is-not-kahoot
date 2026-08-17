#!/usr/bin/env python3
"""Generate PT/EN literal catalogs for one CloudPath study-trail HTML page.

The HTML markup remains canonical and single-source. Only visible prose/accessible
labels are extracted. script/style/pre/code blocks are excluded so code examples,
selectors and runtime logic are never translated by this pipeline.
"""
from __future__ import annotations
import argparse, hashlib, html, json, os, re, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; API='https://models.github.ai/inference/chat/completions'
PAGES={'clf':'trilha.html','dea':'trilha-dea.html','dva':'trilha-dva.html','saa':'trilha-saa.html'}
PT=re.compile(r"[áéíóúâêôãõç]|\b(?:a|o|as|os|um|uma|de|do|da|dos|das|para|por|com|sem|que|qual|quando|como|onde|seu|sua|seus|suas|você|nuvem|serviço|serviços|dados|recurso|recursos|segurança|rede|armazenamento|banco|aplicação|usuário|conta|região|zona|disponibilidade|gerenciado|permite|utiliza|utilizar|criar|configurar|acesso|custo|custos|exemplo|importante|lembre|resumo|capítulo|conceito|conceitos|prática|práticas|arquitetura|responsabilidade|monitoramento|processamento|mensagem|mensagens|função|funções)\b",re.I)

def clean_html(raw):
    for tag in ('script','style','pre','code','svg'):
        raw=re.sub(fr'<{tag}\b[^>]*>.*?</{tag}>',' ',raw,flags=re.S|re.I)
    return raw

def candidate(value):
    value=html.unescape(value).replace('\xa0',' '); value=re.sub(r'\s+',' ',value).strip()
    if len(value)<2 or not re.search(r'[A-Za-zÀ-ÿ]',value): return None
    if len(value)>5000: return None
    if PT.search(value): return value
    return None

def extract(page):
    raw=clean_html((ROOT/page).read_text(encoding='utf-8')); values=set()
    for m in re.finditer(r'>([^<>]+)<',raw):
        v=candidate(m.group(1));
        if v: values.add(v)
    for m in re.finditer(r'(?:aria-label|title|placeholder|alt)=["\']([^"\']+)["\']',raw,re.I):
        v=candidate(m.group(1));
        if v: values.add(v)
    return sorted(values,key=lambda x:(x.casefold(),x))

def call_model(token,model,batch):
    system='''Translate CloudPath AWS study-guide content from Brazilian Portuguese to clear professional US English for certification learners. Preserve technical meaning, AWS official product names, acronyms, numbers, punctuation, emoji and inline terminology. Do not add or remove factual claims. Return JSON only: every exact source string supplied must be a key and the value must be its English translation. Return every key exactly once.'''
    body={'model':model,'temperature':0.1,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(batch,ensure_ascii=False)}]}
    req=urllib.request.Request(API,data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},method='POST')
    last=None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req,timeout=180) as r: payload=json.loads(r.read().decode())
            return json.loads(payload['choices'][0]['message']['content'])
        except Exception as exc:
            last=exc
            if attempt<4: time.sleep(2**attempt)
    raise RuntimeError(f'GitHub Models trail translation failed: {last}')

def batches(values,max_chars=15000,max_items=28):
    batch=[]; chars=0
    for value in values:
        if batch and (len(batch)>=max_items or chars+len(value)>max_chars):
            yield batch; batch=[]; chars=0
        batch.append(value); chars+=len(value)
    if batch: yield batch

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('request'); args=parser.parse_args()
    req=json.loads((ROOT/args.request).read_text(encoding='utf-8')); trail=req['trail']; page=PAGES[trail]
    token=os.environ.get('GITHUB_TOKEN'); model=req.get('model','openai/gpt-4.1-mini')
    if not token: raise RuntimeError('GITHUB_TOKEN required')
    values=extract(page); translated={}
    print(f'{trail}: translating {len(values)} unique visible text fragments from {page}')
    for batch in batches(values):
        got=call_model(token,model,batch)
        if set(got)!=set(batch): raise RuntimeError('trail translation response key mismatch')
        translated.update(got); time.sleep(.5)
    pt={}; en={}
    for source in values:
        key='literal_'+hashlib.sha1(source.encode()).hexdigest()[:14]; pt[key]=source; en[key]=str(translated[source]).strip()
        if not en[key]: raise RuntimeError(f'empty EN trail literal: {source[:80]}')
    filename=f'trail-{trail}-literals.json'
    for locale,data in [('pt-BR',pt),('en',en)]:
        path=ROOT/'locales'/locale/filename; path.write_text(json.dumps({'trailLiterals':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {path.relative_to(ROOT)}: {len(data)} fragments')
    return 0
if __name__=='__main__': raise SystemExit(main())
