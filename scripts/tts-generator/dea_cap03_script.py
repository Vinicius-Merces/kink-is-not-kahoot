"""Roteiro DEA-C01 Capitulo 3 — Ingestão batch e migração de dados."""

from glossary import SAY, EMPH, BRK, PHON

DMS = PHON("di ɛm ɛs", "DMS")
DATASYNC = PHON("ˈdeɪtəsɪŋk", "DataSync")
APPFLOW = PHON("ˈæpfloʊ", "AppFlow")
TRANSFER_FAMILY = PHON("ˈtrænsfɚ ˈfæməli", "Transfer Family")
SNOWBALL = PHON("ˈsnoʊbɔl", "Snowball")
CDC = PHON("si di si", "CDC")
SCT = PHON("ɛs si ti", "SCT")
FULL_LOAD = PHON("fʊl loʊd", "full load")
ZERO_ETL = PHON("ˈzɪroʊ i ti ɛl", "zero-ETL")
MULTIPART = PHON("ˈmʌltipɑrt", "multipart upload")
BATCH_OPERATIONS = PHON("bætʃ ˌɑpəˈreɪʃənz", "Batch Operations")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo três: ingestão batch e migração de dados. A pergunta "
            f"central deste capítulo é simples — de onde vem o dado? A origem "
            f"determina o serviço, e a questão sempre revela a origem."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Tabela de decisao por origem ----
    {
        "voice": "antonio",
        "text": (
            f"A tabela de decisão por origem. Banco de dados relacional — "
            f"contínuo ou pontual: {DMS}, com {CDC} para replicação contínua. "
            f"Arquivos {SAY('NFS')} ou {SAY('SMB')} on-premises indo para o "
            f"{SAY('S3')}: {DATASYNC} — agendável, com verificação de "
            f"integridade e controle de banda. Aplicações SaaS como Salesforce "
            f"ou {SAY('SAP')}: {APPFLOW} — conectores prontos, sem código."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Parceiros enviando arquivos por {SAY('SFTP')}: "
            f"{TRANSFER_FAMILY} — {SAY('SFTP')} gerenciado sobre o {SAY('S3')}. "
            f"Volumes enormes com rede lenta: família Snow — a regra prática é "
            f"que mais de uma semana pela rede leva ao {SNOWBALL}. E Aurora "
            f"indo para o Redshift sem construir pipeline: integração "
            f"{ZERO_ETL} — replicação contínua gerenciada pela {SAY('AWS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"A pegadinha de classificação: {DMS} é para BANCOS de dados — "
            f"linhas e tabelas, com {CDC}. {DATASYNC} é para ARQUIVOS. "
            f"{APPFLOW} é para SaaS. Basta classificar a origem e a resposta "
            f"aparece."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- DMS a fundo ----
    {
        "voice": "antonio",
        "text": (
            f"{DMS} a fundo. Uma instância de replicação executa tasks entre um "
            f"endpoint de origem e um de destino. Três modos: {FULL_LOAD}, cópia "
            f"única; {FULL_LOAD} mais {CDC}, a migração sem downtime — copia "
            f"tudo e depois replica as mudanças; e {CDC} only, replicação "
            f"contínua. O {CDC} lê o log de transações do banco — binlog, "
            f"{SAY('WAL')}, redo log."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Migração homogênea, Oracle para Oracle, não precisa de "
            f"conversão. Heterogênea, Oracle para PostgreSQL, exige o {SCT} — "
            f"Schema Conversion Tool — antes, para converter schema e "
            f"procedures. Com destino {SAY('S3')}, o {DMS} grava arquivos com "
            f"uma coluna de operação: insert, update ou delete — para "
            f"materializar o estado final no lake, use um formato transacional "
            f"como Iceberg. E existe o {DMS} Serverless: capacidade automática, "
            f"sem dimensionar instância."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- S3 como porta de entrada ----
    {
        "voice": "francisca",
        "text": (
            f"O {SAY('S3')} como porta de entrada tem três recursos de ingestão "
            f"que caem em prova. {SAY('S3')} Event Notifications disparando "
            f"EventBridge, {SAY('SQS')} ou Lambda: o padrão 'chegou arquivo, "
            f"dispara pipeline'. {MULTIPART} para arquivos grandes — obrigatório "
            f"acima de cinco gigabytes. E {SAY('S3')} {BATCH_OPERATIONS}: aplicar "
            f"uma operação sobre BILHÕES de objetos já existentes — copiar, "
            f"etiquetar ou invocar uma Lambda por objeto."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Agendado vs orientado a evento ----
    {
        "voice": "antonio",
        "text": (
            f"Batch agendado versus orientado a evento. Agendado: EventBridge "
            f"Scheduler dispara o job às duas da manhã — simples, mas se o "
            f"arquivo atrasar, o job roda no vazio. Orientado a evento: o "
            f"{SAY('S3')} notifica quando o arquivo chega — processa na hora. "
            f"A prova favorece evento quando diz 'assim que os dados chegarem' "
            f"ou 'horário imprevisível'; e agenda quando há consolidação diária."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: replicar continuamente um PostgreSQL "
            f"on-premises para o {SAY('S3')}, capturando cada mudança?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DMS} com {CDC} e destino {SAY('S3')} — {FULL_LOAD} inicial mais "
            f"replicação contínua."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: trazer dados do Salesforce para o {SAY('S3')} toda noite, "
            f"sem escrever código?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{APPFLOW} — conector nativo do Salesforce, agendamento e "
            f"mapeamento de campos sem código."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: dados do Aurora precisam aparecer no Redshift 'sem "
            f"construir e manter pipeline'?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Integração {ZERO_ETL} Aurora Redshift — replicação contínua "
            f"gerenciada, sem Glue nem {DMS}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo três. No próximo, o coração do exame: "
            f"{SAY('AWS')} Glue. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
