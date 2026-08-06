"""Roteiro DVA-C02 Capitulo 3 — Amazon API Gateway."""

from glossary import SAY, EMPH, BRK, PHON

REST_API = PHON("rɛst eɪ pi aɪ", "REST API")
HTTP_API = PHON("eɪtʃ ti ti pi eɪ pi aɪ", "HTTP API")
USAGE_PLANS = PHON("ˈjusɪdʒ plænz", "Usage Plans")
API_KEYS = PHON("eɪ pi aɪ kiz", "API Keys")
LAMBDA_AUTHORIZER = PHON("ˈlæmdə ˈɔθəraɪzɚ", "Lambda Authorizer")
USER_POOL = PHON("ˈjuzɚ pul", "User Pool")
STAGES = PHON("ˈsteɪdʒɪz", "stages")
STAGE_VARIABLES = PHON("steɪdʒ ˈvɛriəbəlz", "stage variables")
CANARY = PHON("kəˈnɛri", "canary release")
CORS = PHON("kɔrz", "CORS")
PREFLIGHT = PHON("ˈpriflaɪt", "preflight")
BAD_GATEWAY = PHON("bæd ˈɡeɪtweɪ", "Bad Gateway")
PROXY = PHON("ˈprɑksi", "proxy")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo três: Amazon {SAY('API')} Gateway. Aqui caem a escolha "
            f"entre {REST_API} e {HTTP_API}, as quatro portas de autorização, "
            f"os códigos de erro — e a armadilha dos vinte e nove segundos."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- REST vs HTTP ----
    {
        "voice": "antonio",
        "text": (
            f"{REST_API} versus {HTTP_API}. A {HTTP_API} é até setenta por "
            f"cento mais barata e mais rápida — {PROXY} simples para Lambda com "
            f"{SAY('JWT')} authorizer nativo e {CORS} fácil. A {REST_API} tem "
            f"os recursos completos: cache, {API_KEYS} com {USAGE_PLANS}, "
            f"request validation, {CANARY} e {SAY('WAF')}. Precisa de cache, "
            f"chave por cliente ou validação? {REST_API}. Só um {PROXY} barato? "
            f"{HTTP_API}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Autorizacao ----
    {
        "voice": "francisca",
        "text": (
            f"As quatro portas de autorização. {SAY('IAM')} com Sig V quatro: "
            f"requisição assinada — chamadores internos com roles. Cognito "
            f"{USER_POOL} Authorizer: valida o {SAY('JWT')} do pool — apps com "
            f"usuários finais. {LAMBDA_AUTHORIZER}: função customizada que "
            f"valida o token e devolve uma policy — auth de terceiros ou "
            f"legado. E {API_KEYS} com {USAGE_PLANS}: identificam o cliente e "
            f"limitam taxa e cota — mas atenção: {API_KEYS} NÃO são "
            f"autenticação de usuários."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Erros ----
    {
        "voice": "antonio",
        "text": (
            f"Os códigos de erro de cabeça. Quatro dois nove: {SAY('throttling')} "
            f"— limite de taxa ou cota excedidos. Cinco zero dois, {BAD_GATEWAY}: "
            f"resposta MALFORMADA da integração — a Lambda {PROXY} devolveu "
            f"fora do formato status code, headers e body. Cinco zero quatro: "
            f"a integração estourou o timeout do {SAY('API')} Gateway — máximo "
            f"de VINTE E NOVE segundos. E quatro zero três: negado por "
            f"authorizer, resource policy, {SAY('WAF')} ou {API_KEYS} inválida."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A armadilha dos vinte e nove segundos: a Lambda aguenta "
            f"quinze minutos, mas atrás do {SAY('API')} Gateway a resposta "
            f"precisa voltar em vinte e nove segundos. Processo longo via "
            f"{SAY('API')}? Padrão assíncrono: enfileira no {SAY('SQS')} ou "
            f"dispara Step Functions e responde duzentos e dois com um "
            f"{SAY('ID')} para consulta — 'aumentar o timeout da {SAY('API')}' "
            f"NÃO existe."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Stages, canary, cache, CORS ----
    {
        "voice": "francisca",
        "text": (
            f"{STAGES} e amigos. Deploys vão para {STAGES} — dev, prod — com "
            f"{STAGE_VARIABLES} apontando integrações diferentes, como o alias "
            f"da Lambda por ambiente. {CANARY} no stage divide o tráfego entre "
            f"a versão atual e a nova. O cache da {REST_API} é por stage, "
            f"{SAY('TTL')} padrão de trezentos segundos. E o erro de {CORS} no "
            f"navegador — chamada de outro domínio — se resolve habilitando "
            f"{CORS} na {SAY('API')}: resposta ao {PREFLIGHT} com o header "
            f"Access Control Allow Origin."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: a {SAY('API')} retorna cinco zero dois "
            f"intermitente com integração Lambda {PROXY}. Causa provável?"
            f"{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A função devolveu resposta fora do formato exigido — status code, "
            f"headers e body string — ou lançou exceção não tratada."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: processamento de três minutos exposto via {SAY('API')} "
            f"Gateway. Qual o padrão?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Assíncrono: aceita com duzentos e dois, enfileira no {SAY('SQS')} "
            f"ou inicia Step Functions, e o cliente consulta o status depois."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: clientes B2B precisam de limites de requisições e cotas "
            f"mensais individuais?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{API_KEYS} associadas a {USAGE_PLANS} com throttling e quota por "
            f"cliente — na {REST_API}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo três. No próximo, o banco do serverless: "
            f"{SAY('DynamoDB')} para desenvolvedores — com a conta de "
            f"{SAY('RCU')} que VAI cair. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
