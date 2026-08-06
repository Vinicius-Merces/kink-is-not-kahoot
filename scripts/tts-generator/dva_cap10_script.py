"""Roteiro DVA-C02 Capitulo 10 — CI/CD com a CodeSuite."""

from glossary import SAY, EMPH, BRK, PHON

CODEPIPELINE = PHON("koʊd ˈpaɪplaɪn", "CodePipeline")
CODEBUILD = PHON("koʊd bɪld", "CodeBuild")
CODEDEPLOY = PHON("koʊd dɪˈplɔɪ", "CodeDeploy")
CODEARTIFACT = PHON("koʊd ˈɑrtəfækt", "CodeArtifact")
CODEGURU = PHON("koʊd ˈɡuru", "CodeGuru")
COPILOT = PHON("ˈkoʊpaɪlət", "Copilot")
AMPLIFY = PHON("ˈæmplɪfaɪ", "Amplify")
CLOUDSHELL = PHON("klaʊd ʃɛl", "CloudShell")
BUILDSPEC = PHON("bɪld spɛk", "buildspec.yml")
APPSPEC = PHON("æp spɛk", "appspec.yml")
CANARY_CONFIG = PHON("kəˈnɛri tɛn pɚˈsɛnt faɪv ˈmɪnəts", "Canary10Percent5Minutes")
VALIDATE_SERVICE = PHON("ˈvælɪdeɪt ˈsɜrvɪs", "ValidateService")
APPLICATION_STOP = PHON("ˌæplɪˈkeɪʃən stɑp", "ApplicationStop")
BLUE_GREEN = PHON("blu ɡrin", "blue green")
MANUAL_APPROVAL = PHON("ˈmænjuəl əˈpruvəl", "manual approval")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dez: {SAY('CI')} {SAY('CD')} com a CodeSuite — o "
            f"{CODEPIPELINE} orquestrando, o {CODEBUILD} construindo e o "
            f"{CODEDEPLOY} implantando. E os DOIS arquivos que a prova cobra: "
            f"{BUILDSPEC} e {APPSPEC}."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Quem faz o que ----
    {
        "voice": "antonio",
        "text": (
            f"Quem faz o quê. O {CODEPIPELINE} orquestra o fluxo — source, "
            f"build, deploy — com stages, actions e {MANUAL_APPROVAL}: o "
            f"pipeline pausa até um gestor aprovar, com notificação "
            f"{SAY('SNS')}. O {CODEBUILD} compila, testa e empacota em "
            f"containers efêmeros, guiado pelo {BUILDSPEC} na raiz do repo. E "
            f"o {CODEDEPLOY} implanta em {SAY('EC2')}, Lambda e {SAY('ECS')}, "
            f"guiado pelo {APPSPEC}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- buildspec ----
    {
        "voice": "francisca",
        "text": (
            f"A anatomia do {BUILDSPEC}: fases em ordem — install para "
            f"runtimes, pre build para login no {SAY('ECR')} e dependências, "
            f"build para compilar e testar, e post build para o push da "
            f"imagem. Além das fases: artifacts define o que sai do build, "
            f"cache acelera, e env puxa variáveis do Parameter Store ou do "
            f"Secrets Manager — nunca hardcode. Build falhou? Logs no "
            f"CloudWatch Logs."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- CodeDeploy ----
    {
        "voice": "antonio",
        "text": (
            f"{CODEDEPLOY} — estratégias e hooks por plataforma. Em "
            f"{SAY('EC2')}: in-place ou {BLUE_GREEN}, com os hooks na ordem — "
            f"{APPLICATION_STOP}, before install, after install, application "
            f"start e {VALIDATE_SERVICE}, onde rodam os smoke tests que podem "
            f"reprovar o deploy. Na Lambda: shifting no alias — canary, como "
            f"{CANARY_CONFIG}, ou linear — com os hooks before e after allow "
            f"traffic. No {SAY('ECS')}: {BLUE_GREEN} com dois target groups no "
            f"{SAY('ALB')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o rollback automático: 'reverter se a taxa de erros "
            f"subir durante o deploy' = alarmes do CloudWatch associados ao "
            f"deployment group com rollback on alarm."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Outras ferramentas ----
    {
        "voice": "francisca",
        "text": (
            f"As outras ferramentas in-scope que o guide lista. "
            f"{CODEARTIFACT}: repositório gerenciado de pacotes — npm, pip, "
            f"Maven — 'repositório privado de dependências aprovadas'. "
            f"{CODEGURU} Reviewer: revisão automática de código com machine "
            f"learning no pull request. {CODEGURU} Profiler: perfil de "
            f"{SAY('CPU')} em produção — 'descobrir qual método consome "
            f"{SAY('CPU')}'. {SAY('AWS')} {COPILOT}: {SAY('CLI')} que cria e "
            f"deploya apps em contêiner no {SAY('ECS')} sem escrever "
            f"CloudFormation na mão."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {AMPLIFY}: build e hosting full-stack com BRANCHES "
            f"por ambiente — 'cada branch do Git vira um ambiente de preview'. "
            f"E o {CLOUDSHELL}: shell no navegador já autenticado com suas "
            f"credenciais, {SAY('CLI')} pré-instalada."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: nova versão de Lambda deve receber dez por "
            f"cento do tráfego por cinco minutos antes de completar?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{CODEDEPLOY} para Lambda com a config {CANARY_CONFIG} — shifting "
            f"no alias com rollback por alarme."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: em qual arquivo e seção o {CODEBUILD} busca os comandos "
            f"de teste, e onde declarar o artefato?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BUILDSPEC} — comandos nas fases build e post build; a seção "
            f"artifacts define os arquivos de saída."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: no deploy {SAY('EC2')} in-place, onde parar o serviço "
            f"antigo e onde validar a saúde do novo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{APPLICATION_STOP}, o primeiro hook, e {VALIDATE_SERVICE}, o "
            f"último — o smoke test que dispara rollback."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dez. No próximo, infraestrutura como "
            f"código: CloudFormation, {SAY('SAM')} e AppConfig. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
