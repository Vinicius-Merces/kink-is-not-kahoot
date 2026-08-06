"""Roteiro DVA-C02 Capitulo 8 — Amazon Cognito."""

from glossary import SAY, EMPH, BRK, PHON

USER_POOL = PHON("ˈjuzɚ pul", "User Pool")
IDENTITY_POOL = PHON("aɪˈdɛntɪti pul", "Identity Pool")
JWT = PHON("dʒeɪ dabliu ti", "JWT")
ID_TOKEN = PHON("aɪ di ˈtoʊkən", "ID token")
ACCESS_TOKEN = PHON("ˈæksɛs ˈtoʊkən", "Access token")
REFRESH_TOKEN = PHON("rɪˈfrɛʃ ˈtoʊkən", "Refresh token")
HOSTED_UI = PHON("ˈhoʊstɪd ju aɪ", "Hosted UI")
GUEST = PHON("ɡɛst", "guest")
SAML = PHON("ˈsæməl", "SAML")
OIDC = PHON("oʊ aɪ di si", "OIDC")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo oito: Amazon Cognito. UMA distinção decide quase todas "
            f"as questões: {USER_POOL} responde 'quem é você'; {IDENTITY_POOL} "
            f"responde 'quais credenciais {SAY('AWS')} você recebe'."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- User Pool ----
    {
        "voice": "antonio",
        "text": (
            f"O {USER_POOL} é AUTENTICAÇÃO: cadastro, login, {SAY('MFA')}, "
            f"{HOSTED_UI}, federação com redes sociais, {SAML} e {OIDC}, e "
            f"triggers Lambda para customizar o fluxo. Ele entrega TRÊS tokens "
            f"{JWT}: o {ID_TOKEN}, com os claims de identidade — e-mail, nome; "
            f"o {ACCESS_TOKEN}, que autoriza chamadas com escopos; e o "
            f"{REFRESH_TOKEN}, que renova os outros dois sem novo login. "
            f"Gatilho: 'login de usuários' ou 'validar {JWT} no {SAY('API')} "
            f"Gateway'."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Identity Pool ----
    {
        "voice": "francisca",
        "text": (
            f"O {IDENTITY_POOL} é AUTORIZAÇÃO para serviços {SAY('AWS')}: "
            f"troca um token de identidade — do {USER_POOL} ou de um provedor "
            f"externo — por CREDENCIAIS {SAY('AWS')} temporárias via "
            f"{SAY('STS')}, mapeadas a uma role do {SAY('IAM')}. E suporta "
            f"identidades NÃO autenticadas — o modo {GUEST} — para dar acesso "
            f"limitado a visitantes. Gatilho: 'o app acessa {SAY('S3')} ou "
            f"{SAY('DynamoDB')} DIRETAMENTE'."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O combo completo: o app faz login no {USER_POOL} e "
            f"recebe o {JWT}; troca o {JWT} no {IDENTITY_POOL}; recebe "
            f"credenciais temporárias; e acessa o {SAY('S3')} direto com a "
            f"role de usuário autenticado. Mas atenção: se a pergunta é SÓ "
            f"proteger uma {SAY('API')}, o {USER_POOL} authorizer no "
            f"{SAY('API')} Gateway basta — o {IDENTITY_POOL} entra quando o "
            f"CLIENTE chama serviços {SAY('AWS')} diretamente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: app mobile precisa que usuários logados enviem "
            f"fotos direto para o {SAY('S3')}. Qual arquitetura?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{USER_POOL} para autenticar, mais {IDENTITY_POOL} para trocar o "
            f"{JWT} por credenciais temporárias com role de escrita no prefixo "
            f"do usuário."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: qual token carrega os claims de identidade — e-mail, "
            f"nome?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O {ID_TOKEN}. O {ACCESS_TOKEN} autoriza chamadas, e o "
            f"{REFRESH_TOKEN} renova os dois sem novo login."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: visitantes não logados precisam de leitura limitada a "
            f"um recurso {SAY('AWS')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{IDENTITY_POOL} com identidades não autenticadas — modo {GUEST} "
            f"— mapeadas a uma role restrita de leitura."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo oito. No próximo, o domínio três começa: "
            f"containers e {SAY('ECR')} para desenvolvedores. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
