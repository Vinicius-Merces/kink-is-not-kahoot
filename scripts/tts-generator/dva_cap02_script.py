"""Roteiro DVA-C02 Capitulo 2 — AWS Lambda a fundo."""

from glossary import SAY, EMPH, BRK, PHON

TMP = PHON("tɛmp", "/tmp")
LAYERS = PHON("ˈleɪɚz", "layers")
ALIAS = PHON("ˈeɪliəs", "alias")
VERSIONS = PHON("ˈvɜrʒənz", "versions")
LATEST = PHON("ˈleɪtɪst", "$LATEST")
DESTINATIONS = PHON("ˌdɛstəˈneɪʃənz", "Destinations")
DLQ = PHON("di ɛl kju", "DLQ")
RESERVED = PHON("rɪˈzɜrvd kənˈkɜrənsi", "Reserved Concurrency")
PROVISIONED = PHON("prəˈvɪʒənd kənˈkɜrənsi", "Provisioned Concurrency")
COLD_START = PHON("koʊld stɑrt", "cold start")
EXECUTION_ROLE = PHON("ˌɛksəˈkjuʃən ɹoʊl", "Execution Role")
RESOURCE_POLICY = PHON("ˈrisɔrs beɪst ˈpɑləsi", "resource-based policy")
EVENT_SOURCE_MAPPING = PHON("ɪˈvɛnt sɔrs ˈmæpɪŋ", "event source mapping")
BISECT = PHON("baɪˈsɛkt", "bisect")
CANARY = PHON("kəˈnɛri", "canário")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dois: {SAY('AWS')} Lambda a fundo — o serviço mais "
            f"cobrado do {SAY('DVA')}. Aqui caem os números, os três modos de "
            f"invocação, {VERSIONS} e {ALIAS}, e as duas concorrências."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Numeros ----
    {
        "voice": "antonio",
        "text": (
            f"Os números que caem na prova. Timeout máximo: QUINZE minutos — "
            f"tarefa mais longa vai para Fargate, Batch ou Step Functions. "
            f"Memória: de cento e vinte e oito megabytes a dez gigabytes — e "
            f"{SAY('CPU')} e rede escalam JUNTO com a memória; função lenta de "
            f"{SAY('CPU')}? Aumente a memória. {TMP}: de quinhentos e doze "
            f"megabytes a dez gigabytes de armazenamento efêmero."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Payload síncrono: seis megabytes — arquivo maior passa "
            f"pelo {SAY('S3')} com presigned {SAY('URL')}. Deploy em zip: "
            f"cinquenta megabytes direto, duzentos e cinquenta descomprimido — "
            f"maior que isso, imagem de container de até dez gigabytes, ou "
            f"{LAYERS}. E variáveis de ambiente: quatro kilobytes no total — "
            f"segredos grandes ficam no Secrets Manager."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Modos de invocacao ----
    {
        "voice": "francisca",
        "text": (
            f"Os três modos de invocação — e o que acontece no ERRO, que é o "
            f"que a prova pergunta. Modo síncrono — {SAY('API')} Gateway, "
            f"{SAY('ALB')}, chamada direta: o erro volta ao CHAMADOR; retry é "
            f"responsabilidade do cliente. Modo assíncrono — {SAY('S3')}, "
            f"{SAY('SNS')}, EventBridge: o Lambda tenta DOIS retries "
            f"automáticos e depois manda para a {DLQ} ou para os "
            f"{DESTINATIONS}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E o {EVENT_SOURCE_MAPPING} — {SAY('SQS')}, Kinesis, "
            f"{SAY('DynamoDB')} Streams: o Lambda faz polling e processa em "
            f"lotes; em streams, um lote com erro TRAVA o shard até resolver — "
            f"as defesas são {BISECT} batch on error, retry máximo e destino "
            f"on-failure. Identificar o modo de invocação é o primeiro passo de "
            f"metade das questões de Lambda."
        ),
    },
    {"voice": "francisca", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A armadilha {DESTINATIONS} versus {DLQ}: a {DLQ} "
            f"recebe só o evento que falhou. Os {DESTINATIONS} são mais ricos — "
            f"roteiam sucesso E falha, com o contexto completo de request e "
            f"response, para {SAY('SQS')}, {SAY('SNS')}, EventBridge ou outra "
            f"Lambda. 'Registro do resultado com detalhes do erro' = "
            f"{DESTINATIONS}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Versions e aliases ----
    {
        "voice": "antonio",
        "text": (
            f"{VERSIONS} e {ALIAS}. Publicar uma version congela código e "
            f"configuração — imutável e numerada; o {LATEST} é a versão mutável "
            f"de trabalho. O {ALIAS} é um ponteiro nomeado para uma version — "
            f"prod apontando para a quarenta e dois — e aceita PESOS de tráfego "
            f"entre duas versions: noventa por cento na atual, dez por cento na "
            f"nova — o deploy {CANARY}. O CodeDeploy automatiza esse shifting "
            f"com rollback automático por alarme do CloudWatch."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Concorrencia ----
    {
        "voice": "francisca",
        "text": (
            f"As duas concorrências — não confunda. {RESERVED}: reserva E "
            f"LIMITA o máximo de execuções simultâneas — protege um banco a "
            f"jusante; custo zero. {PROVISIONED}: mantém N ambientes "
            f"PRÉ-INICIALIZADOS — elimina {COLD_START} em {SAY('APIs')} "
            f"sensíveis a latência; tem custo por hora. 'Eliminar {COLD_START}' "
            f"= {PROVISIONED}; 'limitar para proteger o downstream' = "
            f"{RESERVED}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Lambda em {SAY('VPC')}: sem internet a menos que haja "
            f"NAT Gateway com rota — e para {SAY('S3')} e {SAY('DynamoDB')}, o "
            f"caminho barato é o Gateway {SAY('VPC')} Endpoint."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Layers e permissoes ----
    {
        "voice": "antonio",
        "text": (
            f"{LAYERS} empacotam dependências compartilhadas — até cinco por "
            f"função. E o par de permissões: a {EXECUTION_ROLE} é o que a "
            f"FUNÇÃO pode fazer — escrever no {SAY('DynamoDB')}; a "
            f"{RESOURCE_POLICY} é QUEM pode invocar a função — permitir que o "
            f"{SAY('S3')} de outra conta a invoque."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: função com processamento pesado de {SAY('CPU')} "
            f"está lenta — como acelerar sem mudar código?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"Aumentar a memória — {SAY('CPU')} e rede escalam proporcionalmente.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: {SAY('API')} de baixa latência sofre com {COLD_START} "
            f"nos picos?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{PROVISIONED} — ambientes pré-aquecidos. {RESERVED} limita "
            f"quantidade, mas NÃO elimina {COLD_START}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: o {SAY('S3')} invoca uma Lambda que falha às vezes; o "
            f"time quer capturar os eventos com contexto do erro?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Lambda {DESTINATIONS} on-failure — invocação do {SAY('S3')} é "
            f"assíncrona; após os dois retries, o evento vai com request e "
            f"response ao destino."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dois. No próximo, a porta de entrada das "
            f"suas {SAY('APIs')}: o Amazon {SAY('API')} Gateway. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
