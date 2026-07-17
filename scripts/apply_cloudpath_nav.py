#!/usr/bin/env python3
"""Aplica a navbar CloudPath (grupos + dropdowns) e o tema novo em todas as
paginas. Idempotente: rodar duas vezes nao duplica nada.

O que faz por pagina:
  1. Substitui o bloco <nav class="navbar">...</nav> pelo template novo
     (paginas internas). A pagina atual e marcada em runtime pelo nav-menu.js.
  2. Injeta as fontes (Space Grotesk + JetBrains Mono) e css/cloudpath.css
     antes do </head>.
"""
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

NAV_TEMPLATE = '''<nav class="navbar" aria-label="Navega\u00e7\u00e3o principal">
        <div class="nav-container">
            <a href="index.html" class="nav-logo" aria-label="CloudPath \u2014 p\u00e1gina inicial">
                <img class="brand-logo-img" src="images/branding/cloudpath-logo-sm.png" alt="CloudPath" width="160" height="37" decoding="async">
            </a>
            <button class="nav-toggle" id="navToggle" type="button" aria-expanded="false" aria-controls="navMenu" aria-label="Abrir menu">
                <span class="nav-toggle-bar"></span>
                <span class="nav-toggle-bar"></span>
                <span class="nav-toggle-bar"></span>
            </button>
            <div class="nav-menu" id="navMenu">
                <div class="nav-group">
                    <button type="button" class="nav-group-btn" aria-expanded="false" aria-controls="navGroupEstudar">Estudar <span class="chev" aria-hidden="true"></span></button>
                    <div class="nav-dropdown" id="navGroupEstudar">
                        <a href="simulados.html" class="nav-item"><span class="nav-item-label">Simulados AWS</span><span class="nav-item-hint">CLF \u00b7 SAA \u00b7 DVA \u00b7 DEA</span></a>
                        <a href="trilha.html" class="nav-item"><span class="nav-item-label">Trilha de Estudos</span><span class="nav-item-hint">apostilas SAA-C03 e DEA-C01</span></a>
                        <a href="cloudarena.html" class="nav-item"><span class="nav-item-label">CloudArena</span><span class="nav-item-hint">desafio de servi\u00e7os AWS</span></a>
                    </div>
                </div>
                <div class="nav-group">
                    <button type="button" class="nav-group-btn" aria-expanded="false" aria-controls="navGroupQuizzes">Quizzes <span class="chev" aria-hidden="true"></span></button>
                    <div class="nav-dropdown" id="navGroupQuizzes">
                        <a href="my-quizzes.html" class="nav-item"><span class="nav-item-label">Meus Quizzes</span><span class="nav-item-hint">suas salas e jogos ao vivo</span></a>
                        <a href="create-quiz.html" class="nav-item"><span class="nav-item-label">Criar Quiz</span><span class="nav-item-hint">perguntas sem limite</span></a>
                    </div>
                </div>
                <div class="nav-group">
                    <button type="button" class="nav-group-btn" aria-expanded="false" aria-controls="navGroupDesempenho">Desempenho <span class="chev" aria-hidden="true"></span></button>
                    <div class="nav-dropdown" id="navGroupDesempenho">
                        <a href="progresso.html" class="nav-item"><span class="nav-item-label">Meu Progresso</span><span class="nav-item-hint">dom\u00ednio por t\u00f3pico</span></a>
                        <a href="historico.html" class="nav-item"><span class="nav-item-label">Hist\u00f3rico</span><span class="nav-item-hint">simulados anteriores</span></a>
                    </div>
                </div>
                <button id="logoutBtn" class="btn-logout">Sair</button>
            </div>
            <div class="user-info">
                <span id="userName" style="display: none;"></span>
                <div class="user-avatar" style="display: none;"></div>
            </div>
        </div>
    </nav>'''

HEAD_INJECT = ('    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700'
               '&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">\n'
               '    <link rel="stylesheet" href="css/cloudpath.css">\n')

# Paginas internas que recebem a nav completa
NAV_PAGES = [
    "admin.html", "cloudarena.html", "create-quiz.html", "historico.html",
    "host.html", "my-quizzes.html", "progresso.html", "simulados.html",
    "trilha.html", "trilha-saa.html", "trilha-dea.html", "trilha-dva.html",
]

# Todas as paginas recebem fontes + tema
ALL_PAGES = NAV_PAGES + ["index.html", "player.html"]

nav_re = re.compile(r'<nav class="navbar">.*?</nav>', re.S)

for page in ALL_PAGES:
    path = os.path.join(ROOT, page)
    src = open(path, encoding="utf-8").read()
    changed = []

    if page in NAV_PAGES:
        if 'nav-group-btn' not in src and nav_re.search(src):
            src = nav_re.sub(lambda _: NAV_TEMPLATE, src, count=1)
            changed.append("nav")

    if 'css/cloudpath.css' not in src:
        src = src.replace('</head>', HEAD_INJECT + '</head>', 1)
        changed.append("tema")

    open(path, "w", encoding="utf-8").write(src)
    print(f"  {page}: {', '.join(changed) if changed else 'ja aplicado'}")

print("\nFeito.")
