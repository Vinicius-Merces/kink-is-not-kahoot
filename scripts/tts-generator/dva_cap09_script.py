"""Roteiro DVA-C02 Capitulo 9 — Containers e ECR para desenvolvedores."""

from glossary import SAY, EMPH, BRK, PHON

DOCKER_LOGIN = PHON("ˈdɑkɚ ˈlɔɡɪn", "docker login")
DOCKER_PUSH = PHON("ˈdɑkɚ pʊʃ", "docker push")
DOCKER_TAG = PHON("ˈdɑkɚ tæɡ", "docker tag")
EXECUTION_ROLE = PHON("tæsk ˌɛksəˈkjuʃən ɹoʊl", "Task Execution Role")
TASK_ROLE = PHON("tæsk ɹoʊl", "Task Role")
FARGATE = PHON("ˈfɑrɡeɪt", "Fargate")
IMAGE_SCANNING = PHON("ˈɪmɪdʒ ˈskænɪŋ", "image scanning")
LIFECYCLE_POLICY = PHON("ˈlaɪfsaɪkəl ˈpɑləsi", "lifecycle policy")
AWSLOGS = PHON("eɪ dabliu ɛs lɔɡz", "awslogs")
SECRETS_FIELD = PHON("ˈsikrəts", "secrets")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo nove: containers e {SAY('ECR')} para desenvolvedores. A "
            f"estrela deste capítulo é a pegadinha das DUAS roles do "
            f"{SAY('ECS')} — quem puxa a imagem e quem roda o código."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- ECR ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('ECR')} é o registry. O fluxo de publicação que cai "
            f"literalmente: {SAY('AWS')} {SAY('ECR')} get login password "
            f"encadeado no {DOCKER_LOGIN}; docker build; {DOCKER_TAG} com a "
            f"{SAY('URI')} do repositório; e {DOCKER_PUSH}. Erros de denied no "
            f"push ou pull são permissão do {SAY('IAM')}. E o {SAY('ECR')} "
            f"ainda oferece {IMAGE_SCANNING} de vulnerabilidades e "
            f"{LIFECYCLE_POLICY} para expirar imagens antigas — 'manter só as "
            f"dez mais recentes'."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- As duas roles ----
    {
        "voice": "francisca",
        "text": (
            f"As DUAS roles da task definition — não confunda. A "
            f"{EXECUTION_ROLE} é usada pelo AGENTE do {SAY('ECS')} para "
            f"PREPARAR a task: puxar a imagem do {SAY('ECR')}, criar o log "
            f"stream, ler os segredos para injetar. A {TASK_ROLE} é usada pelo "
            f"SEU CÓDIGO dentro do container: ler do {SAY('S3')}, escrever no "
            f"{SAY('DynamoDB')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A armadilha: 'a task não consegue puxar a imagem' é "
            f"problema na {EXECUTION_ROLE}; 'o código recebe access denied no "
            f"{SAY('DynamoDB')}' é problema na {TASK_ROLE}. Trocar uma pela "
            f"outra é exatamente o erro que a prova quer que você identifique."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Fargate, segredos, logs ----
    {
        "voice": "antonio",
        "text": (
            f"{FARGATE} elimina o gerenciamento de instâncias — a task define "
            f"{SAY('vCPU')} e memória, e você paga por segundo. Configuração "
            f"vai como variável de ambiente na task definition; SEGREDOS vão "
            f"no campo {SECRETS_FIELD}, referenciando o {SAY('ARN')} no "
            f"Secrets Manager ou no Parameter Store — o valor NUNCA fica em "
            f"texto na definição; o {SAY('ECS')} injeta em runtime. E os logs "
            f"saem pelo driver {AWSLOGS} para o CloudWatch Logs."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: task {FARGATE} falha ao iniciar com erro de "
            f"pull da imagem. Onde mexer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Na {EXECUTION_ROLE} — é ela que o agente usa para autenticar no "
            f"{SAY('ECR')} e baixar a imagem."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: entregar a senha do banco ao container sem deixá-la em "
            f"texto na task definition?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Campo {SECRETS_FIELD} referenciando o Secrets Manager — o "
            f"{SAY('ECS')} injeta como variável de ambiente em runtime."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: manter só as dez imagens mais recentes no repositório "
            f"automaticamente?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{LIFECYCLE_POLICY} do {SAY('ECR')} expirando além das dez mais novas.",
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo nove. No próximo, a esteira completa: "
            f"{SAY('CI')} {SAY('CD')} com a CodeSuite. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
