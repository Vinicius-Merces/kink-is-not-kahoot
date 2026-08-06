"""Roteiro DVA-C02 Capitulo 6 — Mensageria, Kinesis e Step Functions."""

from glossary import SAY, EMPH, BRK, PHON

VISIBILITY = PHON("ˌvɪzəˈbɪləti ˈtaɪmaʊt", "visibility timeout")
LONG_POLLING = PHON("lɔŋ ˈpoʊlɪŋ", "long polling")
DLQ = PHON("di ɛl kju", "DLQ")
FIFO = PHON("ˈfaɪfoʊ", "FIFO")
FAN_OUT = PHON("fæn aʊt", "fan-out")
FILTER_POLICIES = PHON("ˈfɪltɚ ˈpɑləsiz", "filter policies")
STEP_FUNCTIONS = PHON("stɛp ˈfʌŋkʃənz", "Step Functions")
RETRY = PHON("riˈtraɪ", "Retry")
CATCH = PHON("kætʃ", "Catch")
TASK_TOKEN = PHON("tæsk ˈtoʊkən", "task token")
STANDARD = PHON("ˈstændɚd", "Standard")
EXPRESS = PHON("ɪkˈsprɛs", "Express")
KINESIS = PHON("kɪˈnisɪs", "Kinesis")
SHARD = PHON("ʃɑrd", "shard")
APPSYNC = PHON("ˈæpsɪŋk", "AppSync")
GRAPHQL = PHON("ˈɡræf kju ɛl", "GraphQL")
EXTENDED_CLIENT = PHON("ɪkˈstɛndɪd ˈklaɪənt", "Extended Client Library")
POISON = PHON("ˈpɔɪzən pɪl", "poison pill")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo seis: mensageria, {KINESIS} e {STEP_FUNCTIONS} — o kit "
            f"de desacoplamento e orquestração do desenvolvedor."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- SQS ----
    {
        "voice": "antonio",
        "text": (
            f"{SAY('SQS')} — os parâmetros que caem. {VISIBILITY}: padrão de "
            f"trinta segundos — 'mensagens processadas em duplicidade' é "
            f"timeout MENOR que o tempo de processamento; aumente. "
            f"{LONG_POLLING}: wait time até vinte segundos — 'reduzir custo e "
            f"chamadas vazias'. {DLQ} com max receive count: isola a mensagem "
            f"venenosa, a {POISON}. Tamanho máximo: duzentos e cinquenta e seis "
            f"kilobytes — maior que isso, {EXTENDED_CLIENT} com o payload no "
            f"{SAY('S3')}. E filas {FIFO}: ordem e exactly-once por message "
            f"group, com deduplicação — em troca de menos throughput."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- SNS / EventBridge ----
    {
        "voice": "francisca",
        "text": (
            f"{SAY('SNS')} e EventBridge. O {SAY('SNS')} é pub sub push com o "
            f"{FAN_OUT} clássico — publica uma vez, múltiplas filas {SAY('SQS')} "
            f"assinam — e {FILTER_POLICIES} por atributo: filtrar NO {SAY('SNS')} "
            f"evita entregar o que o consumidor descartaria; o guide cita isso "
            f"como otimização. O EventBridge filtra pelo CONTEÚDO do evento com "
            f"regras, integra SaaS, agenda e tem archive com replay — 'rotear "
            f"eventos por conteúdo' ou 'eventos de terceiros' é EventBridge."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Kinesis ----
    {
        "voice": "antonio",
        "text": (
            f"{KINESIS} para o desenvolvedor. Data Streams com {SHARD}s: um "
            f"megabyte por segundo de entrada e dois de saída por {SHARD}; a "
            f"partition key decide o {SHARD} — chave quente dá throughput "
            f"exceeded, melhore a distribuição. Ordem garantida POR {SHARD}. "
            f"Consumo via Lambda event source mapping. E a diferença-chave "
            f"para o {SAY('SQS')}: {KINESIS} RETÉM e permite reler — replay e "
            f"múltiplos consumidores; o {SAY('SQS')} deleta ao consumir. "
            f"'Vários consumidores no mesmo fluxo em tempo real' é {KINESIS}; "
            f"'distribuir trabalho para workers' é {SAY('SQS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o {APPSYNC} em uma dose: {GRAPHQL} gerenciado — o "
            f"cliente pede exatamente os campos de que precisa, com "
            f"subscriptions para tempo real via WebSocket. 'App mobile com "
            f"chat ou colaboração em tempo real' ou 'reduzir over-fetching' é "
            f"{APPSYNC}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Step Functions ----
    {
        "voice": "francisca",
        "text": (
            f"{STEP_FUNCTIONS} — orquestração com estado. {STANDARD}: até um "
            f"ano, exactly-once, auditável — fluxos longos. {EXPRESS}: até "
            f"cinco minutos, altíssimo volume, mais barato. Os states: Task, "
            f"Choice, Wait, Parallel, e Map para iterar sobre listas. O "
            f"tratamento de erro é DECLARATIVO: {RETRY} com backoff rate e max "
            f"attempts, e {CATCH} desviando para o estado de tratamento — a "
            f"resposta para 'retry com backoff SEM escrever código'. E o "
            f"{TASK_TOKEN}: pausa o fluxo até um send task success — aprovação "
            f"humana."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A regra de eliminação: Lambda chamando Lambda "
            f"diretamente é acoplamento sem retry gerenciado — a alternativa "
            f"com {STEP_FUNCTIONS} vence para workflows de múltiplas etapas. "
            f"Desacoplamento simples produtor-consumidor: {SAY('SQS')}. Um "
            f"evento para N interessados: {SAY('SNS')} ou EventBridge."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: consumidores levam dois minutos por mensagem e "
            f"mensagens são processadas duas vezes. Causa e correção?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{VISIBILITY} de trinta segundos menor que o processamento — a "
            f"mensagem reaparece antes do delete. Aumente o timeout."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: pedido criado precisa acionar estoque, faturamento e "
            f"e-mail de forma independente e durável?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{FAN_OUT}: {SAY('SNS')} publica e três filas {SAY('SQS')} "
            f"assinam — durabilidade e retry por consumidor."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: workflow de seis etapas com aprovação humana no meio e "
            f"retries automáticos?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{STEP_FUNCTIONS} {STANDARD} — {RETRY} e {CATCH} declarativos, e "
            f"callback com {TASK_TOKEN} para a aprovação."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo seis. No próximo, o domínio dois começa: "
            f"segurança para devs — {SAY('IAM')}, {SAY('STS')}, {SAY('KMS')} e "
            f"segredos. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
