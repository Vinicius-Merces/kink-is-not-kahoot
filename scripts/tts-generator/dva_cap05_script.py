"""Roteiro DVA-C02 Capitulo 5 — S3 para desenvolvedores."""

from glossary import SAY, EMPH, BRK, PHON

PRESIGNED = PHON("priˈsaɪnd ju ɑr ɛl", "presigned URL")
MULTIPART = PHON("ˈmʌltipɑrt ˈʌploʊd", "multipart upload")
TRANSFER_ACCELERATION = PHON("ˈtrænsfɚ ækˌsɛləˈreɪʃən", "Transfer Acceleration")
BUCKET_KEYS = PHON("ˈbʌkət kiz", "S3 Bucket Keys")
CORS = PHON("kɔrz", "CORS")
SSE_S3 = PHON("ɛs ɛs i ɛs tri", "SSE-S3")
SSE_KMS = PHON("ɛs ɛs i keɪ ɛm ɛs", "SSE-KMS")
SSE_C = PHON("ɛs ɛs i si", "SSE-C")
CLIENT_SIDE = PHON("ˈklaɪənt saɪd", "client-side")
EVENT_NOTIFICATIONS = PHON("ɪˈvɛnt ˌnoʊtɪfɪˈkeɪʃənz", "Event Notifications")
STRONGLY = PHON("ˈstrɔŋli kənˈsɪstənt", "fortemente consistente")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo cinco: {SAY('S3')} para desenvolvedores — upload direto "
            f"do cliente, as quatro siglas de criptografia e a armadilha do "
            f"{SSE_KMS} em escala."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Upload/download ----
    {
        "voice": "antonio",
        "text": (
            f"Upload e download do jeito certo. Usuário sobe ou baixa DIRETO "
            f"sem passar pelo backend: {PRESIGNED} — temporária, assinada com "
            f"as credenciais de quem gerou, herda as permissões dessa "
            f"identidade e expira. Arquivos grandes: {MULTIPART} — recomendado "
            f"acima de cem megabytes, OBRIGATÓRIO acima de cinco gigabytes; "
            f"partes em paralelo e retomável — e limpe uploads incompletos com "
            f"lifecycle rule. Clientes distantes: {TRANSFER_ACCELERATION}, "
            f"subindo pela edge location. E para reagir a novos objetos: "
            f"{EVENT_NOTIFICATIONS} para Lambda, {SAY('SQS')}, {SAY('SNS')} ou "
            f"EventBridge."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Criptografia ----
    {
        "voice": "francisca",
        "text": (
            f"As quatro siglas de criptografia. {SSE_S3}: o {SAY('S3')} "
            f"gerencia tudo — 'criptografia sem gerenciar nada', é o padrão "
            f"atual. {SSE_KMS}: chave no {SAY('KMS')} — auditoria de cada uso "
            f"pelo CloudTrail, controle de acesso à chave, rotação. {SSE_C}: "
            f"VOCÊ envia a chave em cada request — compliance com chave fora da "
            f"{SAY('AWS')}. E {CLIENT_SIDE}: cifra ANTES do upload — a "
            f"{SAY('AWS')} nunca vê o dado em claro."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A armadilha do {SSE_KMS} em escala: cada GET e PUT "
            f"chama o {SAY('KMS')} — que tem cota de requisições. Aplicação de "
            f"altíssimo volume tomando throttling do {SAY('KMS')} ao ler do "
            f"{SAY('S3')}? A resposta é {BUCKET_KEYS} — reduz as chamadas ao "
            f"{SAY('KMS')} em até noventa e nove por cento. E erro quatro zero "
            f"três com {SSE_KMS} geralmente é falta de {SAY('KMS')} decrypt na "
            f"ROLE, não no bucket."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- CORS e consistencia ----
    {
        "voice": "antonio",
        "text": (
            f"{CORS} e consistência. Front-end em um domínio consumindo bucket "
            f"em outro dá erro de {CORS} no navegador — configure as regras de "
            f"{CORS} no BUCKET: allowed origins, methods e headers. E "
            f"consistência: o {SAY('S3')} hoje é {STRONGLY} para leitura após "
            f"escrita, incluindo sobrescritas e deleções — questão antiga "
            f"falando em consistência eventual do {SAY('S3')} está "
            f"desatualizada."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: app mobile sobe vídeos de dois gigabytes direto "
            f"ao {SAY('S3')} sem sobrecarregar o backend?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Backend gera a {PRESIGNED} e o app faz {MULTIPART} direto ao "
            f"{SAY('S3')} — o backend nunca toca nos bytes."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: auditores exigem registro de CADA uso da chave que "
            f"criptografa os objetos. Qual modo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SSE_KMS} com customer managed key — cada operação aparece no "
            f"CloudTrail; {SSE_S3} não dá auditoria por chave."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: GETs massivos com {SSE_KMS} falhando com throttling. "
            f"Solução de baixo esforço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"Habilitar {BUCKET_KEYS} no bucket — alivia a cota do {SAY('KMS')} drasticamente.",
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo cinco. No próximo, desacoplamento: "
            f"mensageria, Kinesis e Step Functions. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
