"""Roteiro DEA-C01 Capitulo 5 — Data Lake no S3."""

from glossary import SAY, EMPH, BRK, PHON

PARQUET = PHON("ˈpɑrkɛt", "Parquet")
ICEBERG = PHON("ˈaɪsbɜrɡ", "Iceberg")
HUDI = PHON("ˈhudi", "Hudi")
DELTA_LAKE = PHON("ˈdɛltə leɪk", "Delta Lake")
SMALL_FILES = PHON("smɔl faɪlz", "small files")
COMPACTION = PHON("kəmˈpækʃən", "compaction")
TIME_TRAVEL = PHON("taɪm ˈtrævəl", "time travel")
FIREHOSE = PHON("ˈfaɪɚhoʊz", "Firehose")
INTELLIGENT_TIERING = PHON("ɪnˈtɛlɪdʒənt ˈtɪrɪŋ", "Intelligent-Tiering")
GLACIER = PHON("ˈɡleɪʃɚ", "Glacier")
STORAGE_LENS = PHON("ˈstɔrɪdʒ lɛnz", "Storage Lens")
SNAPSHOT = PHON("ˈsnæpʃɑt", "snapshot")
RAW = PHON("rɔ", "raw")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo cinco: o data lake no {SAY('S3')}. O {SAY('S3')} é o "
            f"centro de gravidade do {SAY('DEA')} — aqui entram a arquitetura de "
            f"zonas, o problema dos {SMALL_FILES}, os formatos transacionais e o "
            f"ciclo de vida do dado."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Arquitetura de zonas ----
    {
        "voice": "antonio",
        "text": (
            f"A arquitetura de zonas — também chamada de medallion. Zona {RAW}, "
            f"ou bronze: o dado como chegou, {SAY('JSON')} ou {SAY('CSV')}, "
            f"IMUTÁVEL — é a fonte da verdade para reprocessar. Zona processed, "
            f"ou silver: limpo, deduplicado, {PARQUET} particionado, qualidade "
            f"validada. Zona curated, ou gold: agregado e modelado para consumo "
            f"— Athena, QuickSight, Redshift. Erro no pipeline? Reprocessa da "
            f"{RAW}. Consulta lenta ou cara? O problema quase sempre está na "
            f"processed — formato, partição ou {SMALL_FILES}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Small files ----
    {
        "voice": "francisca",
        "text": (
            f"O problema dos {SMALL_FILES} — clássico absoluto de prova. Milhões "
            f"de arquivos de poucos kilobytes matam a performance do Athena e do "
            f"Spark: o custo de abrir cada arquivo supera o tempo de leitura. O "
            f"tamanho ideal é de cento e vinte e oito megabytes a um gigabyte. "
            f"Soluções: aumentar o buffer do {FIREHOSE} na origem, e "
            f"{COMPACTION} periódica — um job que reescreve os arquivos pequenos "
            f"em arquivos grandes."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Performance do S3 ----
    {
        "voice": "antonio",
        "text": (
            f"Performance do {SAY('S3')}: três mil e quinhentos PUTs e cinco mil "
            f"e quinhentos GETs por segundo POR PREFIXO — e escala com mais "
            f"prefixos. Por isso o particionamento também ajuda o {SAY('I/O')}, "
            f"não só o pruning. Se a questão fala em throttling cinco zero três "
            f"num único prefixo, a resposta é distribuir as chaves em mais "
            f"prefixos. Para arquivos grandes: multipart upload na escrita e "
            f"byte-range fetches na leitura paralela."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Formatos transacionais ----
    {
        "voice": "francisca",
        "text": (
            f"Formatos de tabela transacionais — o lakehouse. Arquivos {PARQUET} "
            f"puros são imutáveis: não existe update nem delete. O Apache "
            f"{ICEBERG} adiciona transações {SAY('ACID')}, {TIME_TRAVEL}, "
            f"evolução de schema e upserts e deletes no {SAY('S3')} — suportado "
            f"por Athena, Glue, {SAY('EMR')} e Redshift. É o preferido da prova. "
            f"{HUDI} e {DELTA_LAKE} aparecem como alternativas da mesma "
            f"categoria."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O gatilho: 'precisamos fazer update ou delete em "
            f"registros no data lake' ou 'atender exclusão de dados pessoais da "
            f"{SAY('LGPD')} no lake' — resposta: {ICEBERG}. E os detalhes que "
            f"caem: cada escrita cria um {SNAPSHOT} — {TIME_TRAVEL} é consultar "
            f"um {SNAPSHOT} antigo; a manutenção usa OPTIMIZE para {COMPACTION} "
            f"e VACUUM para expirar {SNAPSHOT}s antigos e conter custo."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Ciclo de vida ----
    {
        "voice": "antonio",
        "text": (
            f"Ciclo de vida e custo. Dado quente fica em Standard. Padrão de "
            f"acesso desconhecido: {INTELLIGENT_TIERING} — move sozinho entre "
            f"camadas, sem taxa de retrieval. {RAW} antiga de acesso raro: "
            f"Standard {SAY('IA')} via lifecycle rule. Arquivo de longo prazo: "
            f"{GLACIER} — Instant, Flexible ou Deep Archive, conforme o tempo de "
            f"retrieval aceito. E lifecycle expiration apaga objetos após o "
            f"período de retenção — o requisito legal de apagar depois de X anos."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A armadilha do arquivamento: objetos pequenos no "
            f"{GLACIER} têm overhead de metadados e mínimos de cobrança de "
            f"noventa a cento e oitenta dias — arquivar milhões de arquivos "
            f"minúsculos pode custar MAIS. Compacte antes de arquivar. Proteção: "
            f"versionamento contra deleção acidental, Cross-Region Replication "
            f"para {SAY('DR')}, {SAY('S3')} Inventory para auditar o que existe, "
            f"e {STORAGE_LENS} para visibilidade de uso."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: o Athena ficou lento após meses de ingestão via "
            f"{FIREHOSE} com buffer de sessenta segundos — milhões de arquivos "
            f"pequenos. O que fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{COMPACTION}: job periódico reescrevendo em arquivos de cento e "
            f"vinte e oito megabytes ou mais; e aumentar o buffer do {FIREHOSE} "
            f"daqui em diante."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: requisição legal exige deletar os registros de um cliente "
            f"específico armazenados em {PARQUET} no {SAY('S3')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Gerenciar a tabela com Apache {ICEBERG} — formato transacional "
            f"permite delete em nível de linha no data lake."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: milhares de requisições por segundo num único prefixo "
            f"do {SAY('S3')} retornando erro cinco zero três?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Distribuir as chaves em mais prefixos — o limite de requisições é "
            f"por prefixo e escala horizontalmente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo cinco. No próximo, modelagem de dados e "
            f"evolução de schema. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
