"""Roteiro DEA-C01 Capitulo 1 — Fundamentos de engenharia de dados."""

from glossary import SAY, EMPH, BRK, PHON

ETL = PHON("i ti ɛl", "ETL")
ELT = PHON("i ɛl ti", "ELT")
CDC = PHON("si di si", "CDC")
PARQUET = PHON("ˈpɑrkɛt", "Parquet")
AVRO = PHON("ˈɑvroʊ", "Avro")
SCHEMA_EVOLUTION = PHON("ˈskimə ˌɛvəˈluʃən", "schema evolution")
DATA_SKEW = PHON("ˈdeɪtə skju", "data skew")
SNAPPY = PHON("ˈsnæpi", "Snappy")
HIVE = PHON("haɪv", "Hive")
IDEMPOTENCIA = "idempotência"

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Bem-vindo à trilha {SAY('DEA')} dash C zero um, o exame de "
            f"Engenheiro de Dados da {SAY('AWS')}. Capítulo um: fundamentos. "
            f"Este capítulo cobre o vocabulário que a prova pressupõe — sem "
            f"dominar esses conceitos, as questões ficam ambíguas mesmo quando "
            f"você conhece os serviços."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- ETL vs ELT ----
    {
        "voice": "antonio",
        "text": (
            f"Primeiro vocabulário: {ETL} versus {ELT}. No {ETL}, você transforma "
            f"o dado ANTES de carregar no destino — por exemplo, Glue processa e "
            f"depois grava no Redshift. No {ELT}, você carrega o dado cru e "
            f"transforma DENTRO do destino usando {SAY('SQL')} — por exemplo, "
            f"copia para o {SAY('S3')} ou Redshift e transforma lá com "
            f"stored procedures ou {SAY('CTAS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},

    # ---- Batch vs Streaming ----
    {
        "voice": "francisca",
        "text": (
            f"Segundo vocabulário: batch versus streaming. Batch processa lotes "
            f"em intervalos — jobs do Glue rodando de hora em hora, por exemplo. "
            f"Streaming processa eventos conforme chegam, com latência de "
            f"milissegundos a segundos — Kinesis, Flink. A diferença não é sobre "
            f"volume, é sobre latência e modelo de processamento."
        ),
    },
    {"voice": "francisca", "text": BRK(600)},

    # ---- Data Lake vs Data Warehouse ----
    {
        "voice": "antonio",
        "text": (
            f"Data Lake versus Data Warehouse. O lake, tipicamente no {SAY('S3')}, "
            f"armazena dado cru em qualquer formato, com schema-on-read — o schema "
            f"é definido na hora da consulta, não na hora da escrita. O Warehouse, "
            f"tipicamente o Redshift, é estruturado e otimizado para análise, com "
            f"schema-on-write — você define a estrutura antes de inserir."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},

    # ---- Outros conceitos ----
    {
        "voice": "francisca",
        "text": (
            f"Outros três conceitos-chave. O {CDC}, Change Data Capture: capturar "
            f"apenas as mudanças de um banco — inserts, updates e deletes — sem "
            f"re-ler a tabela inteira. É a base do {SAY('DMS')} e da replicação "
            f"contínua. {IDEMPOTENCIA}: reprocessar o mesmo dado produz o mesmo "
            f"resultado — essencial em pipelines com retry automático. E "
            f"{SCHEMA_EVOLUTION}: o schema do dado muda com o tempo; formatos como "
            f"{AVRO} e {PARQUET} mais o Glue Schema Registry lidam com isso."
        ),
    },
    {"voice": "francisca", "text": BRK(600)},

    # ---- OLTP vs OLAP e conceitos operacionais ----
    {
        "voice": "antonio",
        "text": (
            f"Mais quatro conceitos que o exame pressupõe. {SAY('OLTP')} versus "
            f"{SAY('OLAP')}: {SAY('OLTP')} é transação rápida linha a linha — "
            f"{SAY('RDS')}, {SAY('DynamoDB')}; {SAY('OLAP')} é análise agregada "
            f"em massa, orientada a colunas — Redshift, Athena. "
            f"{BRK(400)} Replayability: a capacidade de reprocessar dados já "
            f"ingeridos — a retenção do Kinesis e a zona raw imutável no "
            f"{SAY('S3')} existem para isso. Se o pipeline falhar, você reprocessa "
            f"a partir da fonte da verdade."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Stateful versus stateless: transformação stateless não "
            f"depende de contexto — transformar um registro por vez; stateful "
            f"precisa de estado acumulado — janelas, agregações, deduplicação. "
            f"Por isso deduplicar em streaming pede Flink, não uma Lambda simples. "
            f"{BRK(400)} E data lineage: o rastro de onde o dado veio e por quais "
            f"transformações passou — dá confiança e auditabilidade ao número que "
            f"chega no dashboard."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Os 3 Vs ----
    {
        "voice": "francisca",
        "text": (
            f"Os três Vs decidem a arquitetura. VOLUME decide entre Lambda e "
            f"Spark distribuído — e volumes enormes com rede lenta levam à "
            f"família Snow. VELOCIDADE decide entre batch e streaming: segundos "
            f"é streaming, minutos é {SAY('Firehose')}, horas é batch. VARIEDADE "
            f"decide o store: estruturado vai para Redshift ou {SAY('RDS')}; "
            f"semiestruturado vai para {SAY('S3')} com Athena ou "
            f"{SAY('DynamoDB')}; não estruturado vai para {SAY('S3')} puro. "
            f"Quando a questão descreve o dado, ela está te dizendo a resposta."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Formatos de arquivo ----
    {
        "voice": "antonio",
        "text": (
            f"Formatos de arquivo — a decisão mais repetida do exame. {PARQUET} é "
            f"colunar, binário e comprimido: é a resposta para analytics em quase "
            f"todos os casos — Athena, Redshift Spectrum, Glue. Lê só as colunas "
            f"necessárias, reduzindo bytes escaneados em até noventa por cento. "
            f"{AVRO} é linha a linha, binário, com schema embutido — ideal para "
            f"streaming com {SCHEMA_EVOLUTION}, como em Kafka e Kinesis."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {SAY('JSON')} e {SAY('CSV')} são linha a linha, texto — "
            f"usados na ingestão inicial. A prática é converter para {PARQUET} o "
            f"mais cedo possível. O mantra do {SAY('DEA')}: {PARQUET} mais "
            f"particionamento mais compressão igual a menos dado escaneado igual "
            f"a menos custo mais performance. Quando duas alternativas parecem "
            f"certas, a que envolve formato colunar e partição costuma vencer."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Compressao ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre compressão — o detalhe que derruba candidatos. {SNAPPY} é "
            f"rápido, taxa moderada, divisível dentro de {PARQUET} e {SAY('ORC')} "
            f"— o padrão para analytics. G Z I P tem boa taxa mas um arquivo "
            f"ponto g z gigante NÃO pode ser dividido entre workers: um único "
            f"worker processa tudo, criando um gargalo. A pergunta clássica do "
            f"exame: arquivo de cinquenta gigabytes em g z i p está lento no "
            f"processamento Spark. O problema é a não-divisibilidade. Solução: "
            f"vários arquivos menores ou formato colunar com {SNAPPY}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Particionamento ----
    {
        "voice": "antonio",
        "text": (
            f"Particionamento estilo {HIVE}: os arquivos ficam em pastas com o "
            f"padrão 'coluna igual valor' no caminho — por exemplo, 'ano igual "
            f"dois mil e vinte seis, mês igual seis, dia igual doze'. Quando "
            f"você filtra por essas colunas no {SAY('WHERE')}, o Athena e o Spark "
            f"leem só a pasta certa — isso se chama partition pruning. Particione "
            f"pelas colunas mais usadas em filtros, geralmente data. Cuidado com "
            f"cardinalidade alta: particionar por cliente com milhões de clientes "
            f"cria o problema de small files."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- SQL que a prova espera ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre {SAY('SQL')}: o {SAY('DEA')} não cobra sintaxe decorada, mas "
            f"espera que você LEIA queries: joins, group by com having, "
            f"{SAY('CTEs')} e window functions — row number para deduplicar, "
            f"sum over partition para acumulados, lag e lead para comparar com a "
            f"linha anterior. E princípios de otimização: filtrar cedo, "
            f"selecionar só as colunas necessárias. Vamos aprofundar isso no "
            f"capítulo doze."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: queries no Athena estão caras, escaneiam a tabela "
            f"inteira em {SAY('CSV')}. Quais as duas otimizações?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Converter para {PARQUET} — colunar, lê só as colunas do SELECT. "
            f"E particionar por data — partition pruning, lê só as pastas "
            f"filtradas. Compressão {SNAPPY} complementa."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: pipeline de streaming precisa lidar com mudanças frequentes "
            f"de schema. Qual formato?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{AVRO} com schema embutido e {SCHEMA_EVOLUTION} nativa, idealmente "
            f"com Glue Schema Registry para validar compatibilidade entre "
            f"producers e consumers."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: qual a diferença prática entre {ETL} e {ELT} na {SAY('AWS')}?"
            f"{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{ETL}: Glue ou {SAY('EMR')} transforma antes de gravar no destino. "
            f"{ELT}: carrega cru no {SAY('S3')} ou Redshift e transforma lá "
            f"dentro com {SAY('SQL')} — {SAY('CTAS')}, stored procedures ou dbt."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo um. No próximo, entramos no streaming com "
            f"Kinesis e {SAY('MSK')}. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
