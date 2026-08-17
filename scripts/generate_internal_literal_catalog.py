#!/usr/bin/env python3
"""Generate paired PT/EN literal catalogs for CloudPath internal pages offline."""
from __future__ import annotations
import hashlib, html, json, re
from pathlib import Path
from offline_mt import OfflineTranslator

ROOT=Path(__file__).resolve().parents[1]
HTML_FILES=['admin.html','create-quiz.html','historico.html','host.html','my-quizzes.html','player.html','progresso.html']
JS_FILES=['js/admin.js','js/create-quiz.js','js/historico.js','js/host-socket.js','js/player-socket.js','js/progresso.js','js/quiz-manager.js','js/report-question.js','js/study-progress.js']
CLUES=re.compile(r"[áéíóúâêôãõç]|\b(?:a|o|de|do|da|para|com|sem|seu|sua|voc[eê]|usu[aá]rio|usu[aá]rios|quiz|pergunta|perguntas|resposta|respostas|correta|errada|criar|editar|excluir|salvar|cancelar|voltar|continuar|iniciar|finalizar|resultado|resultados|hist[oó]rico|progresso|desempenho|carregando|erro|sucesso|sala|jogador|jogadores|participante|participantes|c[oó]digo|copiar|entrar|sair|administrador|certifica[cç][aã]o|dificuldade|n[ií]vel|pontos|pontua[cç][aã]o|tempo|filtro|filtrar|buscar|nenhum|nenhuma|todos|todas|confirmar)\b",re.I)
ONE={'salvar','cancelar','voltar','continuar','iniciar','finalizar','excluir','editar','criar','progresso','histórico','resultados','entrar','sair','copiar','buscar','todos','todas'}

def candidate(s):
    s=html.unescape(re.sub(r'\\[nrt]',' ',s)).strip()
    if len(s)<2 or len(s)>320 or not re.search(r'[A-Za-zÀ-ÿ]',s): return None
    low=s.lower()
    if low.startswith(('http','/','.','#','data-','aria-')) or any(x in low for x in ('.html','.json','.mp3','.png','.svg','queryselector','classlist','firebase')): return None
    if '${' in s: return None
    if CLUES.search(s) or low.strip(' !?.:') in ONE: return s
    return None

def extract():
    values=set()
    for name in HTML_FILES:
        path=ROOT/name
        if not path.exists(): continue
        text=path.read_text(encoding='utf-8'); text=re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>',' ',text,flags=re.S|re.I)
        for m in re.finditer(r'>([^<>]+)<',text):
            v=candidate(m.group(1));
            if v: values.add(v)
        for m in re.finditer(r'(?:aria-label|title|placeholder)=["\']([^"\']+)["\']',text,re.I):
            v=candidate(m.group(1));
            if v: values.add(v)
    for name in JS_FILES:
        path=ROOT/name
        if not path.exists(): continue
        text=path.read_text(encoding='utf-8')
        for m in re.finditer(r"(['\"])((?:\\.|(?!\1).){2,320})\1",text):
            v=candidate(m.group(2));
            if v: values.add(v)
    return sorted(values,key=lambda x:(x.casefold(),x))

def main():
    sources=extract()
    print(f'internal UI: translating {len(sources)} unique literals offline')
    translator=OfflineTranslator(); values=translator.translate_many(sources,batch_size=12)
    pt={}; en={}
    for source,value in zip(sources,values):
        key='literal_'+hashlib.sha1(source.encode()).hexdigest()[:12]; pt[key]=source; en[key]=value.strip()
        if not en[key]: raise RuntimeError(f'empty EN literal: {source}')
    for locale,data in [('pt-BR',pt),('en',en)]:
        path=ROOT/'locales'/locale/'internal-literals.json'; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'internalLiterals':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {path.relative_to(ROOT)}: {len(data)} literals')
    return 0
if __name__=='__main__': raise SystemExit(main())
