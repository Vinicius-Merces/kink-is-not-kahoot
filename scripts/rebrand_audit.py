#!/usr/bin/env python3
"""Auditoria pos-rebrand: classifica TODA ocorrencia restante de KINK/Kahoot.

Rode DEPOIS do rebrand.py. A pergunta que ele responde nao e "sobrou alguma?",
e sim "sobrou alguma que DEVERIA ter mudado?".

Nem tudo pode ser renomeado. Tres categorias:

  🔴 NAO TOCAR   - renomear QUEBRA o sistema
  🟡 OPCIONAL    - interno, ninguem ve; renomear e cosmetico e arriscado
  🟢 TROCAR      - visivel ao usuario; deveria ter sido pego pelo rebrand.py
"""
import glob
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# 🔴 Padroes que NAO podem ser renomeados, com o motivo.
INTOCAVEL = [
    (r'(authDomain|projectId|storageBucket|messagingSenderId|appId)\s*:',
     "ID do projeto Firebase é IMUTÁVEL — renomear derruba login/Firestore/Storage"),
    (r"kink_[a-z_0-9]*",
     "chave de localStorage — renomear APAGA o progresso salvo dos usuários"),
    (r"kink-is-not-kahoot\.(firebaseapp|firebasestorage|web)\.",
     "domínio real do Firebase — não é texto, é endereço"),
    (r"/assets/music/.*KINK",
     "NOME DE ARQUIVO em disco — renomear no código quebraria o player de música"),
    (r"kink-pwa-banner-dismissed",
     "chave de localStorage do banner PWA"),
]

# 🟡 Interno: valido renomear, mas nao urgente e nao visivel.
OPCIONAL = [
    (r"--kink-[a-z-]+", "variável CSS — invisível ao usuário"),
    (r"kink-is-not-kahoot", "nome do repositório/pasta — o GitHub redireciona sozinho"),
    (r"kink[A-Z][a-zA-Z]+", "nome de @keyframes/animação CSS — invisível"),
    (r"CACHE_NAME|cacheName", "nome do cache do service worker — trocar só invalida o cache"),
]

IGNORAR_ARQUIVOS = {"scripts/rebrand.py", "scripts/rebrand_audit.py",
                    "REBRAND-CLOUDPATH.md", "js/branding.js"}


# Comentario de codigo ou documentacao: nao chega ao usuario.
COMENTARIO = re.compile(r"^\s*(//|/\*|\*|#|<!--)")


def classificar(linha):
    if COMENTARIO.match(linha):
        return "🔵 comentário", "comentário de código — invisível ao usuário"
    for pat, motivo in INTOCAVEL:
        if re.search(pat, linha, re.I):
            return "🔴 NÃO TOCAR", motivo
    for pat, motivo in OPCIONAL:
        if re.search(pat, linha):
            return "🟡 opcional", motivo
    return "🟢 TROCAR", "visível ao usuário"


def main():
    alvos = []
    for pad in ("*.html", "*.json", "*.js", "*.md", "css/*.css", "js/*.js",
                "scripts/*.py", "squarecloud.app"):
        alvos += glob.glob(os.path.join(ROOT, pad))

    buckets = {"🔴 NÃO TOCAR": [], "🟡 opcional": [], "🔵 comentário": [], "🟢 TROCAR": []}

    for path in sorted(set(alvos)):
        rel = os.path.relpath(path, ROOT)
        if rel in IGNORAR_ARQUIVOS or "node_modules" in rel:
            continue
        try:
            conteudo = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue

        # Neutraliza comentarios de BLOCO (/* ... */ e <!-- ... -->) preservando
        # a numeracao: troca o miolo por espacos, mantendo as quebras de linha.
        def _apagar(m):
            return re.sub(r"[^\n]", " ", m.group(0))

        conteudo = re.sub(r"/\*.*?\*/", _apagar, conteudo, flags=re.S)
        conteudo = re.sub(r"<!--.*?-->", _apagar, conteudo, flags=re.S)
        linhas = conteudo.split("\n")
        for i, linha in enumerate(linhas, 1):
            if not re.search(r"kink|kahoot", linha, re.I):
                continue
            cat, motivo = classificar(linha)
            if rel.endswith(".md") and cat == "🟢 TROCAR":
                cat, motivo = "🔵 comentário", "documentação — atualize o README à mão"
            buckets[cat].append((rel, i, linha.strip()[:62], motivo))

    for cat in ("🔴 NÃO TOCAR", "🟡 opcional", "🔵 comentário", "🟢 TROCAR"):
        itens = buckets[cat]
        print(f"\n{'=' * 76}\n{cat} — {len(itens)} ocorrências\n{'=' * 76}")
        if not itens:
            print("  (nenhuma)")
            continue
        # agrupa por motivo para nao virar uma parede de texto
        por_motivo = {}
        for rel, i, txt, motivo in itens:
            por_motivo.setdefault(motivo, []).append((rel, i, txt))
        for motivo, lst in por_motivo.items():
            arquivos = {}
            for rel, i, txt in lst:
                arquivos.setdefault(rel, []).append(i)
            print(f"\n  ▸ {motivo}")
            for rel, ls in sorted(arquivos.items()):
                amostra = ", ".join(map(str, ls[:4])) + ("..." if len(ls) > 4 else "")
                print(f"      {rel} ({len(ls)}x — linhas {amostra})")
            if cat == "🟢 TROCAR":
                for rel, i, txt in lst[:6]:
                    print(f"        {rel}:{i}  {txt}")

    restantes = len(buckets["🟢 TROCAR"])
    print(f"\n{'=' * 76}")
    if restantes:
        print(f"⚠️  {restantes} ocorrências VISÍVEIS ainda não trocadas — resolva estas.")
    else:
        print("✅ Nada visível ao usuário ficou para trás.")
    print("As 🔴 devem permanecer como estão. As 🟡 podem ficar para depois.")


if __name__ == "__main__":
    main()
