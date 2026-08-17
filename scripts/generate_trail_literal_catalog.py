#!/usr/bin/env python3
"""Generate PT/EN literal catalogs for one CloudPath study-trail HTML page offline.

The HTML markup remains canonical and single-source. Only visible prose/accessible
labels are extracted. script/style/pre/code/svg blocks are excluded so code and
runtime logic are never translated by this pipeline.
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

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('request'); args=parser.parse_args()
    req=json.loads((ROOT/args.request).read_text(encoding='utf-8')); trail=req['trail']; page=PAGES[trail]
    values=extract(page)
    print(f'{trail}: translating {len(values)} visible fragments from {page} offline')
    translator=OfflineTranslator(); translated=translator.translate_many(values,batch_size=10)
    pt={}; en={}
    for source,value in zip(values,translated):
        key='literal_'+hashlib.sha1(source.encode()).hexdigest()[:14]; pt[key]=source; en[key]=value.strip()
        if not en[key]: raise RuntimeError(f'empty EN trail literal: {source[:80]}')
    filename=f'trail-{trail}-literals.json'
    for locale,data in [('pt-BR',pt),('en',en)]:
        path=ROOT/'locales'/locale/filename; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'trailLiterals':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {path.relative_to(ROOT)}: {len(data)} fragments')
    return 0
if __name__=='__main__': raise SystemExit(main())
