#!/usr/bin/env python3
"""Generate paired PT/EN literal catalogs for CloudPath internal application pages."""
from __future__ import annotations
import hashlib, html, json, os, re, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; API='https://models.github.ai/inference/chat/completions'
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

def translate(token,model,batch):
    body={'model':model,'temperature':0.1,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':'Translate user-visible CloudPath application UI strings from Brazilian Portuguese to concise natural US English. Preserve AWS names, emoji, punctuation and numbers. Return a JSON object mapping every exact supplied source string to its English translation. Return every key exactly once and no commentary.'},{'role':'user','content':json.dumps(batch,ensure_ascii=False)}]}
    req=urllib.request.Request(API,data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},method='POST')
    last=None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req,timeout=120) as response: payload=json.loads(response.read().decode())
            return json.loads(payload['choices'][0]['message']['content'])
        except Exception as exc:
            last=exc
            if attempt<4: time.sleep(2**attempt)
    raise RuntimeError(f'GitHub Models translation failed: {last}')

def main():
    token=os.environ.get('GITHUB_TOKEN'); model=os.environ.get('TRANSLATION_MODEL','openai/gpt-4.1-mini')
    if not token: raise RuntimeError('GITHUB_TOKEN required')
    sources=extract(); translated={}
    for i in range(0,len(sources),40):
        batch=sources[i:i+40]; got=translate(token,model,batch)
        if set(got)!=set(batch): raise RuntimeError('internal literal translation key mismatch')
        translated.update(got); time.sleep(.5)
    pt={}; en={}
    for source in sources:
        key='literal_'+hashlib.sha1(source.encode()).hexdigest()[:12]; pt[key]=source; en[key]=translated[source].strip()
        if not en[key]: raise RuntimeError(f'empty EN literal: {source}')
    for locale,data in [('pt-BR',pt),('en',en)]:
        path=ROOT/'locales'/locale/'internal-literals.json'; path.write_text(json.dumps({'internalLiterals':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'wrote {path.relative_to(ROOT)}: {len(data)} literals')
    return 0
if __name__=='__main__': raise SystemExit(main())
