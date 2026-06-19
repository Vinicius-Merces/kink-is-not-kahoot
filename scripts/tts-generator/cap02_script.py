"""Roteiro tratado do Capitulo 2 (EC2, Auto Scaling, ELB)."""

from glossary import (
    SAY, BRK, PHON, TARGET_GROUP, SPOT,
    SCALE_IN, STICKY_SESSIONS, CROSS_ZONE,
    LIFECYCLE_HOOK,
)

INSTANCE_PROFILE = PHON("ˈɪnstəns ˈproʊfaɪl", "Instance Profile")
BURSTABLE = PHON("ˈbɜrstəbəl", "burstable")
UNLIMITED = PHON("ʌnˈlɪmɪtɪd", "unlimited")
RESERVED = PHON("rɪˈzɜrvd", "Reserved")
SAVINGS_PLAN = PHON("ˈseɪvɪŋz plæn", "Savings Plan")
DEDICATED_HOST = PHON("ˈdɛdɪkeɪtɪd hoʊst", "Dedicated Host")
THROTTLED = PHON("ˈθrɑtəld", "throttled")
MULTI_ATTACH = PHON("ˈmʌlti əˈtætʃ", "Multi-Attach")
DEREGISTRATION_DELAY = PHON("diˌrɛdʒɪˈstreɪʃən dɪˈleɪ", "Deregistration Delay")
CONNECTION_DRAINING = PHON("kəˈnɛkʃən ˈdreɪnɪŋ", "Connection Draining")
WEBSOCKET = PHON("wɛb ˈsɑkɪt", "WebSocket")
X_FORWARDED_FOR = PHON("ɛks ˈfɔrwərdɪd fɔr", "X-Forwarded-For")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dois: computação. Vamos falar de {SAY('EC2')}, Auto Scaling e "
            f"balanceamento de carga — a espinha dorsal de praticamente toda arquitetura "
            f"na {SAY('AWS')}."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    {
        "voice": "antonio",
        "text": (
            f"Vamos começar pelas famílias de instância. A prova raramente pergunta o "
            f"tamanho exato — ela descreve um cenário e espera que você reconheça a "
            f"família certa."
            f"{BRK(400)} A família T é {BURSTABLE}: acumula créditos de C P U quando "
            f"ociosa e gasta esses créditos em picos. Se a carga é constante e alta, os "
            f"créditos se esgotam e a instância fica {THROTTLED}, ou seja, limitada."
            f"{BRK(400)} A família M é uso geral balanceado. A família C é otimizada para "
            f"C P U. As famílias R e X são otimizadas para memória. E as famílias P e G "
            f"trazem G P U, usadas para machine learning e renderização."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Agora os modelos de compra, que é a tabela mais cobrada deste domínio."
            f"{BRK(300)} On-Demand não tem desconto nem compromisso: é para cargas "
            f"imprevisíveis. {RESERVED} oferece até setenta e dois por cento de desconto, "
            f"mas exige compromisso de um ou três anos, para cargas estáveis."
            f"{BRK(300)} {SAVINGS_PLAN}s dão um desconto parecido, só que com muito mais "
            f"flexibilidade de família e região, e cobrem até Fargate e Lambda."
            f"{BRK(300)} E {SPOT} oferece até noventa por cento de desconto, mas pode ser "
            f"interrompida com dois minutos de aviso — perfeita para processamento em "
            f"lote tolerante a falha, nunca para banco de dados crítico."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Sobre volumes {SAY('EBS')}: o tipo gp três é o padrão moderno, com I O P S "
            f"configurável independente do tamanho. O io um e io dois são para bancos "
            f"críticos que precisam de I O P S garantido, e são os únicos com "
            f"{MULTI_ATTACH}, ou seja, vários servidores acessando o mesmo volume."
            f"{BRK(400)} Já s t um e s c um são discos magnéticos de baixo custo, bons "
            f"para dados sequenciais grandes, como logs."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Vamos falar do Auto Scaling Group agora. Ele garante que o número certo de "
            f"instâncias esteja sempre rodando, definido por três números: o mínimo, que "
            f"nunca é ultrapassado para baixo; o desejado, o estado normal de operação; e "
            f"o máximo, o teto de custo."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A política mais usada é a Target Tracking: você define um alvo, "
            f"como C P U em sessenta por cento, e o grupo se ajusta automaticamente. "
            f"Existe também o Scheduled Scaling, para picos previsíveis em horário fixo, "
            f"e o Predictive Scaling, que usa aprendizado de máquina para escalar antes "
            f"do pico acontecer."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Um detalhe importante: se a aplicação precisa de tempo para encerrar com "
            f"calma antes de ser desligada, em um {SCALE_IN}, use um {LIFECYCLE_HOOK}. "
            f"Ele coloca a instância em espera por até uma hora antes de finalizar, "
            f"evitando perda de dados em processamento."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Agora, os balanceadores de carga. Existem quatro tipos, mas só dois "
            f"realmente importam na prova."
            f"{BRK(400)} O {SAY('ALB')} trabalha na camada sete, entende {SAY('HTTP')} e "
            f"{WEBSOCKET}, e permite rotear por caminho, por domínio ou por cabeçalho. É "
            f"o mais usado para aplicações web."
            f"{BRK(400)} O {SAY('NLB')} trabalha na camada quatro, é muito mais rápido, e "
            f"oferece I P estático por zona de disponibilidade — ótimo quando o cliente "
            f"precisa colocar seu I P numa lista de permissões."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Vale conhecer alguns detalhes operacionais. O {SAY('ALB')} pode fazer "
            f"roteamento avançado usando {TARGET_GROUP}s diferentes, e suporta "
            f"{STICKY_SESSIONS}, que mantêm o usuário sempre na mesma instância."
            f"{BRK(400)} O balanceamento {CROSS_ZONE} distribui o tráfego igualmente "
            f"entre todas as instâncias de todas as zonas, não apenas entre os nós do "
            f"balanceador. No {SAY('ALB')} isso vem ativado por padrão. No {SAY('NLB')}, "
            f"precisa ser ativado manualmente, e pode gerar custo de tráfego entre zonas."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} E como o {SAY('ALB')} substitui o I P original do cliente pelo "
            f"seu próprio I P, para recuperar o I P verdadeiro do visitante é preciso "
            f"olhar o cabeçalho {X_FORWARDED_FOR}. O {SAY('NLB')} já preserva o I P "
            f"original, sem precisar desse cabeçalho."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Para fechar: quando uma instância está sendo removida, o balanceador para "
            f"de mandar tráfego novo para ela, mas espera as conexões atuais terminarem. "
            f"Isso se chama {DEREGISTRATION_DELAY}, e o padrão é trezentos segundos. "
            f"Reduza esse tempo para aplicações sem estado, e aumente para aplicações com "
            f"sessões longas."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Um lembrete rápido: se o cenário não precisa de servidor dedicado, vale a "
            f"pena considerar alternativas antes de ir direto para {SAY('EC2')}. "
            f"{BRK(300)} Tarefas curtas e orientadas a evento? Lambda. {BRK(200)} "
            f"Containers sem gerenciar servidor? Fargate. {BRK(200)} Time que já usa "
            f"Kubernetes? {SAY('EKS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira pergunta: um workload de renderização tolerante "
            f"a interrupção — qual o modelo de compra mais barato?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SPOT}. Desconto de até noventa por cento. Se for interrompida, o ideal é "
            f"ter checkpointing salvando o progresso, por exemplo no {SAY('S3')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: um banco Oracle com licença por núcleo físico, modelo {SAY('BYOL')} "
            f"— qual o modelo de compra correto?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DEDICATED_HOST}. É o único modelo que dá visibilidade total do hardware "
            f"físico subjacente, necessária para esse tipo de licenciamento."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: uma aplicação fica lenta depois de horas de uso intenso numa "
            f"instância t três média. O que está acontecendo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Os créditos de C P U se esgotaram e a instância está sendo {THROTTLED}. A "
            f"correção é trocar para uma família M ou C, sem limite de crédito, ou "
            f"ativar o modo {UNLIMITED} da própria T três."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: uma aplicação precisa que o I P do balanceador seja fixo, para "
            f"entrar numa lista de permissões do firewall do cliente. Qual "
            f"balanceador?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('NLB')}. Ele fornece um I P estático por zona de disponibilidade. O "
            f"{SAY('ALB')} tem I Ps dinâmicos, sem essa garantia."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dois. No próximo, vamos falar de armazenamento: "
            f"{SAY('S3')}, {SAY('EFS')} e {SAY('FSx')}. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
