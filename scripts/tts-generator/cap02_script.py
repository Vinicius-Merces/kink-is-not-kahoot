"""Roteiro tratado do Capitulo 2 (EC2, Auto Scaling, ELB) - cobertura completa.

Nada do conteudo conceitual e omitido: todas as tabelas, callouts e as
7 perguntas do checkpoint original sao narradas. Apenas o passo a passo
literal do laboratorio pratico e resumido (e hands-on, nao serve para
audio passivo).
"""

from glossary import (
    SAY, EMPH, BRK, PHON, TARGET_GROUP, SPOT, SCALE_IN,
    STICKY_SESSIONS, CROSS_ZONE, LIFECYCLE_HOOK,
)

USER_DATA = PHON("ˈjuzɚ ˈdeɪtə", "User Data")
INSTANCE_PROFILE = PHON("ˈɪnstəns ˈproʊfaɪl", "Instance Profile")
BURSTABLE = PHON("ˈbɜrstəbəl", "burstable")
UNLIMITED = PHON("ʌnˈlɪmɪtɪd", "unlimited")
RESERVED = PHON("rɪˈzɜrvd", "Reserved")
SAVINGS_PLAN = PHON("ˈseɪvɪŋz plæn", "Savings Plan")
DEDICATED_HOST = PHON("ˈdɛdɪkeɪtɪd hoʊst", "Dedicated Host")
DEDICATED_INSTANCE = PHON("ˈdɛdɪkeɪtɪd ˈɪnstəns", "Dedicated Instance")
THROTTLED = PHON("ˈθrɑtəld", "throttled")
MULTI_ATTACH = PHON("ˈmʌlti əˈtætʃ", "Multi-Attach")
INSTANCE_STORE = PHON("ˈɪnstəns stɔr", "Instance Store")
DATA_LIFECYCLE_MANAGER = PHON("ˈdeɪtə ˈlaɪfsaɪkəl ˈmænɪdʒɚ", "Data Lifecycle Manager")
PLACEMENT_GROUP = PHON("ˈpleɪsmənt ɡrup", "Placement Group")
LAUNCH_TEMPLATE = PHON("lɔntʃ ˈtɛmplət", "Launch Template")
LAUNCH_CONFIGURATION = PHON("lɔntʃ kənˌfɪɡjəˈreɪʃən", "Launch Configuration")
TARGET_TRACKING = PHON("ˈtɑrɡət ˈtrækɪŋ", "Target Tracking")
STEP_SCALING = PHON("stɛp ˈskeɪlɪŋ", "Step Scaling")
SIMPLE_SCALING = PHON("ˈsɪmpəl ˈskeɪlɪŋ", "Simple Scaling")
SCHEDULED_SCALING = PHON("ˈskɛdʒuld ˈskeɪlɪŋ", "Scheduled Scaling")
PREDICTIVE_SCALING = PHON("prɪˈdɪktɪv ˈskeɪlɪŋ", "Predictive Scaling")
COOLDOWN = PHON("ˈkuldaʊn", "cooldown")
HEALTH_CHECK = PHON("hɛlθ tʃɛk", "health check")
WEBSOCKET = PHON("wɛb ˈsɑkɪt", "WebSocket")
X_FORWARDED_FOR = PHON("ɛks ˈfɔrwərdɪd fɔr", "X-Forwarded-For")
DEREGISTRATION_DELAY = PHON("diˌrɛdʒɪˈstreɪʃən dɪˈleɪ", "Deregistration Delay")
CONNECTION_DRAINING = PHON("kəˈnɛkʃən ˈdreɪnɪŋ", "Connection Draining")
PRIVATELINK = PHON("ˈpraɪvətlɪŋk", "PrivateLink")
MIXED_INSTANCES_POLICY = PHON("mɪkst ˈɪnstənsɪz ˈpɑləsi", "mixed instances policy")
BYOL = PHON("bi waɪ oʊ ɛl", "BYOL")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dois: computação. O {SAY('EC2')} é o serviço de computação "
            f"base da {SAY('AWS')} e aparece em quase toda arquitetura. A prova vai "
            f"muito além de simplesmente subir uma instância — ela testa sua "
            f"capacidade de escolher o modelo de compra certo, dimensionar com Auto "
            f"Scaling, e distribuir carga com o tipo certo de balanceador."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Familias de instancia ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos começar pelas famílias de instância. Decore a letra, não o "
            f"número: a prova raramente pergunta o tipo exato, ela descreve um "
            f"cenário e espera que você reconheça a família certa."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} A família T é {BURSTABLE}, de uso geral com créditos de "
            f"C P U — pensa em desenvolvimento e cargas variáveis. A família M é uso "
            f"geral balanceado, para web servers de produção sem requisito extremo."
            f"{BRK(300)} A família C é otimizada para C P U: processamento intenso, "
            f"encoding de vídeo, computação de alta performance. As famílias R e X "
            f"são otimizadas para memória: bancos em memória, S A P HANA, Redis."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} As famílias I e D trazem armazenamento local N V M e, para "
            f"altíssimo I O P S, como bancos NoSQL auto-gerenciados. E as famílias P, "
            f"G, Trn e Inf trazem G P U ou aceleradores dedicados, para treinamento "
            f"de machine learning, inferência e renderização."
        ),
    },
    {"voice": "antonio", "text": BRK(500)},
    {
        "voice": "francisca",
        "text": (
            f"Atenção a uma armadilha clássica: a família T acumula créditos de C P "
            f"U quando ociosa, e gasta esses créditos em picos. Se a carga é "
            f"constante e alta, os créditos se esgotam e a instância fica "
            f"{THROTTLED}, ou seja, limitada. Se o enunciado descreve carga contínua "
            f"elevada e mostra uma instância T como opção, isso é um distrator. A "
            f"correção é migrar para M ou C, ou ativar o modo {UNLIMITED} da própria "
            f"família T."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- User Data e IMDS ----
    {
        "voice": "antonio",
        "text": (
            f"Agora, {USER_DATA} e o {SAY('IMDS')}. O {USER_DATA} é um script "
            f"executado uma única vez no primeiro boot da instância, como root — o "
            f"mecanismo padrão para instalar pacotes e configurar serviços "
            f"automaticamente."
            f"{BRK(400)} Já o {SAY('IMDS')}, o serviço de metadados, é acessível de "
            f"dentro da instância, e fornece, entre outras coisas, as credenciais "
            f"temporárias da {INSTANCE_PROFILE}. É por isso que uma {SAY('EC2')} "
            f"nunca precisa de chave de acesso fixa no código."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} A versão dois do {SAY('IMDS')} exige um token temporário "
            f"antes de aceitar requisições, protegendo contra ataques de "
            f"falsificação de requisição do lado do servidor que tentam roubar essas "
            f"credenciais. Se a questão menciona proteção contra esse tipo de "
            f"ataque, a resposta é exigir o I M D S versão dois."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Modelos de compra ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos para a tabela mais cobrada do domínio quatro: os modelos de "
            f"compra."
            f"{BRK(300)} On-Demand não tem desconto nem compromisso — para carga "
            f"imprevisível ou que não pode ser interrompida."
            f"{BRK(300)} {RESERVED}, ou Reservada, oferece até setenta e dois por "
            f"cento de desconto, com compromisso de um ou três anos, em modalidade "
            f"Standard ou Convertible — ideal para carga estável que já roda há "
            f"tempo."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {SAVINGS_PLAN}s dão um desconto parecido, só que com muito "
            f"mais flexibilidade de família, tamanho e região — e cobrem até Fargate "
            f"e Lambda."
            f"{BRK(300)} {SPOT} oferece até noventa por cento de desconto, sem "
            f"compromisso, mas pode ser interrompida com dois minutos de aviso — "
            f"ideal para processamento em lote, integração contínua e renderização."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {DEDICATED_INSTANCE} custa cerca de dez por cento mais, e "
            f"isola o hardware físico sem se importar com qual servidor — atende "
            f"compliance simples. {DEDICATED_HOST} dá visibilidade total do hardware "
            f"físico, necessária para licenciamento {BYOL}, do tipo Oracle ou "
            f"Windows Server, por socket ou núcleo."
        ),
    },
    {"voice": "francisca", "text": BRK(600)},
    {
        "voice": "antonio",
        "text": (
            f"Dois detalhes importantes: na modalidade {RESERVED} Standard você não "
            f"pode trocar de família, mas o desconto é maior; na Convertible você "
            f"pode trocar de família, com desconto um pouco menor. Se a questão "
            f"sugere que a família pode mudar no futuro, escolha Convertible."
            f"{BRK(400)} E a combinação favorita da prova: base estável em "
            f"{RESERVED} ou {SAVINGS_PLAN}, mais picos em On-Demand, se crítico, ou "
            f"{SPOT}, se tolerante a falha, tudo dentro de um Auto Scaling Group com "
            f"uma {MIXED_INSTANCES_POLICY}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- EBS ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre armazenamento em bloco: o {SAY('EBS')} é o disco padrão da "
            f"{SAY('EC2')}, e persiste independente da instância. Um volume só pode "
            f"ser anexado a uma instância por vez, exceto io um e io dois com "
            f"{MULTI_ATTACH}. E o {SAY('EBS')} sempre fica na mesma zona de "
            f"disponibilidade da instância."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O tipo g p três é o padrão moderno: I O P S e throughput "
            f"configuráveis independente do tamanho, substituindo o g p dois antigo "
            f"com menor custo. O io um e io dois são para bancos críticos que "
            f"precisam de I O P S garantido, e são os únicos com {MULTI_ATTACH}."
            f"{BRK(400)} Já s t um e s c um são discos magnéticos: s t um para dados "
            f"sequenciais grandes, como logs, e s c um para o menor custo possível, "
            f"com acesso muito raro. Nenhum dos dois pode ser volume de boot."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Snapshots do {SAY('EBS')} são backups incrementais "
            f"guardados no {SAY('S3')}, embora você não os veja diretamente lá. "
            f"Podem ser copiados entre regiões — operação básica de qualquer "
            f"estratégia de recuperação de desastre. E o {DATA_LIFECYCLE_MANAGER} "
            f"automatiza a criação, retenção e exclusão desses snapshots."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Instance Store ----
    {
        "voice": "francisca",
        "text": (
            f"O {INSTANCE_STORE} é armazenamento físico diretamente acoplado ao "
            f"servidor. Some se a instância parar, falhar ou for terminada — não "
            f"pode ser desconectado nem movido. Em troca, oferece o maior I O P S "
            f"possível na {SAY('AWS')}."
            f"{BRK(400)} Use {EMPH('apenas para dados temporários')} que podem ser "
            f"recriados: buffers, caches, dados que replicam de um cluster. Nunca "
            f"para dados únicos que precisam sobreviver a uma falha de instância."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Placement Groups ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre {PLACEMENT_GROUP}s: o tipo Cluster coloca tudo no mesmo rack, na "
            f"mesma zona, para a menor latência possível entre instâncias — mas se o "
            f"rack falhar, tudo cai junto."
            f"{BRK(400)} O tipo Spread distribui em hardware distinto, até sete "
            f"instâncias por zona, para máxima isolação de falha — bom para um "
            f"pequeno número de máquinas críticas."
            f"{BRK(400)} E o tipo Partition organiza grupos em racks separados, sem "
            f"limite prático de instâncias — usado por sistemas distribuídos como "
            f"Hadoop, Cassandra e Kafka, que já sabem gerenciar replicação por "
            f"partição."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- ASG ----
    {
        "voice": "francisca",
        "text": (
            f"Agora o componente mais testado da prova: o Auto Scaling Group. Ele "
            f"garante que o número certo de instâncias esteja sempre rodando, usando "
            f"um {LAUNCH_TEMPLATE}, ou o legado {LAUNCH_CONFIGURATION}, para definir "
            f"tipo, imagem, security group e {INSTANCE_PROFILE} de cada instância "
            f"nova."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Três números definem o grupo: o mínimo, que nunca é "
            f"ultrapassado para baixo — por exemplo dois, para alta disponibilidade "
            f"em pelo menos duas zonas. O desejado, o estado normal de operação — "
            f"por exemplo quatro. E o máximo, o teto de custo — por exemplo dez."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Sobre as políticas de scaling: {TARGET_TRACKING} mantém uma métrica "
            f"num alvo, como C P U em sessenta por cento, e o grupo se ajusta "
            f"automaticamente — é a mais usada, configure uma vez e esqueça."
            f"{BRK(400)} {STEP_SCALING} define incrementos diferentes por nível de "
            f"severidade do alarme — por exemplo, mais uma instância se a C P U "
            f"passar de sessenta por cento, mais três se passar de oitenta."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {SIMPLE_SCALING} é legado: uma ação por alarme, com um "
            f"{COOLDOWN} obrigatório antes da próxima ação — prefira as duas "
            f"anteriores. {SCHEDULED_SCALING} altera os números em horários "
            f"predefinidos, para picos previsíveis, como toda segunda-feira às oito "
            f"da manhã. E {PREDICTIVE_SCALING} usa aprendizado de máquina para "
            f"prever o padrão e escalar antes do pico acontecer."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},
    {
        "voice": "francisca",
        "text": (
            f"Um ponto de atenção: se a aplicação precisa de tempo para encerrar "
            f"com calma — drenando conexões, salvando dados — antes de ser "
            f"desligada num {SCALE_IN}, use um {LIFECYCLE_HOOK}. Ele coloca a "
            f"instância em espera por até uma hora antes de finalizar de fato, "
            f"evitando perda de dados em processamento."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Sobre {HEALTH_CHECK}s do Auto Scaling Group: por padrão, ele usa só o "
            f"status da {SAY('EC2')}. Para substituir instâncias que estão de pé, "
            f"mas servindo erro, configure o grupo para usar o {HEALTH_CHECK} do "
            f"próprio balanceador — se ele disser que a instância não está saudável, "
            f"o grupo termina e sobe outra."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- ELB ----
    {
        "voice": "francisca",
        "text": (
            f"Agora os balanceadores de carga. Existem quatro tipos."
            f"{BRK(300)} O {SAY('ALB')} trabalha na camada sete, entende H T T P, H T "
            f"T P S e {WEBSOCKET}, e permite rotear por caminho, domínio ou "
            f"cabeçalho. {BRK(300)} O {SAY('NLB')} trabalha na camada quatro, entende "
            f"T C P, U D P e T L S, com latência ultra baixa e I P estático por "
            f"zona."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O {SAY('GLB')}, Gateway, trabalha na camada três, "
            f"transparente para qualquer protocolo — usado para inserir appliances "
            f"de segurança, como firewalls, no caminho do tráfego. E o {SAY('CLB')}, "
            f"Classic, é legado: não crie mais, migre para {SAY('ALB')} ou "
            f"{SAY('NLB')}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O {SAY('ALB')} é o mais cobrado da prova. Ele permite roteamento "
            f"baseado em caminho — por exemplo, barra A P I vai para um {TARGET_GROUP}, "
            f"barra estático vai para outro. Permite roteamento baseado em domínio, "
            f"e em cabeçalhos ou parâmetros de busca, para direcionar usuários beta "
            f"a uma versão canary."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Ele também suporta autenticação integrada com Cognito User "
            f"Pool e provedores O I D C, eliminando código de autenticação da "
            f"aplicação. Pode ter {TARGET_GROUP}s heterogêneos, misturando "
            f"{SAY('EC2')}, tarefas do {SAY('ECS')}, Lambda e até outro {SAY('ALB')}. "
            f"E suporta {STICKY_SESSIONS}, cookies de afinidade que mantêm o usuário "
            f"sempre na mesma instância — útil para sessão local, mas prefira "
            f"sessões centralizadas em Redis ou {SAY('DynamoDB')} quando possível."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O {SAY('NLB')} opera na camada quatro — não lê H T T P, só encaminha "
            f"pacotes. Por isso a latência é muito menor, em microssegundos. Ele "
            f"oferece I P estático por zona de disponibilidade, essencial quando o "
            f"cliente precisa colocar seu I P numa lista de permissões."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E ele preserva o I P de origem do cliente — diferente do "
            f"{SAY('ALB')}, que substitui pelo seu próprio I P. Para recuperar o I P "
            f"original no {SAY('ALB')}, é preciso olhar o cabeçalho "
            f"{X_FORWARDED_FOR}. O {SAY('NLB')} também se integra com "
            f"{PRIVATELINK}, para expor serviços internos a outras V P Cs de forma "
            f"privada."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Sobre balanceamento {CROSS_ZONE}: por padrão, um balanceador distribui "
            f"tráfego igualmente entre os nós em cada zona, não entre as "
            f"instâncias. Se você tem uma instância numa zona e nove em outra, a "
            f"zona com uma instância pode receber a metade do tráfego, sobrecarregada."
            f"{BRK(400)} Com balanceamento {CROSS_ZONE} ativado, o tráfego se "
            f"distribui uniformemente entre todas as instâncias de todas as zonas. "
            f"No {SAY('ALB')} isso já vem ativado, sem custo extra. No {SAY('NLB')} e "
            f"{SAY('GLB')}, vem desativado, e ativar gera custo de tráfego entre "
            f"zonas — um detalhe que a prova adora testar em questões de custo."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Por fim: quando uma instância é removida, o balanceador para de "
            f"mandar tráfego novo para ela, mas espera as conexões já abertas "
            f"terminarem. No {SAY('ALB')} e {SAY('NLB')} isso se chama "
            f"{DEREGISTRATION_DELAY}; no {SAY('CLB')}, {CONNECTION_DRAINING}. O "
            f"padrão é trezentos segundos — reduza para aplicações sem estado, e "
            f"aumente para aplicações com sessões longas."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Escada do compute ----
    {
        "voice": "antonio",
        "text": (
            f"Para fechar a parte teórica: nem todo cenário pede {SAY('EC2')}. Se o "
            f"enunciado fala em evento, sem servidor, menos de quinze minutos, é "
            f"Lambda. Containers sem gerenciar servidor: Fargate, em {SAY('ECS')} ou "
            f"{SAY('EKS')}. Time que já usa Kubernetes: {SAY('EKS')}. Containers "
            f"simples integrados à {SAY('AWS')}: {SAY('ECS')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Job de lote de longa duração, sem servidor: A W S Batch "
            f"sobre Fargate. E quando o desenvolvedor só quer subir código sem "
            f"pensar em infraestrutura: Elastic Beanstalk ou App Runner."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito também traz um laboratório prático de duas horas, "
            f"por menos de um dólar, onde você sobe uma instância com {USER_DATA}, "
            f"cria um Auto Scaling Group atrás de um {SAY('ALB')}, testa "
            f"{TARGET_TRACKING}, e configura roteamento por caminho entre dois "
            f"{TARGET_GROUP}s. Vale fazer com o computador na mão."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: um workload de renderização tolerante a "
            f"interrupção — qual o modelo de compra mais barato?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SPOT}. Desconto de até noventa por cento. Se interrompido, o job "
            f"reinicia do zero, ou usa checkpointing — combine Auto Scaling com "
            f"{SPOT} e checkpointing no {SAY('S3')} para garantir progresso."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: um banco Oracle com licença por núcleo físico, modelo "
            f"{BYOL}. Qual o modelo de compra correto?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DEDICATED_HOST}. É o único com visibilidade e controle total do "
            f"hardware físico subjacente, necessário para esse tipo de "
            f"licenciamento. O {DEDICATED_INSTANCE} isola, mas não dá essa "
            f"visibilidade."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: duas instâncias {SAY('EC2')} precisam escrever no mesmo "
            f"volume de bloco simultaneamente. O que usar?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"io um ou io dois com {MULTI_ATTACH} ativado — único tipo {SAY('EBS')} "
            f"que permite isso, dentro da mesma zona. Se for arquivo compartilhado "
            f"em vez de bloco, reavalie usar {SAY('EFS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: uma aplicação numa t três média fica lenta depois de horas de "
            f"uso intenso contínuo. Qual a causa, e a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Os créditos de C P U se esgotaram, e a instância está sendo "
            f"{THROTTLED}. A solução é trocar para a família M ou C, sem limite de "
            f"crédito, ou ativar o modo {UNLIMITED} da própria T três — que cobra o "
            f"excedente por hora."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: uma aplicação precisa que o I P do balanceador seja fixo, "
            f"para entrar numa lista de permissões do firewall do cliente. Qual "
            f"balanceador?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('NLB')}. Fornece I P estático por zona de disponibilidade. O "
            f"{SAY('ALB')} tem I Ps dinâmicos, sem essa garantia."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: qual a diferença entre {LAUNCH_TEMPLATE} e "
            f"{LAUNCH_CONFIGURATION} no Auto Scaling Group?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{LAUNCH_CONFIGURATION} é legado, sem versionamento e sem suporte a "
            f"{MIXED_INSTANCES_POLICY}. {LAUNCH_TEMPLATE} suporta versionamento, "
            f"mistura de tipos e modelos de compra, e é obrigatório para recursos "
            f"mais novos, como instance refresh."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: o {SAY('ALB')} precisa recuperar o I P do cliente "
            f"original. Como?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('ALB')} substitui o I P de origem pelo próprio I P ao "
            f"encaminhar ao backend. O I P original fica disponível no cabeçalho "
            f"{X_FORWARDED_FOR}. O {SAY('NLB')} preserva o I P original sem "
            f"precisar desse cabeçalho."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dois. No próximo, vamos falar de "
            f"armazenamento: {SAY('S3')}, {SAY('EFS')} e {SAY('FSx')}. Até a "
            f"próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
