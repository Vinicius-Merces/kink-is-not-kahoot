#!/usr/bin/env python3
"""Inject shared internal literal adapter into non-trail application pages."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGES=['admin.html','create-quiz.html','historico.html','host.html','my-quizzes.html','player.html','progresso.html']
SCRIPT='    <script src="js/i18n-internal-literals.js" defer></script>\n'

def main():
    changed=0
    for name in PAGES:
        path=ROOT/name
        if not path.exists(): continue
        text=path.read_text(encoding='utf-8')
        if 'js/i18n-internal-literals.js' in text: continue
        if text.count('</body>')!=1: raise RuntimeError(f'{name}: expected one </body>')
        path.write_text(text.replace('</body>',SCRIPT+'</body>',1),encoding='utf-8'); changed+=1
        print(f'patched {name}')
    print(f'internal adapter injection complete: {changed} page(s) changed')
    return 0
if __name__=='__main__': raise SystemExit(main())
