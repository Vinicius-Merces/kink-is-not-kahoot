"""Roteiro tratado do Capitulo 8 (Computacao serverless) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON, COLD_START, PROVISIONED_CONCURRENCY

TIMEOUT = PHON("ˈtaɪmaʊt", "timeout")
CONCURRENCY = PHON("kənˈkɜrənsi", "concurrency")
RESERVED_CONCURRENCY = PHON("rɪˈzɜrvd kənˈkɜrənsi", "Reserved Concurrency")
PAYLOAD = PHON("ˈpeɪloʊd", "payload")
FUNCTION_URLS = PHON("ˈfʌŋkʃən ˌjuˈɑrˈɛlz", "Function URLs")
SNAPSTART = PHON("snæpstɑrt", "SnapStart")
EVENT_SOURCE_MAPPING = PHON("ɪˈvɛnt sɔrs ˈmæpɪŋ", "Event Source Mapping")
LAMBDA_DESTINATIONS = PHON("ˈlæmdə ˌdɛstəˈneɪʃənz", "Lambda Destinations")
BISECT_ON_ERROR = PHON("baɪˈsɛkt ɑn ˈɛrɚ", "bisect on error")
LAYERS = PHON("ˈleɪɚz", "Layers")
APP_RUNNER = PHON("æp ˈrʌnɚ", "App Runner")
AWS_BATCH = PHON("eɪ dʌbəlju ɛs bætʃ", "AWS Batch")
RUNTIME = PHON("ˈrʌntaɪm", "runtime")
WEBSOCKET = PHON("wɛb ˈsɑkɪt", "WebSocket")
SIDECAR_LOCAL = PHON("ˈsaɪdkɑr", "sidecar")
MAX_RECEIVE_COUNT = PHON("mæks rɪˈsiv kaʊnt", "maxReceiveCount")
REDRIVE_POLICY = PHON("riˈdraɪv ˈpɑləsi", "redrive policy")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo oito: computação serverless. Na prova, serverless é "
            f"sinônimo de menor esforço operacional. Quando o enunciado fala "
            f"em sem servidores para gerenciar, ou sem provisionar "
            f"infraestrutura, o leque de respostas se reduz quase sempre a "
            f"Lambda, Fargate, ou um serviço totalmente gerenciado."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Lambda limites ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos pelos limites e padrões do Lambda."
            f"{BRK(300)} O {TIMEOUT} máximo é de quinze minutos — tarefa mais "
            f"longa exige Fargate, Batch ou Step Functions. A memória vai de "
            f"cento e vinte e oito megabytes a dez gigabytes, e a C P U escala "
            f"junto com ela — se o app está lento por C P U, aumente a "
            f"memória, não só o {TIMEOUT}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {COLD_START} acontece na primeira invocação, ou "
            f"depois de um período ocioso, quando o ambiente precisa "
            f"inicializar o runtime e o código — para latência consistente, "
            f"use {PROVISIONED_CONCURRENCY}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Lambda dentro de uma {SAY('VPC')} é necessário para "
            f"acessar {SAY('RDS')} ou ElastiCache privados. Para acessar a "
            f"internet de dentro da {SAY('VPC')}, ainda precisa de um N A T "
            f"{SAY('Gateway')}."
            f"{BRK(400)} A {CONCURRENCY} tem limite de mil execuções "
            f"simultâneas por conta, podendo ser aumentado. {RESERVED_CONCURRENCY} "
            f"garante, e limita, capacidade para uma função específica."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {PAYLOAD} síncrono tem limite de seis megabytes; "
            f"assíncrono, via S Q S ou S N S, duzentos e cinquenta e seis "
            f"kilobytes; e dez megabytes para {FUNCTION_URLS} com streaming. E "
            f"o diretório temporário, barra tmp, vai de quinhentos e doze "
            f"megabytes a dez gigabytes — efêmero, não persiste entre "
            f"invocações, exceto se o mesmo ambiente continuar quente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- SnapStart ----
    {
        "voice": "francisca",
        "text": (
            f"Para runtimes como Java, que historicamente têm "
            f"{COLD_START}s lentos, o {SNAPSTART} tira um snapshot do "
            f"ambiente já inicializado, depois que o código de inicialização "
            f"roda, e o restaura em invocações seguintes — reduzindo o "
            f"{COLD_START} de segundos para milissegundos, {EMPH('sem o custo extra')} "
            f"do {PROVISIONED_CONCURRENCY}, que mantém ambientes quentes o "
            f"tempo todo."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Event Source Mappings ----
    {
        "voice": "antonio",
        "text": (
            f"O Lambda pode ser invocado de três formas, e isso muda o "
            f"tratamento de erro."
            f"{BRK(300)} No modelo síncrono — API Gateway, {SAY('ALB')}, "
            f"{FUNCTION_URLS} — o erro retorna direto ao chamador, sem retry "
            f"automático."
            f"{BRK(300)} No modelo assíncrono — eventos do {SAY('S3')}, S N S, "
            f"EventBridge — há retry automático duas vezes, e depois vai para "
            f"uma D L Q ou para {LAMBDA_DESTINATIONS}, se configurado."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} E no modelo de {EVENT_SOURCE_MAPPING} — S Q S, "
            f"Kinesis, {SAY('DynamoDB')} Streams — o próprio serviço Lambda "
            f"faz o polling da fonte. Em caso de erro, a mensagem permanece na "
            f"fonte para nova tentativa, configurável com {BISECT_ON_ERROR} e "
            f"número máximo de tentativas."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {LAMBDA_DESTINATIONS} permitem rotear o resultado, "
            f"sucesso ou falha, de uma invocação assíncrona para outro "
            f"destino — S Q S, S N S, EventBridge, outra Lambda — sem precisar "
            f"escrever código de tratamento. Útil para orquestração leve sem "
            f"precisar de Step Functions."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} O padrão típico de orquestração serverless da prova: "
            f"API Gateway chama uma Lambda para validar e transformar a "
            f"requisição, que então inicia uma Step Functions, que por sua vez "
            f"grava o resultado em {SAY('DynamoDB')}, S Q S ou {SAY('S3')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Uma armadilha importante: colocar uma Lambda dentro "
            f"de uma {SAY('VPC')} dá acesso a recursos privados, como o "
            f"{SAY('RDS')}, mas {EMPH('remove')} o acesso direto à internet "
            f"que ela tinha por padrão fora da {SAY('VPC')}. Se essa Lambda "
            f"também precisa chamar uma A P I externa, é necessário um N A T "
            f"{SAY('Gateway')} — um custo adicional que o enunciado pode "
            f"estar tentando evitar com uma resposta mais simples, como um "
            f"{SAY('VPC')} Endpoint, se o destino for um serviço da "
            f"{SAY('AWS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Layers e Function URLs ----
    {
        "voice": "francisca",
        "text": (
            f"As {LAYERS} empacotam dependências compartilhadas entre "
            f"múltiplas funções, separadas do código principal — reduz "
            f"duplicação e acelera deploys, já que o código muda, mas a layer "
            f"com dependências pesadas não."
            f"{BRK(400)} {FUNCTION_URLS} dão a uma Lambda um {SAY('endpoint')} "
            f"H T T P S dedicado, sem precisar de API Gateway — mais simples "
            f"para um webhook único, mas sem os recursos de gerenciamento de "
            f"A P I, como throttling avançado e chaves de uso."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Decisao de containers ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre containers — vamos ver com mais detalhe no capítulo "
            f"catorze, mas a visão geral é essa."
            f"{BRK(300)} Containers, sem gerenciar servidores: {SAY('ECS')} "
            f"mais Fargate. Time que já usa Kubernetes, evitando "
            f"{SAY('lock-in')}: {SAY('EKS')}. Containers Kubernetes sem "
            f"gerenciar nós: {SAY('EKS')} mais Fargate."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Só quer fazer deploy de um container web: "
            f"{APP_RUNNER}. Registro de imagens privado: {SAY('ECR')}. E job "
            f"de lote longo, containerizado, sem gerenciar fila ou instância: "
            f"{AWS_BATCH} sobre Fargate."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Sinal prático: um job de processamento longo, de "
            f"quarenta e cinco minutos, em container, sem gerenciar servidor, "
            f"é {AWS_BATCH} sobre Fargate. O Batch gerencia filas e "
            f"prioridade; o Fargate executa sem provisionar instâncias. Lambda "
            f"fica fora, porque excede o limite de quinze minutos."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Quando serverless nao e resposta certa ----
    {
        "voice": "antonio",
        "text": (
            f"A prova também testa se você reconhece os limites do "
            f"serverless. Sinais de que {SAY('EC2')} ou containers "
            f"tradicionais são mais adequados: throughput altíssimo, "
            f"sustentado e previsível, onde Reserved Instances batem o custo "
            f"por invocação do Lambda; necessidade de controle total sobre o "
            f"{RUNTIME} ou sistema operacional; ou processos longos com "
            f"estado em memória entre requisições, como um {WEBSOCKET} "
            f"persistente ou um cache local grande."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito traz um laboratório prático de uma hora e "
            f"meia, no Free Tier, onde você mede o {COLD_START} de uma "
            f"Lambda, ativa {PROVISIONED_CONCURRENCY} e compara, configura uma "
            f"fila S Q S como {EVENT_SOURCE_MAPPING}, e roda um container "
            f"simples no {SAY('ECS')} com Fargate."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (6 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: um job de processamento que leva "
            f"quarenta e cinco minutos, em container, sem gerenciar servidor. "
            f"Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{AWS_BATCH} sobre Fargate. Batch gerencia filas e prioridade; "
            f"Fargate executa sem gerenciar instâncias. Lambda não serve, pelo "
            f"limite de quinze minutos."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: a latência do Lambda precisa ser consistente, sem "
            f"{COLD_START} perceptível pelo usuário. Como resolver?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{PROVISIONED_CONCURRENCY} — mantém ambientes já inicializados e "
            f"prontos. Para Java especificamente, {SNAPSTART} é uma "
            f"alternativa sem custo extra, restaurando de um snapshot já "
            f"inicializado."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: a empresa migra de {SAY('EC2')} para containers, e o "
            f"time já mantém manifests Kubernetes. Qual serviço minimiza "
            f"retrabalho?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('EKS')}. Reaproveita os manifests Kubernetes existentes; "
            f"{SAY('ECS')} exigiria reescrever tudo em task definitions "
            f"proprietárias da {SAY('AWS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: uma Lambda precisa acessar um {SAY('RDS')} numa "
            f"{SAY('subnet')} privada. O que muda na configuração e no acesso "
            f"à internet?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A função precisa ser configurada para rodar dentro da "
            f"{SAY('VPC')}. Isso permite alcançar o {SAY('RDS')} privado, mas "
            f"remove o acesso padrão à internet pública — se ainda precisar "
            f"de internet, requer N A T {SAY('Gateway')}; se for só outro "
            f"serviço da {SAY('AWS')}, um {SAY('VPC')} Endpoint é mais barato."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: uma fila S Q S alimenta uma Lambda, mas mensagens com "
            f"erro ficam sendo reprocessadas indefinidamente. Como "
            f"isolar?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Configurar uma D L Q, via {REDRIVE_POLICY}, com "
            f"{MAX_RECEIVE_COUNT} definido. Depois desse número de tentativas "
            f"falhas, a mensagem vai automaticamente para a D L Q, liberando a "
            f"fila principal."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como decidir rapidamente entre {APP_RUNNER} e "
            f"{SAY('ECS')} com Fargate para um novo serviço web?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Se o requisito é só fazer deploy de um container com H T T P S e "
            f"escala automática prontos, com mínima configuração, "
            f"{APP_RUNNER} é a resposta. Se há necessidade de controle fino "
            f"sobre rede, {SIDECAR_LOCAL}s, ou integração profunda com o "
            f"ecossistema {SAY('ECS')} e {SAY('EKS')}, use {SAY('ECS')} com "
            f"Fargate."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo oito. No próximo, vamos falar de "
            f"segurança: K M S, criptografia e proteção contra D D o S. Até a "
            f"próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
