"""Roteiro DEA-C01 Capitulo 10 — Computacao para pipelines: Lambda, Batch e conteineres."""

from glossary import SAY, EMPH, BRK, PHON

RESERVED_CONCURRENCY = PHON("rɪˈzɜrvd kənˈkɜrənsi", "reserved concurrency")
PROVISIONED_CONCURRENCY = PHON("prəˈvɪʒənd kənˈkɜrənsi", "provisioned concurrency")
FARGATE = PHON("ˈfɑrɡeɪt", "Fargate")
SPOT = PHON("spɑt", "Spot")
RDS_PROXY = PHON("ɑr di ɛs ˈprɑksi", "RDS Proxy")
TMP = PHON("tɛmp", "/tmp")
FIREHOSE = PHON("ˈfaɪɚhoʊz", "Firehose")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dez: computação para pipelines — Lambda, {SAY('AWS')} "
            f"Batch e contêineres. Nem todo processamento é Spark: a prova cobra "
            f"os limites da Lambda em profundidade e quando cada motor é a "
            f"resposta."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Lambda: limites ----
    {
        "voice": "antonio",
        "text": (
            f"Lambda para dados — os limites que decidem questões. Timeout "
            f"máximo: QUINZE minutos — 'o processamento leva vinte minutos' "
            f"elimina a Lambda. Memória de cento e vinte e oito megabytes a dez "
            f"gigabytes — e a {SAY('CPU')} escala JUNTO com a memória: Lambda "
            f"lenta em tarefa de {SAY('CPU')}? Aumente a memória. Storage "
            f"efêmero em {TMP}: até dez gigabytes, para staging temporário. E a "
            f"Lambda pode MONTAR um {SAY('EFS')} — arquivos compartilhados e "
            f"persistentes entre invocações, citado no exam guide."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Concorrência: escala automática por invocações "
            f"simultâneas. {RESERVED_CONCURRENCY} LIMITA o paralelismo — protege "
            f"o banco a jusante. {PROVISIONED_CONCURRENCY} elimina cold start. "
            f"A pegadinha: 'milhares de Lambdas simultâneas esgotando as "
            f"conexões do {SAY('RDS')}' — resposta: {RESERVED_CONCURRENCY} "
            f"e/ou {RDS_PROXY} para pool de conexões, com {SAY('SQS')} "
            f"amortecendo os picos."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- AWS Batch ----
    {
        "voice": "francisca",
        "text": (
            f"{SAY('AWS')} Batch — o que a Lambda não aguenta. Jobs em contêiner "
            f"de LONGA duração, horas, com fila, prioridade, retry e "
            f"dependências entre jobs — o Batch provisiona e desliga o compute "
            f"sozinho, inclusive {SPOT}. Gatilho: 'processamento de três horas, "
            f"sem gerenciar servidores, com {SPOT} para reduzir custo'. "
            f"Diferença para o Glue: o Batch roda QUALQUER contêiner — binário "
            f"proprietário, código C — enquanto o Glue é especializado em "
            f"{SAY('ETL')} Spark com Catalog."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Conteineres ----
    {
        "voice": "antonio",
        "text": (
            f"Contêineres: {SAY('ECS')} e {SAY('EKS')} no contexto de dados. "
            f"Papel: rodar aplicações de processamento próprias — consumidores "
            f"{SAY('KCL')}, ferramentas de terceiros — com {FARGATE} serverless "
            f"ou {SAY('EC2')} para mais controle. As imagens ficam no "
            f"{SAY('ECR')}. Na prova, contêiner aparece quando o código não "
            f"cabe no modelo Lambda — runtime custom, execução longa — e o time "
            f"já opera Kubernetes, {SAY('EKS')}, ou prefere a simplicidade do "
            f"{SAY('ECS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Tabela de decisao ----
    {
        "voice": "francisca",
        "text": (
            f"A tabela de decisão da computação. Transformação por evento, menos "
            f"de quinze minutos: Lambda. {SAY('ETL')} Spark gerenciado com "
            f"Catalog: Glue. Job containerizado de horas com fila e {SPOT}: "
            f"{SAY('AWS')} Batch. Frameworks big data variados com controle do "
            f"cluster: {SAY('EMR')}. Spark esporádico sem cluster: {SAY('EMR')} "
            f"Serverless. E aplicação própria contínua em contêiner: {SAY('ECS')} "
            f"ou {SAY('EKS')} com {FARGATE}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: transformação com binário proprietário que leva "
            f"duas horas por lote, com a menor gestão de infraestrutura?"
            f"{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('AWS')} Batch com {FARGATE} — ou {SPOT} para custo. Lambda "
            f"está fora pelo limite de quinze minutos."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: uma Lambda de parsing está lenta e o gargalo é "
            f"{SAY('CPU')}. Como acelerar sem mudar código?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Aumentar a memória — a {SAY('CPU')} da Lambda escala "
            f"proporcionalmente à memória alocada."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: várias Lambdas precisam ler e escrever nos mesmos "
            f"arquivos de referência persistentes?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Montar {SAY('EFS')} nas funções — o {TMP} é efêmero e local; o "
            f"{SAY('EFS')} é compartilhado e persistente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dez. No próximo, quem coordena tudo: "
            f"orquestração de pipelines. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
