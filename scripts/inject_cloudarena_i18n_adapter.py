#!/usr/bin/env python3
"""Inject the CloudArena literal i18n adapter once without disturbing markup."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'cloudarena.html'
SCRIPT='    <script src="js/i18n-cloudarena.js" defer></script>\n'

def main():
    text=HTML.read_text(encoding='utf-8')
    if 'js/i18n-cloudarena.js' in text:
        print('cloudarena.html: i18n adapter already present'); return 0
    marker='</body>'
    if text.count(marker)!=1: raise RuntimeError(f'expected one </body>, found {text.count(marker)}')
    text=text.replace(marker,SCRIPT+marker,1)
    HTML.write_text(text,encoding='utf-8')
    print('patched cloudarena.html: reactive i18n adapter injected'); return 0
if __name__=='__main__': raise SystemExit(main())
