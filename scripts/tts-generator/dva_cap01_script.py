"""Roteiro DVA-C02 Capitulo 1 — Fundamentos do dev AWS: SDK, CLI, credenciais e padroes."""

from glossary import SAY, EMPH, BRK, PHON

SDK = PHON("ɛs di keɪ", "SDK")
INSTANCE_PROFILE = PHON("ˈɪnstəns ˈproʊfaɪl", "Instance Profile")
EXECUTION_ROLE = PHON("ˌɛksəˈkjuʃən ɹoʊl", "Execution Role")
TASK_ROLE = PHON("tæsk ɹoʊl", "Task Role")
BACKOFF = PHON("ˈbækɔf", "backoff")
JITTER = PHON("ˈdʒɪtɚ", "jitter")
THROTTLING = PHON("ˈθrɑtlɪŋ", "throttling")
PROFILES = PHON("ˈproʊfaɪlz", "profiles")
PAGINATORS = PHON("ˈpædʒɪneɪtɚz", "paginators")
DRY_RUN = PHON("draɪ rʌn", "dry run")
FAN_OUT = PHON("fæn aʊt", "fan-out")
COREOGRAFIA = "coreografia"
IDEMPOTENCIA = "idempotência"

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Bem-vindo à trilha {SAY('DVA')} dash C zero dois, o exame de "
            f"Desenvolvedor da {SAY('AWS')}. Capítulo um: fundamentos — como o "
            f"seu código fala com a {SAY('AWS')}, e o vocabulário de arquitetura "
            f"que a prova pressupõe."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Cadeia de credenciais ----
    {
        "voice": "antonio",
        "text": (
            f"A cadeia de credenciais — a ordem em que o {SDK} e a {SAY('CLI')} "
            f"procuram credenciais. Primeiro, parâmetros explícitos no código — "
            f"e hardcoded é SEMPRE a alternativa errada. Depois, variáveis de "
            f"ambiente. Depois, os arquivos de perfil, com suporte a múltiplos "
            f"{PROFILES}. Depois, credenciais de container — a {TASK_ROLE} do "
            f"{SAY('ECS')}. E por último, o {INSTANCE_PROFILE} via "
            f"{SAY('IMDS')} no {SAY('EC2')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A armadilha clássica: 'aplicação em {SAY('EC2')} "
            f"precisa acessar o {SAY('S3')} — qual a forma MAIS segura?' A "
            f"resposta é sempre a role: {INSTANCE_PROFILE} no {SAY('EC2')}, "
            f"{EXECUTION_ROLE} na Lambda, {TASK_ROLE} no {SAY('ECS')}. "
            f"Credenciais temporárias, rotação automática, nada armazenado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Retries e backoff ----
    {
        "voice": "francisca",
        "text": (
            f"Retries e {THROTTLING}. Toda {SAY('API')} da {SAY('AWS')} pode "
            f"responder quatro dois nove — {THROTTLING}. O {SDK} já faz retry "
            f"automático com exponential {BACKOFF}: espera um, dois, quatro, "
            f"oito segundos. O refinamento cobrado é o {JITTER}: aleatoriedade "
            f"nas esperas para milhares de clientes não tentarem juntos. E as "
            f"regras: erro cinco X X, retry cabe; erro quatro zero zero de "
            f"validação, retry NÃO adianta — corrija a requisição. E se o retry "
            f"pode duplicar o efeito, torne a operação idempotente."
        ),
    },
    {"voice": "francisca", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Três miudezas que rendem questões: o {SDK} precisa de Região "
            f"definida — 'endpoint não encontrado' costuma ser Região errada; "
            f"listagens são paginadas — use os {PAGINATORS} do {SDK}; e para "
            f"testar permissão sem executar, a {SAY('CLI')} tem o {DRY_RUN}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Padroes de arquitetura ----
    {
        "voice": "antonio",
        "text": (
            f"Agora o vocabulário de arquitetura da Task um ponto um. "
            f"Event-driven: componentes reagem a eventos em vez de se chamarem "
            f"diretamente — a resposta padrão para 'reduzir acoplamento'. "
            f"Microsserviços versus monolito: deploys independentes e escala por "
            f"parte contra aplicação única. {COREOGRAFIA} versus orquestração: "
            f"na {COREOGRAFIA}, cada serviço reage a eventos sem coordenador — "
            f"EventBridge; na orquestração, um coordenador central dirige o "
            f"fluxo — Step Functions. 'Fluxo complexo com estado e tratamento "
            f"de erro central' pede orquestração."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Acoplamento forte versus fraco: chamada síncrona "
            f"direta propaga falha; fila ou evento no meio isola — {SAY('SQS')} "
            f"é o desacoplador clássico. Síncrono versus assíncrono: síncrono "
            f"espera a resposta; assíncrono aceita com duzentos e dois e "
            f"processa depois — o padrão para trabalho demorado. "
            f"{IDEMPOTENCIA}: processar a mesma requisição duas vezes produz o "
            f"mesmo resultado — obrigatório onde há retry, implementado com "
            f"chave de idempotência e condition expression. E {FAN_OUT}: um "
            f"evento para N consumidores — {SAY('SNS')} para múltiplas filas "
            f"{SAY('SQS')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o princípio geral: a prova favorece componentes "
            f"STATELESS — estado fora, em {SAY('DynamoDB')}, ElastiCache ou "
            f"{SAY('S3')} — porque escalam horizontalmente sem sessão presa."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: aplicação em {SAY('EC2')} precisa acessar o "
            f"{SAY('DynamoDB')} — forma mais segura de credenciais?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('IAM')} role anexada à instância — {INSTANCE_PROFILE}. "
            f"Credenciais temporárias via {SAY('IMDS')}, rotação automática."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: sua aplicação recebe {THROTTLING} exception em picos. O "
            f"que implementar no cliente?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Exponential {BACKOFF} com {JITTER} — o {SDK} da {SAY('AWS')} já "
            f"faz por padrão; não desative."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: um fluxo de pedido com seis etapas, decisões e retry "
            f"central — {COREOGRAFIA} ou orquestração?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Orquestração — Step Functions como coordenador central, com "
            f"estado e tratamento de erro declarativo."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo um. No próximo, o coração do exame: "
            f"{SAY('AWS')} Lambda a fundo. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
