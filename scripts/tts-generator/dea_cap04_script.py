"""Roteiro DEA-C01 Capitulo 4 — AWS Glue: ETL e Data Catalog."""

from glossary import SAY, EMPH, BRK, PHON

CRAWLER = PHON("ˈkrɔlɚ", "crawler")
CRAWLERS = PHON("ˈkrɔlɚz", "crawlers")
JOB_BOOKMARK = PHON("dʒɑb ˈbʊkmɑrk", "Job Bookmark")
DATABREW = PHON("ˈdeɪtəbru", "DataBrew")
SCHEMA_REGISTRY = PHON("ˈskimə ˈrɛdʒɪstri", "Schema Registry")
DATA_QUALITY = PHON("ˈdeɪtə ˈkwɑləti", "Data Quality")
DYNAMICFRAME = PHON("daɪˈnæmɪk freɪm", "DynamicFrame")
DATAFRAME = PHON("ˈdeɪtə freɪm", "DataFrame")
DATA_SKEW = PHON("ˈdeɪtə skju", "data skew")
PARQUET = PHON("ˈpɑrkɛt", "Parquet")
FLEX = PHON("flɛks", "Flex")
PARTITION_INDEXES = PHON("pɑrˈtɪʃən ˈɪndɛksɪz", "partition indexes")
DETECT_PII = PHON("dɪˈtɛkt pi aɪ aɪ", "Detect PII")
HIVE = PHON("haɪv", "Hive")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quatro: {SAY('AWS')} Glue — o {SAY('ETL')} serverless e o "
            f"catálogo central do data lake. O Glue é provavelmente o serviço "
            f"mais cobrado do {SAY('DEA')}, e a chave é não confundir o papel de "
            f"cada peça."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- As pecas do Glue ----
    {
        "voice": "antonio",
        "text": (
            f"As peças. O Data Catalog é o catálogo central de metadados — "
            f"databases, tabelas, schemas e partições — usado pelo Athena, "
            f"Redshift Spectrum, {SAY('EMR')} e Lake Formation; é o índice do "
            f"data lake, compatível com o metastore do {HIVE}. O {CRAWLER} "
            f"varre a fonte, infere o schema e cria ou atualiza as tabelas no "
            f"Catalog. E o Job é o {SAY('ETL')} em si — Spark serverless, pago "
            f"por {SAY('DPU')} hora."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {JOB_BOOKMARK} lembra o que já foi processado — "
            f"execuções incrementais; gatilho: 'processar apenas dados novos'. "
            f"Triggers e Workflows orquestram {CRAWLERS} e jobs em um "
            f"{SAY('DAG')} nativo. O Glue {DATA_QUALITY} valida regras de "
            f"completude e unicidade. O {SCHEMA_REGISTRY} versiona schemas de "
            f"streaming. E o {DATABREW} é a preparação VISUAL de dados, sem "
            f"código — gatilho: 'analistas sem programação precisam limpar "
            f"dados'."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Workers e tipos de job ----
    {
        "voice": "francisca",
        "text": (
            f"Dimensionamento — os tipos de worker e de job. O padrão é o job "
            f"Spark com workers G ponto um X — quatro {SAY('vCPUs')} e dezesseis "
            f"gigas. Dobre o worker, G dois X ou maior, para resolver falta de "
            f"memória e {DATA_SKEW}; aumente o NÚMERO de workers para "
            f"paralelismo. Python Shell: tarefas leves sem Spark, por uma fração "
            f"do custo. Streaming {SAY('ETL')}: job contínuo lendo Kinesis ou "
            f"Kafka em micro-batches."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E duas opções de custo: {FLEX} execution — capacidade "
            f"ociosa, uns trinta e cinco por cento mais barata, para jobs que "
            f"toleram atraso de início; é o Spot do Glue. E auto scaling: o job "
            f"ajusta os workers durante a execução e você paga só pelo que usa "
            f"em cada fase."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Tuning e troubleshooting ----
    {
        "voice": "antonio",
        "text": (
            f"Tuning e troubleshooting — o domínio três adora. Job lento ou com "
            f"out of memory: poucos workers, worker pequeno, ou {DATA_SKEW}. Job "
            f"reprocessando tudo: {JOB_BOOKMARK} desativado. Milhares de "
            f"arquivos pequenos na saída: use coalesce ou repartition antes de "
            f"gravar. Job lendo a tabela inteira sem precisar: pushdown "
            f"predicates e partition pruning. E para o diagnóstico profundo: "
            f"habilite o Spark {SAY('UI')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {DYNAMICFRAME} versus {DATAFRAME}: o {DYNAMICFRAME} é a "
            f"abstração do Glue — tolera schema inconsistente com os choice "
            f"types e tem transformações próprias como ResolveChoice. Converta "
            f"para {DATAFRAME} do Spark quando precisar da {SAY('API')} completa."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Connections e Catalog na pratica ----
    {
        "voice": "francisca",
        "text": (
            f"Connections e o Catalog na prática. As Glue Connections guardam o "
            f"acesso a fontes {SAY('JDBC')} — endpoint, credenciais via Secrets "
            f"Manager, e a {SAY('VPC')} por onde o job sai. Se o job não alcança "
            f"o banco, verifique o security group — a regra clássica é o self "
            f"referencing rule. Nos {CRAWLERS}: exclusions para pular pastas e "
            f"crawls incrementais para acelerar. E em tabelas com muitas "
            f"partições, os {PARTITION_INDEXES} aceleram o planejamento do "
            f"Athena."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Detect PII ----
    {
        "voice": "antonio",
        "text": (
            f"Dados sensíveis: a transformação {DETECT_PII} identifica {SAY('CPF')}, "
            f"e-mail e cartão DURANTE o {SAY('ETL')}, e pode mascarar as colunas "
            f"na escrita. A diferença de papel: Macie encontra {SAY('PII')} "
            f"ARMAZENADA no {SAY('S3')}; o {DETECT_PII} trata {SAY('PII')} em "
            f"MOVIMENTO no pipeline. 'Impedir que {SAY('PII')} chegue à zona "
            f"curated' se resolve no pipeline — Glue, não Macie."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: job diário deve processar apenas os arquivos "
            f"que chegaram desde a última execução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{JOB_BOOKMARK} — o Glue rastreia o que já foi processado e roda incremental.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: job Spark falhando com out of memory numa tabela com "
            f"distribuição desigual?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DATA_SKEW} — redistribuir com salting ou repartition, e usar "
            f"workers maiores, G dois X, ou mais numerosos."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: job {SAY('ETL')} noturno sem urgência precisa custar "
            f"menos — qual opção do próprio Glue?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{FLEX} execution — capacidade ociosa com desconto, aceitando "
            f"possível atraso de início. Auto scaling complementa."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo quatro. No próximo, o data lake no "
            f"{SAY('S3')} — zonas, small files e Iceberg. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
