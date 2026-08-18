#!/usr/bin/env python3
"""Extract CloudArena PT literals and generate paired PT/EN catalogs offline."""
from __future__ import annotations
import hashlib, html, json, re
from pathlib import Path
from offline_mt import OfflineTranslator

ROOT=Path(__file__).resolve().parents[1]
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

def main():
    sources=extract()
    print(f'CloudArena UI: translating {len(sources)} unique literals offline')
    translator=OfflineTranslator(); translations=translator.translate_many(sources,batch_size=12)
    pt={}; en={}
    for source,value in zip(sources,translations):
        key='literal_'+hashlib.sha1(source.encode()).hexdigest()[:12]
        pt[key]=source; en[key]=value.strip()
        if not en[key]: raise RuntimeError(f'empty translation: {source}')
    for locale,data in [('pt-BR',pt),('en',en)]:
        path=ROOT/'locales'/locale/'cloudarena-literals.json'; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'cloudarenaLiterals':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {path.relative_to(ROOT)}: {len(data)} literals')
    return 0
if __name__=='__main__': raise SystemExit(main())
