"""Roteiro tratado do Capitulo 19 (Organizations, Control Tower) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

MANAGEMENT_ACCOUNT = PHON("ˈmænɪdʒmənt əˈkaʊnt", "Management account")
MEMBER_ACCOUNTS = PHON("ˈmɛmbɚ əˈkaʊnts", "Member accounts")
ORGANIZATIONAL_UNITS = PHON("ˌɔrɡənəˈzeɪʃənəl ˈjunɪts", "Organizational Units")
SCP = PHON("ɛs si pi", "SCP")
DENY_LIST = PHON("dɪˈnaɪ lɪst", "deny-list")
ALLOW_LIST = PHON("əˈlaʊ lɪst", "allow-list")
FULL_AWS_ACCESS = PHON("fʊl eɪ dʌbəlju ɛs ˈæksɛs", "FullAWSAccess")
PERMISSION_BOUNDARY = PHON("pɚˈmɪʃən ˈbaʊndri", "permission boundary")
CONTROL_TOWER = PHON("kənˈtroʊl ˈtaʊɚ", "Control Tower")
LANDING_ZONE = PHON("ˈlændɪŋ zoʊn", "Landing Zone")
GUARDRAILS_PREVENTIVE = PHON("ˈɡɑrdreɪlz prɪˈvɛntɪv", "guardrail preventivo")
GUARDRAILS_DETECTIVE = PHON("ˈɡɑrdreɪlz dɪˈtɛktɪv", "guardrail detetivo")
ACCOUNT_FACTORY = PHON("əˈkaʊnt ˈfæktəri", "Account Factory")
CONSOLIDATED_BILLING = PHON("kənˈsɑlɪdeɪtɪd ˈbɪlɪŋ", "Consolidated Billing")
SAVINGS_PLANS = PHON("ˈseɪvɪŋz plænz", "Savings Plans")
VOLUME_PRICING_TIERS = PHON("ˈvɑljum ˈpraɪsɪŋ tɪrz", "volume pricing tiers")
RAM = PHON("ɑr eɪ ɛm", "RAM")
RESOURCE_ACCESS_MANAGER = PHON("ˈrisɔrs ˈæksɛs ˈmænɪdʒɚ", "Resource Access Manager")
TAG_POLICIES = PHON("tæɡ ˈpɑləsiz", "Tag Policies")
COST_ALLOCATION_TAGS = PHON("kɔst ˌæləˈkeɪʃən tæɡz", "Cost Allocation Tags")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dezenove: A W S Organizations, Control Tower e "
            f"governança multi-conta. Empresas reais raramente vivem numa "
            f"única conta — usam múltiplas contas para isolar produção de "
            f"desenvolvimento, separar times, e limitar o raio de impacto "
            f"de erros e incidentes."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Estrutura Organizations ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre a estrutura do A W S Organizations: a "
            f"{MANAGEMENT_ACCOUNT} é a conta raiz — paga a fatura "
            f"consolidada, cria e gerencia as demais contas. Pela boa "
            f"prática, ela {EMPH('não deve')} hospedar nenhum "
            f"{SAY('workload')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {MEMBER_ACCOUNTS} são contas individuais — "
            f"produção, desenvolvimento, segurança — isoladas entre si "
            f"por padrão, cada uma com seu próprio {SAY('IAM')}. As "
            f"{ORGANIZATIONAL_UNITS}, ou {SAY('OUs')}, são pastas que "
            f"agrupam contas com necessidades de política semelhantes — "
            f"{SCP}s aplicadas numa {SAY('OU')} são herdadas por todas as "
            f"contas dentro dela. E o {SAY('Root')} é o nível mais alto da "
            f"árvore — {SCP}s ali afetam toda a organização."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- SCPs ----
    {
        "voice": "antonio",
        "text": (
            f"{SCP}s definem o {EMPH('teto máximo de permissões')} para "
            f"todas as identidades dentro das contas afetadas, incluindo "
            f"administradores — mas, diferente de uma política "
            f"{SAY('IAM')}, uma {SCP} {EMPH('nunca concede')} nada por si "
            f"só."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Por exemplo, uma {SCP} do tipo {DENY_LIST} pode "
            f"negar o uso de {SAY('EC2')} fora de uma região específica, "
            f"com uma condição na região solicitada. O resultado: "
            f"ninguém na conta usa {SAY('EC2')} fora dali — nem mesmo um "
            f"administrador com acesso total."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Armadilha importante: uma {SCP} do tipo "
            f"{ALLOW_LIST}, aplicada no {SAY('Root')}, substitui a "
            f"política padrão {FULL_AWS_ACCESS} — a partir daí, "
            f"{EMPH('nenhuma')} ação fora dessa lista funciona em conta "
            f"alguma, mesmo que a política {SAY('IAM')} do usuário "
            f"permita. {SCP} e política {SAY('IAM')} ou "
            f"{PERMISSION_BOUNDARY} precisam {EMPH('ambas')} permitir — é "
            f"uma interseção de permissões, não uma soma."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Control Tower ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre o A W S {CONTROL_TOWER}: a {LANDING_ZONE} é um "
            f"ambiente multi-conta pré-configurado — cria automaticamente "
            f"as {SAY('OUs')} de Segurança e {SAY('Sandbox')}, contas "
            f"dedicadas de arquivo de log e auditoria, e a estrutura "
            f"básica do Organizations."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {GUARDRAILS_PREVENTIVE}s são implementados via "
            f"{SCP} — {EMPH('impedem')} que uma ação proibida ocorra, "
            f"como desabilitar o CloudTrail. {GUARDRAILS_DETECTIVE}s são "
            f"implementados via regras do A W S Config — "
            f"{EMPH('identificam')} recursos não conformes depois do "
            f"fato, como um bucket {SAY('S3')} público. E o "
            f"{ACCOUNT_FACTORY} provisiona novas contas-membro já com a "
            f"configuração padrão de rede e segurança da organização."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Faturamento ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre faturamento consolidado: o {CONSOLIDATED_BILLING} dá "
            f"uma fatura única para toda a organização, facilitando "
            f"rateio interno e visibilidade central de custos."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Descontos de instâncias Reservadas e "
            f"{SAVINGS_PLANS} comprados numa conta se aplicam "
            f"automaticamente ao uso elegível de {EMPH('qualquer')} conta "
            f"da organização — esse compartilhamento pode ser desligado "
            f"por conta, se necessário. E {VOLUME_PRICING_TIERS}, "
            f"descontos por volume de {SAY('S3')} ou CloudFront, são "
            f"calculados pelo uso agregado de toda a organização, não "
            f"conta a conta."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- AWS RAM e tags ----
    {
        "voice": "antonio",
        "text": (
            f"O A W S {RESOURCE_ACCESS_MANAGER}, ou {RAM}, compartilha "
            f"recursos específicos — {SAY('subnets')} de {SAY('VPC')}, "
            f"{SAY('Transit Gateways')}, licenças — entre contas da "
            f"organização, sem duplicar o recurso nem montar "
            f"{SAY('peering')} ou políticas cruzadas para cada caso."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Combinado com uma estratégia de {SAY('tags')} "
            f"consistente — centro de custo, ambiente, responsável — "
            f"aplicada via {TAG_POLICIES} do Organizations, e "
            f"{COST_ALLOCATION_TAGS} ativadas no {SAY('Billing')}, a "
            f"empresa consegue fatiar o relatório de custo e uso por "
            f"equipe ou projeto, mesmo dentro de uma fatura consolidada "
            f"única."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito traz um laboratório de trinta minutos, "
            f"gratuito, onde você cria uma {SAY('OU')} chamada "
            f"{SAY('Sandbox')}, cria uma {SCP} que nega o lançamento de "
            f"instâncias fora de uma lista pequena de tipos, e anexa essa "
            f"{SCP} à {SAY('OU')}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (5 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: um usuário com a política "
            f"{SAY('AdministratorAccess')} não consegue usar o "
            f"{SAY('S3')}, mesmo a política permitindo explicitamente. "
            f"Qual a causa mais provável?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Uma {SCP} aplicada à conta ou {SAY('OU')} está negando, ou "
            f"não incluindo, a ação de {SAY('S3')}. {SCP}s são avaliadas "
            f"em conjunto com as políticas {SAY('IAM')} — se a {SCP} não "
            f"permite, nenhuma política {SAY('IAM')} consegue sobrepor "
            f"isso."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: a empresa quer garantir que nenhuma conta possa "
            f"desabilitar o CloudTrail, mesmo administradores locais. "
            f"Qual mecanismo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Um {GUARDRAILS_PREVENTIVE}, do {CONTROL_TOWER}, "
            f"implementado via {SCP}, negando ações de parar ou deletar o "
            f"{SAY('trail')} em todas as contas-membro."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: como identificar, de forma centralizada, todas "
            f"as contas com buckets {SAY('S3')} públicos, sem bloquear "
            f"preventivamente?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Um {GUARDRAILS_DETECTIVE}, do {CONTROL_TOWER}, uma regra do "
            f"A W S Config que verifica a configuração de bloqueio de "
            f"acesso público em todas as contas e reporta as não "
            f"conformidades."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: a empresa comprou {SAVINGS_PLANS} na conta de "
            f"produção. As instâncias da conta de desenvolvimento também "
            f"recebem o desconto automaticamente?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Sim, por padrão. {SAVINGS_PLANS}, assim como Reservadas, "
            f"compartilham o desconto com todas as contas da organização "
            f"com {CONSOLIDATED_BILLING} habilitado, a menos que esse "
            f"compartilhamento seja explicitamente desligado."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: o time de rede centralizado precisa "
            f"compartilhar {SAY('subnets')} de uma {SAY('VPC')} com cinco "
            f"contas de aplicação diferentes, sem que elas gerenciem a "
            f"{SAY('VPC')}. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {RESOURCE_ACCESS_MANAGER} — compartilha "
            f"{SAY('subnets')} específicas da {SAY('VPC')} com as contas "
            f"da organização; as contas participantes lançam recursos "
            f"nessas {SAY('subnets')}, mas a {SAY('VPC')} continua "
            f"gerenciada centralmente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dezenove. No último capítulo, "
            f"vamos falar do A W S Well-Architected Framework. Até a "
            f"próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
