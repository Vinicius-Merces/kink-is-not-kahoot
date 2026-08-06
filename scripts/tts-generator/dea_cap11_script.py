"""Roteiro DEA-C01 Capitulo 11 — Orquestracao de pipelines."""

from glossary import SAY, EMPH, BRK, PHON

STEP_FUNCTIONS = PHON("stɛp ˈfʌŋkʃənz", "Step Functions")
MWAA = PHON("ɛm dabliu eɪ eɪ", "MWAA")
AIRFLOW = PHON("ˈɛrfloʊ", "Airflow")
DAG = PHON("dæɡ", "DAG")
DAGS = PHON("dæɡz", "DAGs")
RETRY = PHON("riˈtraɪ", "Retry")
CATCH = PHON("kætʃ", "Catch")
CHOICE = PHON("tʃɔɪs", "Choice")
PARALLEL = PHON("ˈpærəlɛl", "Parallel")
MAP = PHON("mæp", "Map")
DISTRIBUTED_MAP = PHON("dɪˈstrɪbjətɪd mæp", "Distributed Map")
STANDARD = PHON("ˈstændɚd", "Standard")
EXPRESS = PHON("ɪkˈsprɛs", "Express")
SYNC = PHON("sɪŋk", "sync")
SCHEDULER = PHON("ˈskɛdʒulɚ", "Scheduler")
WORKFLOWS = PHON("ˈwɜrkfloʊz", "Workflows")
TASK_TOKEN = PHON("tæsk ˈtoʊkən", "task token")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo onze: orquestração de pipelines — quem coordena o quê. "
            f"Aqui a decisão central é {STEP_FUNCTIONS} versus {MWAA}, com "
            f"EventBridge disparando tudo."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Quem coordena o que ----
    {
        "voice": "antonio",
        "text": (
            f"O mapa. {STEP_FUNCTIONS}: state machine serverless com "
            f"tratamento de erro nativo — gatilho: 'coordenar Lambda, Glue e "
            f"Athena com retry, tudo serverless'. {MWAA}: Apache {AIRFLOW} "
            f"gerenciado, {DAGS} em Python — gatilho: 'o time JÁ USA "
            f"{AIRFLOW}'. EventBridge {SCHEDULER} e rules: cron e eventos — "
            f"'disparar todo dia às duas' ou 'quando o arquivo chegar'. Glue "
            f"{WORKFLOWS}: {DAG} nativo para pipelines cem por cento Glue. E "
            f"{SAY('SQS')} com {SAY('SNS')}: desacoplamento entre etapas."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Step Functions a fundo ----
    {
        "voice": "francisca",
        "text": (
            f"{STEP_FUNCTIONS} a fundo — os estados que caem. Task chama o "
            f"serviço, e com o padrão ponto {SYNC} ESPERA o Glue Job ou o "
            f"{SAY('EMR')} step terminar, sem polling manual. {CHOICE} ramifica. "
            f"{PARALLEL} executa ramos simultâneos. {MAP} itera sobre uma lista "
            f"— e o {DISTRIBUTED_MAP} processa MILHÕES de objetos do {SAY('S3')} "
            f"em paralelo massivo: 'reprocessar milhões de arquivos, "
            f"orquestrado e serverless'."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {RETRY} com backoff e {CATCH} roteando para o ramo de "
            f"erro são o coração do tratamento de falhas. O {TASK_TOKEN} cobre "
            f"aprovação humana ou espera por evento externo. E os dois tipos: "
            f"{STANDARD} — até um ano, exactly once, auditável passo a passo — "
            f"para pipelines de dados; {EXPRESS} — alto volume, até cinco "
            f"minutos, mais barato — para ingestão de eventos em massa."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- MWAA ----
    {
        "voice": "antonio",
        "text": (
            f"{MWAA} — quando o {AIRFLOW} é a resposta. {DAGS} Python no "
            f"{SAY('S3')}, ambiente gerenciado com scheduler e workers. "
            f"Atenção: {MWAA} NÃO é serverless — tem custo fixo por hora. Por "
            f"isso a decisão: pipeline novo, cem por cento {SAY('AWS')} — "
            f"{STEP_FUNCTIONS}; time com {DAGS} e expertise {AIRFLOW} existentes, "
            f"ou que precisa dos operadores da comunidade — {MWAA}. "
            f"Troubleshooting: {DAG} que não aparece é erro de import — veja os "
            f"logs do scheduler; tasks na fila sem executar é worker no limite — "
            f"aumente o auto scaling."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Padrao completo ----
    {
        "voice": "francisca",
        "text": (
            f"O padrão completo que a prova adora: evento no {SAY('S3')}, "
            f"EventBridge dispara o {STEP_FUNCTIONS}, que inicia o Glue Job com "
            f"ponto {SYNC}, valida a qualidade, e um {CHOICE} decide — sucesso "
            f"publica no {SAY('SNS')}, falha vai para o fluxo de erro com "
            f"{RETRY} e alerta. Montar essa cadeia de cabeça resolve várias "
            f"questões do domínio três."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: coordenar Glue, validação e carga no Redshift "
            f"com retry automático e alerta, tudo serverless?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{STEP_FUNCTIONS} {STANDARD} com integrações nativas, {RETRY} e "
            f"{CATCH}, e {SAY('SNS')} para alertas."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: o time tem oitenta {DAGS} de {AIRFLOW} on-premises e quer "
            f"migrar com mínimo retrabalho?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{MWAA} — os {DAGS} Python migram praticamente como estão.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: reprocessar quatro milhões de objetos históricos do "
            f"{SAY('S3')} em paralelo, orquestrado e serverless?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{STEP_FUNCTIONS} {DISTRIBUTED_MAP} — paralelismo massivo com retry "
            f"por item. {SAY('S3')} Batch Operations é a alternativa quando é "
            f"uma única operação simples por objeto."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo onze. No próximo, análise, {SAY('SQL')} e "
            f"visualização com QuickSight. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
