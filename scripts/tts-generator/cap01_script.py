"""Roteiro tratado do Capitulo 1 (IAM) - texto falado, nao e copia literal do HTML.

Decisoes editoriais:
- Blocos de codigo JSON/CLI: parafraseados, nunca lidos literalmente.
- Tabelas: convertidas em comparacoes fluidas, nao lidas celula a celula.
- Lab pratico: mencao breve (nao serve para audio passivo).
- Checkpoint: convertido em dialogo Francisca pergunta / Antonio responde.
- Siglas puras (IAM, STS, SCP, ARN, ABAC, OIDC, SAML, MFA, JWT, CLI, ADFS): say-as characters.
- Termos compostos ingles-AWS (DynamoDB, CloudTrail, Cognito, Lambda): texto plano, voz neural bilingue.
"""

SAY = lambda s: f'<say-as interpret-as="characters">{s}</say-as>'
EMPH = lambda s: f'<emphasis level="moderate">{s}</emphasis>'
BRK = lambda ms: f'<break time="{ms}ms"/>'

BLOCKS = [
    # ---- Abertura ----
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Bem-vindos ao capitulo um da nossa trilha de estudos para o exame "
            f"Solutions Architect Associate. {BRK(400)} "
            f"Hoje vamos explorar o {SAY('IAM')}: identidade, acesso e federacao."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Introducao teorica ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('IAM')} e o sistema nervoso de seguranca de toda conta da {SAY('AWS')}. "
            f"Cada chamada de {SAY('API')} que voce faz passa pelo {SAY('IAM')} antes de chegar "
            f"ao servico de destino. {BRK(400)} "
            f"Entender o {SAY('IAM')} profundamente e um pre-requisito para todos os outros "
            f"capitulos, especialmente os de seguranca, rede e arquitetura multi-conta."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Avaliacao de permissoes ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos comecar pela logica de avaliacao de permissoes. "
            f"Toda requisicao passa por um juiz que avalia todas as politicas aplicaveis. "
            f"Essa ordem de avaliacao e deterministica e nao tem excecoes."
            f"{BRK(500)} "
            f"Primeiro: existe um {EMPH('Deny explicito')} em qualquer politica? "
            f"Se sim, o acesso e negado, e isso encerra a avaliacao."
            f"{BRK(300)} "
            f"Segundo: existe um {EMPH('Allow explicito')} em alguma politica? "
            f"Se sim, o acesso e permitido."
            f"{BRK(300)} "
            f"Terceiro, e ultimo: se nenhuma das anteriores se aplicar, a negacao e implicita. "
            f"Ou seja, por padrao, tudo e negado."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Um ponto de atencao importante: em acesso entre contas diferentes, "
            f"chamado de {EMPH('cross-account')}, isso funciona de forma diferente. "
            f"Um unico Allow nao e suficiente. Ambas as contas precisam permitir: "
            f"a politica de identidade da conta de origem, e a politica baseada em recurso, "
            f"ou a trust policy da role, na conta de destino."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Anatomia da policy (parafraseado) ----
    {
        "voice": "francisca",
        "text": (
            f"Na pratica, uma politica do {SAY('IAM')} e um documento em formato {SAY('JSON')}. "
            f"Pense nela como uma receita com alguns ingredientes principais: "
            f"{BRK(300)} o efeito, que pode ser permitir ou negar; a acao, ou seja, o que pode "
            f"ser feito; o recurso, sobre o qual a acao se aplica; e, opcionalmente, condicoes "
            f"que restringem quando a regra vale."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Aqui vai uma armadilha classica que aparece muito na prova: existe "
            f"diferenca entre se referir ao bucket em si, e se referir aos objetos dentro do "
            f"bucket. O primeiro e necessario para listar o conteudo do bucket. O segundo e "
            f"necessario para ler ou gravar um objeto especifico. {EMPH('Esquecer um dos dois')} "
            f"formatos gera erro de acesso negado."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Tipos de policy ----
    {
        "voice": "antonio",
        "text": (
            f"Existem cinco tipos principais de politica no {SAY('IAM')}, e a prova adora "
            f"testar a diferenca entre eles."
            f"{BRK(300)} Politicas baseadas em identidade sao anexadas a usuarios, grupos ou "
            f"roles, e respondem a pergunta: o que esta identidade pode fazer."
            f"{BRK(300)} Politicas baseadas em recurso sao anexadas ao proprio recurso, como "
            f"um bucket {SAY('S3')} ou uma fila {SAY('SQS')}, e respondem a pergunta: quem pode "
            f"acessar este recurso. Esse e o {EMPH('unico tipo')} que permite acesso entre "
            f"contas diferentes sem precisar de uma role."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {SAY('SCPs')}, do Organizations, definem o teto maximo de permissoes "
            f"de uma conta ou unidade organizacional. Atencao: uma {SAY('SCP')} "
            f"{EMPH('nunca concede')} permissao, ela so limita o que ja foi concedido."
            f"{BRK(300)} Permission boundaries funcionam de forma parecida, mas em nivel de "
            f"usuario ou role: o acesso final e sempre a {EMPH('intersecao')} entre o que a "
            f"politica de identidade permite e o que o boundary permite."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- STS ----
    {
        "voice": "antonio",
        "text": (
            f"Por tras de toda credencial temporaria na {SAY('AWS')} existe um servico chamado "
            f"{SAY('STS')}, o Security Token Service. Toda vez que algo assume uma role, "
            f"esta chamando o {SAY('STS')} por baixo dos panos. "
            f"{BRK(400)} Essas credenciais expiram entre quinze minutos e doze horas, "
            f"dependendo da configuracao."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Cross-account scenario (parafraseado) ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos ver um exemplo pratico de acesso entre contas. Imagine que a Conta A, "
            f"onde esta um desenvolvedor, precisa acessar um bucket {SAY('S3')} que esta na "
            f"Conta B."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O processo funciona em tres passos. "
            f"Primeiro, na Conta B, e criada uma role com uma trust policy que confia na "
            f"Conta A. {BRK(200)} Segundo, na Conta A, o usuario recebe permissao para "
            f"assumir essa role especifica na Conta B. {BRK(200)} Terceiro, o usuario na "
            f"Conta A chama a operacao Assume Role do {SAY('STS')}, informando o caminho "
            f"da role e, se configurado, um External {SAY('ID')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} E por que o External {SAY('ID')} importa tanto? Ele evita o chamado "
            f"problema do procurador confuso. Imagine uma empresa de auditoria que atende "
            f"varios clientes diferentes usando a mesma ferramenta. {BRK(300)} Sem um "
            f"External {SAY('ID')} exclusivo para cada cliente, uma conta de cliente "
            f"comprometida poderia se aproveitar da ferramenta para acessar a conta de outro "
            f"cliente. O External {SAY('ID')} funciona como um {EMPH('segredo exclusivo')} "
            f"entre voce e o seu fornecedor."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Permission boundary aprofundado ----
    {
        "voice": "antonio",
        "text": (
            f"Voltando ao conceito de permission boundary: ele define um teto maximo do que "
            f"uma identidade pode fazer, independente de qualquer outra politica concedida "
            f"a ela."
            f"{BRK(400)} O uso mais comum e permitir que desenvolvedores criem suas proprias "
            f"roles, mas impedir que essas roles tenham mais permissao do que o proprio "
            f"desenvolvedor possui. O desenvolvedor tem um boundary que inclui apenas os "
            f"servicos que ele usa no dia a dia, e qualquer role que ele criar herda "
            f"automaticamente esse teto."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Quando usar role (condensado) ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos repassar rapidamente quando usar cada tipo de role."
            f"{BRK(300)} Uma aplicacao na {SAY('EC2')} que precisa acessar o {SAY('S3')}? "
            f"Use um Instance Profile, que e uma role anexada a instancia."
            f"{BRK(300)} Uma funcao Lambda que precisa acessar o DynamoDB? "
            f"Use a execution role da propria Lambda."
            f"{BRK(300)} Login corporativo com Active Directory? "
            f"Use o {SAY('IAM')} Identity Center, ou federacao {SAY('SAML')} direta."
            f"{BRK(300)} E um pipeline de integracao continua, como o GitHub Actions? "
            f"Use um provedor {SAY('OIDC')} combinado com Assume Role With Web Identity, "
            f"eliminando a necessidade de guardar chaves de acesso nos segredos do "
            f"repositorio."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Identity Center ----
    {
        "voice": "antonio",
        "text": (
            f"Falando em Identity Center: ele e a solucao recomendada para organizacoes com "
            f"multiplas contas {SAY('AWS')}. Ele centraliza o login e provisiona acesso "
            f"atraves de Permission Sets, que sao colecoes de politicas aplicadas a pares "
            f"de conta e grupo."
            f"{BRK(400)} A grande vantagem sobre a federacao {SAY('SAML')} tradicional e a "
            f"flexibilidade: voce pode ajustar o acesso por conta e por grupo de forma "
            f"muito mais granular."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Cognito (analogia) ----
    {
        "voice": "francisca",
        "text": (
            f"E quando o assunto sao os usuarios finais do seu proprio aplicativo, nao "
            f"funcionarios da empresa, entra o Amazon Cognito."
            f"{BRK(400)} Pense assim: o User Pool e {EMPH('o porteiro')}, que verifica o "
            f"convite, autenticando quem e o usuario. Ja o Identity Pool e "
            f"{EMPH('o crache temporario')}, que troca esse convite verificado por "
            f"credenciais reais da {SAY('AWS')}."
            f"{BRK(400)} Na pratica, os dois trabalham juntos: o User Pool autentica, emite "
            f"um token, e o Identity Pool troca esse token por credenciais temporarias que "
            f"o aplicativo usa para falar diretamente com o {SAY('S3')} ou o DynamoDB."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- ABAC ----
    {
        "voice": "antonio",
        "text": (
            f"Outro conceito importante e o {SAY('ABAC')}, controle baseado em atributos. "
            f"Em vez de criar uma politica para cada usuario e cada recurso, voce usa tags "
            f"como condicao."
            f"{BRK(400)} Por exemplo: em vez de dizer que o desenvolvedor Joao pode acessar "
            f"o bucket do Joao, voce escreve uma regra generica: qualquer desenvolvedor pode "
            f"acessar qualquer recurso que tenha a mesma tag de equipe que ele."
            f"{BRK(400)} A vantagem e que isso {EMPH('escala automaticamente')}. Quando um "
            f"novo membro entra na equipe, basta atribuir a tag correta a ele, sem precisar "
            f"editar nenhuma politica."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Access Analyzer ----
    {
        "voice": "francisca",
        "text": (
            f"Uma ferramenta que vale a pena conhecer e o {SAY('IAM')} Access Analyzer. "
            f"Ele analisa automaticamente as suas politicas e identifica recursos que estao "
            f"acessiveis a entidades de fora da sua conta ou organizacao."
            f"{BRK(400)} Isso inclui buckets {SAY('S3')} publicos, roles com trust policies "
            f"abertas demais, chaves do {SAY('KMS')}, filas {SAY('SQS')}, e ate segredos do "
            f"Secrets Manager."
            f"{BRK(300)} E uma forma rapida de descobrir o que esta exposto, sem precisar "
            f"revisar politica por politica manualmente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Conditions + password policy ----
    {
        "voice": "antonio",
        "text": (
            f"Para fechar a parte teorica, vale destacar algumas condicoes que aparecem com "
            f"frequencia na prova: o endereco {SAY('IP')} de origem da requisicao, a regiao "
            f"onde a acao esta sendo executada, se a sessao tem autenticacao multifator "
            f"ativa, e tags tanto da identidade quanto do recurso, usadas justamente no "
            f"{SAY('ABAC')} que vimos ha pouco."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} E um detalhe que costuma confundir: o usuario root de uma conta "
            f"{SAY('AWS')} {EMPH('nao pode')} ter politicas do {SAY('IAM')} aplicadas a ele. "
            f"Isso porque, por definicao, o root ja tem acesso total."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Sinal pratico ----
    {
        "voice": "francisca",
        "text": (
            f"Um sinal pratico para reconhecer na prova: quando o enunciado fala em milhoes "
            f"de usuarios ou aplicativo para celular, pense em Cognito. "
            f"{BRK(300)} Quando fala em funcionarios da empresa com Active Directory, pense "
            f"em Identity Center ou federacao {SAY('SAML')}. "
            f"{BRK(300)} Quando fala em um servico da {SAY('AWS')} acessando outro servico, "
            f"pense em role. "
            f"{BRK(300)} E se o enunciado sugerir guardar uma chave de acesso direto no "
            f"codigo, desconfie: a resposta certa quase nunca e essa."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Lab (mencao breve) ----
    {
        "voice": "francisca",
        "text": (
            f"No material escrito, este capitulo ainda traz um laboratorio pratico de uma "
            f"hora e meia, totalmente gratuito, onde voce cria uma role de leitura no "
            f"{SAY('S3')}, testa um permission boundary na pratica, e configura o Access "
            f"Analyzer. Vale a pena fazer com o computador na mao quando puder."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint como dialogo ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisao. "
            f"{BRK(300)} Primeira pergunta: uma politica de identidade permite acesso total "
            f"ao {SAY('S3')}, mas a politica do bucket tem um Deny explicito. Qual o "
            f"resultado?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Negado. Um {EMPH('Deny explicito sempre vence')} qualquer Allow, nao importa "
            f"de onde ele venha: politica de identidade, politica de recurso, {SAY('SCP')}, "
            f"ou qualquer outro tipo."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda pergunta: qual a diferenca pratica entre uma role e um usuario do "
            f"{SAY('IAM')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Um usuario tem credenciais permanentes e identidade propria. Uma role e "
            f"assumida temporariamente atraves do {SAY('STS')}: ninguem e uma role, apenas "
            f"a veste por um tempo limitado. As credenciais expiram entre quinze minutos e "
            f"doze horas, e roles nao tem senha nem chave de acesso fixa."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: para que serve o External {SAY('ID')} numa role entre contas "
            f"diferentes?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Ele evita o problema do procurador confuso. Quando um fornecedor gerencia "
            f"varias contas de clientes diferentes, sem um External {SAY('ID')}, uma conta "
            f"comprometida poderia usar o fornecedor para acessar a conta de outro cliente. "
            f"Com um External {SAY('ID')} exclusivo, o fornecedor so consegue assumir a role "
            f"se apresentar o segredo correto."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: qual a diferenca entre o User Pool e o Identity Pool do "
            f"Cognito?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O User Pool autentica o usuario e emite tokens, respondendo a pergunta: quem "
            f"e voce. O Identity Pool troca esse token por credenciais temporarias da "
            f"{SAY('AWS')}, respondendo a pergunta: o que voce pode fazer na {SAY('AWS')}. "
            f"User Pool e o porteiro. Identity Pool e o crache temporario."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: um desenvolvedor tem acesso total de administrador, mas um permission "
            f"boundary que so permite leitura no {SAY('S3')}. O que ele consegue "
            f"fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Apenas a leitura no {SAY('S3')}. O permission boundary define o teto, e o "
            f"acesso final e sempre a intersecao entre a politica e o boundary. Mesmo com "
            f"acesso total de administrador na politica, o boundary limita o que de fato "
            f"funciona."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a ultima: como garantir que uma instancia {SAY('EC2')} numa sub-rede "
            f"privada acesse a {SAY('AWS')} sem chave de acesso e sem sair para a "
            f"internet?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Combine duas coisas: um Instance Profile, que e uma role anexada a "
            f"{SAY('EC2')}, para autenticacao sem chaves fixas. E um {SAY('VPC')} Endpoint, "
            f"para que o trafego para o servico da {SAY('AWS')}, como o {SAY('S3')}, nunca "
            f"precise sair para a internet publica."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Encerramento ----
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capitulo um. No proximo, vamos mergulhar em {SAY('EC2')}, "
            f"Auto Scaling e Load Balancers. Ate a proxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
