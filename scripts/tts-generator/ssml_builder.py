"""Monta SSML multi-voz para a Azure Speech API a partir de uma lista de blocos."""

VOICE_MAP = {
    "antonio": "pt-BR-AntonioNeural",
    "francisca": "pt-BR-FranciscaNeural",
}


def build_ssml(blocks: list[dict]) -> str:
    """
    blocks: lista de dicts com:
      - voice: "antonio" | "francisca"
      - style: "cheerful" | None
      - text: string já com tags inline (<break/>, <emphasis>, <say-as>)
    """
    parts = [
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="pt-BR">'
    ]
    for block in blocks:
        voice_name = VOICE_MAP[block["voice"]]
        text = block["text"]
        if block.get("style"):
            text = f'<mstts:express-as style="{block["style"]}">{text}</mstts:express-as>'
        parts.append(f'<voice name="{voice_name}">{text}</voice>')
    parts.append("</speak>")
    return "\n".join(parts)
