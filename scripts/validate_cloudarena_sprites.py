#!/usr/bin/env python3
"""Valida os spritesheets 4x4 publicados para inimigos do CloudArena."""

from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SHEETS = (
    ROOT / "images/arena/enemies/secure-architectures/sentinela-fortaleza-sheet.png",
    ROOT / "images/arena/enemies/secure-architectures/arquimago-chaves-sheet.png",
)
GRID = 4
MIN_TRANSPARENT_RATIO = 0.10


def validate(path: Path) -> list[str]:
    errors = []
    if not path.exists():
        return [f"arquivo ausente: {path.relative_to(ROOT)}"]

    with Image.open(path) as image:
        if image.format != "PNG" or "transparency" not in image.info and image.mode != "RGBA":
            errors.append(f"{path.name}: esperado PNG com canal alfa, recebido {image.format} {image.mode}")
            return errors
        image = image.convert("RGBA")
        width, height = image.size
        if min(width, height) < 400:
            errors.append(f"{path.name}: dimensões {width}x{height} pequenas para uma grade 4x4")
        alpha = image.getchannel("A")
        transparent = alpha.histogram()[0]
        if transparent / (width * height) < MIN_TRANSPARENT_RATIO:
            errors.append(f"{path.name}: transparência insuficiente; possível fundo incorporado")

        for row in range(GRID):
            for col in range(GRID):
                x0, x1 = round(col * width / GRID), round((col + 1) * width / GRID)
                y0, y1 = round(row * height / GRID), round((row + 1) * height / GRID)
                frame_alpha = alpha.crop((x0, y0, x1, y1))
                if frame_alpha.getbbox() is None:
                    errors.append(f"{path.name}: frame vazio em linha {row + 1}, coluna {col + 1}")
                    continue
                if frame_alpha.histogram()[0] == 0:
                    errors.append(f"{path.name}: frame {row + 1},{col + 1} não possui área transparente")
    return errors


def main() -> int:
    errors = [error for sheet in SHEETS for error in validate(sheet)]
    if errors:
        print("FALHOU: validação dos sprites do CloudArena")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: 2 spritesheets RGBA transparentes e 16 frames válidos por personagem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
