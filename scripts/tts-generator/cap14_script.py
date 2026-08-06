"""Roteiro tratado do Capitulo 14 (Containers: ECS, EKS, Fargate) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON, SPOT, SIDECAR, TARGET_GROUP

TASK_DEFINITION = PHON("tæsk ˌdɛfəˈnɪʃən", "Task Definition")
EXECUTION_ROLE = PHON("ˌɛksəˈkjuʃən ɹoʊl", "execution role")
TASK_ROLE = PHON("tæsk ɹoʊl", "task role")
CAPACITY_PROVIDERS = PHON("kəˈpæsɪti prəˈvaɪdɚz", "capacity providers")
CAPACITY_PROVIDER = PHON("kəˈpæsɪti prəˈvaɪdɚ", "capacity provider")
FARGATE_SPOT = PHON("ˈfɑrɡeɪt spɑt", "Fargate Spot")
BIN_PACKING = PHON("bɪn ˈpækɪŋ", "bin packing")
CONTROL_PLANE = PHON("kənˈtroʊl pleɪn", "control plane")
MANAGED_NODE_GROUPS = PHON("ˈmænɪdʒd noʊd ɡrups", "Managed Node Groups")
FARGATE_PROFILES = PHON("ˈfɑrɡeɪt ˈproʊfaɪlz", "Fargate Profiles")
DAEMONSETS = PHON("ˈdimənsɛts", "DaemonSets")
AWSVPC = PHON("eɪ dʌbəlju ɛs vi pi si", "awsvpc")
ENI_TRUNKING = PHON("i ɛn aɪ ˈtrʌŋkɪŋ", "ENI trunking")
IMAGE_SCANNING = PHON("ˈɪmɪdʒ ˈskænɪŋ", "image scanning")
SERVICE_CONNECT = PHON("ˈsɜrvɪs kəˈnɛkt", "Service Connect")
CLOUD_MAP = PHON("klaʊd mæp", "Cloud Map")
APP_MESH = PHON("æp mɛʃ", "App Mesh")
ENVOY = PHON("ˈɛnvɔɪ", "Envoy")
FLUENT_BIT = PHON("ˈfluənt bɪt", "Fluent Bit")
ADOT_COLLECTOR = PHON("ˈeɪdɑt kəˈlɛktɚ", "ADOT collector")
APP_RUNNER = PHON("æp ˈrʌnɚ", "App Runner")
ROLLING_UPDATE = PHON("ˈroʊlɪŋ ˈʌpdeɪt", "rolling update")
MIN_HEALTHY_PERCENT = PHON("ˈmɪnɪməm ˈhɛlθi pɚˈsɛnt", "minimumHealthyPercent")
BLUE_GREEN = PHON("blu ɡrin", "blue/green")
CODEDEPLOY = PHON("koʊd dɪˈplɔɪ", "CodeDeploy")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo catorze: containers. O capítulo oito já apresentou "
            f"containers como um degrau da escada de computação. Aqui vamos "
            f"abrir o {SAY('ECS')} e o {SAY('EKS')} por dentro — como cada "
            f"peça se encaixa, e os detalhes operacionais que a prova adora "
            f"cobrar."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- ECS 4 pecas ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('ECS')} tem quatro peças que formam um serviço."
            f"{BRK(300)} A {TASK_DEFINITION} é o molde: imagem do container, "
            f"C P U, memória, portas, variáveis de ambiente, e as roles — a "
            f"{EXECUTION_ROLE}, usada pelo {SAY('ECS')} para buscar a "
            f"imagem e gravar logs, e a {TASK_ROLE}, usada pela aplicação "
            f"dentro do container."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Uma {SAY('task')} é uma instância em execução da "
            f"{TASK_DEFINITION} — pode ser isolada, para lote, ou parte de "
            f"um serviço. O {SAY('service')} garante N {SAY('tasks')} "
            f"rodando, integra com {TARGET_GROUP} do {SAY('ALB')} ou "
            f"{SAY('NLB')}, e faz Auto Scaling e {ROLLING_UPDATE}s."
            f"{BRK(300)} E o {SAY('cluster')} é o agrupamento lógico de "
            f"capacidade — {SAY('EC2')}, Fargate, ou ambos."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Capacity providers ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre {CAPACITY_PROVIDERS}, onde as {SAY('tasks')} de fato "
            f"rodam: Fargate, sem servidor para gerenciar, pagando por v C "
            f"P U e memória da {SAY('task')} — ótimo para cargas variáveis "
            f"e times pequenos."
            f"{BRK(300)} {FARGATE_SPOT}, até setenta por cento mais barato, "
            f"mas a {SAY('task')} pode ser interrompida com dois minutos de "
            f"aviso — ideal para {SAY('workers')} tolerantes a falha."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {SAY('EC2')} com Auto Scaling: você gerencia as "
            f"instâncias do {SAY('cluster')} — mais controle, como G P U, "
            f"{SAY('Instance Store')} e {BIN_PACKING} denso — e pode ser "
            f"mais barato em alta escala constante."
            f"{BRK(300)} E {SAY('EC2')} mais Fargate misto: uma estratégia "
            f"com pesos, por exemplo base garantida em {SAY('EC2')} "
            f"reservado mais estouro em Fargate."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- EKS ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('EKS')} gerencia o {CONTROL_PLANE} — servidor de A P I "
            f"e {SAY('etcd')} — com acordo de nível de serviço da "
            f"{SAY('AWS')}. Você ainda escolhe onde os {SAY('pods')} rodam."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {MANAGED_NODE_GROUPS} são {SAY('EC2')}, "
            f"{SAY('on-demand')} ou {SPOT}, provisionadas pelo {SAY('EKS')} "
            f"via Auto Scaling Groups — você escolhe o tipo de instância. "
            f"Melhor custo em escala, com acesso a recursos de nó, como "
            f"{DAEMONSETS}, G P U e volumes {SAY('EBS')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Já os {FARGATE_PROFILES} rodam cada {SAY('pod')} "
            f"isolado numa mini máquina virtual Fargate, sem gerenciar "
            f"nós — mas {EMPH('não suportam')} {DAEMONSETS}, "
            f"{SAY('hostPort')} ou volumes {SAY('EBS')} diretos. Bom para "
            f"{SAY('workloads')} simples e multi-cliente."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Uma armadilha de rede: no modo {AWSVPC}, "
            f"obrigatório no Fargate, cada {SAY('task')} recebe sua própria "
            f"interface de rede com I P da {SAY('VPC')} — isso limita o "
            f"número de {SAY('tasks')} por instância {SAY('EC2')} pelo "
            f"número de interfaces que o tipo de instância suporta, mesmo "
            f"com {ENI_TRUNKING} ajudando. Em {SAY('subnets')} pequenas, "
            f"muitas {SAY('tasks')} Fargate podem esgotar os I Ps "
            f"disponíveis — dimensione a {SAY('subnet')} pensando em "
            f"containers, não só em instâncias."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- ECR ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre o {SAY('ECR')}, o registro de imagens: o "
            f"{IMAGE_SCANNING} automático, básico ou avançado via "
            f"Inspector, ao fazer {SAY('push')}, identifica vulnerabilidades "
            f"nas camadas da imagem."
            f"{BRK(300)} {SAY('Lifecycle policies')} expiram imagens "
            f"antigas ou sem {SAY('tag')} automaticamente, evitando acúmulo "
            f"de custo. Replicação entre regiões ou contas serve para times "
            f"distribuídos ou recuperação de desastre. E a criptografia, "
            f"via K M S ou A E S, vem por padrão."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Service Discovery / Sidecar ----
    {
        "voice": "francisca",
        "text": (
            f"Quando microsserviços em containers precisam se encontrar "
            f"dinamicamente, sem I Ps fixos, o {SAY('ECS')} "
            f"{SERVICE_CONNECT}, ou o A W S {CLOUD_MAP}, fornece nomes D N "
            f"S internos estáveis que sempre resolvem para as {SAY('tasks')} "
            f"saudáveis atuais, com métricas de tráfego e nova tentativa "
            f"automática entre serviços."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O padrão {SIDECAR} roda um container auxiliar na "
            f"mesma {SAY('task')} que o container principal, compartilhando "
            f"rede e armazenamento — usado para proxies, como o {ENVOY} no "
            f"{APP_MESH}, agentes de log, como o {FLUENT_BIT}, ou coleta de "
            f"métricas, com o {ADOT_COLLECTOR} — sem acoplar essa "
            f"responsabilidade ao código da aplicação."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Decisao final ----
    {
        "voice": "antonio",
        "text": (
            f"A decisão final: equipe que já usa Kubernetes, ou quer "
            f"portabilidade entre nuvens diferentes, vai de {SAY('EKS')}. "
            f"Quer a integração mais simples com o ecossistema "
            f"{SAY('AWS')}, sem aprender Kubernetes, vai de {SAY('ECS')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Não quer gerenciar nenhuma infraestrutura, nem "
            f"{SAY('cluster')}: Fargate, em {SAY('ECS')} ou {SAY('EKS')}. "
            f"Só quer fazer {SAY('deploy')} de uma imagem com H T T P S e "
            f"escala automática de graça: {APP_RUNNER}, mais simples, mas "
            f"com menos controle. E carga em lote, tolerante a "
            f"interrupção, alto volume: {FARGATE_SPOT} ou {SAY('EC2')} "
            f"{SPOT}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Deploy sem downtime ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre {SAY('deploy')} sem tempo de inatividade: o "
            f"{SAY('ECS')} suporta {ROLLING_UPDATE} nativo, substituindo "
            f"{SAY('tasks')} gradualmente respeitando o {MIN_HEALTHY_PERCENT}, "
            f"e {BLUE_GREEN} via {CODEDEPLOY}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} No {BLUE_GREEN}, um conjunto totalmente novo de "
            f"{SAY('tasks')} sobe, é testado, e o {TARGET_GROUP} do "
            f"{SAY('ALB')} é trocado de uma vez, com {EMPH('rollback automático')} "
            f"por alarme do CloudWatch. Quando o enunciado pede capacidade "
            f"de {SAY('rollback')} automático e teste antes do tráfego "
            f"total, a resposta é {BLUE_GREEN} com {CODEDEPLOY}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório prático de uma hora, "
            f"por dez centavos de dólar, onde você empacota uma imagem no "
            f"{SAY('ECR')}, cria uma {TASK_DEFINITION} Fargate, monta um "
            f"serviço com duas {SAY('tasks')} atrás de um {SAY('ALB')}, e "
            f"força um novo {SAY('deployment')} observando o "
            f"{ROLLING_UPDATE}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: a equipe quer rodar containers sem "
            f"gerenciar nenhum servidor, mas continuar no ecossistema "
            f"{SAY('ECS')}. Qual {CAPACITY_PROVIDER}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Fargate — sem {SAY('EC2')} para corrigir ou escalar, paga por "
            f"v C P U e memória reservada pela {SAY('task')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: um {SAY('workload')} de processamento em lote, com "
            f"picos noturnos, pode ser interrompido sem problema. Qual a "
            f"opção mais barata?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{FARGATE_SPOT} — até setenta por cento de desconto, com dois "
            f"minutos de aviso antes da interrupção. Para {SAY('tasks')} "
            f"críticas e longas, use {SAY('on-demand')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: uma aplicação Kubernetes precisa de {DAEMONSETS} e "
            f"volumes {SAY('EBS')} persistentes por {SAY('pod')}. "
            f"{FARGATE_PROFILES} resolve?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Não. {FARGATE_PROFILES} no {SAY('EKS')} não suportam "
            f"{DAEMONSETS} nem volumes {SAY('EBS')} persistentes por "
            f"{SAY('pod')} — esse cenário exige {MANAGED_NODE_GROUPS}, com "
            f"{SAY('EC2')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: como reduzir o risco de um {SAY('deploy')} ruim ir "
            f"para cem por cento do tráfego de produção no {SAY('ECS')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('Deployment')} {BLUE_GREEN} via {CODEDEPLOY}: o novo "
            f"conjunto de {SAY('tasks')} sobe em paralelo, recebe tráfego "
            f"de teste, e só é promovido para cem por cento, com "
            f"{SAY('rollback')} automático por alarme, após validação."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: vulnerabilidades conhecidas em imagens Docker. Como "
            f"detectar antes do {SAY('deploy')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Habilitar {IMAGE_SCANNING} no {SAY('ECR')}, básico ou "
            f"avançado via Inspector — escaneia as camadas da imagem no "
            f"{SAY('push')} e reporta vulnerabilidades antes da produção."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: microsserviços em containers precisam se descobrir "
            f"dinamicamente, sem fixar I Ps, à medida que {SAY('tasks')} são "
            f"substituídas pelo Auto Scaling. Como?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('ECS')} {SERVICE_CONNECT}, ou A W S {CLOUD_MAP} — "
            f"fornece nomes D N S internos estáveis, que sempre resolvem "
            f"para as {SAY('tasks')} saudáveis atuais, sem configuração "
            f"manual a cada {SAY('deploy')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como coletar logs e métricas de uma aplicação em "
            f"container sem modificar o código?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Padrão {SIDECAR} — um container auxiliar, como o "
            f"{FLUENT_BIT} para logs ou o {ADOT_COLLECTOR} para métricas, "
            f"roda na mesma {SAY('task')}, compartilhando rede e volumes, "
            f"capturando dados sem nenhuma mudança no código da aplicação."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo catorze. No próximo, vamos falar de "
            f"API Gateway e Step Functions. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
