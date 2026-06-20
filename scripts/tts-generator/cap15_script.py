"""Roteiro tratado do Capitulo 15 (API Gateway, Step Functions) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

HTTP_API = PHON("eɪtʃ ti ti pi eɪ pi aɪ", "HTTP API")
REST_API = PHON("rɛst eɪ pi aɪ", "REST API")
WEBSOCKET_API = PHON("wɛb ˈsɑkɪt eɪ pi aɪ", "WebSocket API")
JWT_AUTHORIZERS = PHON("dʒeɪ dʌbəlju ti ɔˈθɔraɪzɚz", "JWT authorizers")
USAGE_PLANS = PHON("ˈjusɪdʒ plænz", "Usage Plans")
API_KEYS = PHON("eɪ pi aɪ kiz", "API Keys")
LAMBDA_AUTHORIZER = PHON("ˈlæmdə ɔˈθɔraɪzɚ", "Lambda Authorizer")
COGNITO_AUTHORIZER = PHON("kɑgˈnitoʊ ɔˈθɔraɪzɚ", "Cognito Authorizer")
IAM_AUTHORIZATION = PHON("aɪ eɪ ɛm ɔθəraɪˈzeɪʃən", "IAM Authorization")
SIGV4 = PHON("sɪɡ vi fɔr", "SigV4")
THROTTLING = PHON("ˈθrɑtlɪŋ", "throttling")
TOKEN_BUCKET = PHON("ˈtoʊkən ˈbʌkɪt", "token bucket")
STAGE = PHON("ˈsteɪdʒ", "Stage")
CACHING = PHON("ˈkeɪʃɪŋ", "Caching")
CANARY_RELEASE = PHON("kəˈnɛri rɪˈlis", "Canary Release")
STANDARD_WORKFLOWS = PHON("ˈstændɚd ˈwɜrkfloʊz", "Standard Workflows")
STANDARD_WORKFLOW = PHON("ˈstændɚd ˈwɜrkfloʊ", "Standard Workflow")
EXPRESS_WORKFLOWS = PHON("ɪkˈsprɛs ˈwɜrkfloʊz", "Express Workflows")
EXPRESS_WORKFLOW = PHON("ɪkˈsprɛs ˈwɜrkfloʊ", "Express Workflow")
EXACTLY_ONCE = PHON("ɪɡˈzæktli wʌns", "exactly-once")
AT_LEAST_ONCE = PHON("æt list wʌns", "at-least-once")
EVENT_BRIDGE_SCHEDULER = PHON("ɪˈvɛnt brɪdʒ ˈskɛdʒulɚ", "EventBridge Scheduler")
EVENT_BRIDGE_RULES = PHON("ɪˈvɛnt brɪdʒ rulz", "EventBridge Rules")
START_EXECUTION = PHON("stɑrt ˌɛksəˈkjuʃən", "StartExecution")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quinze: API Gateway, Step Functions e orquestração "
            f"serverless. O capítulo oito cobriu Lambda a fundo, mas tratou "
            f"orquestração só de passagem — aqui entramos nos detalhes que "
            f"separam funciona no laboratório de passa na prova."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- REST/HTTP/WebSocket API ----
    {
        "voice": "francisca",
        "text": (
            f"Existem três tipos de A P I."
            f"{BRK(300)} {HTTP_API} é o padrão para A P Is REST modernas — "
            f"até setenta por cento mais barata e com menor latência que "
            f"{REST_API}. Suporta {JWT_AUTHORIZERS} e integração direta com "
            f"Lambda."
            f"{BRK(300)} {REST_API} tem recursos completos: {API_KEYS}, "
            f"{USAGE_PLANS}, transformação de requisição e resposta, "
            f"{CACHING} nativo, e integração com {SAY('WAF')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} E {WEBSOCKET_API} dá conexões persistentes "
            f"bidirecionais — chat, painéis em tempo real, jogos — usando "
            f"rotas especiais em vez de métodos H T T P."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Regra rápida: se o enunciado não menciona "
            f"{API_KEYS}, {USAGE_PLANS}, {CACHING} ou {SAY('WAF')}, e só "
            f"quer expor uma Lambda via H T T P da forma mais barata, a "
            f"resposta é {HTTP_API}. Se menciona monetizar por chave de A P "
            f"I, ou transformar o {SAY('payload')} antes do backend, é "
            f"{REST_API}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Controle de acesso ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre controle de acesso e tráfego: o {THROTTLING}, com "
            f"limite por taxa e estouro, usa um modelo de {TOKEN_BUCKET} — "
            f"protege os backends de picos, configurável por método ou "
            f"plano de uso."
            f"{BRK(300)} {USAGE_PLANS} mais {API_KEYS} dão cotas e limites "
            f"por cliente ou parceiro."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O {LAMBDA_AUTHORIZER} dá lógica de autorização "
            f"customizada, validando token J W T ou O Auth de terceiros. O "
            f"{COGNITO_AUTHORIZER} valida tokens emitidos por um User Pool "
            f"do Cognito, sem código de validação. E a {IAM_AUTHORIZATION} "
            f"exige que o chamador assine a requisição com {SIGV4} — para "
            f"comunicação entre serviços ou contas da {SAY('AWS')} "
            f"confiáveis."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- 29s trap ----
    {
        "voice": "antonio",
        "text": (
            f"Uma armadilha muito importante: o API Gateway tem um "
            f"{EMPH('timeout fixo de vinte e nove segundos')} — não "
            f"configurável — para qualquer integração, mesmo que a Lambda "
            f"por trás permita até quinze minutos."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Se o processamento pode demorar mais que isso, o "
            f"API Gateway não pode chamar a Lambda de forma síncrona e "
            f"esperar o resultado. O padrão correto: a A P I retorna "
            f"duzentos e dois imediatamente — por exemplo, enfileirando em "
            f"S Q S ou iniciando uma Step Functions — e o cliente consulta "
            f"o resultado depois, ou recebe via {SAY('WebSocket')} ou S N S."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Stages, caching, canary ----
    {
        "voice": "francisca",
        "text": (
            f"Cada {STAGE} — desenvolvimento, "
            f"{SAY('staging')}, produção — é uma versão {SAY('deployed')} "
            f"independente da A P I, com suas próprias variáveis e logs."
            f"{BRK(300)} O {CACHING} nativo do {REST_API} guarda respostas "
            f"por um T T L configurável, reduzindo chamadas ao backend para "
            f"dados que não mudam a cada requisição."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} E o {CANARY_RELEASE} direciona uma porcentagem do "
            f"tráfego para uma nova versão da A P I antes de promovê-la "
            f"cem por cento — reduzindo o risco de um {SAY('deploy')} ruim "
            f"afetar todos os usuários de uma vez."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Step Functions Standard vs Express ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre Step Functions: {STANDARD_WORKFLOWS} duram até um ano, "
            f"com execução {EXACTLY_ONCE}, histórico visual completo, preço "
            f"por transição de estado. Ideal para fluxos longos com "
            f"aprovações humanas — processos de negócio, orquestração de "
            f"{SAY('pipelines')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {EXPRESS_WORKFLOWS} duram até cinco minutos, com "
            f"execução {AT_LEAST_ONCE}, preço por número de execuções mais "
            f"duração — como a Lambda. Ideal para alto volume de eventos — "
            f"processamento de {SAY('streaming')}, ingestão de dados."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Agendamento ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre agendamento de tarefas: rodar uma Lambda toda noite às "
            f"duas da manhã é {EVENT_BRIDGE_SCHEDULER} — expressões "
            f"{SAY('cron')}, fuso horário, alvo flexível, incluindo Lambda, "
            f"Step Functions, S Q S e até A P Is de terceiros."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Reagir quando algo acontece no ambiente "
            f"{SAY('AWS')} — um objeto criado no {SAY('S3')}, uma "
            f"{SAY('EC2')} mudando de estado — é {EVENT_BRIDGE_RULES}, um "
            f"barramento de eventos com filtro por padrão."
            f"{BRK(300)} E milhares de agendamentos independentes por "
            f"cliente: {EVENT_BRIDGE_SCHEDULER} também, suportando até "
            f"milhões de agendamentos criados dinamicamente via A P I."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Padrao de orquestracao ----
    {
        "voice": "antonio",
        "text": (
            f"O padrão típico de orquestração: o cliente chama o API "
            f"Gateway, que inicia uma Step Functions de forma assíncrona, "
            f"via {START_EXECUTION}, evitando o {SAY('timeout')} de vinte e "
            f"nove segundos."
            f"{BRK(400)} Dentro da Step Functions Standard: uma Lambda "
            f"valida a entrada, outra chama um serviço de I A, um estado "
            f"{SAY('Choice')} decide se houve sucesso — indo para o "
            f"próximo passo, ou capturando o erro e notificando via S N S — "
            f"e uma última Lambda grava o resultado no {SAY('DynamoDB')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Se você está tentado a fazer uma Lambda invocar "
            f"outra Lambda de forma síncrona, e mais outra, pare: isso cria "
            f"acoplamento forte e dificulta a depuração. Step Functions "
            f"move a lógica de o que vem depois para fora do código — cada "
            f"Lambda fica pequena e independente, com novas tentativas, "
            f"{SAY('timeouts')} e tratamento de erro configurados "
            f"visualmente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório de uma hora, no Free "
            f"Tier, onde você cria duas Lambdas, uma Step Functions "
            f"Standard chamando as duas com tratamento de erro, e uma "
            f"{HTTP_API} integrada diretamente ao {START_EXECUTION}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (5 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: um {SAY('endpoint')} simples, sem "
            f"necessidade de {API_KEYS} ou {CACHING}, prioridade é menor "
            f"custo e latência. Qual tipo de A P I Gateway?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{HTTP_API} — mais barata e com menor latência que "
            f"{REST_API}, suficiente quando não há necessidade dos "
            f"recursos avançados."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: um processo de aprovação de crédito que pode levar "
            f"até três dias esperando ação humana. Standard ou "
            f"{EXPRESS_WORKFLOW}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{STANDARD_WORKFLOW} — "
            f"suporta execuções de até um ano, com estados de espera até "
            f"alguém aprovar manualmente."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: milhões de eventos de telemetria por dia precisam "
            f"disparar um pequeno fluxo de poucos segundos cada. Standard "
            f"ou Express?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{EXPRESS_WORKFLOW} — o "
            f"preço por execução compensa em alto volume, e a semântica "
            f"{AT_LEAST_ONCE} é aceitável para esse tipo de processamento."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: uma chamada à A P I precisa rodar um relatório que "
            f"demora três minutos, mas o cliente recebe {SAY('timeout')} "
            f"antes disso. Por quê, e como corrigir?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O API Gateway tem {SAY('timeout')} fixo de vinte e nove "
            f"segundos, independente do {SAY('timeout')} da Lambda. "
            f"Corrigir tornando a chamada assíncrona: a A P I retorna "
            f"duzentos e dois mais um identificador de tarefa, e o cliente "
            f"consulta o status depois."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como expor uma A P I apenas para outros serviços "
            f"dentro da mesma conta, sem expor um {SAY('endpoint')} "
            f"público?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{REST_API} com {SAY('endpoint')} do tipo {SAY('Private')}, "
            f"associado a um {SAY('VPC')} {SAY('Endpoint')}. O tráfego "
            f"nunca sai para a internet pública, e uma política de recurso "
            f"controla quais {SAY('VPCs')} ou contas podem chamá-la."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo quinze. No próximo, vamos aprofundar "
            f"em Route cinquenta e três e CloudFront. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
