"""Roteiro DVA-C02 Capitulo 4 — DynamoDB para desenvolvedores."""

from glossary import SAY, EMPH, BRK, PHON

RCU = PHON("ɑr si ju", "RCU")
WCU = PHON("dabliu si ju", "WCU")
GSI = PHON("dʒi ɛs aɪ", "GSI")
LSI = PHON("ɛl ɛs aɪ", "LSI")
DAX = PHON("dæks", "DAX")
TTL = PHON("ti ti ɛl", "TTL")
QUERY = PHON("ˈkwɪri", "Query")
SCAN = PHON("skæn", "Scan")
CONDITION = PHON("kənˈdɪʃən ɪkˈsprɛʃən", "condition expression")
OPTIMISTIC = PHON("ˌɑptɪˈmɪstɪk ˈlɑkɪŋ", "optimistic locking")
LAZY_LOADING = PHON("ˈleɪzi ˈloʊdɪŋ", "lazy loading")
WRITE_THROUGH = PHON("raɪt θru", "write-through")
ELASTICACHE = PHON("ɪˈlæstɪkæʃ", "ElastiCache")
MEMORYDB = PHON("ˈmɛməri di bi", "MemoryDB")
REDIS = PHON("ˈrɛdɪs", "Redis")
MEMCACHED = PHON("ˈmɛmkæʃt", "Memcached")
BATCH_WRITE = PHON("bætʃ raɪt ˈaɪtəm", "BatchWriteItem")
PARALLEL_SCAN = PHON("ˈpærəlɛl skæn", "Parallel Scan")
STALE = PHON("steɪl", "stale")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quatro: {SAY('DynamoDB')} para desenvolvedores. Este "
            f"capítulo tem a conta de capacidade que VAI cair na sua prova, "
            f"{GSI} contra {LSI}, escrita concorrente segura — e as estratégias "
            f"de cache que o exam guide cita nominalmente."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- RCU/WCU ----
    {
        "voice": "antonio",
        "text": (
            f"A conta de {RCU} e {WCU}. Uma {RCU}: uma leitura fortemente "
            f"consistente por segundo de item de até QUATRO kilobytes — ou DUAS "
            f"leituras eventualmente consistentes. Uma {WCU}: uma escrita por "
            f"segundo de item de até UM kilobyte. O tamanho SEMPRE arredonda "
            f"para cima em blocos. E transações consomem o DOBRO."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Exemplo resolvido: dez leituras fortes por segundo de "
            f"itens de seis kilobytes. Seis arredonda para oito — dois blocos "
            f"de quatro — logo duas {RCU} por leitura, vezes dez: vinte {RCU}. "
            f"Se fossem eventualmente consistentes, metade: dez. A fórmula: "
            f"blocos vezes taxa, dividido por dois se eventual, vezes dois se "
            f"transação."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- GSI vs LSI ----
    {
        "voice": "francisca",
        "text": (
            f"{GSI} versus {LSI}. O {GSI} tem partition e sort key NOVAS, pode "
            f"ser criado a qualquer momento, só tem consistência eventual, e "
            f"tem capacidade PRÓPRIA — throttling no {GSI} pode travar a "
            f"escrita na tabela, a pegadinha favorita. O {LSI} mantém a MESMA "
            f"partition key com sort key diferente, só nasce junto com a "
            f"tabela, e aceita consistência forte."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Escritas seguras ----
    {
        "voice": "antonio",
        "text": (
            f"Escrita concorrente segura. {CONDITION}: a escrita só acontece se "
            f"a condição valer — attribute not exists evita sobrescrever. E o "
            f"{OPTIMISTIC}: comparar um atributo version na condição — se outro "
            f"processo alterou antes, a escrita falha com Conditional Check "
            f"Failed e o app decide. É a resposta padrão para 'dois usuários "
            f"editando o mesmo registro'."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Streams, TTL, DAX, batch ----
    {
        "voice": "francisca",
        "text": (
            f"O kit de recursos. Streams: fluxo ordenado de mudanças por vinte "
            f"e quatro horas — aciona Lambda a cada insert ou update. {TTL}: "
            f"expira itens por timestamp SEM consumir {WCU} — sessões e caches. "
            f"{DAX}: o cache nativo do {SAY('DynamoDB')}, leituras em "
            f"MICROSSEGUNDOS, {WRITE_THROUGH}, compatível com a {SAY('API')} — "
            f"para leitura repetitiva intensa. E os batches: até cem leituras "
            f"ou vinte e cinco escritas por chamada — o que falhar volta em "
            f"Unprocessed e você reenvia com backoff."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {QUERY} versus {SCAN}, de novo, porque cai: o {SCAN} "
            f"lê a tabela INTEIRA — o filter expression filtra DEPOIS e você "
            f"paga tudo. Consulta por atributo que não é chave? Crie um {GSI} e "
            f"use {QUERY}. {SCAN} legítimo de exportação? {PARALLEL_SCAN}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- ElastiCache ----
    {
        "voice": "antonio",
        "text": (
            f"As estratégias de cache do {ELASTICACHE} — nominais no guide. "
            f"{LAZY_LOADING}: busca no cache; deu miss, lê do banco e grava no "
            f"cache — eficiente, mas o primeiro acesso é lento e o dado pode "
            f"ficar {STALE}. {WRITE_THROUGH}: toda escrita atualiza banco E "
            f"cache — sempre atual, mas escreve mais. E o {TTL} é o corretivo "
            f"do {STALE} que complementa qualquer estratégia."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {REDIS} versus {MEMCACHED} em uma linha: {REDIS} tem "
            f"persistência, replicação com failover e estruturas ricas — é a "
            f"resposta padrão; {MEMCACHED} é cache puro e simples, "
            f"multi-thread. {MEMORYDB} é o {REDIS} durável como banco primário. "
            f"E lembre: {DAX} é SÓ para {SAY('DynamoDB')}; {ELASTICACHE} é "
            f"genérico."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: quantas {RCU} para vinte leituras eventualmente "
            f"consistentes por segundo de itens de cinco kilobytes?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Cinco arredonda para dois blocos de quatro — duas {RCU} fortes por "
            f"leitura, vezes vinte dá quarenta; eventual divide por dois: VINTE "
            f"{RCU}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: dois usuários salvam o mesmo item e um sobrescreve o "
            f"outro. Como prevenir?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{OPTIMISTIC} com {CONDITION} no atributo version — a escrita "
            f"concorrente falha e o app resolve."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: leituras repetidas dominam o custo e a latência precisa "
            f"cair para microssegundos?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{DAX} — cache nativo, {WRITE_THROUGH}, compatível com a {SAY('API')} existente.",
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo quatro. No próximo, {SAY('S3')} para "
            f"desenvolvedores: presigned {SAY('URLs')}, multipart e as quatro "
            f"siglas de criptografia. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
