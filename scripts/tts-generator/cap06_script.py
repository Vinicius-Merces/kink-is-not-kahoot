"""Roteiro tratado do Capitulo 6 (Alta disponibilidade e escalabilidade) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

FAULT_TOLERANCE = PHON("fɔlt ˈtɑlərəns", "Fault Tolerance")
BULKHEAD = PHON("ˈbʌlkhɛd", "Bulkhead")
CIRCUIT_BREAKER = PHON("ˈsɜrkɪt ˈbreɪkɚ", "Circuit Breaker")
GRACEFUL_DEGRADATION = PHON("ˈɡreɪsfəl dɛɡrəˈdeɪʃən", "Graceful Degradation")
STATIC_STABILITY = PHON("ˈstætɪk stəˈbɪləti", "Static Stability")
CONTROL_PLANE = PHON("kənˈtroʊl pleɪn", "control plane")
EXPONENTIAL_BACKOFF = PHON("ˌɛkspoʊˈnɛnʃəl ˈbækɔf", "exponential backoff")
JITTER = PHON("ˈdʒɪtɚ", "jitter")
RETRY_STORM = PHON("ˈritraɪ stɔrm", "retry storm")
TARGET_TRACKING = PHON("ˈtɑrɡət ˈtrækɪŋ", "Target Tracking")
STEP_SCALING = PHON("stɛp ˈskeɪlɪŋ", "Step Scaling")
SCHEDULED = PHON("ˈskɛdʒuld", "Scheduled")
PREDICTIVE = PHON("prɪˈdɪktɪv", "Predictive")
TIGHT_COUPLING = PHON("taɪt ˈkʌplɪŋ", "tight coupling")
AT_LEAST_ONCE = PHON("æt list wʌns", "at-least-once")
EXACTLY_ONCE = PHON("ɪɡˈzæktli wʌns", "exactly-once")
MESSAGE_GROUP = PHON("ˈmɛsɪdʒ ɡrup", "Message Group")
FAN_OUT = PHON("fæn aʊt", "fan-out")
EVENT_BRIDGE = PHON("ɪˈvɛnt brɪdʒ", "EventBridge")
KINESIS_DATA_STREAMS = PHON("kɪˈnisɪs ˈdeɪtə strimz", "Kinesis Data Streams")
AMAZON_MQ = PHON("ˈæməzɑn ɛm kju", "Amazon MQ")
VISIBILITY_TIMEOUT = PHON("ˌvɪzəˈbɪləti ˈtaɪmaʊt", "Visibility Timeout")
IDEMPOTENT = PHON("aɪˈdɛmpətənt", "idempotente")
DEAD_LETTER_QUEUE = PHON("dɛd ˈlɛtɚ kju", "Dead-Letter Queue")
MAX_RECEIVE_COUNT = PHON("mæks rɪˈsiv kaʊnt", "maxReceiveCount")
LONG_POLLING = PHON("lɔŋ ˈpoʊlɪŋ", "Long Polling")
SHORT_POLLING = PHON("ʃɔrt ˈpoʊlɪŋ", "short polling")
DELAY_QUEUE = PHON("dɪˈleɪ kju", "Delay Queue")
MESSAGE_ATTRIBUTES = PHON("ˈmɛsɪdʒ ˈætrəbjuts", "Message Attributes")
PUB_SUB = PHON("pʌb sʌb", "Pub/Sub")
FILTER_POLICIES = PHON("ˈfɪltɚ ˈpɑləsiz", "Filter Policies")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo seis: alta disponibilidade e escalabilidade. "
            f"{SAY('EC2')}, Auto Scaling e balanceadores dão os blocos de "
            f"construção. Aqui vamos juntar essas peças em padrões de "
            f"arquitetura resilientes, e na camada de mensageria que separa uma "
            f"arquitetura que funciona de uma que aguenta picos e falhas "
            f"parciais sem cair."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- HA / FT / Resiliencia ----
    {
        "voice": "antonio",
        "text": (
            f"Primeiro, o vocabulário que muda a resposta na prova."
            f"{BRK(400)} Alta disponibilidade minimiza o tempo fora do ar — "
            f"redundância N mais um em zonas diferentes, atrás de um "
            f"balanceador, com {SAY('failover')} que leva de segundos a "
            f"minutos."
            f"{BRK(400)} {FAULT_TOLERANCE}, tolerância a falhas, exige operar "
            f"{EMPH('sem nenhuma degradação perceptível')} durante a falha — "
            f"redundância ativa duplicada, processando em paralelo o tempo "
            f"todo. Custa significativamente mais."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E resiliência é a capacidade do sistema de se "
            f"recuperar de falhas e continuar operando — engloba alta "
            f"disponibilidade, tolerância a falhas, backups e recuperação de "
            f"desastre como ferramentas."
            f"{BRK(400)} Se o enunciado diz sem impacto perceptível ao usuário "
            f"durante a falha, é tolerância a falhas. Se aceita uma breve "
            f"interrupção até o {SAY('failover')}, é alta disponibilidade."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Padroes arquiteturais ----
    {
        "voice": "francisca",
        "text": (
            f"Existem padrões de arquitetura específicos para aumentar a "
            f"resiliência."
            f"{BRK(300)} Multi A Z são réplicas idênticas em zonas diferentes da "
            f"mesma região — o padrão mínimo de alta disponibilidade para "
            f"qualquer componente, com ou sem estado."
            f"{BRK(300)} O {BULKHEAD}, ou compartimentalização, isola recursos "
            f"por cliente ou função, para que a falha de um não afete os "
            f"outros — por exemplo, pools de conexão separados por cliente."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O {CIRCUIT_BREAKER} para de chamar um serviço que está "
            f"falhando repetidamente, evitando uma cascata de falhas pelo "
            f"sistema inteiro — isso é implementado em código, não é um "
            f"serviço gerenciado da {SAY('AWS')}."
            f"{BRK(300)} A {GRACEFUL_DEGRADATION} serve uma versão reduzida ou "
            f"cacheada quando um componente não crítico falha — por exemplo, "
            f"mostrar um produto sem recomendações personalizadas, em vez de "
            f"quebrar a página toda."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E a {STATIC_STABILITY} é um princípio do "
            f"Well-Architected: o sistema continua funcionando com a última "
            f"configuração conhecida, mesmo que o {CONTROL_PLANE} — por "
            f"exemplo, a A P I do Auto Scaling — esteja indisponível. A ideia é "
            f"evitar dependências do {CONTROL_PLANE} no caminho crítico durante "
            f"uma falha regional."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Exponential backoff ----
    {
        "voice": "francisca",
        "text": (
            f"Quando uma chamada falha, por throttling ou erro transitório, "
            f"repetir imediatamente só piora — gera uma onda sincronizada de "
            f"tentativas, o {RETRY_STORM}, que sobrecarrega ainda mais o "
            f"serviço."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A prática correta é o {EXPONENTIAL_BACKOFF} com "
            f"{JITTER}: a primeira tentativa falha e espera cerca de um "
            f"segundo; a segunda falha e espera cerca de dois segundos, mais um "
            f"componente aleatório; a terceira, cerca de quatro segundos; e "
            f"assim por diante, dobrando a cada vez."
            f"{BRK(400)} O {JITTER}, esse componente aleatório, evita que "
            f"múltiplos clientes re-tentem exatamente no mesmo instante. Os "
            f"S D Ks da {SAY('AWS')} já implementam isso nativamente — por "
            f"isso throttling ocasional do K M S ou {SAY('DynamoDB')} raramente "
            f"quebra uma aplicação bem configurada."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Auto Scaling recap ----
    {
        "voice": "antonio",
        "text": (
            f"Recapitulando rapidamente as políticas de Auto Scaling: "
            f"{TARGET_TRACKING} mantém uma métrica num alvo, como C P U em "
            f"cinquenta por cento — é o padrão, simples e eficaz para a "
            f"maioria dos casos."
            f"{BRK(300)} {STEP_SCALING} dá controle mais fino, escalando em "
            f"passos proporcionais à severidade do alarme."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {SCHEDULED} Scaling muda a capacidade em horário "
            f"definido, para picos previsíveis e recorrentes. E "
            f"{PREDICTIVE} Scaling usa aprendizado de máquina para escalar "
            f"proativamente antes do pico, evitando o atraso do scaling "
            f"reativo."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Desacoplamento ----
    {
        "voice": "francisca",
        "text": (
            f"Arquiteturas resilientes não fazem componentes se chamarem "
            f"diretamente, evitando o {TIGHT_COUPLING}. Elas inserem uma "
            f"camada de mensageria que absorve picos e isola falhas — se o "
            f"consumidor cair, as mensagens esperam na fila em vez de serem "
            f"perdidas."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} S Q S Standard desacopla com {AT_LEAST_ONCE} e melhor "
            f"esforço de ordem — para absorver picos e dar velocidade "
            f"independente ao backend."
            f"{BRK(300)} S Q S F I F O garante {EXACTLY_ONCE} dentro do mesmo "
            f"{MESSAGE_GROUP}, com ordem garantida, mas throughput menor."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} S N S é publicação e assinatura — todos os assinantes "
            f"recebem a mensagem, ótimo para alertas e notificações."
            f"{BRK(300)} E o padrão favorito da prova: S N S fazendo "
            f"{FAN_OUT} para várias filas S Q S, uma por sistema consumidor — "
            f"um evento, processado de forma independente por N sistemas "
            f"diferentes, cada um no seu próprio ritmo."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {EVENT_BRIDGE} é um barramento de eventos com regras "
            f"de filtro por conteúdo — ótimo para reagir a eventos de outros "
            f"serviços {SAY('AWS')} ou parceiros, e para agendamento do tipo "
            f"cron."
            f"{BRK(300)} {KINESIS_DATA_STREAMS} é streaming de alto "
            f"throughput, onde múltiplos consumidores leem o mesmo stream com "
            f"retenção configurável — use quando S Q S não escala o "
            f"suficiente, para milhões de eventos por segundo."
            f"{BRK(300)} E {AMAZON_MQ} é um broker gerenciado para protocolos "
            f"como M Q T T, A M Q P e J M S — usado para migrar aplicações "
            f"legadas que já usam ActiveMQ ou RabbitMQ, sem reescrever código."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- SQS pontos de prova ----
    {
        "voice": "francisca",
        "text": (
            f"Pontos de prova sobre S Q S, em detalhe."
            f"{BRK(300)} O {VISIBILITY_TIMEOUT} esconde a mensagem dos outros "
            f"consumidores enquanto ela está sendo processada — se não for "
            f"deletada a tempo, ela reaparece na fila, então o consumidor "
            f"precisa ser {IDEMPOTENT}: processar a mesma mensagem duas vezes "
            f"não pode causar efeito colateral duplicado."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A {DEAD_LETTER_QUEUE} isola mensagens que falharam "
            f"repetidas vezes, depois de um número definido de tentativas, o "
            f"{MAX_RECEIVE_COUNT}, sem travar o processamento das demais "
            f"mensagens saudáveis."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O {LONG_POLLING} espera até vinte segundos por uma "
            f"mensagem antes de retornar vazio, reduzindo custo e latência de "
            f"detecção comparado ao {SHORT_POLLING}. A {DELAY_QUEUE} atrasa a "
            f"entrega inicial por até quinze minutos, útil para esperar um "
            f"processo dependente terminar. E {MESSAGE_ATTRIBUTES} são "
            f"metadados estruturados, separados do corpo da mensagem, usados "
            f"pelo S N S para filtrar por assinante."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Um ponto importante: S Q S {EMPH('não é')} "
            f"{PUB_SUB}. Uma mensagem na fila é consumida por apenas um "
            f"consumidor, mesmo com vários workers competindo pela fila. Se "
            f"múltiplos sistemas independentes precisam receber a mesma "
            f"mensagem, S Q S sozinho não resolve — é preciso S N S fazendo "
            f"{FAN_OUT} para múltiplas filas."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- SNS filtros ----
    {
        "voice": "francisca",
        "text": (
            f"Um tópico S N S pode ter múltiplos assinantes, mas nem todos "
            f"precisam receber toda mensagem. As {FILTER_POLICIES} permitem "
            f"que cada assinante só receba mensagens cujos atributos casem com "
            f"seu filtro — evitando que cada consumidor precise filtrar no "
            f"próprio código, economizando invocações de Lambda com mensagens "
            f"irrelevantes."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório prático de três horas, "
            f"por cerca de cinquenta centavos, onde você monta um {SAY('ALB')} "
            f"na frente de um Auto Scaling Group, testa o auto-healing "
            f"terminando uma instância manualmente, configura S Q S com "
            f"{DEAD_LETTER_QUEUE}, e monta um {FAN_OUT} de S N S com "
            f"{FILTER_POLICIES} diferentes por fila."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (6 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: pedidos de um e-commerce devem ser "
            f"processados na ordem exata em que chegam, sem duplicatas. Qual "
            f"serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"S Q S F I F O — garante processamento {EXACTLY_ONCE} e ordem "
            f"dentro do mesmo {MESSAGE_GROUP}. S Q S Standard só garante "
            f"melhor esforço de ordem, e pode entregar duplicatas."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: upload de imagem precisa disparar três sistemas "
            f"independentes — gerar thumbnail, moderar conteúdo e indexar para "
            f"busca. Como fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"S N S fazendo {FAN_OUT} para três filas S Q S, cada uma com seu "
            f"próprio consumidor. Cada sistema processa no seu próprio ritmo, "
            f"sem que a falha de um afete os outros."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: a aplicação web fica lenta às nove da manhã em ponto, "
            f"todo dia útil, de forma previsível. Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SCHEDULED} Scaling — escala antes das nove, eliminando o atraso "
            f"do scaling reativo. {PREDICTIVE} Scaling é uma alternativa que "
            f"detecta o padrão automaticamente via aprendizado de máquina."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: por que alta disponibilidade e tolerância a falhas não "
            f"são sinônimos na prova?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Alta disponibilidade aceita um pequeno tempo de inatividade "
            f"durante o {SAY('failover')}. {FAULT_TOLERANCE} exige redundância "
            f"ativa duplicada o tempo todo, sem nenhuma degradação perceptível "
            f"— e custa significativamente mais."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: um serviço dependente está lento, e isso está "
            f"derrubando o sistema inteiro em cascata. Qual padrão de "
            f"resiliência aplicar?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{CIRCUIT_BREAKER} — para de chamar o serviço problemático após "
            f"detectar falhas repetidas, retornando erro imediatamente em vez "
            f"de esperar timeout a cada chamada. Depois de um período, ele "
            f"testa novamente antes de voltar ao normal."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: um worker chama repetidamente uma A P I que está "
            f"sendo {SAY('throttled')}, e cada nova tentativa imediata piora a "
            f"situação. O que fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Implementar {EXPONENTIAL_BACKOFF} com {JITTER} — aumentar o "
            f"tempo de espera exponencialmente entre tentativas, com um "
            f"componente aleatório, evitando que múltiplos clientes re-tentem "
            f"no mesmo instante. Os S D Ks da {SAY('AWS')} já fazem isso "
            f"nativamente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo seis. No próximo, vamos falar de "
            f"recuperação de desastre. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
