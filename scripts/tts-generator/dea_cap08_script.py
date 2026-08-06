"""Roteiro DEA-C01 Capitulo 8 — Amazon Athena."""

from glossary import SAY, EMPH, BRK, PHON

PARQUET = PHON("ˈpɑrkɛt", "Parquet")
CTAS = PHON("si tæs", "CTAS")
WORKGROUPS = PHON("ˈwɜrkɡrups", "workgroups")
PARTITION_PROJECTION = PHON("pɑrˈtɪʃən prəˈdʒɛkʃən", "partition projection")
FEDERATED = PHON("ˈfɛdəreɪtɪd ˈkwɪriz", "federated queries")
ICEBERG = PHON("ˈaɪsbɜrɡ", "Iceberg")
MSCK = PHON("ɛm ɛs si keɪ", "MSCK REPAIR TABLE")
QUERY_RESULT_REUSE = PHON("ˈkwɪri rɪˈzʌlt riˈjuz", "query result reuse")
SMALL_FILES = PHON("smɔl faɪlz", "small files")
TIME_TRAVEL = PHON("taɪm ˈtrævəl", "time travel")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo oito: Amazon Athena — {SAY('SQL')} serverless direto no "
            f"{SAY('S3')}, pago por terabyte escaneado. Toda a otimização do "
            f"Athena gira em torno de UMA ideia: escanear menos."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Como escanear menos ----
    {
        "voice": "antonio",
        "text": (
            f"Como escanear menos — e pagar menos. Formato colunar: um select de "
            f"três colunas em {PARQUET} lê SÓ essas três colunas — redução de "
            f"noventa por cento ou mais contra {SAY('CSV')}. Particionamento com "
            f"WHERE na coluna de partição: partition pruning, lê só as pastas "
            f"filtradas. Compressão: menos bytes lidos, menos cobrado. E nunca "
            f"select asterisco em produção."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Mais duas armas: {PARTITION_PROJECTION} — o Athena "
            f"calcula as partições por regra, sem consultar o Catalog nem rodar "
            f"crawler; resolve 'tabela com milhões de partições lenta para "
            f"planejar'. E {CTAS} — create table as select: materializa o "
            f"resultado já em {PARQUET} particionado; também serve para "
            f"converter formatos só com {SAY('SQL')}, sem job Glue."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Recursos de prova ----
    {
        "voice": "francisca",
        "text": (
            f"Recursos de prova. {WORKGROUPS}: separam times, aplicam LIMITE de "
            f"bytes escaneados por query — o controle de custo — e métricas por "
            f"grupo. {FEDERATED}: consultar fontes fora do {SAY('S3')} — "
            f"{SAY('RDS')}, {SAY('DynamoDB')}, CloudWatch Logs — via conectores "
            f"Lambda. Suporte nativo a {ICEBERG}, incluindo update, delete e "
            f"{TIME_TRAVEL}. {QUERY_RESULT_REUSE}: reaproveita o resultado de "
            f"query idêntica recente sem re-escanear."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Views encapsulam lógica e escondem colunas dos "
            f"consumidores. E o Athena for Apache Spark: notebooks Spark "
            f"serverless dentro do Athena — gatilho: 'explorar dados "
            f"interativamente com Spark sem provisionar cluster'."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Erros classicos ----
    {
        "voice": "antonio",
        "text": (
            f"Os diagnósticos clássicos. Tabela existe mas retorna zero linhas: "
            f"partições não registradas no Catalog — rode {MSCK}, ou adicione a "
            f"partição com alter table, ou use {PARTITION_PROJECTION}. Query "
            f"lenta em tabela particionada: o WHERE não filtra pela coluna de "
            f"partição. Timeout com milhares de arquivos: {SMALL_FILES} — "
            f"compaction; no {ICEBERG}, o comando OPTIMIZE."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o erro {SAY('HIVE')} BAD DATA: o schema do Catalog "
            f"difere dos arquivos — um tipo mudou. Corrigir a tabela, resolver "
            f"com ResolveChoice no Glue, ou reprocessar os arquivos fora do "
            f"padrão."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: limitar quanto cada time pode escanear por "
            f"query?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{WORKGROUPS} com data usage controls — limite de bytes por query e "
            f"por workgroup."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: tabela com milhões de partições de data está lenta para "
            f"INICIAR as queries?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{PARTITION_PROJECTION} — partições calculadas por regra, sem "
            f"consultar o Catalog nem crawler por partição nova."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: converter terabytes de {SAY('JSON')} para {PARQUET} "
            f"usando apenas {SAY('SQL')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{CTAS} — create table as select com format {PARQUET} e "
            f"particionamento na própria query."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo oito. No próximo, {SAY('EMR')} e Apache "
            f"Spark — o big data com controle total. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
