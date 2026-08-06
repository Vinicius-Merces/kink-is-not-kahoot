import os
import requests
from dotenv import load_dotenv

load_dotenv()

KEY = os.environ["AZURE_SPEECH_KEY"]
REGION = os.environ["AZURE_SPEECH_REGION"]

TOKEN_URL = f"https://{REGION}.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
TTS_URL = f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

def get_token():
    resp = requests.post(TOKEN_URL, headers={"Ocp-Apim-Subscription-Key": KEY})
    resp.raise_for_status()
    return resp.text

SSML = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="pt-BR">
  <voice name="pt-BR-FranciscaNeural">
    <mstts:express-as style="cheerful">
      Bem-vindos ao capítulo um da nossa trilha de estudos.
    </mstts:express-as>
    <break time="800ms"/>
    Hoje vamos falar sobre <emphasis level="moderate">gerenciamento de identidade e acesso</emphasis>.
    <break time="500ms"/>
    Esse é um dos pilares mais importantes da prova.
  </voice>
</speak>"""

def synthesize(ssml: str, out_path: str):
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
        "User-Agent": "kink-is-not-kahoot-tts-test",
    }
    resp = requests.post(TTS_URL, headers=headers, data=ssml.encode("utf-8"))
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(resp.content)
    print(f"Salvo: {out_path} ({len(resp.content)} bytes)")

if __name__ == "__main__":
    synthesize(SSML, "azure_test_francisca.mp3")
