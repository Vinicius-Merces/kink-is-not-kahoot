#!/usr/bin/env python3
"""Inject the shared study-trail content adapter without reserializing HTML."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGES=['trilha.html','trilha-dea.html','trilha-dva.html','trilha-saa.html']
SCRIPT='    <script src="js/i18n-trail-content.js" defer></script>\n'

def main():
    changed=0
    for name in PAGES:
        path=ROOT/name
        if not path.exists(): continue
        text=path.read_text(encoding='utf-8')
        if 'js/i18n-trail-content.js' in text: continue
        if text.count('</body>')!=1: raise RuntimeError(f'{name}: expected one </body>')
        path.write_text(text.replace('</body>',SCRIPT+'</body>',1),encoding='utf-8'); changed+=1; print(f'patched {name}')
    print(f'trail adapter injection complete: {changed} page(s) changed'); return 0
if __name__=='__main__': raise SystemExit(main())
