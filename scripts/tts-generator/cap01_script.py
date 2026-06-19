"""Roteiro tratado do Capitulo 1 (IAM) - texto falado, nao e copia literal do HTML.

Decisoes editoriais:
- Blocos de codigo JSON/CLI: parafraseados, nunca lidos literalmente.
- Tabelas: convertidas em comparacoes fluidas, nao lidas celula a celula.
- Lab pratico: mencao breve (nao serve para audio passivo).
- Checkpoint: convertido em dialogo Francisca pergunta / Antonio responde.
- Siglas puras (IAM, STS, SCP, ARN, ABAC, OIDC, SAML, MFA, JWT, CLI, ADFS): say-as characters.
- Termos em ingles (role, Deny, Allow, GitHub, Identity Center...): <phoneme ipa> -
  Antonio/Francisca sao vozes de locale unico (nao multilingual), entao <lang> nao
  funciona; phoneme IPA e a melhor aproximacao possivel sem trocar de voz.
"""

SAY = lambda s: f'<say-as interpret-as="characters">{s}</say-as>'
EMPH = lambda s: f'<emphasis level="moderate">{s}</emphasis>'
BRK = lambda ms: f'<break time="{ms}ms"/>'
PHON = lambda ipa, text: f'<phoneme alphabet="ipa" ph="{ipa}">{text}</phoneme>'

# Termos em ingles recorrentes, com IPA aproximado
ROLE = PHON("ɹoʊl", "role")
DENY = PHON("dɪˈnaɪ", "Deny")
ALLOW = PHON("əˈlaʊ", "Allow")
GITHUB = PHON("ˈɡɪthʌb", "GitHub")
IDENTITY_CENTER = PHON("aɪˈdɛntɪti ˈsɛnɚ", "Identity Center")
INSTANCE_PROFILE = PHON("ˈɪnstəns ˈproʊfaɪl", "Instance Profile")
TRUST_POLICY = PHON("trʌst ˈpɑləsi", "trust policy")
ACCESS_ANALYZER = PHON("ˈæksɛs ˈænəlaɪzɚ", "Access Analyzer")
SECRETS_MANAGER = PHON("ˈsikrəts ˈmænɪdʒɚ", "Secrets Manager")
USER_POOL = PHON("ˈjuzɚ pul", "User Pool")
IDENTITY_POOL = PHON("aɪˈdɛntɪti pul", "Identity Pool")
ACTIVE_DIRECTORY = PHON("ˈæktɪv dɪˈrɛktəri", "Active Directory")
DYNAMODB = PHON("ˈdaɪnəmoʊ diˈbi", "DynamoDB")
AUTO_SCALING = PHON("ˈɔtoʊ ˈskeɪlɪŋ", "Auto Scaling")
LOAD_BALANCERS = PHON("loʊd ˈbælənsɚz", "Load Balancers")
PERMISSION_SET = PHON("pɚˈmɪʃən sɛt", "Permission Set")
PERMISSION_BOUNDARY = PHON("pɚˈmɪʃən ˈbaʊndri", "permission boundary")
EXECUTION_ROLE = PHON("ˌɛksəˈkjuʃən ɹoʊl", "execution role")

BLOCKS = [
    # ---- Abertura ----
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Bem-vindos ao capítulo um da nossa trilha de estudos para o exame "
            f"Solutions Architect Associate. {BRK(400)} "
            f"Hoje vamos explorar o {SAY('IAM')}: identidade, acesso e federação."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Introducao teorica ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('IAM')} é o sistema nervoso de segurança de toda conta da {SAY('AWS')}. "
            f"Cada chamada de {SAY('API')} que você faz passa pelo {SAY('IAM')} antes de chegar "
            f"ao serviço de destino. {BRK(400)} "
            f"Entender o {SAY('IAM')} profundamente é um pré-requisito para todos os outros "
            f"capítulos, especialmente os de segurança, rede e arquitetura multi-conta."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Avaliacao de permissoes ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos começar pela lógica de avaliação de permissões. "
            f"Toda requisição passa por um juiz que avalia todas as políticas aplicáveis. "
            f"Essa ordem de avaliação é determinística e não tem exceções."
            f"{BRK(500)} "
            f"Primeiro: existe um {EMPH(f'{DENY} explícito')} em qualquer política? "
            f"Se sim, o acesso é negado, e isso encerra a avaliação."
            f"{BRK(300)} "
            f"Segundo: existe um {EMPH(f'{ALLOW} explícito')} em alguma política? "
            f"Se sim, o acesso é permitido."
            f"{BRK(300)} "
            f"Terceiro, e último: se nenhuma das anteriores se aplicar, a negação é implícita. "
            f"Ou seja, por padrão, tudo é negado."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Um ponto de atenção importante: em acesso entre contas diferentes, "
            f"chamado de {EMPH('cross-account')}, isso funciona de forma diferente. "
            f"Um único {ALLOW} não é suficiente. Ambas as contas precisam permitir: "
            f"a política de identidade da conta de origem, e a política baseada em recurso, "
            f"ou a {TRUST_POLICY} da {ROLE}, na conta de destino."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Anatomia da policy (parafraseado) ----
    {
        "voice": "francisca",
        "text": (
            f"Na prática, uma política do {SAY('IAM')} é um documento em formato {SAY('JSON')}. "
            f"Pense nela como uma receita com alguns ingredientes principais: "
            f"{BRK(300)} o efeito, que pode ser permitir ou negar; a ação, ou seja, o que pode "
            f"ser feito; o recurso, sobre o qual a ação se aplica; e, opcionalmente, condições "
            f"que restringem quando a regra vale."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Aqui vai uma armadilha clássica que aparece muito na prova: existe "
            f"diferença entre se referir ao bucket em si, e se referir aos objetos dentro do "
            f"bucket. O primeiro é necessário para listar o conteúdo do bucket. O segundo é "
            f"necessário para ler ou gravar um objeto específico. {EMPH('Esquecer um dos dois')} "
            f"formatos gera erro de acesso negado."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Tipos de policy ----
    {
        "voice": "antonio",
        "text": (
            f"Existem cinco tipos principais de política no {SAY('IAM')}, e a prova adora "
            f"testar a diferença entre eles."
            f"{BRK(300)} Políticas baseadas em identidade são anexadas a usuários, grupos ou "
            f"{ROLE}s, e respondem à pergunta: o que esta identidade pode fazer."
            f"{BRK(300)} Políticas baseadas em recurso são anexadas ao próprio recurso, como "
            f"um bucket {SAY('S3')} ou uma fila {SAY('SQS')}, e respondem à pergunta: quem pode "
            f"acessar este recurso. Esse é o {EMPH('único tipo')} que permite acesso entre "
            f"contas diferentes sem precisar de uma {ROLE}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {SAY('SCPs')}, do Organizations, definem o teto máximo de permissões "
            f"de uma conta ou unidade organizacional. Atenção: uma {SAY('SCP')} "
            f"{EMPH('nunca concede')} permissão, ela só limita o que já foi concedido."
            f"{BRK(300)} Permission boundaries funcionam de forma parecida, mas em nível de "
            f"usuário ou {ROLE}: o acesso final é sempre a {EMPH('interseção')} entre o que a "
            f"política de identidade permite e o que o {PERMISSION_BOUNDARY} permite."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- STS ----
    {
        "voice": "antonio",
        "text": (
            f"Por trás de toda credencial temporária na {SAY('AWS')} existe um serviço chamado "
            f"{SAY('STS')}, o Security Token Service. Toda vez que algo assume uma {ROLE}, "
            f"está chamando o {SAY('STS')} por baixo dos panos. "
            f"{BRK(400)} Essas credenciais expiram entre quinze minutos e doze horas, "
            f"dependendo da configuração."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Cross-account scenario (parafraseado) ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos ver um exemplo prático de acesso entre contas. Imagine que a Conta A, "
            f"onde está um desenvolvedor, precisa acessar um bucket {SAY('S3')} que está na "
            f"Conta B."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O processo funciona em três passos. "
            f"Primeiro, na Conta B, é criada uma {ROLE} com uma {TRUST_POLICY} que confia na "
            f"Conta A. {BRK(200)} Segundo, na Conta A, o usuário recebe permissão para "
            f"assumir essa {ROLE} específica na Conta B. {BRK(200)} Terceiro, o usuário na "
            f"Conta A chama a operação Assume {EMPH(ROLE)} do {SAY('STS')}, informando o "
            f"caminho da {ROLE} e, se configurado, um External {SAY('ID')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} E por que o External {SAY('ID')} importa tanto? Ele evita o chamado "
            f"problema do procurador confuso. Imagine uma empresa de auditoria que atende "
            f"vários clientes diferentes usando a mesma ferramenta. {BRK(300)} Sem um "
            f"External {SAY('ID')} exclusivo para cada cliente, uma conta de cliente "
            f"comprometida poderia se aproveitar da ferramenta para acessar a conta de outro "
            f"cliente. O External {SAY('ID')} funciona como um {EMPH('segredo exclusivo')} "
            f"entre você e o seu fornecedor."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Permission boundary aprofundado ----
    {
        "voice": "antonio",
        "text": (
            f"Voltando ao conceito de {PERMISSION_BOUNDARY}: ele define um teto máximo do que "
            f"uma identidade pode fazer, independente de qualquer outra política concedida "
            f"a ela."
            f"{BRK(400)} O uso mais comum é permitir que desenvolvedores criem suas próprias "
            f"{ROLE}s, mas impedir que essas {ROLE}s tenham mais permissão do que o próprio "
            f"desenvolvedor possui. O desenvolvedor tem um {PERMISSION_BOUNDARY} que inclui "
            f"apenas os serviços que ele usa no dia a dia, e qualquer {ROLE} que ele criar "
            f"herda automaticamente esse teto."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Quando usar role (condensado) ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos repassar rapidamente quando usar cada tipo de {ROLE}."
            f"{BRK(300)} Uma aplicação na {SAY('EC2')} que precisa acessar o {SAY('S3')}? "
            f"Use um {INSTANCE_PROFILE}, que é uma {ROLE} anexada à instância."
            f"{BRK(300)} Uma função Lambda que precisa acessar o {DYNAMODB}? "
            f"Use a {EXECUTION_ROLE} da própria Lambda."
            f"{BRK(300)} Login corporativo com {ACTIVE_DIRECTORY}? "
            f"Use o {SAY('IAM')} {IDENTITY_CENTER}, ou federação {SAY('SAML')} direta."
            f"{BRK(300)} E um pipeline de integração contínua, como o {GITHUB} Actions? "
            f"Use um provedor {SAY('OIDC')} combinado com Assume {ROLE} With Web Identity, "
            f"eliminando a necessidade de guardar chaves de acesso nos segredos do "
            f"repositório."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Identity Center ----
    {
        "voice": "antonio",
        "text": (
            f"Falando em {IDENTITY_CENTER}: ele é a solução recomendada para organizações com "
            f"múltiplas contas {SAY('AWS')}. Ele centraliza o login e provisiona acesso "
            f"através de {PERMISSION_SET}s, que são coleções de políticas aplicadas a pares "
            f"de conta e grupo."
            f"{BRK(400)} A grande vantagem sobre a federação {SAY('SAML')} tradicional é a "
            f"flexibilidade: você pode ajustar o acesso por conta e por grupo de forma "
            f"muito mais granular."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Cognito (analogia) ----
    {
        "voice": "francisca",
        "text": (
            f"E quando o assunto são os usuários finais do seu próprio aplicativo, não "
            f"funcionários da empresa, entra o Amazon Cognito."
            f"{BRK(400)} Pense assim: o {USER_POOL} é {EMPH('o porteiro')}, que verifica o "
            f"convite, autenticando quem é o usuário. Já o {IDENTITY_POOL} é "
            f"{EMPH('o crachá temporário')}, que troca esse convite verificado por "
            f"credenciais reais da {SAY('AWS')}."
            f"{BRK(400)} Na prática, os dois trabalham juntos: o {USER_POOL} autentica, emite "
            f"um token, e o {IDENTITY_POOL} troca esse token por credenciais temporárias que "
            f"o aplicativo usa para falar diretamente com o {SAY('S3')} ou o {DYNAMODB}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- ABAC ----
    {
        "voice": "antonio",
        "text": (
            f"Outro conceito importante é o {SAY('ABAC')}, controle baseado em atributos. "
            f"Em vez de criar uma política para cada usuário e cada recurso, você usa tags "
            f"como condição."
            f"{BRK(400)} Por exemplo: em vez de dizer que o desenvolvedor João pode acessar "
            f"o bucket do João, você escreve uma regra genérica: qualquer desenvolvedor pode "
            f"acessar qualquer recurso que tenha a mesma tag de equipe que ele."
            f"{BRK(400)} A vantagem é que isso {EMPH('escala automaticamente')}. Quando um "
            f"novo membro entra na equipe, basta atribuir a tag correta a ele, sem precisar "
            f"editar nenhuma política."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Access Analyzer ----
    {
        "voice": "francisca",
        "text": (
            f"Uma ferramenta que vale a pena conhecer é o {SAY('IAM')} {ACCESS_ANALYZER}. "
            f"Ele analisa automaticamente as suas políticas e identifica recursos que estão "
            f"acessíveis a entidades de fora da sua conta ou organização."
            f"{BRK(400)} Isso inclui buckets {SAY('S3')} públicos, {ROLE}s com {TRUST_POLICY} "
            f"abertas demais, chaves do {SAY('KMS')}, filas {SAY('SQS')}, e até segredos do "
            f"{SECRETS_MANAGER}."
            f"{BRK(300)} É uma forma rápida de descobrir o que está exposto, sem precisar "
            f"revisar política por política manualmente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Conditions + password policy ----
    {
        "voice": "antonio",
        "text": (
            f"Para fechar a parte teórica, vale destacar algumas condições que aparecem com "
            f"frequência na prova: o endereço {SAY('IP')} de origem da requisição, a região "
            f"onde a ação está sendo executada, se a sessão tem autenticação multifator "
            f"ativa, e tags tanto da identidade quanto do recurso, usadas justamente no "
            f"{SAY('ABAC')} que vimos há pouco."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} E um detalhe que costuma confundir: o usuário root de uma conta "
            f"{SAY('AWS')} {EMPH('não pode')} ter políticas do {SAY('IAM')} aplicadas a ele. "
            f"Isso porque, por definição, o root já tem acesso total."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Sinal pratico ----
    {
        "voice": "francisca",
        "text": (
            f"Um sinal prático para reconhecer na prova: quando o enunciado fala em milhões "
            f"de usuários ou aplicativo para celular, pense em Cognito. "
            f"{BRK(300)} Quando fala em funcionários da empresa com {ACTIVE_DIRECTORY}, "
            f"pense em {IDENTITY_CENTER} ou federação {SAY('SAML')}. "
            f"{BRK(300)} Quando fala em um serviço da {SAY('AWS')} acessando outro serviço, "
            f"pense em {ROLE}. "
            f"{BRK(300)} E se o enunciado sugerir guardar uma chave de acesso direto no "
            f"código, desconfie: a resposta certa quase nunca é essa."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Lab (mencao breve) ----
    {
        "voice": "francisca",
        "text": (
            f"No material escrito, este capítulo ainda traz um laboratório prático de uma "
            f"hora e meia, totalmente gratuito, onde você cria uma {ROLE} de leitura no "
            f"{SAY('S3')}, testa um {PERMISSION_BOUNDARY} na prática, e configura o "
            f"{ACCESS_ANALYZER}. Vale a pena fazer com o computador na mão quando puder."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint como dialogo ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. "
            f"{BRK(300)} Primeira pergunta: uma política de identidade permite acesso total "
            f"ao {SAY('S3')}, mas a política do bucket tem um {DENY} explícito. Qual o "
            f"resultado?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Negado. Um {EMPH(f'{DENY} explícito sempre vence')} qualquer {ALLOW}, não "
            f"importa de onde ele venha: política de identidade, política de recurso, "
            f"{SAY('SCP')}, ou qualquer outro tipo."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda pergunta: qual a diferença prática entre uma {ROLE} e um usuário do "
            f"{SAY('IAM')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Um usuário tem credenciais permanentes e identidade própria. Uma {ROLE} é "
            f"assumida temporariamente através do {SAY('STS')}: ninguém é uma {ROLE}, apenas "
            f"a veste por um tempo limitado. As credenciais expiram entre quinze minutos e "
            f"doze horas, e {ROLE}s não têm senha nem chave de acesso fixa."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: para que serve o External {SAY('ID')} numa {ROLE} entre contas "
            f"diferentes?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Ele evita o problema do procurador confuso. Quando um fornecedor gerencia "
            f"várias contas de clientes diferentes, sem um External {SAY('ID')}, uma conta "
            f"comprometida poderia usar o fornecedor para acessar a conta de outro cliente. "
            f"Com um External {SAY('ID')} exclusivo, o fornecedor só consegue assumir a "
            f"{ROLE} se apresentar o segredo correto."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: qual a diferença entre o {USER_POOL} e o {IDENTITY_POOL} do "
            f"Cognito?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O {USER_POOL} autentica o usuário e emite tokens, respondendo à pergunta: "
            f"quem é você. O {IDENTITY_POOL} troca esse token por credenciais temporárias da "
            f"{SAY('AWS')}, respondendo à pergunta: o que você pode fazer na {SAY('AWS')}. "
            f"{USER_POOL} é o porteiro. {IDENTITY_POOL} é o crachá temporário."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: um desenvolvedor tem acesso total de administrador, mas um "
            f"{PERMISSION_BOUNDARY} que só permite leitura no {SAY('S3')}. O que ele "
            f"consegue fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Apenas a leitura no {SAY('S3')}. O {PERMISSION_BOUNDARY} define o teto, e o "
            f"acesso final é sempre a interseção entre a política e o {PERMISSION_BOUNDARY}. "
            f"Mesmo com acesso total de administrador na política, o {PERMISSION_BOUNDARY} "
            f"limita o que de fato funciona."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como garantir que uma instância {SAY('EC2')} numa sub-rede "
            f"privada acesse a {SAY('AWS')} sem chave de acesso e sem sair para a "
            f"internet?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Combine duas coisas: um {INSTANCE_PROFILE}, que é uma {ROLE} anexada à "
            f"{SAY('EC2')}, para autenticação sem chaves fixas. E um {SAY('VPC')} Endpoint, "
            f"para que o tráfego para o serviço da {SAY('AWS')}, como o {SAY('S3')}, nunca "
            f"precise sair para a internet pública."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Encerramento ----
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo um. No próximo, vamos mergulhar em {SAY('EC2')}, "
            f"{AUTO_SCALING} e {LOAD_BALANCERS}. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
