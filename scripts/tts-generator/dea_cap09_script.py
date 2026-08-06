"""Roteiro DEA-C01 Capitulo 9 — Amazon EMR e Apache Spark."""

from glossary import SAY, EMPH, BRK, PHON

EMRFS = PHON("i ɛm ɑr ɛf ɛs", "EMRFS")
HDFS = PHON("eɪtʃ di ɛf ɛs", "HDFS")
SPOT = PHON("spɑt", "Spot")
TASK_NODES = PHON("tæsk noʊdz", "task nodes")
CORE_NODES = PHON("kɔr noʊdz", "core nodes")
INSTANCE_FLEETS = PHON("ˈɪnstəns flits", "instance fleets")
MANAGED_SCALING = PHON("ˈmænɪdʒd ˈskeɪlɪŋ", "managed scaling")
BOOTSTRAP = PHON("ˈbutstræp", "bootstrap actions")
STEPS = PHON("stɛps", "steps")
DRIVER = PHON("ˈdraɪvɚ", "driver")
EXECUTORS = PHON("ɪɡˈzɛkjətɚz", "executors")
SHUFFLE = PHON("ˈʃʌfəl", "shuffle")
DATA_SKEW = PHON("ˈdeɪtə skju", "data skew")
SALTING = PHON("ˈsɔltɪŋ", "salting")
BROADCAST_JOIN = PHON("ˈbrɔdkæst dʒɔɪn", "broadcast join")
COALESCE = PHON("ˌkoʊəˈlɛs", "coalesce")
SMALL_FILES = PHON("smɔl faɪlz", "small files")
FLINK = PHON("flɪŋk", "Flink")
HIVE = PHON("haɪv", "Hive")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo nove: Amazon {SAY('EMR')} e Apache Spark. O {SAY('EMR')} "
            f"é o big data com controle total — e o Spark é o motor que a prova "
            f"espera que você entenda por dentro: partições, {SHUFFLE} e "
            f"{DATA_SKEW}."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Anatomia do cluster ----
    {
        "voice": "antonio",
        "text": (
            f"Anatomia do cluster. O nó primary coordena. Os {CORE_NODES} "
            f"processam E armazenam o {HDFS} — perder um core é perder dado "
            f"local. Os {TASK_NODES} só processam, sem storage — e por isso a "
            f"resposta clássica de custo é: {SPOT} nos {TASK_NODES}, on-demand "
            f"no primary e nos cores."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Use o {EMRFS} — dados no {SAY('S3')} — em vez de "
            f"{HDFS}, para desacoplar storage de compute. O padrão de custo: "
            f"clusters TRANSIENTES que sobem, processam e morrem, com "
            f"auto-terminate após o último step. {INSTANCE_FLEETS} misturam "
            f"tipos de instância e estratégias {SPOT}; {MANAGED_SCALING} ajusta "
            f"o cluster à carga; {BOOTSTRAP} instalam dependências na subida; e "
            f"{STEPS} submetem os trabalhos em sequência."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Variantes: {SAY('EMR')} Serverless — jobs Spark ou "
            f"{HIVE} sem dimensionar cluster nenhum; e {SAY('EMR')} on "
            f"{SAY('EKS')} — Spark no cluster Kubernetes existente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Spark essencial ----
    {
        "voice": "francisca",
        "text": (
            f"Spark essencial para a prova. O modelo: um {DRIVER} coordena "
            f"{EXECUTORS} que processam PARTIÇÕES em paralelo. Transformações "
            f"são lazy — só executam na ação. O vilão da performance é o "
            f"{SHUFFLE}: redistribuir dados entre {EXECUTORS} em joins e group "
            f"by. E o vilão do {SHUFFLE} é o {DATA_SKEW}: uma chave dominante "
            f"concentra tudo num executor — o job para em noventa e nove por "
            f"cento com um executor em out of memory."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} As mitigações que caem: {SALTING} — sufixo aleatório na "
            f"chave quente; {BROADCAST_JOIN} — a tabela pequena é copiada para "
            f"todos os {EXECUTORS} e o join vira operação local, sem {SHUFFLE}; "
            f"{COALESCE} ou repartition antes da escrita para evitar "
            f"{SMALL_FILES}; e cache apenas do que é reutilizado. No Glue valem "
            f"as mesmas ideias — mudam só os nomes."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Glue vs EMR vs Lambda ----
    {
        "voice": "antonio",
        "text": (
            f"A decisão dos trinta e quatro por cento — Glue versus {SAY('EMR')} "
            f"versus Lambda. '{SAY('ETL')} serverless integrado ao Catalog, "
            f"mínimo esforço': Glue. 'Controle do cluster, bibliotecas "
            f"customizadas, frameworks além do Spark — {HIVE}, Presto, HBase, "
            f"{FLINK}': {SAY('EMR')}. 'Jobs Spark esporádicos sem dimensionar "
            f"cluster': {SAY('EMR')} Serverless. 'Transformação leve, por "
            f"evento, menos de quinze minutos': Lambda. 'Migrar Hadoop "
            f"on-premises mantendo o ecossistema': {SAY('EMR')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: reduzir o custo de um cluster de processamento "
            f"noturno que tolera perda de nós?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SPOT} nos {TASK_NODES}, cluster transiente com dados no "
            f"{SAY('S3')} via {EMRFS}, terminando após o job."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: job Spark trava em noventa e nove por cento com um único "
            f"executor sobrecarregado. Diagnóstico e correção?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DATA_SKEW} — {SALTING} na chave quente, {BROADCAST_JOIN} se um "
            f"lado for pequeno, workers maiores. O Spark {SAY('UI')} mostra a "
            f"tarefa desproporcional."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: join de uma tabela de dois terabytes com uma dimensão de "
            f"vinte megabytes causando {SHUFFLE} gigante?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BROADCAST_JOIN} — replica a tabela pequena para todos os "
            f"{EXECUTORS}; o join vira local e o {SHUFFLE} desaparece."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo nove. No próximo, a computação além do "
            f"Spark: Lambda, {SAY('AWS')} Batch e contêineres. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
