"""Roteiro DEA-C01 Capitulo 15 — Seguranca e governanca de dados."""

from glossary import SAY, EMPH, BRK, PHON

LAKE_FORMATION = PHON("leɪk fɔrˈmeɪʃən", "Lake Formation")
LF_TAGS = PHON("ɛl ɛf tæɡz", "LF-Tags")
GRANT_REVOKE = PHON("ɡrænt ænd rɪˈvoʊk", "grant e revoke")
SECRETS_MANAGER = PHON("ˈsikrəts ˈmænɪdʒɚ", "Secrets Manager")
PARAMETER_STORE = PHON("pəˈræmɪtɚ stɔr", "Parameter Store")
MACIE = PHON("ˈmeɪsi", "Macie")
KMS = PHON("keɪ ɛm ɛs", "KMS")
CMK = PHON("si ɛm keɪ", "CMK")
MASKING = PHON("ˈmæskɪŋ", "masking")
SALTING = PHON("ˈsɔltɪŋ", "salting")
TOKENIZACAO = "tokenização"
CLOUDTRAIL_LAKE = PHON("klaʊd treɪl leɪk", "CloudTrail Lake")
CONFIG = PHON("kənˈfɪɡ", "Config")
SCP = PHON("ɛs si pi", "SCP")
ACCESS_POINTS = PHON("ˈæksɛs pɔɪnts", "Access Points")
GATEWAY_ENDPOINT = PHON("ˈɡeɪtweɪ ˈɛndpɔɪnt", "Gateway Endpoint")
INTERFACE_ENDPOINT = PHON("ˈɪntɚfeɪs ˈɛndpɔɪnt", "Interface Endpoint")
SELF_REFERENCING = PHON("sɛlf ˈrɛfərɛnsɪŋ", "self-referencing")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quinze: segurança e governança de dados — o domínio "
            f"quatro inteiro, dezoito por cento do exame. O centro é o "
            f"{LAKE_FORMATION}, cercado por criptografia, mascaramento, rede e "
            f"auditoria."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Lake Formation ----
    {
        "voice": "antonio",
        "text": (
            f"{LAKE_FORMATION} — o centro da governança. O {SAY('IAM')} controla "
            f"acesso a SERVIÇOS; o {LAKE_FORMATION} controla acesso a DADOS, com "
            f"granularidade que o {SAY('IAM')} não alcança: database, tabela, "
            f"COLUNA, LINHA e CÉLULA — via {GRANT_REVOKE}. Athena, Redshift "
            f"Spectrum, Glue e {SAY('EMR')} respeitam as regras. Column-level: "
            f"'analistas veem a tabela, mas não a coluna salário'. Row-level: "
            f"'cada filial só vê as próprias linhas'."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {LF_TAGS}: gerenciar permissões em ESCALA etiquetando "
            f"dados — tag confidencial — em vez de conceder tabela por tabela. E "
            f"cross-account sharing: compartilhar tabelas do Catalog com outra "
            f"conta de forma governada. A confusão clássica: se a questão pede "
            f"permissão por coluna ou linha, {SAY('IAM')} e bucket policy NÃO "
            f"resolvem — é {LAKE_FORMATION}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- IAM e autenticacao ----
    {
        "voice": "francisca",
        "text": (
            f"Autenticação e {SAY('IAM')}. Roles, NUNCA chaves de acesso: Glue, "
            f"Lambda e {SAY('EMR')} assumem roles — credencial hardcoded é "
            f"sempre errada. Managed policies são genéricas; customer managed "
            f"policies dão o least privilege — a resposta quando a pronta "
            f"permite demais. Cross-account: a conta A assume role na conta B "
            f"via trust policy; para o {SAY('S3')}, os {ACCESS_POINTS} gerenciam "
            f"múltiplos consumidores do mesmo bucket com políticas separadas. E "
            f"credenciais: {SECRETS_MANAGER} com rotação automática; "
            f"configuração NÃO sensível fica no {PARAMETER_STORE}, mais barato."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Rede ----
    {
        "voice": "antonio",
        "text": (
            f"Rede segura para o dado. {SAY('VPC')} endpoints mantêm o tráfego "
            f"fora da internet: {GATEWAY_ENDPOINT} para {SAY('S3')} e "
            f"{SAY('DynamoDB')} — grátis; {INTERFACE_ENDPOINT}, o PrivateLink, "
            f"para Glue, Kinesis, Redshift e afins. 'Os dados não podem trafegar "
            f"pela internet' se resolve aqui. Security groups: para o Glue "
            f"acessar um {SAY('RDS')} na {SAY('VPC')}, a regra clássica é o "
            f"{SELF_REFERENCING} rule exigido pela connection."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Criptografia ----
    {
        "voice": "francisca",
        "text": (
            f"Criptografia — server-side versus client-side. Server-side: a "
            f"{SAY('AWS')} criptografa ao receber — {SAY('SSE')} {SAY('S3')} com "
            f"chave da própria {SAY('AWS')}, zero gestão; ou {SAY('SSE')} "
            f"{KMS} com a sua {CMK} — auditoria pelo CloudTrail e controle por "
            f"key policy; é a resposta quando há requisito de auditoria. "
            f"Client-side: o dado sai da aplicação JÁ criptografado — quando nem "
            f"a {SAY('AWS')} pode ver o conteúdo."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E a pegadinha cross-account do {KMS}: a conta B recebe "
            f"access denied ao ler objetos criptografados da conta A MESMO com a "
            f"bucket policy correta — falta {KMS} decrypt na KEY POLICY da "
            f"{CMK}. Acesso a objeto criptografado exige permissão no bucket E "
            f"na chave."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Mascaramento ----
    {
        "voice": "antonio",
        "text": (
            f"Anonimização e mascaramento. {MASKING}: ocultar parte do valor na "
            f"EXIBIÇÃO — dynamic data {MASKING} no Redshift, detect {SAY('PII')} "
            f"no Glue. Anonimização: substituir o identificador de forma "
            f"irreversível — hash. {SALTING}: adicionar um salt antes do hash — "
            f"sem ele, hash de {SAY('CPF')} é quebrável por dicionário; o exam "
            f"guide cita key {SALTING} nominalmente. E {TOKENIZACAO}: trocar o "
            f"valor por um token com o mapa guardado à parte. O {MACIE} "
            f"encontra {SAY('PII')} esquecida nos buckets — e integra com o "
            f"{LAKE_FORMATION}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Auditoria ----
    {
        "voice": "francisca",
        "text": (
            f"Auditoria e governança de conta. CloudTrail registra as chamadas "
            f"de {SAY('API')} — e os data events do {SAY('S3')}, que são opt-in, "
            f"auditam LEITURAS de objetos do lake. O {CLOUDTRAIL_LAKE} consulta "
            f"anos de eventos de várias contas com {SAY('SQL')}, sem montar "
            f"pipeline próprio. O {SAY('AWS')} {CONFIG} registra MUDANÇAS de "
            f"configuração e avalia conformidade — 'bucket não pode ficar "
            f"público'. Diferencie: CloudTrail é quem chamou o quê; {CONFIG} é "
            f"como o recurso estava configurado. E soberania de dados: {SCP} "
            f"negando regiões, mais bloqueio de replicação para regiões "
            f"proibidas."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: {SAY('RH')} vê todas as colunas; os demais veem "
            f"a mesma tabela sem as colunas de salário — menor esforço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{LAKE_FORMATION} column-level security, ou {LF_TAGS} — política "
            f"central respeitada por Athena, Spectrum e Glue."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: conta B recebe access denied ao ler objetos {SAY('SSE')} "
            f"{KMS} da conta A, mesmo com bucket policy correta?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Falta {KMS} decrypt na key policy da {CMK} para a role da conta B "
            f"— bucket E chave precisam permitir."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: publicar um dataset para parceiros sem expor clientes, "
            f"resistente a ataque de dicionário?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Anonimizar com hash MAIS salt — key {SALTING}. Hash puro de valor "
            f"previsível é reversível por força bruta."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo quinze. No próximo, {SAY('DynamoDB')} e os "
            f"demais data stores. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
