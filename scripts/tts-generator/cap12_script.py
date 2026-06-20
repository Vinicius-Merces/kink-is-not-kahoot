"""Roteiro tratado do Capitulo 12 (Analytics) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

KINESIS_DATA_STREAMS = PHON("kɪˈnisɪs ˈdeɪtə strimz", "Kinesis Data Streams")
DATA_FIREHOSE = PHON("ˈdeɪtə ˈfaɪɚhoʊs", "Data Firehose")
SHARDS = PHON("ʃɑrdz", "shards")
REPLAY = PHON("riˈpleɪ", "replay")
PARQUET = PHON("pɑrˈkeɪ", "Parquet")
LAKE_FORMATION = PHON("leɪk fɔrˈmeɪʃən", "Lake Formation")
ROW_LEVEL_SECURITY = PHON("roʊ ˈlɛvəl sɪˈkjʊrəti", "row-level security")
QUICKSIGHT = PHON("ˈkwɪksaɪt", "QuickSight")
SPICE = PHON("spaɪs", "SPICE")
REDSHIFT_SPECTRUM = PHON("ˈrɛdʃɪft ˈspɛktrəm", "Redshift Spectrum")
OPENSEARCH = PHON("ˈoʊpənsɜrtʃ", "OpenSearch")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo doze: analytics. A prova cobra esse domínio "
            f"principalmente como qual serviço processa ou consulta este "
            f"tipo e volume de dados com menos esforço operacional."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Tabela de servicos ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos pelo vocabulário completo desse domínio."
            f"{BRK(300)} Athena: S Q L {SAY('serverless')} direto no "
            f"{SAY('S3')}, pagando por dado escaneado — otimize com "
            f"{PARQUET} e particionamento."
            f"{BRK(300)} Glue: E T L {SAY('serverless')} mais o Data "
            f"Catalog, o catálogo de metadados usado por Athena, Redshift "
            f"{SAY('Spectrum')} e {SAY('EMR')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {KINESIS_DATA_STREAMS}: ingestão de "
            f"{SAY('streaming')} em tempo real, ordenada, com {REPLAY}, "
            f"múltiplos consumidores."
            f"{BRK(300)} {DATA_FIREHOSE}: entrega {SAY('streaming')} quase "
            f"em tempo real, direto para {SAY('S3')} ou Redshift, zero "
            f"administração."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Redshift: {SAY('data warehouse')} para B I e O L A "
            f"P em escala — não para O L T P. {SAY('EMR')}: Hadoop e Spark "
            f"gerenciado, use quando precisar de controle ou o Glue não for "
            f"suficiente. E {OPENSEARCH}: busca de texto livre e análise de "
            f"logs."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Kinesis vs Firehose ----
    {
        "voice": "francisca",
        "text": (
            f"Aprofundando no {SAY('pipeline')} de {SAY('streaming')}: no "
            f"{KINESIS_DATA_STREAMS}, você controla os consumidores — "
            f"{SHARDS}, retenção de até trezentos e sessenta e cinco dias, "
            f"{REPLAY} de eventos. Vários consumidores independentes podem "
            f"ler o mesmo {SAY('stream')}. Use quando a aplicação precisa "
            f"processar os eventos em tempo real com lógica própria."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Já o {DATA_FIREHOSE} é totalmente gerenciado, sem "
            f"{SHARDS} para administrar — entrega automaticamente para "
            f"{SAY('S3')}, Redshift ou {OPENSEARCH}, com transformação "
            f"opcional via Lambda. Use quando o destino é só carregar os "
            f"dados em algum lugar, sem lógica de consumo customizada."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Athena vs Redshift trap ----
    {
        "voice": "antonio",
        "text": (
            f"A distinção favorita da prova: analisar logs do {SAY('ALB')} "
            f"ou Flow Logs já armazenados no {SAY('S3')}, com S Q L, menor "
            f"custo e esforço, é Athena — {EMPH('não Redshift, não EMR')}. "
            f"Athena é {SAY('serverless')} e consulta o {SAY('S3')} "
            f"diretamente, sem carregar dado em lugar nenhum."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Sinal prático: reduzir o custo das queries do "
            f"Athena tem quase sempre a mesma resposta — converter os dados "
            f"para um formato colunar comprimido, como {PARQUET} ou {SAY('ORC')}, "
            f"e particionar por data ou categoria. O Athena cobra por "
            f"bytes escaneados, então menos dados lidos é menos custo."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- EMR vs Glue ----
    {
        "voice": "antonio",
        "text": (
            f"Glue é a resposta padrão para E T L {SAY('serverless')} "
            f"simples. {SAY('EMR')} entra quando o enunciado menciona "
            f"frameworks específicos — Spark, Hive, Presto, HBase — com "
            f"configuração detalhada do cluster, ou quando o time já tem "
            f"experiência em Hadoop e Spark e precisa de controle total, "
            f"incluindo usar instâncias {SAY('Spot')} nos nós de tarefa, "
            f"reduzindo custo de processamento em até noventa por cento."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Lake Formation ----
    {
        "voice": "francisca",
        "text": (
            f"Construir um {SAY('data lake')} no {SAY('S3')} com o Glue "
            f"Catalog resolve o armazenamento, mas não o controle de acesso "
            f"granular. O {LAKE_FORMATION} adiciona permissões em nível de "
            f"tabela, coluna e até linha, a {ROW_LEVEL_SECURITY}, sobre os "
            f"dados catalogados — um único lugar para conceder acesso a "
            f"múltiplos serviços, em vez de replicar políticas de bucket "
            f"individualmente para cada consumidor."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- QuickSight, Spectrum, OpenSearch ----
    {
        "voice": "antonio",
        "text": (
            f"O {QUICKSIGHT} é o serviço de B I {SAY('serverless')} da "
            f"{SAY('AWS')} — conecta a Athena, Redshift, {SAY('RDS')} e "
            f"{SAY('S3')} para criar painéis interativos. Usa o motor "
            f"{SPICE}, em memória, para acelerar consultas repetidas sem "
            f"sobrecarregar a fonte de dados a cada visualização."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {REDSHIFT_SPECTRUM} estende as consultas S Q L do "
            f"Redshift para consultar dados direto no {SAY('S3')}, via Glue "
            f"Catalog, sem precisar carregar tudo no cluster primeiro — útil "
            f"para juntar dados quentes, já no Redshift, com dados frios "
            f"históricos numa única consulta."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E o {OPENSEARCH}, um {SAY('fork')} de código aberto "
            f"do Elasticsearch mantido pela {SAY('AWS')}, é a resposta para "
            f"busca de texto livre, análise de logs quase em tempo real, ou "
            f"painéis de observabilidade. Diferente do Athena, que é S Q L "
            f"sobre arquivos estáticos, o {OPENSEARCH} é um motor de busca "
            f"com ingestão contínua — mais adequado para buscar por "
            f"palavra-chave em milhões de logs."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório de uma hora e meia, "
            f"por centavos, onde você cria uma tabela no Glue Data Catalog, "
            f"compara bytes escaneados pelo Athena antes e depois de "
            f"converter para {PARQUET}, e cria um {KINESIS_DATA_STREAMS} "
            f"com um {SAY('shard')}, enviando e lendo registros via linha "
            f"de comando."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: a empresa quer consultar logs de "
            f"Flow Logs armazenados no {SAY('S3')} com S Q L, sem "
            f"provisionar infraestrutura. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Athena — {SAY('serverless')}, paga por dado escaneado, "
            f"consulta o {SAY('S3')} diretamente via S Q L padrão."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: múltiplas aplicações precisam consumir o mesmo "
            f"{SAY('stream')} de eventos de cliques em tempo real, cada uma "
            f"com sua própria lógica. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{KINESIS_DATA_STREAMS} — suporta múltiplos consumidores "
            f"independentes lendo o mesmo {SAY('stream')}, com retenção "
            f"configurável e {REPLAY}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: dados de I o T devem ser entregues automaticamente "
            f"ao {SAY('S3')} em lotes, sem gerenciar infraestrutura de "
            f"consumo. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DATA_FIREHOSE} — totalmente gerenciado, entrega quase em "
            f"tempo real para {SAY('S3')}, Redshift ou {OPENSEARCH}, com "
            f"transformação opcional via Lambda."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: como reduzir o custo das consultas do Athena sem "
            f"perder dados?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Converter os arquivos para um formato colunar comprimido, "
            f"como {PARQUET} ou {SAY('ORC')}, e particionar por colunas "
            f"usadas em filtros, como data. O Athena cobra por bytes "
            f"escaneados — menos dados lidos reduz o custo diretamente."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: o time de dados já tem {SAY('jobs')} Spark complexos, "
            f"e precisa de controle fino sobre o cluster, incluindo uso de "
            f"{SAY('Spot')} nos nós de tarefa. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('EMR')}, Elastic MapReduce — Hadoop e Spark gerenciado, "
            f"com controle total da configuração do cluster, suportando "
            f"instâncias {SAY('Spot')} nos nós de tarefa para reduzir custo."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: a empresa precisa que analistas de diferentes "
            f"departamentos vejam apenas as colunas e linhas do "
            f"{SAY('data lake')} relevantes ao seu time, sem replicar dados. "
            f"Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {LAKE_FORMATION} — define permissões granulares em "
            f"nível de tabela, coluna e linha sobre os dados catalogados no "
            f"Glue Data Catalog, aplicadas de forma centralizada a qualquer "
            f"serviço que consulte o {SAY('data lake')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: é preciso buscar por palavras-chave em milhões de "
            f"linhas de log de aplicação, com resultados quase em tempo "
            f"real. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{OPENSEARCH} — motor de busca e indexação otimizado para "
            f"texto livre e análise de logs com ingestão contínua, diferente "
            f"do Athena, melhor para consultas S Q L analíticas sobre "
            f"arquivos estáticos."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo doze. No próximo, vamos falar de "
            f"otimização de custos. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
