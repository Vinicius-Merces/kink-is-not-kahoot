#!/usr/bin/env python3
"""Instala PNGs aprovados no CloudArena a partir do ZIP de teste.

Uso:
  python scripts/install_cloudarena_art.py cloudarena_teste_corrigido_v2.zip

Execute na raiz do clone do repositório. O instalador não faz commit/deploy.
"""
import argparse
from pathlib import Path
from struct import unpack
from zipfile import ZipFile

ASSETS = {
    "assets/hero_sheet.png": Path("images/arena/hero/masculino/cloudarena-sheet.png"),
    "assets/enemy_sheet.png": Path("images/arena/enemies/secure-architectures/sentinela-fortaleza-sheet.png"),
}

def dimensions(blob):
    if blob[:8] != b"\x89PNG\r\n\x1a\n" or blob[12:16] != b"IHDR":
        raise ValueError("Não é um PNG válido.")
    return unpack(">II", blob[16:24])

def validate(blob, name):
    width, height = dimensions(blob)
    if min(width, height) < 100:
        raise ValueError(f"{name}: imagem pequena demais.")
    # O mestre tem 4x4 células, mas largura/altura NÃO precisam ser divisíveis por 4.
    if max(width, height) > 8192:
        raise ValueError(f"{name}: dimensões excessivas {width}x{height}.")
    return width, height

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    with ZipFile(args.zip_path) as archive:
        for src, rel_path in ASSETS.items():
            payload = archive.read(src)
            w, h = validate(payload, src)
            target = repo_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            print(f"OK: {target.relative_to(repo_root)} ({w}x{h})")
    print("Assets instalados. Revise visualmente antes de criar commit.")

if __name__ == "__main__":
    main()
