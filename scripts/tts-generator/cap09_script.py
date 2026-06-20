"""Roteiro tratado do Capitulo 9 (Seguranca) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

AWS_OWNED = PHON("eɪ dʌbəlju ɛs ˈoʊnd", "AWS-owned")
AWS_MANAGED = PHON("eɪ dʌbəlju ɛs ˈmænɪdʒd", "AWS-managed")
CUSTOMER_MANAGED = PHON("ˈkʌstəmɚ ˈmænɪdʒd", "Customer-managed")
MULTI_REGION_KEYS = PHON("ˈmʌlti ˈridʒən kiz", "Multi-Region Keys")
ENVELOPE_ENCRYPTION = PHON("ˈɛnvəloʊp ɪnˈkrɪpʃən", "envelope encryption")
DATA_KEY = PHON("ˈdeɪtə ki", "Data Key")
CLOUDHSM = PHON("klaʊd eɪtʃ ɛs ɛm", "CloudHSM")
FIPS = PHON("fɪps", "FIPS")
SECRETS_MANAGER = PHON("ˈsikrəts ˈmænɪdʒɚ", "Secrets Manager")
PARAMETER_STORE = PHON("pəˈræmɪtɚ stɔr", "Parameter Store")
ENCRYPTION_IN_TRANSIT = PHON("ɪnˈkrɪpʃən ɪn ˈtrænzɪt", "Encryption in Transit")
PRIVATE_CA = PHON("ˈpraɪvət si eɪ", "Private CA")
MTLS = PHON("ɛm ti ɛl ɛs", "mTLS")
SHIELD_STANDARD = PHON("ʃild ˈstændɚd", "Shield Standard")
SHIELD_ADVANCED = PHON("ʃild ədˈvænst", "Shield Advanced")
DRT = PHON("di ɑr ti", "DRT")
GUARDDUTY = PHON("ɡɑrd ˈduti", "GuardDuty")
INSPECTOR = PHON("ɪnˈspɛktɚ", "Inspector")
MACIE = PHON("ˈmeɪsi", "Macie")
SECURITY_HUB = PHON("sɪˈkjʊrəti hʌb", "Security Hub")
DETECTIVE = PHON("dɪˈtɛktɪv", "Detective")
ARTIFACT = PHON("ˈɑrtəfækt", "Artifact")
MANAGED_RULE_GROUPS = PHON("ˈmænɪdʒd rul ɡrups", "Managed Rule Groups")
MANAGED_RULE_GROUP = PHON("ˈmænɪdʒd rul ɡrup", "Managed Rule Group")
RATE_BASED_RULES = PHON("reɪt beɪst rulz", "Rate-based rules")
GEO_MATCH = PHON("ˈdʒioʊ mætʃ", "Geo-match")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo nove: segurança. Vamos cobrir K M S, criptografia, e a "
            f"defesa em camadas com Shield e W A F."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- KMS ----
    {
        "voice": "antonio",
        "text": (
            f"O K M S, Key Management Service, gerencia chaves criptográficas "
            f"usadas em praticamente todos os serviços da {SAY('AWS')}. "
            f"Existem chaves simétricas, o padrão para a maioria dos casos, e "
            f"assimétricas, com par público e privado, para assinatura ou "
            f"criptografia entre sistemas externos."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Três tipos de chave: {AWS_OWNED}, invisível para "
            f"você, sem auditoria, grátis. {AWS_MANAGED}, visível na sua "
            f"conta, rotação automática anual, auditável no CloudTrail, "
            f"também grátis. E {CUSTOMER_MANAGED}, a {SAY('CMK')}, onde você "
            f"define a política da chave, rotação e permissões — custa cerca "
            f"de um dólar por mês mais uso, mas é totalmente auditável."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Chaves do K M S são {EMPH('regionais')} — não saem "
            f"da região onde foram criadas, exceto as {MULTI_REGION_KEYS}, "
            f"que replicam a mesma chave para outras regiões mantendo o mesmo "
            f"identificador, úteis para recuperação de desastre ou Aurora "
            f"{SAY('Global Database')} com criptografia."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Envelope encryption ----
    {
        "voice": "antonio",
        "text": (
            f"O K M S não criptografa diretamente arquivos grandes — o "
            f"limite é de quatro kilobytes por chamada. Em vez disso, usa "
            f"{ENVELOPE_ENCRYPTION}: o K M S gera uma {DATA_KEY}, que "
            f"criptografa o dado localmente, e a própria {DATA_KEY} é então "
            f"criptografada pela {SAY('CMK')} e guardada junto com o dado."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Para descriptografar, primeiro descriptografa a "
            f"{DATA_KEY} via K M S, depois usa ela para descriptografar o "
            f"dado. É isso que permite ao {SAY('S3')}, {SAY('EBS')} e "
            f"{SAY('RDS')} criptografarem objetos de qualquer tamanho usando "
            f"o K M S por trás."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Uma armadilha importante: compartilhar um snapshot "
            f"de {SAY('EBS')} ou {SAY('RDS')} criptografado com outra conta "
            f"exige compartilhar acesso à {SAY('CMK')} também, através da "
            f"política da chave — sem isso, a outra conta recebe o snapshot, "
            f"mas não consegue descriptografá-lo, ficando inutilizável. E "
            f"chaves {AWS_MANAGED} {EMPH('não podem')} ser compartilhadas "
            f"entre contas — só {SAY('CMK')}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- CloudHSM ----
    {
        "voice": "antonio",
        "text": (
            f"O {CLOUDHSM} oferece hardware de criptografia dedicado, "
            f"single-tenant, dentro de uma {SAY('VPC')}, atendendo padrões de "
            f"compliance que exigem controle exclusivo do hardware, como "
            f"{FIPS} cento e quarenta dash dois nível três."
            f"{BRK(400)} Diferente do K M S, que é multi-tenant e gerenciado, "
            f"você é responsável por gerenciar o cluster do {CLOUDHSM}. Use "
            f"apenas quando o enunciado exige explicitamente esse nível de "
            f"isolamento — na maioria dos casos, o K M S é suficiente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Secrets Manager vs Parameter Store ----
    {
        "voice": "francisca",
        "text": (
            f"{SECRETS_MANAGER} tem rotação automática nativa — "
            f"{SAY('RDS')}, Redshift e DocumentDB já têm integração pronta, "
            f"outros via Lambda customizada. Cobra por segredo por mês, mais "
            f"por chamada de A P I. Rotacionar senha de banco automaticamente "
            f"é sinônimo de {SECRETS_MANAGER}. Suporta também replicação "
            f"nativa entre regiões."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O {PARAMETER_STORE}, do S S M, tem o tier Standard "
            f"gratuito. Guarda configurações e segredos com criptografia K M "
            f"S opcional, mas {EMPH('sem rotação nativa')} — exigiria "
            f"automação própria. Guardar configuração barata, sem rotação "
            f"automática, é sinônimo de {PARAMETER_STORE}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Encryption in transit ----
    {
        "voice": "antonio",
        "text": (
            f"Criptografia em repouso, via K M S, protege dados parados. "
            f"{ENCRYPTION_IN_TRANSIT} protege dados em movimento, via T L S e "
            f"H T T P S — igualmente cobrado na prova."
            f"{BRK(400)} O {SAY('ACM')}, Certificate Manager, fornece "
            f"certificados T L S públicos, gratuitos e auto-renováveis, para "
            f"{SAY('ALB')}, CloudFront e API Gateway — elimina a gestão "
            f"manual de certificados expirando."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o {SAY('ACM')} {PRIVATE_CA} é uma autoridade "
            f"certificadora privada, para emitir certificados internos — por "
            f"exemplo, comunicação {MTLS} entre microserviços, ou dispositivos "
            f"de I o T — quando os certificados não precisam ser publicamente "
            f"confiáveis."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Zoologico de servicos ----
    {
        "voice": "francisca",
        "text": (
            f"Agora o zoológico de serviços de segurança — vamos passar por "
            f"todos, um a um."
            f"{BRK(300)} O {SAY('WAF')} é um firewall de aplicação, camada "
            f"sete: bloqueia S Q L injection, X S S, e faz limitação de taxa "
            f"e bloqueio geográfico — protege {SAY('ALB')}, CloudFront, API "
            f"Gateway e AppSync."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O {SHIELD_STANDARD} dá proteção D D o S automática e "
            f"gratuita para todo cliente {SAY('AWS')}, contra os ataques mais "
            f"comuns de camada três e quatro. O {SHIELD_ADVANCED} adiciona "
            f"proteção avançada de camada três a sete, mais uma equipe de "
            f"resposta dedicada, o {DRT}, e proteção financeira contra picos "
            f"de custo causados por D D o S."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O {GUARDDUTY} faz detecção inteligente de ameaças "
            f"com aprendizado de máquina, analisando CloudTrail, Flow Logs de "
            f"{SAY('VPC')} e logs de D N S — para atividade maliciosa ou "
            f"comportamento anômalo."
            f"{BRK(300)} O {INSPECTOR} faz varredura automatizada de "
            f"vulnerabilidades conhecidas em {SAY('EC2')}, imagens de "
            f"container no {SAY('ECR')}, e código Lambda."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} O {MACIE} encontra dados sensíveis automaticamente "
            f"em buckets {SAY('S3')}, usando aprendizado de máquina. O "
            f"{SECURITY_HUB} é o painel central, agregando descobertas do "
            f"{GUARDDUTY}, {INSPECTOR}, {MACIE}, Config e parceiros externos "
            f"— uma visão única de postura de segurança."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} O {DETECTIVE} faz investigação visual de "
            f"incidentes, conectando automaticamente eventos relacionados "
            f"para análise de causa raiz. O A W S Config avalia "
            f"continuamente se os recursos estão em conformidade com regras "
            f"definidas, e registra o histórico de configuração."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} O {ARTIFACT} é o portal de relatórios de compliance "
            f"da {SAY('AWS')} — para auditoria, não para detecção. O "
            f"{SAY('ACM')}, como já vimos, dá certificados T L S gratuitos. E "
            f"o Cognito autentica usuários de aplicativos, com User Pools "
            f"para login e Identity Pools para credenciais — já vimos isso no "
            f"capítulo um."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Sinal prático: o {SHIELD_STANDARD} já protege "
            f"gratuitamente, sem nenhuma ação necessária. O "
            f"{SHIELD_ADVANCED} só entra quando o enunciado menciona proteção "
            f"financeira contra D D o S, ou equipe de resposta dedicada — caso "
            f"contrário, é um distrator caro."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- WAF rule types ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre os tipos de regra do {SAY('WAF')}: {MANAGED_RULE_GROUPS} "
            f"são conjuntos pré-configurados pela {SAY('AWS')} ou parceiros, "
            f"cobrindo o {SAY('OWASP')} Top dez, atualizados automaticamente "
            f"contra novas ameaças. {RATE_BASED_RULES} limitam requisições "
            f"por I P num intervalo, mitigando scraping e ataques de força "
            f"bruta."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {GEO_MATCH} bloqueia ou permite por país de origem. "
            f"I P set match usa uma lista de I Ps específicos. E regras "
            f"customizadas aplicam lógica própria sobre cabeçalhos, parâmetros "
            f"de busca ou corpo da requisição, para padrões específicos da "
            f"aplicação."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito traz um laboratório de uma hora e meia, "
            f"gratuito, onde você cria uma {SAY('CMK')}, criptografa um "
            f"objeto e vê o uso no CloudTrail, configura rotação no "
            f"{SECRETS_MANAGER}, cria uma Web {SAY('ACL')} no {SAY('WAF')}, e "
            f"ativa {GUARDDUTY} e {SECURITY_HUB}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: detectar uma {SAY('EC2')} "
            f"comprometida fazendo mineração de criptomoeda, sem configurar "
            f"regras manualmente. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{GUARDDUTY} — analisa CloudTrail, Flow Logs e logs de D N S com "
            f"aprendizado de máquina, detectando padrões maliciosos "
            f"conhecidos automaticamente."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: bloquear tentativas de S Q L injection chegando pelo "
            f"{SAY('ALB')}. Como?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('WAF')} com um {MANAGED_RULE_GROUP} "
            f"de S Q L injection associado ao {SAY('ALB')}. O {SAY('ALB')} "
            f"sozinho não inspeciona o conteúdo das requisições."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: rotação automática da senha do banco {SAY('RDS')} a "
            f"cada trinta dias, sem código customizado. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SECRETS_MANAGER} — tem integração nativa pronta para "
            f"{SAY('RDS')}, Aurora, Redshift e DocumentDB. O "
            f"{PARAMETER_STORE} não tem rotação nativa."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: a empresa precisa descobrir automaticamente números de "
            f"cartão de crédito armazenados indevidamente em buckets "
            f"{SAY('S3')}. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{MACIE} — usa aprendizado de máquina para identificar dados "
            f"sensíveis em objetos {SAY('S3')}, gerando descobertas com a "
            f"localização exata."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: a questão pede {FIPS} cento e quarenta dash dois nível "
            f"três, e controle exclusivo do hardware. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{CLOUDHSM} — hardware dedicado single-tenant. O K M S padrão "
            f"não atende, porque o hardware subjacente é multi-tenant, "
            f"compartilhado entre clientes."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: um snapshot de {SAY('EBS')} criptografado com uma "
            f"{SAY('CMK')} é compartilhado com outra conta, mas a conta "
            f"destino não consegue usá-lo. Por quê?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Compartilhar o snapshot não basta — é preciso também atualizar "
            f"a política da {SAY('CMK')} para conceder permissão de uso à "
            f"conta de destino. Sem isso, ela recebe o snapshot, mas não "
            f"consegue descriptografá-lo."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: investigar a causa raiz de um incidente, "
            f"conectando eventos de CloudTrail, Flow Logs e {GUARDDUTY} "
            f"automaticamente. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Amazon {DETECTIVE} — constrói automaticamente um gráfico de "
            f"comportamento conectando eventos relacionados de múltiplas "
            f"fontes, sem precisar correlacionar logs manualmente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo nove. No próximo, vamos falar de "
            f"monitoramento: CloudWatch, CloudTrail e X-Ray. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
