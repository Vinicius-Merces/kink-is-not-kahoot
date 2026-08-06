#!/usr/bin/env python3
"""Rebrand definitivo: KINK is not Kahoot -> CloudPath.

O `js/branding.js` troca a marca em RUNTIME (o site *parece* CloudPath no dia
17 mesmo sem deploy). Mas o codigo-fonte continua dizendo KINK -- e isso importa
para: preview de link em WhatsApp/LinkedIn, SEO, e quem navega com JS bloqueado.

Este script faz a troca PERMANENTE no HTML/JSON. Rode uma vez, na virada.

    python3 scripts/rebrand.py --dry-run    # mostra o que mudaria
    python3 scripts/rebrand.py              # aplica

O que NAO e tocado de proposito:
  * variaveis CSS (--kink-teal, --kink-space-md...): ninguem ve, e o churn e
    grande demais para o risco. Renomeie depois, com calma, se quiser.
  * chaves de localStorage (kink_*): renomear apagaria o progresso dos usuarios.
    Quem cuida disso e o migrateStorage() do branding.js (copia, nao move).
"""
import glob
import os
import re
import sys

DRY = "--dry-run" in sys.argv
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Ordem importa: as frases mais longas primeiro.
SUBS = [
    ("KINK is not Kahoot", "CloudPath"),
    ("KINK Player", "CloudPath Player"),
    (">KINK<", ">CloudPath<"),
    ('data-text="KINK"', 'data-text="CloudPath"'),
    ('content="KINK"', 'content="CloudPath"'),
    ("<span>is not Kahoot</span>", "<span>Sua trilha para a nuvem</span>"),
    ("<p>is not Kahoot</p>", "<p>Sua trilha para a nuvem</p>"),
    ('<p class="tagline">is not Kahoot</p>',
     '<p class="tagline">Sua trilha para a nuvem</p>'),
    ("⚠️ KINK is not Kahoot - We do things differently ⚠️",
     "☁️ CloudPath — Sua trilha para a nuvem ☁️"),
    ("Carregando KINK...", "Carregando CloudPath..."),
    ('"short_name": "KINK"', '"short_name": "CloudPath"'),
    ("The rebellious quiz platform", "Trilhas de estudo e simulados AWS"),
    # Frase que se auto-referencia: nao da para substituir a palavra, tem que
    # reescrever ("no estilo do CloudPath" nao faria sentido nenhum).
    ("Apostilas completas, no estilo do KINK, para revisar a teoria",
     "Apostilas completas para revisar a teoria"),
    ("Apostilas completas no estilo do KINK para revisar a teoria",
     "Apostilas completas para revisar a teoria"),
    # Texto visivel que a auditoria pegou (o placeholder e melhor sem marca nenhuma)
    ('placeholder="Código KINK"', 'placeholder="Código da sala"'),
    ("Login no KINK", "Login no CloudPath"),
    ("acessar o KINK", "acessar o CloudPath"),
    # Favicons e icones -> assets novos
    ('href="images/icons/icon-32.png"', 'href="images/branding/cloudpath-icon-32.png"'),
    ('href="images/icons/icon-16.png"', 'href="images/branding/cloudpath-icon-16.png"'),
    ('href="images/icons/icon-180.png"', 'href="images/branding/cloudpath-icon-180.png"'),
]

# Substituicoes em CODIGO. Cuidado: aqui "KINK" as vezes e nome de ARQUIVO.
SUBS_CODIGO = [
    ("Instale o KINK", "Instale o CloudPath"),
    ("🎵 Playlist KINK", "🎵 Playlist CloudPath"),
    ("KINK Music", "CloudPath Music"),
    ("track.artist || 'KINK'", "track.artist || 'CloudPath'"),
    # body::before renderiza esse texto na tela (marca d'agua). "CloudPath" e
    # mais longo que "KINK" -- confira o layout depois de trocar.
    ('content: "KINK";', 'content: "CloudPath";'),
    ("Validador dos bancos de questões do KINK.",
     "Validador dos bancos de questões do CloudPath."),
    # Service worker: trocar o nome do cache INVALIDA o cache antigo de proposito
    # (senao o usuario que volta recebe assets e icones velhos).
    ("'kink-cache-v1'", "'cloudpath-cache-v1'"),
    ("'/images/icons/icon-192.png'", "'/images/branding/cloudpath-icon-192.png'"),
    ("'/images/icons/icon-512.png'", "'/images/branding/cloudpath-icon-512.png'"),
    ("permitir instalar o KINK como app", "permitir instalar o CloudPath como app"),
    ("🔥 KINK is not Kahoot Server 🔥", "☁️  CloudPath Server ☁️"),
    ('"description": "KINK is not Kahoot - Plataforma de quizzes em tempo real"',
     '"description": "CloudPath - Trilhas de estudo e simulados AWS"'),
]

ALVOS = sorted(glob.glob(os.path.join(ROOT, "*.html"))) + [
    os.path.join(ROOT, "manifest.json"),
]

ALVOS_CODIGO = [
    os.path.join(ROOT, p)
    for p in ("js/pwa.js", "js/music-player.js", "server.js", "package.json",
              "css/style.css", "scripts/validate_banks.py", "sw.js")
]


def fixar_musicas(src):
    """No music-player.js, "KINK" aparece em title/artist (TEXTO, trocar) e em
    url (NOME DE ARQUIVO em disco, NAO trocar -- quebraria o player).
    Esta funcao troca so os campos de texto.
    """
    def repl(m):
        return m.group(1) + m.group(2).replace("KINK", "CloudPath") + m.group(3)

    return re.sub(r"((?:title|artist):\s*')([^']*)(')", repl, src)


def main():
    total = 0
    for path in ALVOS:
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        novo = src
        for velho, atual in SUBS:
            novo = novo.replace(velho, atual)

        # Sobrou "KINK" solto? (ignora comentarios HTML, que nao sao visiveis)
        sem_comentarios = re.sub(r"<!--.*?-->", "", novo, flags=re.S)
        restos = len(re.findall(r"KINK|Kahoot", sem_comentarios))

        if novo != src:
            n = sum(src.count(v) for v, _ in SUBS)
            total += n
            nome = os.path.relpath(path, ROOT)
            aviso = f"  ⚠ ainda restam {restos} 'KINK/Kahoot'" if restos else ""
            print(f"  {nome}: {n} substituições{aviso}")
            if not DRY:
                open(path, "w", encoding="utf-8").write(novo)

    # Codigo (js/server/package): substituicoes proprias + regra das musicas
    for path in ALVOS_CODIGO:
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        novo = src
        for velho, atual in SUBS_CODIGO:
            novo = novo.replace(velho, atual)
        if path.endswith("music-player.js"):
            novo = fixar_musicas(novo)
        if novo != src:
            n = sum(1 for a, b in zip(src.split("KINK"), novo.split("KINK")) if a != b)
            nome = os.path.relpath(path, ROOT)
            print(f"  {nome}: atualizado"
                  + (" (URLs dos mp3 preservadas)" if path.endswith("music-player.js") else ""))
            total += 1
            if not DRY:
                open(path, "w", encoding="utf-8").write(novo)

    # manifest: nome do app
    mpath = os.path.join(ROOT, "manifest.json")
    if os.path.exists(mpath) and not DRY:
        import json
        m = json.load(open(mpath, encoding="utf-8"))
        m["name"] = "CloudPath"
        m["short_name"] = "CloudPath"
        m["description"] = "Trilhas de estudo e simulados para certificações AWS"
        m["icons"] = [
            {"src": "images/branding/cloudpath-icon-192.png", "sizes": "192x192",
             "type": "image/png", "purpose": "any"},
            {"src": "images/branding/cloudpath-icon-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "any"},
            {"src": "images/branding/cloudpath-icon-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ]
        json.dump(m, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("  manifest.json: nome e ícones atualizados")

    print(f"\n{'[DRY-RUN] ' if DRY else ''}{total} substituições em {len(ALVOS)} arquivos")
    if DRY:
        print("Rode sem --dry-run para aplicar.")
    else:
        print("\nDepois disso:")
        print("  1. Remova o card de aviso do index.html (#rebrandNotice)")
        print("  2. js/branding.js pode ficar (a migração de localStorage ainda serve)")
        print("  3. Atualize o README")


if __name__ == "__main__":
    main()
