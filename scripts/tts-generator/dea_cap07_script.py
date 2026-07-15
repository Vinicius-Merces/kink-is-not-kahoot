"""Roteiro DEA-C01 Capitulo 7 — Amazon Redshift."""

from glossary import SAY, EMPH, BRK, PHON

LEADER_NODE = PHON("ˈlidɚ noʊd", "leader node")
SLICES = PHON("ˈslaɪsɪz", "slices")
COPY = PHON("ˈkɑpi", "COPY")
UNLOAD = PHON("ʌnˈloʊd", "UNLOAD")
PARQUET = PHON("ˈpɑrkɛt", "Parquet")
DISTKEY = PHON("dɪst ki", "DISTKEY")
SORTKEY = PHON("sɔrt ki", "sort key")
VACUUM = PHON("ˈvækjum", "VACUUM")
ANALYZE = PHON("ˈænəlaɪz", "ANALYZE")
SPECTRUM = PHON("ˈspɛktrəm", "Spectrum")
WLM = PHON("dabliu ɛl ɛm", "WLM")
CONCURRENCY_SCALING = PHON("kənˈkɜrənsi ˈskeɪlɪŋ", "Concurrency Scaling")
MATERIALIZED_VIEW = PHON("məˈtɪriəlaɪzd vju", "materialized view")
DATA_SHARING = PHON("ˈdeɪtə ˈʃɛrɪŋ", "data sharing")
DATA_API = PHON("ˈdeɪtə eɪ pi aɪ", "Data API")
STORED_PROCEDURES = PHON("stɔrd prəˈsidʒɚz", "stored procedures")
RA3 = PHON("ɛr eɪ tri", "RA3")
FEDERATED = PHON("ˈfɛdəreɪtɪd", "federated query")
DYNAMIC_MASKING = PHON("daɪˈnæmɪk ˈdeɪtə ˈmæskɪŋ", "dynamic data masking")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo sete: Amazon Redshift, o data warehouse da {SAY('AWS')}. "
            f"Aqui caem arquitetura {SAY('MPP')}, carga de dados, distribuição, "
            f"e uma lista de recursos que a prova adora — {SPECTRUM}, "
            f"Serverless, {WLM} e o {DATA_API}."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Arquitetura ----
    {
        "voice": "antonio",
        "text": (
            f"A arquitetura: um {LEADER_NODE} recebe o {SAY('SQL')}, planeja e "
            f"distribui; os compute nodes executam em paralelo através de "
            f"{SLICES} — cada slice tem sua fatia dos dados e da {SAY('CPU')}. "
            f"É o {SAY('MPP')}: processamento massivamente paralelo. Os nós "
            f"{RA3} separam compute de storage — o managed storage fica no "
            f"{SAY('S3')} e o armazenamento escala sem adicionar compute."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Carga ----
    {
        "voice": "francisca",
        "text": (
            f"Carga de dados — o mantra: {COPY} é a resposta. Para carregar no "
            f"Redshift, o comando {COPY} lê do {SAY('S3')} em paralelo pelos "
            f"{SLICES}. Inserts linha a linha são SEMPRE a alternativa errada. "
            f"Na direção contrária, o {UNLOAD} exporta resultados de query para "
            f"o {SAY('S3')} — inclusive em {PARQUET}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Distribuicao ----
    {
        "voice": "antonio",
        "text": (
            f"Distribuição e ordenação — as duas alavancas de performance. "
            f"{DISTKEY}: linhas com o mesmo valor ficam no mesmo nó — use na "
            f"coluna de join para eliminar o shuffle. DISTSTYLE ALL: cópia "
            f"completa em cada nó — só para dimensões pequenas. EVEN: "
            f"round-robin uniforme. E AUTO: o Redshift decide — boa resposta "
            f"para 'menor esforço'. A {SORTKEY} ordena fisicamente no disco: "
            f"filtros por data leem só os blocos relevantes via zone maps."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Manutenção: {VACUUM} reorganiza e recupera espaço após "
            f"deletes; {ANALYZE} atualiza as estatísticas do otimizador."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Programando o Redshift ----
    {
        "voice": "francisca",
        "text": (
            f"Programando o Redshift. {STORED_PROCEDURES} encapsulam as "
            f"transformações {SAY('ELT')} dentro do warehouse. E o {DATA_API}: "
            f"executa {SAY('SQL')} por chamada {SAY('HTTPS')} assíncrona, SEM "
            f"conexão {SAY('JDBC')} e sem driver — ideal para Lambda e Step "
            f"Functions. O padrão {SAY('ELT')} completo: {COPY} carrega a "
            f"staging, a procedure transforma, e o Step Functions orquestra via "
            f"{DATA_API}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E os locks: {SAY('DDL')} e transações longas bloqueiam "
            f"queries de {SAY('BI')}. Investigue com as system tables — "
            f"{SAY('STV')} locks — e encerre a sessão bloqueadora com PG "
            f"terminate backend. Sintoma clássico: 'uma transação aberta há "
            f"horas está travando o {SAY('ETL')}'."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Recursos de prova ----
    {
        "voice": "antonio",
        "text": (
            f"Os recursos que caem em prova. Redshift {SPECTRUM}: consultar o "
            f"{SAY('S3')} a partir do Redshift SEM carregar — usa o Glue "
            f"Catalog. Redshift Serverless: carga intermitente, paga por "
            f"{SAY('RPUs')}, sem gerenciar cluster. {CONCURRENCY_SCALING}: "
            f"clusters extras transparentes para picos de usuários simultâneos. "
            f"{WLM}: separar e priorizar filas — {SAY('ETL')} pesado versus "
            f"queries de {SAY('BI')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {MATERIALIZED_VIEW}: pré-computa a agregação repetida "
            f"do dashboard, com refresh incremental. {FEDERATED}: consultar "
            f"{SAY('RDS')} direto do Redshift sem mover dado. {DATA_SHARING}: "
            f"compartilhar dados ao vivo entre clusters e contas sem copiar. "
            f"Streaming ingestion: Kinesis ou Kafka direto no Redshift via "
            f"{MATERIALIZED_VIEW}, com latência de segundos. E {DYNAMIC_MASKING}: "
            f"analistas veem o {SAY('CPF')} mascarado, auditores veem completo — "
            f"por política, sem duplicar dado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Troubleshooting ----
    {
        "voice": "francisca",
        "text": (
            f"Troubleshooting de performance — por onde investigar. Query lenta: "
            f"EXPLAIN e as system tables mostram o plano; procure redistribuição "
            f"de dados no join — {SAY('DS')} broadcast ou {SAY('DS')} dist "
            f"indicam {DISTKEY} errada. Disco cheio ou skew: a view {SAY('SVV')} "
            f"table info mostra skew rows e unsorted — {VACUUM} e revisão de "
            f"distribuição. Fila de espera: métricas do {WLM} — resposta: "
            f"automatic {WLM} ou {CONCURRENCY_SCALING}. No CloudWatch: "
            f"{SAY('CPU')}, espaço em disco e duração de query."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: joins entre fato e dimensão lentos, com muita "
            f"movimentação de dados entre nós?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DISTKEY} na coluna de join da fato mais DISTSTYLE ALL na dimensão "
            f"pequena — colocaliza os dados e elimina o shuffle."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: noventa por cento dos dados estão no {SAY('S3')} e só dez "
            f"por cento precisam de performance máxima — menor custo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Carregar os dez por cento quentes no Redshift e consultar o resto "
            f"via {SPECTRUM} direto no {SAY('S3')}, em {PARQUET} particionado."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: rodar {SAY('SQL')} no Redshift a partir de uma Lambda "
            f"sem gerenciar conexões {SAY('JDBC')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Redshift {DATA_API} — chamada {SAY('HTTPS')} assíncrona, sem "
            f"driver e sem pool de conexões."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo sete. No próximo, o {SAY('SQL')} serverless "
            f"direto no lake: Amazon Athena. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
