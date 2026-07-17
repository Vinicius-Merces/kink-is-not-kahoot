#!/usr/bin/env python3
"""Regera as playlists do music-player.js A PARTIR DOS ARQUIVOS EM DISCO.

POR QUE ISSO EXISTE
-------------------
Os nomes dos MP3 novos vieram com maiuscula inconsistente:

    CloudPath Jam.mp3        <- P maiusculo
    Cloudpath Me Chama.mp3   <- p minusculo

O SquareCloud roda LINUX, onde nome de arquivo diferencia maiuscula de
minuscula. Se o codigo apontar para "CloudPath Me Chama.mp3" e o arquivo em
disco for "Cloudpath Me Chama.mp3", a musica toca no seu Windows e da 404 em
producao. E o tipo de bug que so aparece depois do deploy.

A solucao e nao digitar nome de arquivo nenhum: este script LE a pasta e usa
exatamente o nome que esta la.

USO
    python3 scripts/rebuild_playlist.py --dry-run   # mostra o que geraria
    python3 scripts/rebuild_playlist.py             # reescreve o music-player.js
    python3 scripts/rebuild_playlist.py --normalize # renomeia os arquivos para
                                                    # padronizar "CloudPath" antes

TITULOS
    Por padrao o titulo vem do nome do arquivo (sem o prefixo "CloudPath - ").
    Para dar um titulo bonito a uma faixa, edite TITULOS abaixo.
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PASTAS = {
    "menuPlaylist": ("assets/music/Index", "menu"),
    # TEMPORARIO: as instrumentais do KINK foram excluidas na virada e ainda
    # nao ha faixas CloudPath em assets/music/instrumental. Ate la, a playlist
    # de jogo usa as mesmas faixas novas. Quando gravar instrumentais, volte
    # esta linha para "assets/music/instrumental" e rode o script de novo.
    "gamePlaylist": ("assets/music/Index", "game"),
}

# Titulo customizado por nome de arquivo (sem extensao). Opcional.
TITULOS = {
    # "CloudPath Jam": "Cloud Jam",
}

# Emoji da capa, ciclico (so estetica)
CAPAS = ["🎵", "⚡", "☁️", "🎹", "🎯", "⚛️", "🌩️", "🎸"]

DRY = "--dry-run" in sys.argv
NORMALIZE = "--normalize" in sys.argv


def normalizar_nomes(pasta_abs):
    """Padroniza 'Cloudpath'/'CLOUDPATH' -> 'CloudPath' nos nomes dos arquivos."""
    mudou = 0
    for nome in sorted(os.listdir(pasta_abs)):
        if not nome.lower().endswith(".mp3"):
            continue
        novo = re.sub(r"cloudpath", "CloudPath", nome, flags=re.I)
        if novo != nome:
            print(f"    {nome}  ->  {novo}")
            if not DRY:
                os.rename(os.path.join(pasta_abs, nome), os.path.join(pasta_abs, novo))
            mudou += 1
    return mudou


def titulo_de(nome_arquivo):
    base = os.path.splitext(nome_arquivo)[0]
    if base in TITULOS:
        return TITULOS[base]
    # remove prefixos tipo "CloudPath - " ou "CloudPath "
    t = re.sub(r"^CloudPath\s*[-–]?\s*", "", base, flags=re.I).strip()
    return t or base


def listar(pasta_rel):
    abs_ = os.path.join(ROOT, pasta_rel)
    if not os.path.isdir(abs_):
        print(f"  ⚠ pasta não encontrada: {pasta_rel}")
        return []
    faixas = [f for f in sorted(os.listdir(abs_)) if f.lower().endswith(".mp3")]
    # Ignora as musicas antigas do KINK (serao excluidas na virada)
    return [f for f in faixas if "kink" not in f.lower()]


def bloco_js(nome_array, pasta_rel, prefixo):
    arquivos = listar(pasta_rel)
    if not arquivos:
        return None, 0

    linhas = []
    for i, arq in enumerate(arquivos, 1):
        # O caminho usa o nome EXATO do disco (nada digitado a mao).
        url = f"/{pasta_rel}/{arq}"
        linhas.append(
            f"            {{ id: '{prefixo}{i}', title: '{titulo_de(arq)}', "
            f"artist: 'CloudPath Original', url: '{url}', "
            f"cover: '{CAPAS[(i - 1) % len(CAPAS)]}', duration: '0:00' }}"
        )
    corpo = ",\n".join(linhas)
    return f"        const {nome_array} = [\n{corpo}\n        ];", len(arquivos)


def main():
    if NORMALIZE:
        print("Normalizando nomes de arquivo (CloudPath com P maiúsculo):")
        total = 0
        for pasta_rel, _ in PASTAS.values():
            abs_ = os.path.join(ROOT, pasta_rel)
            if os.path.isdir(abs_):
                total += normalizar_nomes(abs_)
        print(f"  {total} arquivos renomeados\n" if total else "  nada a renomear\n")

    path = os.path.join(ROOT, "js/music-player.js")
    src = open(path, encoding="utf-8").read()
    novo = src

    for nome_array, (pasta_rel, prefixo) in PASTAS.items():
        bloco, n = bloco_js(nome_array, pasta_rel, prefixo)
        if not bloco:
            continue
        padrao = re.compile(
            r"        const " + nome_array + r" = \[.*?\n        \];", re.S
        )
        if not padrao.search(novo):
            print(f"  ⚠ não achei o array {nome_array} no music-player.js")
            continue
        novo = padrao.sub(lambda _: bloco, novo, count=1)
        print(f"  {nome_array}: {n} faixas de {pasta_rel}/")
        for linha in bloco.split("\n")[1:-1]:
            m = re.search(r"title: '([^']+)'.*url: '([^']+)'", linha)
            if m:
                print(f"      {m.group(1):<22} {m.group(2)}")

    if novo == src:
        print("\nNada mudou.")
        return

    if DRY:
        print("\n[DRY-RUN] music-player.js NÃO foi alterado. Rode sem --dry-run para aplicar.")
    else:
        open(path, "w", encoding="utf-8").write(novo)
        print("\n✅ music-player.js atualizado com os nomes reais dos arquivos.")
        print("   Confira as durações ('0:00') — o player as ignora, é só rótulo.")


if __name__ == "__main__":
    main()
