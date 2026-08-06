"""Roteiro DEA-C01 Capitulo 14 — CI/CD, IaC e programacao de pipelines."""

from glossary import SAY, EMPH, BRK, PHON

CLOUDFORMATION = PHON("klaʊd fɔrˈmeɪʃən", "CloudFormation")
CDK = PHON("si di keɪ", "CDK")
SAM = PHON("sæm", "SAM")
CODECOMMIT = PHON("koʊd kəˈmɪt", "CodeCommit")
CODEBUILD = PHON("koʊd bɪld", "CodeBuild")
CODEPIPELINE = PHON("koʊd ˈpaɪplaɪn", "CodePipeline")
STACK = PHON("stæk", "stack")
CLONE = PHON("kloʊn", "clone")
BRANCH = PHON("bræntʃ", "branch")
COMMIT = PHON("kəˈmɪt", "commit")
PUSH_PULL = PHON("pʊʃ ænd pʊl", "push e pull")
MERGE = PHON("mɜrdʒ", "merge")
PULL_REQUEST = PHON("pʊl rɪˈkwɛst", "pull request")
BATCH_WRITE = PHON("bætʃ raɪt ˈaɪtəm", "BatchWriteItem")
PUSHDOWN = PHON("ˈpʊʃdaʊn", "pushdown")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quatorze: {SAY('CI')} {SAY('CD')}, infraestrutura como "
            f"código e programação de pipelines. São poucas questões no exame — "
            f"mas fáceis de garantir se você souber o papel de cada ferramenta."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- IaC ----
    {
        "voice": "antonio",
        "text": (
            f"Infraestrutura como código — três ferramentas. {CLOUDFORMATION}: "
            f"templates declarativos em {SAY('YAML')}; a {STACK} é a unidade de "
            f"deploy e rollback — gatilho: 'implantar a mesma infraestrutura em "
            f"dev, homolog e produção de forma repetível'. {CDK}: define a "
            f"infraestrutura em LINGUAGEM de programação — Python, TypeScript — "
            f"e sintetiza {CLOUDFORMATION} — gatilho: 'o time prefere definir "
            f"infra em código com loops e abstrações'."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o {SAY('AWS')} {SAM} — Serverless Application Model, "
            f"citado nominalmente no exam guide: extensão do {CLOUDFORMATION} "
            f"para serverless, com atalhos para Lambda, Step Functions e "
            f"{SAY('DynamoDB')} — {SAM} build, {SAM} deploy. Gatilho: 'empacotar "
            f"e implantar funções Lambda e state machines'. Console manual é "
            f"SEMPRE a alternativa errada para 'repetível'."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- CI/CD ----
    {
        "voice": "francisca",
        "text": (
            f"O fluxo de {SAY('CI')} {SAY('CD')} nativo: {CODECOMMIT} é o "
            f"repositório Git; {CODEBUILD} roda os testes e o build do template; "
            f"{CODEPIPELINE} orquestra os estágios até o deploy via "
            f"{CLOUDFORMATION} ou {SAM}. No contexto de dados, o 'código' inclui "
            f"os scripts de Glue Job — versionados no Git e publicados no "
            f"{SAY('S3')} —, os {SAY('DAGs')} do {SAY('MWAA')} e as definições "
            f"de state machine. Testar pipeline de dados é rodar a transformação "
            f"com um dataset de amostra em dev antes de promover."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Git ----
    {
        "voice": "antonio",
        "text": (
            f"Git — o vocabulário mínimo que o guide pede: {CLONE} copia o "
            f"repositório; {BRANCH} e checkout criam a linha de trabalho "
            f"isolada; add e {COMMIT} registram a mudança; {PUSH_PULL} "
            f"sincronizam com o remoto; {MERGE} integra. O fluxo esperado numa "
            f"questão: {BRANCH} para a mudança, {COMMIT}, push, {PULL_REQUEST}, "
            f"e o {MERGE} na main dispara o {CODEPIPELINE}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Otimizacao de codigo ----
    {
        "voice": "francisca",
        "text": (
            f"Otimização de código e {SAY('SQL')} — os princípios. Filtrar e "
            f"projetar CEDO: predicate {PUSHDOWN}, não arraste linhas e colunas "
            f"que serão descartadas. Operar em LOTE, não registro a registro: "
            f"{BATCH_WRITE} no {SAY('DynamoDB')}, COPY no Redshift. Paralelizar "
            f"o que é independente. Mover a transformação para onde o dado está "
            f"— {SAY('ELT')}. E em {SAY('SQL')}: join nas colunas de "
            f"distribuição, evitar função sobre a coluna filtrada, e "
            f"materializar resultados repetidos."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: implantar um pipeline serverless — Lambda, Step "
            f"Functions, {SAY('DynamoDB')} — de forma repetível em três contas?"
            f"{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAM}, ou {CDK} e {CLOUDFORMATION} — template versionado no Git, "
            f"implantado pelo {CODEPIPELINE} em cada ambiente."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: garantir que mudanças num script de Glue Job passem por "
            f"revisão e teste antes de produção?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Script no Git, {PULL_REQUEST}, {CODEBUILD} testa com amostra, e o "
            f"{CODEPIPELINE} promove para o {SAY('S3')} de produção."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: job gravando item por item no {SAY('DynamoDB')} está "
            f"lento e caro. Otimização de código?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BATCH_WRITE} — até vinte e cinco itens por chamada. O princípio: "
            f"lote, não registro a registro."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo quatorze. No próximo, o domínio quatro "
            f"inteiro: segurança e governança de dados. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
