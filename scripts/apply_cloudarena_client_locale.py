#!/usr/bin/env python3
"""Attach the selected CloudPath locale to CloudArena API requests."""
from __future__ import annotations
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TARGET=ROOT/'js'/'cloudarena.js'
MARKER='cloudpathArenaLocale'

def main():
    text=TARGET.read_text(encoding='utf-8')
    if MARKER in text:
        print('cloudarena.js: locale request already applied'); return 0

    # Prefer a template literal /api/arena/${...}. Keep the original expression intact.
    pattern=re.compile(r"`/api/arena/\$\{([^}]+)\}`")
    matches=list(pattern.finditer(text))
    if matches:
        if len(matches)!=1:
            raise RuntimeError(f'expected one CloudArena template API URL, found {len(matches)}')
        expr=matches[0].group(1)
        replacement=f"`/api/arena/${{{expr}}}?locale=${{encodeURIComponent(window.I18n?.locale || 'pt-BR')}}` /* {MARKER} */"
        text=text[:matches[0].start()]+replacement+text[matches[0].end():]
    else:
        # Fallback for a concatenated URL expression.
        pattern2=re.compile(r"(['\"])/api/arena/\1\s*\+\s*([A-Za-z_$][\w$]*)")
        matches=list(pattern2.finditer(text))
        if len(matches)!=1:
            raise RuntimeError(f'CloudArena API URL marker not found uniquely; template=0 concat={len(matches)}')
        quote,var=matches[0].group(1),matches[0].group(2)
        replacement=f"{quote}/api/arena/{quote} + {var} + '?locale=' + encodeURIComponent(window.I18n?.locale || 'pt-BR') /* {MARKER} */"
        text=text[:matches[0].start()]+replacement+text[matches[0].end():]

    TARGET.write_text(text,encoding='utf-8')
    print('patched js/cloudarena.js: Arena API now carries selected locale')
    return 0
if __name__=='__main__': raise SystemExit(main())
