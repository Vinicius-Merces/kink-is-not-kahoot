import os
import subprocess
import sys
import tempfile
import requests
from dotenv import load_dotenv

from ssml_builder import build_ssml

load_dotenv()

KEY = os.environ["AZURE_SPEECH_KEY"]
REGION = os.environ["AZURE_SPEECH_REGION"]

TOKEN_URL = f"https://{REGION}.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
TTS_URL = f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

MAX_SSML_CHARS = 950  # margem abaixo do limite de 1000 da camada F0
MAX_VOICE_TAGS = 40   # margem abaixo do limite de 50 tags <voice>/<audio>


def get_token():
    resp = requests.post(TOKEN_URL, headers={"Ocp-Apim-Subscription-Key": KEY})
    resp.raise_for_status()
    return resp.text


def chunk_blocks(blocks: list[dict]) -> list[list[dict]]:
    """Agrupa blocos respeitando limites de tamanho e numero de tags <voice> da camada F0."""
    chunks: list[list[dict]] = []
    current: list[dict] = []
    for block in blocks:
        trial = current + [block]
        ssml = build_ssml(trial)
        if current and (len(ssml) > MAX_SSML_CHARS or len(trial) > MAX_VOICE_TAGS):
            chunks.append(current)
            current = [block]
        else:
            current = trial
    if current:
        chunks.append(current)
    return chunks


def synthesize_chunk(token: str, ssml: str) -> bytes:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
        "User-Agent": "kink-is-not-kahoot-tts",
    }
    resp = requests.post(TTS_URL, headers=headers, data=ssml.encode("utf-8"))
    if resp.status_code != 200:
        print("ERRO", resp.status_code, resp.text[:500])
        resp.raise_for_status()
    return resp.content


def concat_mp3s(paths: list[str], out_path: str):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as listfile:
        for p in paths:
            listfile.write(f"file '{os.path.abspath(p)}'\n")
        listfile_path = listfile.name

    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", listfile_path, "-c:a", "libmp3lame", "-q:a", "4",
            out_path,
        ],
        check=True,
        capture_output=True,
    )
    os.unlink(listfile_path)


def generate_chapter(blocks: list[dict], out_path: str):
    chunks = chunk_blocks(blocks)
    print(f"{len(blocks)} blocos -> {len(chunks)} chamadas de API")

    token = get_token()
    tmp_dir = tempfile.mkdtemp(prefix="tts_chunks_")
    chunk_paths = []
    for i, chunk in enumerate(chunks):
        ssml = build_ssml(chunk)
        if len(ssml) > MAX_SSML_CHARS:
            print(f"  AVISO chunk {i}: {len(ssml)} chars (acima do limite, pode falhar)")
        try:
            audio = synthesize_chunk(token, ssml)
        except requests.exceptions.HTTPError:
            token = get_token()  # token pode ter expirado (10 min)
            audio = synthesize_chunk(token, ssml)
        chunk_path = os.path.join(tmp_dir, f"chunk_{i:03d}.mp3")
        with open(chunk_path, "wb") as f:
            f.write(audio)
        chunk_paths.append(chunk_path)
        print(f"  chunk {i+1}/{len(chunks)} ok ({len(ssml)} chars, {len(audio)} bytes)")

    concat_mp3s(chunk_paths, out_path)
    print(f"Salvo: {out_path}")


if __name__ == "__main__":
    module_name = sys.argv[1] if len(sys.argv) > 1 else "cap01_script"
    out_name = sys.argv[2] if len(sys.argv) > 2 else "cap01.mp3"

    mod = __import__(module_name)
    generate_chapter(mod.BLOCKS, out_name)
