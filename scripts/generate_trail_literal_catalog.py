#!/usr/bin/env python3
"""Generate PT/EN literal catalogs for CloudPath study-trail HTML pages offline.

The HTML markup remains canonical and single-source. Only visible prose/accessible
labels are extracted. script/style/pre/code/svg blocks are excluded so code and
runtime logic are never translated. A request may target one trail or `all`; the
translator model is loaded only once per process.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re
from pathlib import Path
from offline_mt import OfflineTranslator

ROOT=Path(__file__).resolve().parents[1]
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
    return value if PT.search(value) else None

def extract(page):
    raw=clean_html((ROOT/page).read_text(encoding='utf-8')); values=set()
    for m in re.finditer(r'>([^<>]+)<',raw):
        v=candidate(m.group(1));
        if v: values.add(v)
    for m in re.finditer(r'(?:aria-label|title|placeholder|alt)=["\']([^"\']+)["\']',raw,re.I):
        v=candidate(m.group(1));
        if v: values.add(v)
    return sorted(values,key=lambda x:(x.casefold(),x))

def write_trail(trail,translator):
    page=PAGES[trail]; values=extract(page)
    print(f'{trail}: translating {len(values)} visible fragments from {page} offline')
    translated=translator.translate_many(values,batch_size=12)
    pt={}; en={}
    for source,value in zip(values,translated):
        key='literal_'+hashlib.sha1(source.encode()).hexdigest()[:14]
        pt[key]=source; en[key]=value.strip()
        if not en[key]: raise RuntimeError(f'empty EN trail literal: {source[:80]}')
    filename=f'trail-{trail}-literals.json'
    for locale,data in [('pt-BR',pt),('en',en)]:
        path=ROOT/'locales'/locale/filename; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'trailLiterals':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {path.relative_to(ROOT)}: {len(data)} fragments')

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('request'); args=parser.parse_args()
    req=json.loads((ROOT/args.request).read_text(encoding='utf-8'))
    requested=req['trail']; targets=list(PAGES) if requested=='all' else [requested]
    unknown=[trail for trail in targets if trail not in PAGES]
    if unknown: raise ValueError(f'unknown trails: {unknown}')
    translator=OfflineTranslator()
    for trail in targets: write_trail(trail,translator)
    return 0
if __name__=='__main__': raise SystemExit(main())
