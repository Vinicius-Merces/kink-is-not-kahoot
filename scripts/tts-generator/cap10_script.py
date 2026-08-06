"""Roteiro tratado do Capitulo 10 (Monitoramento) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

SAMPLING_RULES = PHON("ˈsæmplɪŋ rulz", "sampling rules")
ANNOTATIONS = PHON("ˌænəˈteɪʃənz", "Annotations")
METADATA_XRAY = PHON("ˈmɛtədeɪtə", "Metadata")
METRIC_FILTERS = PHON("ˈmɛtrɪk ˈfɪltɚz", "Metric Filters")
EMF = PHON("i ɛm ɛf", "EMF")
COMPOSITE_ALARMS = PHON("kəmˈpɑzɪt əˈlɑrmz", "Composite Alarms")
ANOMALY_DETECTION = PHON("əˈnɑməli dɪˈtɛkʃən", "Anomaly Detection")
LOGS_INSIGHTS = PHON("lɔɡz ˈɪnsaɪts", "Logs Insights")
SYNTHETICS = PHON("sɪnˈθɛtɪks", "Synthetics")
CONTRIBUTOR_INSIGHTS = PHON("kənˈtrɪbjətɚ ˈɪnsaɪts", "Contributor Insights")
MANAGEMENT_EVENTS = PHON("ˈmænɪdʒmənt ɪˈvɛnts", "Management Events")
MANAGEMENT_EVENT = PHON("ˈmænɪdʒmənt ɪˈvɛnt", "Management Event")
DATA_EVENTS = PHON("ˈdeɪtə ɪˈvɛnts", "Data Events")
DATA_EVENT = PHON("ˈdeɪtə ɪˈvɛnt", "Data Event")
CLOUDTRAIL_LAKE = PHON("klaʊdtreɪl leɪk", "CloudTrail Lake")
CONFIGURATION_ITEM = PHON("kənˌfɪɡjəˈreɪʃən ˈaɪtəm", "ConfigurationItem")
CONFIG_RULES = PHON("ˈkɑnfɪɡ rulz", "Config Rules")
CONFORMANCE_PACKS = PHON("kənˈfɔrməns pæks", "Conformance Packs")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dez: monitoramento. Três serviços respondem três "
            f"perguntas diferentes — e quase toda questão se resolve "
            f"identificando qual das três o enunciado está fazendo."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Trio sagrado ----
    {
        "voice": "antonio",
        "text": (
            f"O CloudWatch responde: o que está acontecendo? Métricas, "
            f"logs, alarmes e {SAY('dashboards')}. E atenção: memória de uma "
            f"{SAY('EC2')} exige o CloudWatch {SAY('Agent')} instalado — "
            f"métricas básicas vêm de fora do {SAY('hypervisor')}, sem "
            f"visibilidade do que acontece dentro do sistema operacional."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O CloudTrail responde: quem fez o quê, e quando? É "
            f"auditoria de A P I — quem deletou o bucket, por exemplo. Um "
            f"{SAY('trail')} configurado para o {SAY('S3')} retém além dos "
            f"noventa dias padrão do console."
            f"{BRK(400)} E o Config responde: como está, ou estava, "
            f"configurado? Use para alertar se um security group abrir a "
            f"porta vinte e dois ao mundo, com histórico de configuração e "
            f"remediação automática."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- X-Ray ----
    {
        "voice": "francisca",
        "text": (
            f"Quando o enunciado descreve uma arquitetura com múltiplos "
            f"microsserviços — API Gateway, Lambda, {SAY('DynamoDB')}, S N S "
            f"— e pede para identificar o gargalo de latência, a resposta é "
            f"o A W S X-Ray. Ele traça o caminho completo de uma requisição "
            f"através dos serviços, mostrando um mapa com o tempo de cada "
            f"salto."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Para reduzir custo, o X-Ray usa {SAMPLING_RULES} — "
            f"não traceia cem por cento das requisições por padrão. "
            f"{ANNOTATIONS} são indexáveis e usadas em filtros; "
            f"{METADATA_XRAY} não é indexável, serve só de contexto."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Sinal prático: identificar qual componente causa "
            f"latência numa cadeia de microsserviços é X-Ray. O que aconteceu "
            f"com C P U, memória ou disco é CloudWatch. São perguntas "
            f"diferentes — não confunda rastreamento de uma requisição com "
            f"métricas agregadas de infraestrutura."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- CloudWatch componentes ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos detalhar os componentes do CloudWatch."
            f"{BRK(300)} Metrics são séries temporais numéricas, com "
            f"métricas customizadas via A P I, ou extraídas de logs via "
            f"{METRIC_FILTERS} e o formato {EMF}."
            f"{BRK(300)} Alarms disparam ações quando uma métrica cruza um "
            f"limiar. {COMPOSITE_ALARMS} combinam múltiplos alarmes com "
            f"lógica E ou OU, reduzindo ruído de alertas correlacionados."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {ANOMALY_DETECTION} usa aprendizado de máquina para "
            f"aprender o padrão normal, considerando sazonalidade — melhor "
            f"que um limiar fixo para métricas cíclicas, como tráfego que "
            f"varia por hora do dia."
            f"{BRK(300)} Logs e {LOGS_INSIGHTS} centralizam logs de Lambda, "
            f"{SAY('ECS')} e {SAY('EC2')}, com consultas próprias, sem "
            f"precisar exportar para outra ferramenta."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {SAY('Dashboards')} dão visualização consolidada de "
            f"múltiplos serviços, regiões ou contas. {SYNTHETICS} são "
            f"canários — {SAY('scripts')} que simulam usuários reais, "
            f"alertando antes que usuários de verdade notem o problema. E "
            f"{CONTRIBUTOR_INSIGHTS} identifica os maiores contribuintes para "
            f"um problema, como qual I P gera mais erros, sem escrever query "
            f"manual."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Armadilha importante: o CloudWatch não vê dentro da "
            f"instância por padrão. Métricas básicas de {SAY('EC2')} — C P U, "
            f"rede, status checks — vêm de fora, sem nada instalado. "
            f"{EMPH('Memória e uso de disco exigem o CloudWatch Agent')} "
            f"instalado dentro da instância — sem ele, alertar sobre memória "
            f"é impossível, porque a {SAY('AWS')} não vê o processo do "
            f"sistema guest por padrão."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- CloudTrail Management/Data Events ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre o CloudTrail: {MANAGEMENT_EVENTS} são operações de "
            f"controle — criar, deletar, mudar configuração. São gravados "
            f"por padrão, e grátis para os últimos noventa dias no console."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {DATA_EVENTS} são operações em nível de dado dentro "
            f"do recurso — ler ou gravar um objeto no {SAY('S3')}, invocar "
            f"uma Lambda — com volume muito maior. Vêm "
            f"{EMPH('desativados por padrão')}, por custo, e precisam ser "
            f"ativados explicitamente quando você precisa auditar quem leu "
            f"um objeto específico."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E o {CLOUDTRAIL_LAKE} permite consultas S Q L "
            f"diretamente sobre os eventos do {SAY('trail')}, sem precisar "
            f"exportar para Athena ou {SAY('S3')} manualmente — útil para "
            f"investigações pontuais de segurança."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- AWS Config ----
    {
        "voice": "antonio",
        "text": (
            f"O A W S Config grava um histórico de configuração de cada "
            f"recurso ao longo do tempo, o {CONFIGURATION_ITEM}, e avalia "
            f"continuamente contra {CONFIG_RULES}, gerenciadas pela "
            f"{SAY('AWS')} ou customizadas via Lambda."
            f"{BRK(400)} {CONFORMANCE_PACKS} agrupam várias regras "
            f"relacionadas a um framework de compliance específico, "
            f"aplicáveis em múltiplas contas via Organizations."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito traz um laboratório de uma hora, gratuito, "
            f"onde você instala o CloudWatch {SAY('Agent')} e cria um alarme "
            f"de memória, configura um {SAY('trail')} de CloudTrail, ativa "
            f"uma regra no Config para portas abertas, e instrumenta uma "
            f"Lambda com X-Ray."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: descobrir quem terminou uma "
            f"instância {SAY('EC2')} ontem. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"CloudTrail — registra toda chamada de A P I, um "
            f"{MANAGEMENT_EVENT}, com usuário, "
            f"horário e I P de origem."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: impedir que qualquer conta da organização use regiões "
            f"fora da América do Sul. Como?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('SCP')} no Organizations, com condição na região "
            f"solicitada. A {SAY('SCP')} define o teto — mesmo "
            f"administradores das contas-membro não conseguem ultrapassar."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: uma aplicação com vários microsserviços está lenta, "
            f"mas não se sabe qual serviço é o gargalo. Qual serviço "
            f"usar?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S X-Ray — gera um mapa de serviço com a latência de cada "
            f"salto da requisição, identificando exatamente onde o tempo "
            f"está sendo gasto."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: a equipe quer ser avisada se alguém abrir a porta "
            f"vinte e dois para o mundo, e corrigir automaticamente se "
            f"possível. Como?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S Config com uma regra gerenciada, que avalia "
            f"continuamente os security groups e pode remediar "
            f"automaticamente via um documento de automação do S S M."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: os logs do CloudTrail precisam ser retidos por cinco "
            f"anos para auditoria de compliance. Qual a configuração "
            f"correta?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Configurar o {SAY('trail')} para entregar os logs a um bucket "
            f"{SAY('S3')}. O console do CloudTrail por padrão só mostra "
            f"noventa dias, mas um {SAY('trail')} configurado para {SAY('S3')} "
            f"retém indefinidamente, conforme a política do bucket."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: é preciso auditar quem leu um objeto {SAY('S3')} "
            f"específico com dados sensíveis. Os {MANAGEMENT_EVENTS} do "
            f"CloudTrail são suficientes?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Não. Ler um objeto é um {DATA_EVENT}, "
            f"desativado por padrão por questão de custo e volume. É preciso "
            f"ativar {DATA_EVENTS} explicitamente para esse bucket."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: uma métrica de tráfego tem padrão sazonal "
            f"previsível, e alarmes de limiar fixo geram falsos positivos "
            f"constantes. Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"CloudWatch {ANOMALY_DETECTION} — usa aprendizado de máquina "
            f"para aprender o padrão normal considerando a sazonalidade, "
            f"criando uma faixa esperada que se ajusta por horário, em vez de "
            f"um limiar fixo único."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dez. No próximo, vamos falar de "
            f"migração: D M S, Snow Family e estratégias de migração. Até a "
            f"próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
