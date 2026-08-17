#!/usr/bin/env python3
"""Extract visible PT CloudArena literals and create paired PT/EN catalogs with GitHub Models."""
from __future__ import annotations
import hashlib, html, json, os, re, time, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; API='https://models.github.ai/inference/chat/completions'
CLUES=re.compile(r"[áéíóúâêôãõç]|\b(?:a|o|de|do|da|para|com|sem|seu|sua|voc[eê]|escolha|come[cç]ar|jogar|batalha|arena|quest[aã]o|resposta|correta|errada|vit[oó]ria|derrota|atacar|ataque|defesa|vida|pontos|pontua[cç][aã]o|n[ií]vel|inimigo|continuar|voltar|pr[oó]ximo|tempo|dano|sequ[eê]ncia|certifica[cç][aã]o|dificuldade|carregando|tentar|novamente|sair|finalizar)\b",re.I)
ONE={'vida','pontos','nível','ataque','defesa','vitória','derrota','atacar','continuar','voltar','sair','arena','batalha'}

def candidate(s):
    s=html.unescape(re.sub(r'\\[nrt]', ' ', s)).strip()
    if len(s)<2 or len(s)>260 or not re.search(r'[A-Za-zÀ-ÿ]',s): return None
    low=s.lower()
    if low.startswith(('http','/','.','#','data-','aria-')) or any(x in low for x in ('.html','.json','.mp3','.png','.svg','queryselector','classlist')): return None
    if '${' in s: return None
    if CLUES.search(s) or low.strip(' !?.:') in ONE: return s
    return None

def extract():
    values=set()
    hp=(ROOT/'cloudarena.html').read_text(encoding='utf-8')
    hp=re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>',' ',hp,flags=re.S|re.I)
    for m in re.finditer(r'>([^<>]+)<',hp):
        v=candidate(m.group(1));
        if v: values.add(v)
    for m in re.finditer(r'(?:aria-label|title|placeholder)=["\']([^"\']+)["\']',hp,re.I):
        v=candidate(m.group(1));
        if v: values.add(v)
    js=(ROOT/'js'/'cloudarena.js').read_text(encoding='utf-8')
    for m in re.finditer(r"(['\"])((?:\\.|(?!\1).){2,260})\1",js):
        v=candidate(m.group(2));
        if v: values.add(v)
    return sorted(values,key=lambda x:(x.casefold(),x))

def translate(token,model,items):
    system='''Translate user-visible CloudArena game-interface literals from Brazilian Portuguese to concise natural US English. Preserve AWS product names, emoji, punctuation, placeholders, numbers and game tone. Return a JSON object where every exact source string is a key and its English translation is the value. Translate only the supplied strings; return every key exactly once. Do not add commentary.'''
    body={'model':model,'temperature':0.1,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(items,ensure_ascii=False)}]}
    req=urllib.request.Request(API,data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},method='POST')
    last=None
    for n in range(5):
        try:
            with urllib.request.urlopen(req,timeout=120) as r: payload=json.loads(r.read().decode())
            return json.loads(payload['choices'][0]['message']['content'])
        except Exception as e:
            last=e
            if n<4: time.sleep(2**n)
    raise RuntimeError(f'GitHub Models translation failed: {last}')

def main():
    token=os.environ.get('GITHUB_TOKEN'); model=os.environ.get('TRANSLATION_MODEL','openai/gpt-4.1-mini')
    if not token: raise RuntimeError('GITHUB_TOKEN required')
    sources=extract(); translations={}
    for i in range(0,len(sources),40):
        batch=sources[i:i+40]; got=translate(token,model,batch)
        if set(got)!=set(batch): raise RuntimeError('literal translation key mismatch')
        translations.update(got); time.sleep(.5)
    pt={}; en={}
    for source in sources:
        key='literal_'+hashlib.sha1(source.encode()).hexdigest()[:12]
        pt[key]=source; value=translations[source]
        if not isinstance(value,str) or not value.strip(): raise RuntimeError(f'empty translation: {source}')
        en[key]=value.strip()
    for locale,data in [('pt-BR',pt),('en',en)]:
        path=ROOT/'locales'/locale/'cloudarena-literals.json'; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'cloudarenaLiterals':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {path.relative_to(ROOT)}: {len(data)} literals')
    return 0
if __name__=='__main__': raise SystemExit(main())
