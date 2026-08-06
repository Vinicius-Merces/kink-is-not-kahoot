"""Roteiro DEA-C01 Capitulo 17 — Tabela mestre de decisao."""

from glossary import SAY, EMPH, BRK, PHON

FIREHOSE = PHON("ˈfaɪɚhoʊz", "Firehose")
KDS = PHON("kɪˈnisɪs ˈdeɪtə strimz", "Kinesis Data Streams")
MSK = PHON("ɛm ɛs keɪ", "MSK")
FLINK = PHON("flɪŋk", "Flink")
DMS = PHON("di ɛm ɛs", "DMS")
DATASYNC = PHON("ˈdeɪtəsɪŋk", "DataSync")
APPFLOW = PHON("ˈæpfloʊ", "AppFlow")
ZERO_ETL = PHON("ˈzɪroʊ i ti ɛl", "zero-ETL")
STEP_FUNCTIONS = PHON("stɛp ˈfʌŋkʃənz", "Step Functions")
MWAA = PHON("ɛm dabliu eɪ eɪ", "MWAA")
LAKE_FORMATION = PHON("leɪk fɔrˈmeɪʃən", "Lake Formation")
MACIE = PHON("ˈmeɪsi", "Macie")
DATA_QUALITY = PHON("ˈdeɪtə ˈkwɑləti", "Data Quality")
ICEBERG = PHON("ˈaɪsbɜrɡ", "Iceberg")
DATABREW = PHON("ˈdeɪtəbru", "DataBrew")
PARQUET = PHON("ˈpɑrkɛt", "Parquet")
SPECTRUM = PHON("ˈspɛktrəm", "Spectrum")
JOB_BOOKMARKS = PHON("dʒɑb ˈbʊkmɑrks", "Job Bookmarks")
DATA_API = PHON("ˈdeɪtə eɪ pi aɪ", "Data API")
SPICE = PHON("spaɪs", "SPICE")
DISTRIBUTED_MAP = PHON("dɪˈstrɪbjətɪd mæp", "Distributed Map")
SCHEMA_REGISTRY = PHON("ˈskimə ˈrɛdʒɪstri", "Schema Registry")
SAM = PHON("sæm", "SAM")
CDK = PHON("si di keɪ", "CDK")
CLOUDTRAIL_LAKE = PHON("klaʊd treɪl leɪk", "CloudTrail Lake")
EXPORT_TO_S3 = PHON("ˈɛkspɔrt tu ɛs tri", "Export to S3")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dezessete: a tabela mestre de decisão — o resumo que vale "
            f"metade do exame. Na última semana, revise este capítulo "
            f"diariamente até responder cada linha de memória. Vamos lá."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Bloco streaming/ETL ----
    {
        "voice": "antonio",
        "text": (
            f"Streaming em tempo real, múltiplos consumidores, replay: {KDS}. "
            f"'Só entregar o stream no {SAY('S3')} sem gerenciar nada': "
            f"{FIREHOSE}. Já usa Kafka: {MSK}. Agregações por janela sobre o "
            f"stream: Managed {FLINK}. {SAY('ETL')} serverless integrado ao "
            f"catálogo: Glue. Big data com controle do cluster: {SAY('EMR')}. "
            f"Transformação leve por evento, menos de quinze minutos: Lambda. "
            f"Job containerizado de horas com fila e Spot: {SAY('AWS')} Batch."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},

    # ---- Bloco consulta/warehouse ----
    {
        "voice": "francisca",
        "text": (
            f"{SAY('SQL')} ad-hoc direto no {SAY('S3')}, pago por scan: Athena. "
            f"Data warehouse com {SAY('BI')} pesado: Redshift. Consultar o "
            f"{SAY('S3')} a partir do Redshift sem carregar: {SPECTRUM}. Rodar "
            f"{SAY('SQL')} no Redshift a partir de Lambda sem driver: "
            f"{DATA_API}. Dashboard rápido sem re-escanear a fonte: QuickSight "
            f"{SPICE}. Update e delete em registros no data lake: {ICEBERG}. "
            f"Otimizar custo de consulta no {SAY('S3')}: {PARQUET} mais partição "
            f"mais compressão — sempre."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Bloco ingestao/migracao ----
    {
        "voice": "antonio",
        "text": (
            f"Migrar ou replicar banco de dados com {SAY('CDC')}: {DMS}. "
            f"Arquivos {SAY('NFS')} on-premises para o {SAY('S3')}: {DATASYNC}. "
            f"Dados de SaaS como Salesforce: {APPFLOW}. Aurora para Redshift sem "
            f"pipeline: {ZERO_ETL}. Processar apenas dados novos a cada "
            f"execução: {JOB_BOOKMARKS}. Schema incompatível não pode quebrar "
            f"consumers: {SCHEMA_REGISTRY}."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},

    # ---- Bloco orquestracao/operacao ----
    {
        "voice": "francisca",
        "text": (
            f"Workflow serverless com retry e tratamento de erro: "
            f"{STEP_FUNCTIONS}. Time já usa Airflow: {MWAA}. Agendar ou reagir a "
            f"evento: EventBridge. Milhões de objetos em paralelo orquestrado: "
            f"{DISTRIBUTED_MAP}. Validar qualidade no pipeline: Glue "
            f"{DATA_QUALITY}. Limpeza visual sem código: {DATABREW}. Deploy "
            f"repetível de pipeline serverless: {SAM}, {CDK} ou CloudFormation."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Bloco seguranca ----
    {
        "voice": "antonio",
        "text": (
            f"Permissões por coluna ou linha no lake: {LAKE_FORMATION}. Achar "
            f"{SAY('PII')} no {SAY('S3')}: {MACIE}. Mascarar coluna sensível na "
            f"consulta: dynamic data masking do Redshift ou célula do "
            f"{LAKE_FORMATION}. Consultar auditoria de várias contas com "
            f"{SAY('SQL')}: {CLOUDTRAIL_LAKE}. Registros que falham no consumo "
            f"do stream: on-failure destination com bisect batch. E tabela "
            f"{SAY('DynamoDB')} analisada sem consumir capacidade: "
            f"{EXPORT_TO_S3} mais Athena."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Estrategia de prova ----
    {
        "voice": "francisca",
        "text": (
            f"A estratégia para o dia da prova. Leia a ÚLTIMA frase do enunciado "
            f"primeiro — 'menor custo?', 'menor esforço operacional?' — ela "
            f"define a resposta antes do cenário. Least operational overhead "
            f"significa serverless e gerenciado: Glue acima de {SAY('EMR')}, "
            f"{FIREHOSE} acima de streams, Serverless acima de cluster. Most "
            f"cost-effective em consulta significa formato e partição — antes de "
            f"trocar de serviço, otimize o dado."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Mais de dois minutos e meio numa questão: marque e "
            f"siga — quinze questões são experimentais e não valem nota. E nunca "
            f"deixe em branco: não há penalidade por erro."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint final ----
    {
        "voice": "francisca",
        "text": (
            f"Última revisão da trilha. Primeira: cliques de site devem cair no "
            f"{SAY('S3')} em {PARQUET}, sem administração e com uns sessenta "
            f"segundos de atraso aceitável?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{FIREHOSE} com conversão nativa para {PARQUET} — entrega gerenciada.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: analistas precisam de permissão por coluna numa tabela do "
            f"lake, valendo no Athena E no Redshift {SPECTRUM}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{LAKE_FORMATION} column-level security — uma política central para "
            f"todos os motores de consulta."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: duas alternativas resolvem o problema tecnicamente. Qual "
            f"critério desempata no {SAY('DEA')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O requisito não-funcional explícito: menor custo, menor esforço, "
            f"menor latência. Na dúvida, gerenciado vence autogerenciado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Parabéns — você chegou ao fim da trilha {SAY('DEA')} dash C zero "
            f"um! Você tem os serviços, os padrões, as armadilhas e o método. "
            f"Meta antes de agendar: oitenta por cento ou mais em simulados "
            f"inéditos, de forma consistente. Agora é hora do simulado completo. "
            f"Boa prova!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
