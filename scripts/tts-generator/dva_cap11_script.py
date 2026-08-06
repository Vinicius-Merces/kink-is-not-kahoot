"""Roteiro DVA-C02 Capitulo 11 — CloudFormation, SAM e AppConfig."""

from glossary import SAY, EMPH, BRK, PHON

CLOUDFORMATION = PHON("klaʊd fɔrˈmeɪʃən", "CloudFormation")
SAM = PHON("sæm", "SAM")
APPCONFIG = PHON("æp kənˈfɪɡ", "AppConfig")
REF = PHON("rɛf", "Ref")
GETATT = PHON("ɡɛt æt", "GetAtt")
SUB = PHON("sʌb", "Sub")
IMPORTVALUE = PHON("ɪmˈpɔrt ˈvælju", "ImportValue")
FINDINMAP = PHON("faɪnd ɪn mæp", "FindInMap")
CHANGE_SETS = PHON("tʃeɪndʒ sɛts", "Change Sets")
DRIFT = PHON("drɪft dɪˈtɛkʃən", "Drift Detection")
STACK_POLICY = PHON("stæk ˈpɑləsi", "Stack Policy")
DELETION_POLICY = PHON("dɪˈliʃən ˈpɑləsi", "DeletionPolicy")
RETAIN = PHON("rɪˈteɪn", "Retain")
SAM_LOCAL = PHON("sæm ˈloʊkəl ɪnˈvoʊk", "sam local invoke")
FEATURE_FLAGS = PHON("ˈfitʃɚ flæɡz", "feature flags")
VALIDATORS = PHON("ˈvælɪdeɪtɚz", "validators")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo onze: {CLOUDFORMATION}, {SAM} e {APPCONFIG} — "
            f"infraestrutura como código e configuração dinâmica."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Template ----
    {
        "voice": "antonio",
        "text": (
            f"A anatomia do template. Parameters: entradas no deploy, para "
            f"reutilizar o template. Mappings: tabelas fixas lidas com "
            f"{FINDINMAP}. Conditions: recursos condicionais — só em prod. "
            f"Resources: a ÚNICA seção obrigatória. E Outputs: valores "
            f"exportáveis — com Export mais {IMPORTVALUE}, compartilham valores "
            f"entre stacks, a cross-stack reference."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} As funções intrínsecas: {REF} devolve o valor do "
            f"parâmetro ou o {SAY('ID')} do recurso; {GETATT} devolve um "
            f"ATRIBUTO do recurso — o {SAY('ARN')}, o endpoint; {SUB} interpola "
            f"strings. 'Preciso do {SAY('ARN')} de um recurso do mesmo "
            f"template' = {GETATT}; 'usar o valor de um parâmetro' = {REF}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Operacoes ----
    {
        "voice": "francisca",
        "text": (
            f"As operações que salvam produção. {CHANGE_SETS}: ver o que vai "
            f"mudar ANTES de aplicar. {DRIFT}: detectar alteração manual fora "
            f"do template. {STACK_POLICY}: proteger recursos críticos de "
            f"updates acidentais. Rollback automático quando o deploy falha no "
            f"meio — é o padrão. E {DELETION_POLICY} {RETAIN} ou Snapshot: "
            f"preservar o recurso quando a stack for deletada — o bucket de "
            f"dados sobrevive."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- SAM ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAM} é uma TRANSFORMAÇÃO do {CLOUDFORMATION} com recursos "
            f"abreviados: Serverless Function, Serverless {SAY('API')}, Simple "
            f"Table. A {SAY('CLI')}: sam build, sam package e sam deploy. E o "
            f"trunfo de prova: {SAM_LOCAL} e sam local start api TESTAM a "
            f"Lambda localmente em Docker — 'testar a função sem fazer "
            f"deploy'. O mesmo template com parâmetros diferentes cria os "
            f"ambientes de staging e produção."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- AppConfig ----
    {
        "voice": "francisca",
        "text": (
            f"E o {APPCONFIG} — configuração dinâmica SEM redeploy: "
            f"{FEATURE_FLAGS}, tuning operacional, allowlists. Os diferenciais "
            f"que a prova cobra: {VALIDATORS} — {SAY('JSON')} Schema ou Lambda "
            f"validam a config ANTES de publicar; deployment strategies — "
            f"rollout gradual da config; e rollback automático por alarme. "
            f"Gatilho: 'ativar uma feature gradualmente sem novo deploy' ou "
            f"'config inválida derrubou a aplicação'."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: a stack de rede exporta o {SAY('ID')} da "
            f"{SAY('VPC')}. Como a stack da aplicação consome?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Output com Export na stack de rede, e {IMPORTVALUE} na stack da "
            f"aplicação — cross-stack reference."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: ver exatamente o que muda antes de atualizar a stack de "
            f"produção?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{CHANGE_SETS} — pré-visualização de criações, modificações e substituições.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: testar uma Lambda localmente com um evento simulado "
            f"antes do deploy?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAM} {SAY('CLI')}: {SAM_LOCAL} com um arquivo de evento — roda "
            f"a função em container Docker local."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo onze. No próximo, o domínio quatro: "
            f"observabilidade com CloudWatch, X-Ray e CloudTrail. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
