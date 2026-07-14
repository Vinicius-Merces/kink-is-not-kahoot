"""Roteiro DEA-C01 Capitulo 2 — Ingestão streaming: Kinesis e MSK."""

from glossary import SAY, EMPH, BRK, PHON

FIREHOSE = PHON("ˈfaɪɚhoʊz", "Firehose")
KINESIS_DATA_STREAMS = PHON("kɪˈnisɪs ˈdeɪtə strimz", "Kinesis Data Streams")
MSK = PHON("ɛm ɛs keɪ", "MSK")
PARQUET = PHON("ˈpɑrkɛt", "Parquet")
SHARD = PHON("ʃɑrd", "shard")
SHARDS = PHON("ʃɑrdz", "shards")
PARTITION_KEY = PHON("pɑrˈtɪʃən ki", "partition key")
HOT_SHARD = PHON("hɑt ʃɑrd", "hot shard")
ENHANCED_FAN_OUT = PHON("ɪnˈhænst fæn aʊt", "Enhanced Fan-Out")
KPL = PHON("keɪ pi ɛl", "KPL")
KCL = PHON("keɪ si ɛl", "KCL")
FLINK = PHON("flɪŋk", "Flink")
BUFFER_HINTS = PHON("ˈbʌfɚ hɪnts", "buffer hints")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dois: ingestão streaming com Kinesis e {SAY('MSK')}. "
            f"O streaming é o domínio que o {SAY('DEA')} mais pesa — entender "
            f"a decisão central entre {KINESIS_DATA_STREAMS}, {FIREHOSE} e {MSK} "
            f"resolve boa parte das questões."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Diagrama ----
    {
        "voice": "antonio",
        "text": (
            f"O diagrama deste capítulo mostra o pipeline de streaming clássico "
            f"do {SAY('DEA')}. Da esquerda para a direita: produtores — apps, "
            f"{SAY('IoT')}, logs — enviam dados para o {KINESIS_DATA_STREAMS}. "
            f"O {KINESIS_DATA_STREAMS} alimenta o {FIREHOSE}, que tem um buffer "
            f"e converte os dados para {PARQUET}. O {FIREHOSE} entrega no "
            f"{SAY('S3')}, particionado por data, e o Glue Data Catalog armazena "
            f"o schema. Por fim, o Athena consulta o {SAY('S3')} com {SAY('SQL')}, "
            f"pagando por terabyte escaneado."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A nota do diagrama: produtores também podem enviar "
            f"direto para o {FIREHOSE} sem passar pelo {KINESIS_DATA_STREAMS}, "
            f"quando não há necessidade de replay nem múltiplos consumidores. "
            f"O {PARQUET} nasce na entrega pelo {FIREHOSE} — não depois como "
            f"uma etapa separada. Guarde essa imagem."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Decisao central ----
    {
        "voice": "francisca",
        "text": (
            f"A decisão central: {KINESIS_DATA_STREAMS} versus {FIREHOSE} versus "
            f"{MSK}."
            f"{BRK(400)} {KINESIS_DATA_STREAMS} é um stream bruto: você produz, "
            f"você consome. Latência de tempo real, abaixo de um segundo. "
            f"Múltiplos consumidores independentes, com replay usando a retenção "
            f"de vinte e quatro horas até trezentos e sessenta e cinco dias. "
            f"Gatilho na questão: 'processar em tempo real', 'múltiplos "
            f"consumidores', 'reprocessar'."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {FIREHOSE} é um serviço de ENTREGA gerenciado: recebe "
            f"e deposita no destino — {SAY('S3')}, Redshift, OpenSearch. Latência "
            f"near real-time, com buffer mínimo de segundos. Zero gestão de "
            f"{SHARDS} ou consumidores. Gatilho: 'só entregar no {SAY('S3')} ou "
            f"Redshift sem gerenciar nada'. Atenção: {FIREHOSE} NÃO é tempo real "
            f"— esse é o engano mais comum do exame."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {MSK} é Apache Kafka gerenciado na {SAY('AWS')}. Gatilho: "
            f"'o time já usa Kafka' ou 'compatibilidade com protocolo Kafka'. "
            f"Tem replay e múltiplos consumidores assim como o {KINESIS_DATA_STREAMS}, "
            f"mas com brokers e tópicos para gerenciar — ou {MSK} Serverless para "
            f"eliminar esse gerenciamento."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- KDS em profundidade ----
    {
        "voice": "antonio",
        "text": (
            f"{KINESIS_DATA_STREAMS} em profundidade. O {SHARD} é a unidade de "
            f"capacidade: um megabyte por segundo ou mil registros por segundo de "
            f"escrita, dois megabytes por segundo de leitura. Escalar significa "
            f"fazer resharding — split para aumentar, merge para diminuir."
            f"{BRK(400)} A {PARTITION_KEY} define para qual {SHARD} o registro "
            f"vai. Se a chave concentra tráfego em poucos {SHARDS}, você tem um "
            f"{HOT_SHARD} e recebe o erro 'ProvisionedThroughputExceeded'. "
            f"Solução: usar uma chave com melhor distribuição."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Dois modos de capacidade: on-demand, para carga "
            f"imprevisível, o stream escala sozinho; e provisioned, mais barato "
            f"para carga estável. O {ENHANCED_FAN_OUT} dá dois megabytes por "
            f"segundo dedicados por consumidor via push — a resposta para "
            f"'vários consumidores independentes com baixa latência'."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Firehose em profundidade ----
    {
        "voice": "francisca",
        "text": (
            f"{FIREHOSE} em profundidade. Origens: Direct PUT, "
            f"{KINESIS_DATA_STREAMS}, {MSK}. Destinos: {SAY('S3')}, Redshift, "
            f"OpenSearch, endpoints {SAY('HTTP')}. Recursos que a prova cobra: "
            f"{BUFFER_HINTS} — buffer por tamanho em megabytes OU por tempo em "
            f"segundos, o que vier primeiro; transformação via Lambda em trânsito; "
            f"conversão nativa para {PARQUET} — exige schema no Glue Catalog; "
            f"particionamento dinâmico na escrita do {SAY('S3')}; e backup de "
            f"registros com falha num bucket de erro."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Flink ----
    {
        "voice": "antonio",
        "text": (
            f"Para processar e transformar o stream em movimento — janelas de "
            f"tempo, agregações em tempo real, detecção de anomalias — o serviço "
            f"é o Managed Service for Apache {FLINK}, o antigo Kinesis Data "
            f"Analytics. Gatilho: 'agregações por janela de um minuto sobre o "
            f"stream' ou 'detectar padrão em tempo real'. Lambda serve para "
            f"transformações simples por registro; {FLINK} para lógica com estado "
            f"e janelas temporais."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: cliques de site precisam cair no {SAY('S3')} em "
            f"{PARQUET} sem nenhuma administração. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Data {FIREHOSE} com conversão de formato para {PARQUET}. Zero "
            f"gestão, entrega gerenciada, buffer configurável."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: stream com cinco consumidores diferentes, todos precisando "
            f"de baixa latência de leitura?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{KINESIS_DATA_STREAMS} com {ENHANCED_FAN_OUT} — dois megabytes por "
            f"segundo dedicados por consumidor via push, sem competir pelo "
            f"throughput compartilhado."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: producers recebendo 'ProvisionedThroughputExceeded' mesmo "
            f"com capacidade total sobrando?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{HOT_SHARD} — a {PARTITION_KEY} está concentrando tráfego em um "
            f"{SHARD}. Solução: chave com melhor distribuição, por exemplo "
            f"adicionar sufixo aleatório."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dois. No próximo, vemos ingestão batch e "
            f"migração de dados. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
