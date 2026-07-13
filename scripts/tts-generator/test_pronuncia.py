#!/usr/bin/env python3
"""Teste de ouvido: gera UM mp3 curto com os termos mais criticos.

Rode isto ANTES de regerar os 20 capitulos. Custa 1-2 chamadas de API e diz
em 40 segundos se a re-grafia esta soando bem.

    python3 test_pronuncia.py              # modo respell (novo)
    python3 test_pronuncia.py --ipa        # modo antigo, para comparar A/B

Saida: teste_pronuncia.mp3  (ou teste_pronuncia_ipa.mp3)

Ouviu algo estranho? Edite o dict RESPELL em glossary.py e rode de novo.
"""
import sys

import glossary
from generate import generate_chapter

USE_IPA = "--ipa" in sys.argv
if USE_IPA:
    glossary.PHONETIC_MODE = "ipa"   # precisa vir antes de montar os termos

from glossary import SAY, BRK, PHON  # noqa: E402

# Termos escolhidos por risco: curtos que o PT leria errado, /h/ ingles,
# th, clusters, e os que voce citou como problematicos.
TERMOS = [
    ("Deny", PHON("dɪˈnaɪ", "Deny")),
    ("Allow", PHON("əˈlaʊ", "Allow")),
    ("gateway", PHON("ˈɡeɪtweɪ", "gateway")),
    ("role", PHON("ɹoʊl", "role")),
    ("bucket", PHON("ˈbʌkɪt", "bucket")),
    ("throughput", PHON("ˈθruːpʊt", "throughput")),
    ("health check", PHON("hɛlθ tʃɛk", "health check")),
    ("GitHub", PHON("ˈɡɪthʌb", "GitHub")),
    ("Auto Scaling", PHON("ˈɔtoʊ ˈskeɪlɪŋ", "Auto Scaling")),
    ("Load Balancer", PHON("loʊd ˈbælənsɚ", "Load Balancer")),
    ("cold start", PHON("koʊld stɑrt", "cold start")),
    ("Bastion Host", PHON("ˈbæstʃən hoʊst", "Bastion Host")),
]

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": f"Teste de pronúncia. {BRK(300)} Vou falar doze termos técnicos.",
    },
    {"voice": "francisca", "text": BRK(600)},
]

for i, (original, falado) in enumerate(TERMOS):
    voice = "antonio" if i % 2 else "francisca"
    BLOCKS.append({
        "voice": voice,
        "text": f"{falado}. {BRK(500)}",
    })

BLOCKS.append({
    "voice": "antonio",
    "text": f"{BRK(600)} Fim do teste. Termos que soarem errados, ajuste no dicionário {SAY('RESPELL')}.",
})


if __name__ == "__main__":
    out = "teste_pronuncia_ipa.mp3" if USE_IPA else "teste_pronuncia.mp3"
    print(f"Modo: {glossary.PHONETIC_MODE}")
    print("Termos que serao falados:")
    for original, falado in TERMOS:
        print(f"   {original:16} -> {falado}")
    print()
    generate_chapter(BLOCKS, out)
