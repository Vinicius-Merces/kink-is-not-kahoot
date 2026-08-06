"""Roteiro DVA-C02 Capitulo 7 — Seguranca para devs: IAM, STS, KMS e segredos."""

from glossary import SAY, EMPH, BRK, PHON

ASSUME_ROLE = PHON("əˈsum ɹoʊl", "AssumeRole")
TRUST_POLICY = PHON("trʌst ˈpɑləsi", "trust policy")
POLICY_SIMULATOR = PHON("ˈpɑləsi ˈsɪmjəleɪtɚ", "Policy Simulator")
GENERATE_DATA_KEY = PHON("ˈdʒɛnəreɪt ˈdeɪtə ki", "GenerateDataKey")
ENVELOPE = PHON("ˈɛnvəloʊp ɪnˈkrɪpʃən", "envelope encryption")
DATA_KEY = PHON("ˈdeɪtə ki", "data key")
SECRETS_MANAGER = PHON("ˈsikrəts ˈmænɪdʒɚ", "Secrets Manager")
PARAMETER_STORE = PHON("pəˈræmɪtɚ stɔr", "Parameter Store")
PRIVATE_CA = PHON("ˈpraɪvət si eɪ", "Private CA")
PII = PHON("pi aɪ aɪ", "PII")
PHI = PHON("pi eɪtʃ aɪ", "PHI")
CMK = PHON("si ɛm keɪ", "CMK")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo sete: segurança para devs — {SAY('IAM')}, {SAY('STS')}, "
            f"{SAY('KMS')} e segredos. O domínio dois vale vinte e seis por "
            f"cento da prova, e este capítulo é o coração dele."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- IAM/STS ----
    {
        "voice": "antonio",
        "text": (
            f"{SAY('IAM')} na prática do desenvolvedor. Policies em "
            f"{SAY('JSON')} com effect, action, resource e condition — e a "
            f"avaliação: deny explícito vence allow, que vence o deny "
            f"implícito. Acesso temporário entre contas: {SAY('STS')} "
            f"{ASSUME_ROLE} — a role na conta de destino precisa da "
            f"{TRUST_POLICY} confiando no chamador, e o chamador precisa da "
            f"permissão de assumir. Para depurar 'por que o acesso foi negado', "
            f"a ferramenta citada é o {SAY('IAM')} {POLICY_SIMULATOR}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- KMS ----
    {
        "voice": "francisca",
        "text": (
            f"{SAY('KMS')} — e o limite de QUATRO kilobytes que define tudo. "
            f"Encrypt e Decrypt criptografam direto com a {CMK} — mas SÓ até "
            f"quatro kilobytes. Para qualquer coisa maior, {ENVELOPE}: chame "
            f"{GENERATE_DATA_KEY}, receba a {DATA_KEY} em claro e a versão "
            f"criptografada; cifre o dado grande LOCALMENTE com a chave em "
            f"claro, descarte-a, e guarde a versão criptografada junto do "
            f"dado. Para ler: Decrypt na {DATA_KEY} e decifra local. 'Como "
            f"criptografar cem megabytes com {SAY('KMS')}' NUNCA é Encrypt "
            f"direto."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Rotação: customer managed keys aceitam rotação "
            f"automática anual — habilitável e desabilitável, como o guide "
            f"cita; as versões antigas continuam decifrando os dados antigos. "
            f"Chave com material importado NÃO tem rotação automática."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Certificados ----
    {
        "voice": "antonio",
        "text": (
            f"Certificados. O {SAY('ACM')} emite e RENOVA certificados "
            f"{SAY('TLS')} públicos de graça — para {SAY('ALB')}, CloudFront e "
            f"{SAY('API')} Gateway; a renovação automática é o motivo de "
            f"prova. O {SAY('AWS')} {PRIVATE_CA} emite certificados PRIVADOS "
            f"para comunicação interna serviço a serviço — 'certificados para "
            f"hosts internos que não são públicos'. Para desenvolvimento, "
            f"self-signed resolve local — nunca em produção."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Segredos ----
    {
        "voice": "francisca",
        "text": (
            f"{SECRETS_MANAGER} versus {PARAMETER_STORE}. {SECRETS_MANAGER}: "
            f"pago, com ROTAÇÃO automática nativa e integração com {SAY('RDS')} "
            f"— a palavra 'rotação automática de credenciais' aponta para ele. "
            f"{PARAMETER_STORE}: gratuito no tier standard, parâmetros "
            f"hierárquicos de configuração, Secure String com {SAY('KMS')} — "
            f"mas sem rotação nativa."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Dados sensiveis ----
    {
        "voice": "antonio",
        "text": (
            f"Dados sensíveis no código — a task três do domínio. "
            f"Classificação: {PII} identifica a pessoa — {SAY('CPF')}, e-mail; "
            f"{PHI} são dados de saúde — tratamento reforçado. As três regras "
            f"práticas: variáveis de ambiente da Lambda são criptografadas com "
            f"{SAY('KMS')} — use {CMK} própria para valores sensíveis, ou "
            f"melhor, busque do {SECRETS_MANAGER} em runtime. NUNCA logue dado "
            f"sensível — sanitize antes; o '{SAY('CPF')} aparecendo no "
            f"CloudWatch Logs' se resolve no código. E segredo commitado no "
            f"Git: REVOGUE e rotacione imediatamente — remover do histórico "
            f"não basta, a chave já vazou."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: criptografar payloads de cinquenta megabytes "
            f"com uma {CMK}. Qual fluxo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{GENERATE_DATA_KEY}, cifrar local com a {DATA_KEY} em claro, "
            f"descartá-la e guardar a versão criptografada — {ENVELOPE}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: credenciais do {SAY('RDS')} girando a cada trinta dias "
            f"sem intervenção?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{SECRETS_MANAGER} com rotação automática — integração nativa com o {SAY('RDS')}.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: certificados {SAY('TLS')} para microsserviços internos "
            f"que não são expostos na internet?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{SAY('AWS')} {PRIVATE_CA} — autoridade certificadora privada para hosts internos.",
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo sete. No próximo, identidade de usuários: "
            f"Amazon Cognito. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
