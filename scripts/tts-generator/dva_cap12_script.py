"""Roteiro DVA-C02 Capitulo 12 — Observabilidade: CloudWatch, X-Ray e CloudTrail."""

from glossary import SAY, EMPH, BRK, PHON

XRAY = PHON("ɛks reɪ", "X-Ray")
PUT_METRIC_DATA = PHON("pʊt ˈmɛtrɪk ˈdeɪtə", "PutMetricData")
HIGH_RESOLUTION = PHON("haɪ ˌrɛzəˈluʃən", "high-resolution")
METRIC_FILTERS = PHON("ˈmɛtrɪk ˈfɪltɚz", "metric filters")
SUBSCRIPTION_FILTERS = PHON("səbˈskrɪpʃən ˈfɪltɚz", "subscription filters")
LOGS_INSIGHTS = PHON("lɔɡz ˈɪnsaɪts", "Logs Insights")
ANNOTATIONS = PHON("ˌænəˈteɪʃənz", "annotations")
METADATA = PHON("ˈmɛtəˌdeɪtə", "metadata")
SEGMENTS = PHON("ˈsɛɡmənts", "segments")
SAMPLING = PHON("ˈsæmplɪŋ", "sampling")
DAEMON = PHON("ˈdimən", "daemon")
EMF = PHON("i ɛm ɛf", "EMF")
STRUCTURED_LOGGING = PHON("ˈstrʌktʃɚd ˈlɔɡɪŋ", "structured logging")
CLOUDWATCH_AGENT = PHON("klaʊd wɑtʃ ˈeɪdʒənt", "CloudWatch Agent")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo doze: observabilidade — CloudWatch, {XRAY} e "
            f"CloudTrail. Os três pilares: métricas e alarmes, traces, e "
            f"auditoria de quem chamou o quê."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Papel de cada um ----
    {
        "voice": "antonio",
        "text": (
            f"Quem responde o quê. 'Como estão meus recursos' — métricas, "
            f"logs, alarmes: CloudWatch. 'Por onde passou e onde travou ESTA "
            f"requisição' — tracing distribuído: {XRAY}. 'Quem chamou qual "
            f"{SAY('API')} na conta' — auditoria: CloudTrail."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- CloudWatch ----
    {
        "voice": "francisca",
        "text": (
            f"CloudWatch para devs. Métricas custom via {PUT_METRIC_DATA}, com "
            f"namespace e dimensions; resolução padrão de um minuto, e "
            f"{HIGH_RESOLUTION} até UM segundo para alarmes de reação rápida. "
            f"Em {SAY('EC2')}, memória e disco NÃO são métricas nativas — "
            f"exigem o {CLOUDWATCH_AGENT}. Nos logs: {METRIC_FILTERS} "
            f"transformam padrões de log em métricas — contar ERROR e alarmar; "
            f"{SUBSCRIPTION_FILTERS} transmitem logs em tempo real para Lambda "
            f"ou Kinesis; e o {LOGS_INSIGHTS} consulta com query language."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E os dois citados nominalmente no guide: o {EMF} — "
            f"Embedded Metric Format — grava o log num {SAY('JSON')} especial "
            f"e o CloudWatch EXTRAI métricas dele automaticamente: métrica "
            f"custom de alto volume SEM chamadas {PUT_METRIC_DATA}. E o "
            f"{STRUCTURED_LOGGING}: logar {SAY('JSON')} com campos "
            f"consistentes — request {SAY('ID')}, user {SAY('ID')}, nível — é "
            f"o que torna o {LOGS_INSIGHTS} realmente útil."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- X-Ray ----
    {
        "voice": "antonio",
        "text": (
            f"{XRAY} — instrumentação. {SEGMENTS} e subsegments são as "
            f"unidades do trace. A distinção que decide questões: "
            f"{ANNOTATIONS} são INDEXADAS — filtráveis por annotation ponto "
            f"user {SAY('ID')}; {METADATA} NÃO é indexada — só contexto. "
            f"'Filtrar traces por {SAY('ID')} do cliente' = {ANNOTATIONS}; "
            f"guardaram em {METADATA} e a busca não encontra — esse é o bug da "
            f"questão. {SAMPLING} controla o custo rastreando uma fração. E o "
            f"{DAEMON}: recebe os {SEGMENTS} via {SAY('UDP')} porta dois mil — "
            f"em {SAY('EC2')} ou {SAY('ECS')} você o roda como sidecar; na "
            f"Lambda, basta ativar o Active Tracing."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: alarmar quando 'Out Of Memory Error' aparecer "
            f"nos logs?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{METRIC_FILTERS} no log group contando o padrão, mais alarme "
            f"sobre a métrica com {SAY('SNS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: emitir métricas custom da Lambda com o menor custo e "
            f"latência, em alto volume?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{EMF} — logar no formato embedded metric; o CloudWatch extrai as "
            f"métricas sem chamadas de {SAY('API')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: traces precisam ser buscados por tenant — annotation ou "
            f"{METADATA}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Annotation — indexada e filtrável. {METADATA} é só contexto, não "
            f"pesquisável."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo doze. No próximo, o veterano dos deploys: "
            f"Elastic Beanstalk. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
