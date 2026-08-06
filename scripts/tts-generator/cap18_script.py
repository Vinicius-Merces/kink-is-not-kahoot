"""Roteiro tratado do Capitulo 18 (Machine Learning e IA na AWS) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

SAGEMAKER = PHON("seɪdʒˈmeɪkɚ", "SageMaker")
BEDROCK = PHON("ˈbɛdrɑk", "Bedrock")
REAL_TIME_ENDPOINT = PHON("ril taɪm ˈɛndpɔɪnt", "Real-time endpoint")
SERVERLESS_INFERENCE = PHON("ˈsɜrvɚlɛs ˈɪnfərəns", "Serverless Inference")
ASYNC_INFERENCE = PHON("ˈeɪsɪŋk ˈɪnfərəns", "Async Inference")
BATCH_TRANSFORM = PHON("bætʃ trænsˈfɔrm", "Batch Transform")
COLD_START = PHON("koʊld stɑrt", "cold start")
SAGEMAKER_STUDIO = PHON("seɪdʒˈmeɪkɚ ˈstudioʊ", "SageMaker Studio")
TRAINING_JOBS = PHON("ˈtreɪnɪŋ dʒɑbz", "Training Jobs")
SAGEMAKER_ENDPOINTS = PHON("seɪdʒˈmeɪkɚ ˈɛndpɔɪnts", "SageMaker Endpoints")
SAGEMAKER_PIPELINES = PHON("seɪdʒˈmeɪkɚ ˈpaɪplaɪnz", "SageMaker Pipelines")
FOUNDATION_MODELS = PHON("faʊnˈdeɪʃən ˈmɑdəlz", "foundation models")
RAG = PHON("ɹæɡ", "RAG")
RETRIEVAL_AUGMENTED_GENERATION = PHON("rɪˈtrivəl ɔɡˈmɛntɪd ˌdʒɛnəˈreɪʃən", "Retrieval-Augmented Generation")
KNOWLEDGE_BASE = PHON("ˈnɑlɪdʒ beɪs", "Knowledge Base")
FINE_TUNING = PHON("faɪn ˈtunɪŋ", "fine-tuning")
REKOGNITION = PHON("ˌrɛkəɡˈnɪʃən", "Rekognition")
TEXTRACT = PHON("ˈtɛkstrækt", "Textract")
COMPREHEND = PHON("ˌkɑmprɪˈhɛnd", "Comprehend")
TRANSCRIBE = PHON("trænˈskraɪb", "Transcribe")
POLLY = PHON("ˈpɑli", "Polly")
TRANSLATE = PHON("trænsˈleɪt", "Translate")
LEX = PHON("lɛks", "Lex")
KENDRA = PHON("ˈkɛndrə", "Kendra")
FORECAST = PHON("ˈfɔrkæst", "Forecast")
PERSONALIZE = PHON("ˈpɜrsənəlaɪz", "Personalize")
PII = PHON("pi aɪ aɪ", "PII")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dezoito: machine learning e inteligência artificial "
            f"na {SAY('AWS')}. A prova não pede para você treinar modelos "
            f"— pede para você escolher o serviço certo entre três níveis "
            f"de abstração. Errar o nível é o erro mais comum nessas "
            f"questões."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- 3 niveis ----
    {
        "voice": "antonio",
        "text": (
            f"O primeiro nível são os serviços de I A pré-treinados: "
            f"extrair texto de uma imagem, detectar sentimento de um "
            f"comentário, transcrever um áudio — tarefa específica, sem "
            f"necessidade de dados próprios de treino."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O segundo nível é o Amazon {BEDROCK}: gerar "
            f"texto, resumos ou respostas com I A generativa, ou um "
            f"{SAY('chatbot')} que responde com base nos documentos da "
            f"empresa — usa {FOUNDATION_MODELS}, como Claude ou Titan, sem "
            f"gerenciar infraestrutura de G P U."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o terceiro nível é o Amazon {SAGEMAKER}: "
            f"treinar um modelo customizado com seus próprios dados, "
            f"modelo proprietário, controle total do ciclo de vida de "
            f"machine learning."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- SageMaker inference ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre os tipos de inferência do {SAGEMAKER}: o "
            f"{REAL_TIME_ENDPOINT} dá resposta em milissegundos, para "
            f"tráfego sustentado — fica sempre ativo, cobrado por hora da "
            f"instância."
            f"{BRK(300)} {SERVERLESS_INFERENCE} é para tráfego intermitente "
            f"ou imprevisível — escala a zero, paga por uso, mas tem "
            f"{COLD_START}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {ASYNC_INFERENCE} é para {SAY('payloads')} "
            f"grandes, até um gigabyte, ou processamento de minutos — "
            f"enfileira a requisição e notifica via S N S quando o "
            f"resultado fica pronto."
            f"{BRK(300)} E {BATCH_TRANSFORM} faz inferência em lote sobre "
            f"um conjunto de dados inteiro no {SAY('S3')}, sem "
            f"{SAY('endpoint')} persistente."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} {SAGEMAKER} em uma frase por etapa: "
            f"{SAGEMAKER_STUDIO} é o ambiente de desenvolvimento. "
            f"{SAGEMAKER} {TRAINING_JOBS} treina o modelo em instâncias "
            f"efêmeras, sem pagar por instâncias ociosas. "
            f"{SAGEMAKER_ENDPOINTS} hospedam o modelo treinado para "
            f"inferência. E {SAGEMAKER_PIPELINES} orquestram o fluxo "
            f"completo de M L Ops — análogo ao Step Functions, mas para "
            f"machine learning."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Bedrock e RAG ----
    {
        "voice": "francisca",
        "text": (
            f"O {BEDROCK} dá acesso via A P I a {FOUNDATION_MODELS} de "
            f"múltiplos provedores — Anthropic, Meta, Amazon Titan — sem "
            f"provisionar G P U. O padrão mais cobrado é o {RAG}, "
            f"{RETRIEVAL_AUGMENTED_GENERATION}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A pergunta do usuário não vai direto para o "
            f"modelo — primeiro, uma {KNOWLEDGE_BASE} do {BEDROCK} busca "
            f"contexto relevante nos seus documentos, usando busca "
            f"vetorial sobre {SAY('S3')} e {SAY('OpenSearch')} ou "
            f"{SAY('Aurora')} com {SAY('pgvector')}. Só então o "
            f"{SAY('foundation model')} recebe a pergunta {EMPH('mais')} os "
            f"trechos recuperados, gerando uma resposta fundamentada nos "
            f"{EMPH('seus')} dados, sem precisar re-treinar o modelo."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} {RAG} contra {FINE_TUNING}: se o enunciado diz "
            f"que as respostas devem refletir documentos internos "
            f"atualizados frequentemente, é {RAG}, com {KNOWLEDGE_BASE}s "
            f"do {BEDROCK}, porque os dados ficam fora do modelo e são "
            f"buscados em tempo real. {FINE_TUNING}, treinar o modelo com "
            f"dados próprios, é mais caro e mais lento de atualizar — "
            f"raramente é a resposta certa quando a palavra-chave é "
            f"atualizado ou dinâmico."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Zoologico de IA ----
    {
        "voice": "francisca",
        "text": (
            f"Agora o zoológico de serviços de I A pré-treinados."
            f"{BRK(300)} {REKOGNITION}: análise de imagens e vídeos — "
            f"detecção de objetos, faces, texto em imagens, moderação de "
            f"conteúdo."
            f"{BRK(300)} {TEXTRACT}: O C R estruturado — extrai texto, "
            f"tabelas e pares chave-valor de documentos escaneados."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {COMPREHEND}: processamento de linguagem natural "
            f"— sentimento, entidades, frases-chave e {PII} em "
            f"{EMPH('texto')}, não em imagens."
            f"{BRK(300)} {TRANSCRIBE}: fala para texto, com suporte a "
            f"múltiplos locutores. {POLLY}: texto para fala, com vozes "
            f"neurais. {TRANSLATE}: tradução entre idiomas."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {LEX}: motor de {SAY('chatbots')} e "
            f"{SAY('voicebots')}, entendendo intenção e extraindo "
            f"parâmetros — o cérebro por trás de assistentes "
            f"conversacionais."
            f"{BRK(300)} {KENDRA}: busca empresarial inteligente, "
            f"indexando documentos de várias fontes e respondendo "
            f"perguntas em linguagem natural."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {FORECAST}: previsão de séries temporais — "
            f"demanda, estoque, tráfego — usando aprendizado de máquina. E "
            f"{PERSONALIZE}: recomendações em tempo real, a mesma "
            f"tecnologia usada pela {SAY('Amazon.com')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Armadilha de confusão entre serviços parecidos: "
            f"{TEXTRACT} é diferente de {COMPREHEND} — {TEXTRACT} lê "
            f"documentos e extrai texto e estrutura; {COMPREHEND} analisa "
            f"texto que já está em formato texto, incluindo o que o "
            f"{TEXTRACT} extraiu. Um {SAY('pipeline')} comum é "
            f"{TEXTRACT} seguido de {COMPREHEND}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {POLLY} é diferente de {TRANSCRIBE} — {POLLY} "
            f"fala, de texto para áudio; {TRANSCRIBE} escuta, de áudio "
            f"para texto — direções opostas. E {REKOGNITION} é diferente "
            f"de {TEXTRACT} — {REKOGNITION} entende o que tem na imagem, "
            f"objetos e faces; {TEXTRACT} entende o que está escrito, de "
            f"forma estruturada."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório de uma hora, no Free "
            f"Tier, onde você cria um {SAY('pipeline')}: um {SAY('trigger')} "
            f"de {SAY('upload')} no {SAY('S3')} chama uma Lambda, que usa "
            f"{TEXTRACT} para extrair texto de uma imagem, e depois "
            f"{COMPREHEND} para analisar o sentimento, gravando o "
            f"resultado no {SAY('DynamoDB')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (5 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: uma aplicação precisa extrair o "
            f"valor total e a data de notas fiscais escaneadas. Qual "
            f"serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Amazon {TEXTRACT} — O C R estruturado, que extrai pares "
            f"chave-valor e tabelas de formulários, não apenas texto "
            f"corrido."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: a empresa quer um {SAY('chatbot')} que responda "
            f"perguntas com base no manual de produtos, atualizado "
            f"mensalmente, sem re-treinar nenhum modelo. Qual a "
            f"abordagem?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Amazon {BEDROCK} com {KNOWLEDGE_BASE}s, ou seja, {RAG} — o "
            f"manual é indexado e consultado em tempo real a cada "
            f"pergunta, sem precisar re-treinar o modelo quando ele muda."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: a equipe de dados quer treinar um modelo "
            f"proprietário de detecção de fraude com anos de dados "
            f"históricos da empresa. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Amazon {SAGEMAKER} — controle total do ciclo de vida: "
            f"preparação de dados, treino, ajuste fino e {SAY('deploy')}, "
            f"para um modelo customizado treinado com dados próprios."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: um modelo de M L é consultado raramente, e manter "
            f"um {SAY('endpoint')} ligado o tempo todo está custando caro "
            f"sem necessidade. Qual tipo de inferência reduz esse "
            f"custo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SERVERLESS_INFERENCE} — escala a zero quando não há "
            f"tráfego, cobrando apenas pelo tempo de computação usado, "
            f"aceitando um {COLD_START} adicional na primeira chamada após "
            f"período ocioso."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: um {SAY('call center')} quer transcrever as "
            f"chamadas e depois identificar o sentimento do cliente. "
            f"Quais dois serviços, em que ordem?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Amazon {TRANSCRIBE} primeiro, de áudio para texto, depois "
            f"Amazon {COMPREHEND} sobre o texto resultante, para análise "
            f"de sentimento — {COMPREHEND} não processa áudio diretamente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dezoito. No próximo, vamos falar de "
            f"A W S Organizations e governança multi-conta. Até a "
            f"próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
