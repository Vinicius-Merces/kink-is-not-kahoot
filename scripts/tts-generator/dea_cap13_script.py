"""Roteiro DEA-C01 Capitulo 13 — Operacoes, monitoramento e qualidade."""

from glossary import SAY, EMPH, BRK, PHON

ITERATOR_AGE = PHON("ɪˈtɚreɪtɚ eɪdʒ", "IteratorAge")
LOGS_INSIGHTS = PHON("lɔɡz ˈɪnsaɪts", "Logs Insights")
DATA_QUALITY = PHON("ˈdeɪtə ˈkwɑləti", "Data Quality")
DQDL = PHON("di kju di ɛl", "DQDL")
QUARANTINE = PHON("ˈkwɔrəntin", "quarentena")
DLQ = PHON("di ɛl kju", "DLQ")
JOB_BOOKMARKS = PHON("dʒɑb ˈbʊkmɑrks", "Job Bookmarks")
CHECKPOINTS = PHON("ˈtʃɛkpɔɪnts", "checkpoints")
AT_LEAST_ONCE = PHON(" æt list wʌns", "at-least-once")
GRAFANA = PHON("ɡrəˈfɑnə", "Grafana")
COST_EXPLORER = PHON("kɔst ɪkˈsplɔrɚ", "Cost Explorer")
BUDGETS = PHON("ˈbʌdʒəts", "Budgets")
DATA_FRESHNESS = PHON("ˈdeɪtə ˈfrɛʃnəs", "DataFreshness")
PROFILING = PHON("ˈproʊfaɪlɪŋ", "profiling")
SAMPLING = PHON("ˈsæmplɪŋ", "sampling")
FIREHOSE = PHON("ˈfaɪɚhoʊz", "Firehose")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo treze: operações, monitoramento e qualidade — o dia a dia "
            f"de manter pipelines vivos. Aqui caem as métricas certas, o padrão "
            f"de alerta, qualidade de dados e custo."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Observabilidade ----
    {
        "voice": "antonio",
        "text": (
            f"Observabilidade — a ferramenta certa para cada pergunta. Métricas "
            f"e alarmes: CloudWatch. Logs de execução de Glue, {SAY('EMR')} e "
            f"Lambda: CloudWatch Logs — com o {LOGS_INSIGHTS} para investigar "
            f"com query language. Quem chamou qual {SAY('API')}: CloudTrail. "
            f"Diagnóstico profundo de Spark: o Spark {SAY('UI')}. E notificar "
            f"falha: EventBridge capturando o estado FAILED e publicando no "
            f"{SAY('SNS')} — polling de status é sempre a alternativa errada."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Metricas-chave ----
    {
        "voice": "francisca",
        "text": (
            f"As métricas que identificam o problema. No Kinesis: "
            f"{ITERATOR_AGE} — consumidor atrasado, os registros envelhecendo no "
            f"stream; soluções: mais paralelismo, parallelization factor, ou "
            f"otimizar o processamento. Na Lambda: errors, throttles — "
            f"concorrência no limite — e duration perto do timeout. No "
            f"{FIREHOSE}: {DATA_FRESHNESS} — atraso de entrega. No {SAY('SQS')}: "
            f"idade da mensagem mais antiga — fila acumulando. E no Redshift: "
            f"{SAY('CPU')}, disco e fila do {SAY('WLM')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Para dashboards de métricas, o CloudWatch Dashboards é "
            f"a resposta nativa; o Amazon Managed {GRAFANA} aparece quando o "
            f"enunciado pede visualização unificada de múltiplas fontes ou 'o "
            f"time já usa {GRAFANA}'."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Qualidade ----
    {
        "voice": "antonio",
        "text": (
            f"Qualidade de dados. O Glue {DATA_QUALITY} com regras {DQDL} — "
            f"completude, unicidade, faixas de valores — roda sobre tabelas do "
            f"Catalog ou dentro de jobs, e TRAVA o pipeline se reprovar. O "
            f"conceito de {QUARANTINE}: registros reprovados vão para um caminho "
            f"separado no {SAY('S3')}, em vez de contaminar a zona processed. "
            f"Antes de definir regras, faça {PROFILING} — estatísticas de nulos "
            f"e distribuições, o DataBrew gera com um clique — e em datasets "
            f"gigantes, valide por {SAMPLING}: uma amostra representativa em vez "
            f"da tabela inteira."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Idempotencia ----
    {
        "voice": "francisca",
        "text": (
            f"Idempotência e reprocessamento — pipelines reais falham e "
            f"re-executam. Os mecanismos: {JOB_BOOKMARKS} no Glue, {CHECKPOINTS} "
            f"no Flink e no {SAY('KCL')}, {DLQ}s no {SAY('SQS')} e na Lambda, e "
            f"escrita idempotente — sobrescrever a partição inteira em vez de "
            f"append duplicado. E lembre: em sistemas {AT_LEAST_ONCE}, o "
            f"consumidor DEVE tolerar duplicatas."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Custo ----
    {
        "voice": "antonio",
        "text": (
            f"Custo do pipeline — gestão financeira é in-scope. {COST_EXPLORER} "
            f"analisa o gasto por serviço, tag e período — 'descobrir o que "
            f"está caro'; use cost allocation tags para atribuir custo por "
            f"projeto. {SAY('AWS')} {BUDGETS} alerta quando o gasto ou a "
            f"previsão estoura o limite. E os controles por serviço: limite de "
            f"bytes no workgroup do Athena, Flex no Glue, Spot no {SAY('EMR')} e "
            f"lifecycle no {SAY('S3')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: garantir que dados com {SAY('IDs')} nulos não "
            f"cheguem à camada curated, com alerta para o time?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Glue {DATA_QUALITY} com regra de completude no pipeline; resultado "
            f"FAILED roteia para {QUARANTINE} e dispara {SAY('SNS')} via "
            f"EventBridge."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: a métrica {ITERATOR_AGE} de um consumidor Kinesis só "
            f"cresce. O que significa e o que fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O consumidor está atrasado. Escalar o consumo: mais shards, "
            f"parallelization factor da Lambda, ou otimizar o tempo por batch."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: ser avisado quando o job Glue noturno falhar, sem "
            f"scripts de polling?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"EventBridge rule no evento de mudança de estado do job, estado "
            f"FAILED, publicando num tópico {SAY('SNS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo treze. No próximo, o pipeline como "
            f"software: {SAY('CI')} {SAY('CD')} e infraestrutura como código. "
            f"Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
