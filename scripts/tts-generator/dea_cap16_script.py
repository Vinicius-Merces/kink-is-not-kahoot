"""Roteiro DEA-C01 Capitulo 16 — DynamoDB e outros data stores."""

from glossary import SAY, EMPH, BRK, PHON

TTL = PHON("ti ti ɛl", "TTL")
EXPORT_TO_S3 = PHON("ˈɛkspɔrt tu ɛs tri", "Export to S3")
ON_DEMAND = PHON("ɑn dɪˈmænd", "on-demand")
PROVISIONED = PHON("prəˈvɪʒənd", "provisioned")
HOT_PARTITION = PHON("hɑt pɑrˈtɪʃən", "hot partition")
FIREHOSE = PHON("ˈfaɪɚhoʊz", "Firehose")
OPENSEARCH = PHON("ˈoʊpənsɜrtʃ", "OpenSearch")
KEYSPACES = PHON("ˈkispeɪsɪz", "Keyspaces")
MEMORYDB = PHON("ˈmɛməri di bi", "MemoryDB")
ELASTICACHE = PHON("ɪˈlæstɪkæʃ", "ElastiCache")
DOCUMENTDB = PHON("ˈdɑkjəmɛnt di bi", "DocumentDB")
NEPTUNE = PHON("ˈnɛptun", "Neptune")
AWS_BACKUP = PHON("eɪ dabliu ɛs ˈbækʌp", "AWS Backup")
PITR = PHON("pi aɪ ti ɑr", "PITR")
STRONGLY = PHON("ˈstrɔŋli kənˈsɪstənt", "strongly consistent")
EVENTUALLY = PHON("ɪˈvɛntʃuəli kənˈsɪstənt", "eventually consistent")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dezesseis: {SAY('DynamoDB')} e os outros data stores — "
            f"sob a ótica do engenheiro de dados. Cada store tem um gatilho; "
            f"reconhecê-lo resolve a questão."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- DynamoDB em pipelines ----
    {
        "voice": "antonio",
        "text": (
            f"{SAY('DynamoDB')} em pipelines. Streams: o {SAY('CDC')} nativo — "
            f"Lambda processa cada mudança, event-driven. {EXPORT_TO_S3}: "
            f"exporta a tabela INTEIRA sem consumir capacidade — analise com "
            f"Athena sem impactar produção. {TTL}: expira itens automaticamente, "
            f"de graça — e os itens expirados aparecem nos Streams para "
            f"arquivar. Capacidade: {ON_DEMAND} para carga imprevisível, "
            f"{PROVISIONED} mais barato para carga estável. E a {HOT_PARTITION}: "
            f"chave quente causa throttling — os mesmos princípios do Kinesis."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Consistencia ----
    {
        "voice": "francisca",
        "text": (
            f"Consistência — tema apontado como difícil pelos candidatos. O "
            f"{SAY('S3')} hoje é {STRONGLY}: leu depois de escrever, vê o dado "
            f"novo. Já o {SAY('DynamoDB')} é {EVENTUALLY} POR PADRÃO — uma "
            f"leitura logo após a escrita pode vir desatualizada. Se precisar, "
            f"peça leitura {STRONGLY} — custa o dobro de {SAY('RCU')} e só "
            f"funciona na tabela base: os {SAY('GSIs')} são SEMPRE eventuais."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Mapa dos stores ----
    {
        "voice": "antonio",
        "text": (
            f"O mapa rápido dos demais stores. {OPENSEARCH}: busca full-text e "
            f"análise de logs em near real-time, com o {FIREHOSE} entregando — e "
            f"a versão Serverless para não dimensionar cluster. {SAY('RDS')} e "
            f"Aurora: a fonte transacional dos pipelines — origem de "
            f"{SAY('DMS')}, federated queries e zero {SAY('ETL')}. "
            f"{DOCUMENTDB}: documentos {SAY('JSON')}, compatível com MongoDB. "
            f"{KEYSPACES}: compatível com Cassandra — 'migrar workload "
            f"Cassandra sem gerenciar cluster'."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {MEMORYDB} e {ELASTICACHE}: in-memory Redis — o "
            f"{MEMORYDB} é durável, serve de store primário; o {ELASTICACHE} é "
            f"CACHE na frente de outro banco. {NEPTUNE}: grafos — 'detecção de "
            f"fraude por conexões'. E atenção: o Timestream está FORA do escopo "
            f"— série temporal na prova se resolve com {SAY('DynamoDB')} com "
            f"{TTL}, {SAY('S3')} particionado por data, ou {OPENSEARCH}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- AWS Backup ----
    {
        "voice": "francisca",
        "text": (
            f"Proteção dos stores: o {AWS_BACKUP} centraliza backup de "
            f"{SAY('RDS')}, {SAY('DynamoDB')}, {SAY('EFS')}, {SAY('EBS')} e "
            f"{SAY('S3')} com planos de agenda e retenção — 'política de backup "
            f"unificada e auditável, sem scripts por serviço'. O Vault Lock dá "
            f"imutabilidade aos backups. Complementa os nativos: {PITR} do "
            f"{SAY('DynamoDB')}, snapshots do {SAY('RDS')} e versionamento do "
            f"{SAY('S3')}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: analisar com {SAY('SQL')} uma tabela "
            f"{SAY('DynamoDB')} de produção sem impactar a performance dela?"
            f"{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{EXPORT_TO_S3} — não consome capacidade — mais Athena sobre o "
            f"export. Para análise contínua: Streams para {FIREHOSE} para "
            f"{SAY('S3')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: logs de aplicação precisam de busca por texto livre e "
            f"dashboards em tempo quase real?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{FIREHOSE} entregando no {OPENSEARCH}, com {OPENSEARCH} Dashboards "
            f"para visualizar."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: logo após gravar no {SAY('DynamoDB')}, uma leitura via "
            f"{SAY('GSI')} vem desatualizada. Por quê?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('GSIs')} são sempre {EVENTUALLY} — leitura {STRONGLY} só "
            f"existe na tabela base, custando o dobro."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dezesseis. No próximo e último, a tabela "
            f"mestre de decisão — o resumo de metade do exame. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
