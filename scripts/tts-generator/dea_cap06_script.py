"""Roteiro DEA-C01 Capitulo 6 — Modelagem de dados e evolucao de schema."""

from glossary import SAY, EMPH, BRK, PHON

STAR_SCHEMA = PHON("stɑr ˈskimə", "star schema")
SNOWFLAKE = PHON("ˈsnoʊfleɪk", "snowflake")
DISTKEY = PHON("dɪst ki", "DISTKEY")
SORTKEY = PHON("sɔrt ki", "SORTKEY")
DISTSTYLE_ALL = PHON("dɪst staɪl ɔl", "DISTSTYLE ALL")
PARTITION_KEY = PHON("pɑrˈtɪʃən ki", "partition key")
SORT_KEY = PHON("sɔrt ki", "sort key")
GSI = PHON("dʒi ɛs aɪ", "GSI")
SINGLE_TABLE = PHON("ˈsɪŋɡəl ˈteɪbəl", "single-table design")
SCHEMA_REGISTRY = PHON("ˈskimə ˈrɛdʒɪstri", "Schema Registry")
SCT = PHON("ɛs si ti", "SCT")
ICEBERG = PHON("ˈaɪsbɜrɡ", "Iceberg")
PARQUET = PHON("ˈpɑrkɛt", "Parquet")
LINEAGE = PHON("ˈlɪniɪdʒ", "lineage")
BEGINS_WITH = PHON("bɪˈɡɪnz wɪθ", "begins with")
SCAN = PHON("skæn", "Scan")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo seis: modelagem de dados e evolução de schema. Este é o "
            f"capítulo que separa 'conheço os serviços' de 'sei desenhar o dado "
            f"dentro deles' — schemas para Redshift, {SAY('DynamoDB')} e o lake."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Star schema ----
    {
        "voice": "antonio",
        "text": (
            f"O {STAR_SCHEMA} — o modelo do warehouse. No centro, a tabela FATO: "
            f"eventos e métricas, grande, cresce sempre. Ao redor, as DIMENSÕES: "
            f"contexto descritivo — cliente, produto, data — pequenas, mudam "
            f"pouco. No Redshift, a receita é: fato com {DISTKEY} na coluna de "
            f"join mais usada e {SORTKEY} na data; dimensões pequenas com "
            f"{DISTSTYLE_ALL}. Os joins viram operações locais em cada slice."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {SNOWFLAKE} schema normaliza as dimensões em "
            f"sub-dimensões — menos redundância, mais joins; a prova prefere o "
            f"{STAR_SCHEMA} para {SAY('BI')}. E desnormalizar — juntar tudo numa "
            f"tabela larga — é aceitável em warehouse colunar: colunas não "
            f"consultadas não são lidas, então a redundância custa menos que os "
            f"joins. Regra geral: normalizado para {SAY('OLTP')}, desnormalizado "
            f"para {SAY('OLAP')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- DynamoDB ----
    {
        "voice": "francisca",
        "text": (
            f"Modelagem no {SAY('DynamoDB')} — o OPOSTO do relacional. Você "
            f"modela pelos PADRÕES DE ACESSO, não pelas entidades: primeiro "
            f"liste as queries, depois desenhe a chave. {PARTITION_KEY} de alta "
            f"cardinalidade e acesso uniforme, para evitar hot partition. "
            f"{SORT_KEY} para ordenar e filtrar dentro da partição — "
            f"{BEGINS_WITH}, between."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {GSI} para consultar por outro atributo — projetando só "
            f"as colunas necessárias. {SINGLE_TABLE}: entidades relacionadas na "
            f"mesma tabela com chaves compostas — 'buscar cliente e pedidos numa "
            f"única query'. E {SCAN} com filtro em tabela grande é SEMPRE a "
            f"alternativa errada."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Schema evolution ----
    {
        "voice": "antonio",
        "text": (
            f"Evolução de schema — quando o dado muda de forma. Streaming com "
            f"producers e consumers evoluindo separados: Glue {SCHEMA_REGISTRY} "
            f"— versiona schemas e REJEITA publicação incompatível antes de "
            f"quebrar os consumers. Coluna nova nos arquivos do lake: {PARQUET} "
            f"com política de update do {SAY('crawler')}, ou {ICEBERG}, que "
            f"evolui schema por metadados sem reescrever dados."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Tipos mistos no mesmo campo — int virou string: os "
            f"choice types do DynamicFrame com ResolveChoice. E migração "
            f"heterogênea entre engines: {SAY('AWS')} {SCT} ou {SAY('DMS')} "
            f"Schema Conversion — convertem {SAY('DDL')}, tipos e procedures, "
            f"com relatório do que precisa de ajuste manual."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Lineage ----
    {
        "voice": "francisca",
        "text": (
            f"E a linhagem de dados — data {LINEAGE}: de onde veio este número? "
            f"Fonte, transformações, destino. O exam guide cita nominalmente o "
            f"SageMaker {SAY('ML')} {LINEAGE} Tracking para artefatos de machine "
            f"learning; no pipeline clássico, a linhagem prática vem dos "
            f"metadados do Catalog e do histórico de jobs. O conceito importa "
            f"mais que a ferramenta: linhagem dá confiança e auditabilidade."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: {SAY('BI')} roda no Redshift com dezenas de "
            f"joins entre fato e dimensões — como desenhar a distribuição?"
            f"{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{STAR_SCHEMA}: {DISTKEY} na coluna de join da fato, "
            f"{DISTSTYLE_ALL} nas dimensões pequenas, {SORTKEY} na data."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: um producer novo publicou schema incompatível e quebrou "
            f"os consumers. Como prevenir?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Glue {SCHEMA_REGISTRY} com regra de compatibilidade — o registry "
            f"rejeita o schema incompatível antes de chegar aos consumers."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: buscar 'todos os pedidos do cliente X no último mês' no "
            f"{SAY('DynamoDB')} com latência mínima?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{PARTITION_KEY} igual cliente, {SORT_KEY} igual data do pedido — "
            f"Query com faixa na {SORT_KEY}. Nunca {SCAN} com filtro."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo seis. No próximo, o gigante: Amazon "
            f"Redshift. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
