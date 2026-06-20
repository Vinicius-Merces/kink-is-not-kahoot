"""Roteiro tratado do Capitulo 13 (Otimizacao de custos) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

COST_EXPLORER = PHON("kɔst ɪkˈsplɔrɚ", "Cost Explorer")
BUDGETS = PHON("ˈbʌdʒɪts", "Budgets")
COST_USAGE_REPORT = PHON("kɔst ˈjusɪdʒ rɪˈpɔrt", "Cost and Usage Report")
COMPUTE_OPTIMIZER = PHON("kəmˈpjut ˈɑptəmaɪzɚ", "Compute Optimizer")
TRUSTED_ADVISOR = PHON("ˈtrʌstɪd ədˈvaɪzɚ", "Trusted Advisor")
STORAGE_LENS = PHON("ˈstɔrɪdʒ lɛnz", "Storage Lens")
GRAVITON = PHON("ˈɡrævɪtɑn", "Graviton")
RIGHTSIZING = PHON("ˈraɪtsaɪzɪŋ", "rightsizing")
FORECASTED_COST = PHON("fɔrˈkæstɪd kɔst", "forecasted cost")
SAVINGS_PLANS = PHON("ˈseɪvɪŋz plænz", "Savings Plans")
COMPUTE_SAVINGS_PLANS = PHON("kəmˈpjut ˈseɪvɪŋz plænz", "Compute Savings Plans")
LOCK_IN = PHON("lɑk ɪn", "lock-in")

BLOCKS = [
    {
        "voice": "antonio", "style": "cheerful",
        "text": (
            f"Capítulo treze: otimização de custos. Este é o capítulo cola "
            f"que amarra todos os outros doze. Toda questão de qual a opção "
            f"mais econômica segue o mesmo roteiro mental: identifique a "
            f"categoria do recurso — computação, armazenamento, banco, rede "
            f"ou governança — e pergunte qual alavanca de custo se aplica."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},

    # ---- Checklist mental ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos pela checklist mental, categoria por categoria."
            f"{BRK(300)} Computação: tolera interrupção? {SAY('Spot')}. "
            f"Carga estável? {SAVINGS_PLANS} ou Reservadas. Intermitente? "
            f"Lambda, Fargate ou Aurora {SAY('Serverless')}. E instâncias "
            f"{GRAVITON} custam de vinte a quarenta por cento menos."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Armazenamento: classe certa do {SAY('S3')} mais "
            f"{SAY('lifecycle')}. g p três em vez de g p dois. E deletar "
            f"{SAY('snapshots')} e volumes órfãos esquecidos."
            f"{BRK(300)} Banco: Aurora {SAY('Serverless')} para carga "
            f"intermitente. {SAY('DynamoDB')} {SAY('provisioned')}, para "
            f"carga previsível, é mais barato que {SAY('on-demand')}. T T L "
            f"para limpar itens antigos."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Rede, o custo invisível: tráfego entre zonas de "
            f"disponibilidade é cobrado. N A T {SAY('Gateway')} cobra por "
            f"hora mais por gigabyte — substitua por Gateway {SAY('Endpoint')} "
            f"para {SAY('S3')} e {SAY('DynamoDB')}. CloudFront reduz a "
            f"saída de dados da origem."
            f"{BRK(300)} E governança: desligar ambientes de "
            f"desenvolvimento à noite, deletar recursos não utilizados, e "
            f"fazer {RIGHTSIZING} com o {COMPUTE_OPTIMIZER}."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} A pergunta que resolve metade das questões de "
            f"custo: {EMPH('esse recurso precisa estar ligado o tempo todo?')} "
            f"Se a resposta for não — desenvolvimento, lote noturno, carga "
            f"intermitente — a resposta certa quase sempre envolve "
            f"{SAY('Spot')}, {SAY('Serverless')} ou agendamento, e não um "
            f"desconto sobre o modelo atual."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Ferramentas de visibilidade ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre ferramentas de visibilidade de custo: o "
            f"{COST_EXPLORER} analisa gastos e dá recomendações de "
            f"Reservadas e {SAVINGS_PLANS}. {BUDGETS} dá alertas e ações "
            f"quando um limite é estourado — pode até parar instâncias "
            f"automaticamente."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} O {COST_USAGE_REPORT} dá dados brutos detalhados "
            f"no {SAY('S3')}, para analisar com Athena ou {SAY('QuickSight')}. "
            f"O {COMPUTE_OPTIMIZER} faz {RIGHTSIZING} com aprendizado de "
            f"máquina, identificando recursos super-provisionados."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} O {TRUSTED_ADVISOR} faz checagens automáticas de "
            f"custo, segurança, performance e limites de serviço — recursos "
            f"ociosos, Reservadas subutilizadas, buckets públicos. E o "
            f"{SAY('S3')} {STORAGE_LENS} dá visibilidade de uso em toda a "
            f"organização, identificando buckets candidatos a {SAY('lifecycle')} "
            f"ou classe mais barata."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Custo de transferencia ----
    {
        "voice": "francisca",
        "text": (
            f"Agora a tabela de custo de transferência de dados, que "
            f"ninguém memoriza, mas devia."
            f"{BRK(300)} Entrada de dados, da internet para a "
            f"{SAY('AWS')}, é {EMPH('grátis')}, em qualquer direção. Saída "
            f"para a internet é cobrada por gigabyte, com desconto "
            f"conforme o volume."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Entre zonas de disponibilidade na mesma região é "
            f"cobrado, cerca de um centavo de dólar por gigabyte em cada "
            f"direção — mesmo dentro da mesma {SAY('VPC')}. Entre regiões "
            f"diferentes é cobrado, e tipicamente mais caro ainda."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Dentro da mesma zona, na mesma instância ou via I "
            f"P privado, é grátis. {SAY('S3')} para CloudFront é grátis. E "
            f"via Gateway {SAY('VPC')} {SAY('Endpoint')}, para {SAY('S3')} "
            f"ou {SAY('DynamoDB')}, também é grátis, sem custo de "
            f"processamento."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Trap e tip ----
    {
        "voice": "francisca",
        "text": (
            f"Uma armadilha importante: mais barato não significa menor "
            f"instância. A prova distingue reduzir custo de "
            f"{EMPH('reduzir custo sem comprometer o requisito')}. Trocar "
            f"um {SAY('RDS')} Multi A Z crítico por uma instância menor sem "
            f"Multi A Z, porque é mais barato, geralmente está errado se o "
            f"enunciado exige alta disponibilidade. A resposta certa busca "
            f"o modelo de compra ou classe mais barata que ainda atenda ao "
            f"requisito — nunca a remoção do requisito."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Sinal prático: tráfego entre zonas de "
            f"disponibilidade tem custo, mesmo na mesma região. Se o "
            f"enunciado pede reduzir custo de transferência entre "
            f"componentes na mesma {SAY('VPC')}, considere colocar recursos "
            f"que conversam muito na mesma zona — avaliando o "
            f"{SAY('trade-off')} de resiliência antes — ou usar "
            f"{SAY('VPC')} {SAY('Endpoints')} para tráfego que sairia para "
            f"serviços da {SAY('AWS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito traz um laboratório de uma hora, gratuito, "
            f"onde você filtra gastos no {COST_EXPLORER}, cria um "
            f"{SAY('Budget')} mensal com alerta em oitenta por cento, e "
            f"revisa os {SAY('labs')} anteriores procurando recursos "
            f"esquecidos ligados."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (8 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão final deste capítulo. Primeira: instâncias "
            f"{SAY('EC2')} privadas transferem dez terabytes por mês para o "
            f"{SAY('S3')} via N A T {SAY('Gateway')}. Como cortar esse "
            f"custo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Gateway {SAY('VPC')} {SAY('Endpoint')} para {SAY('S3')} — "
            f"gratuito, o tráfego vai direto sem passar pelo N A T, "
            f"eliminando o custo de processamento de dados do N A T "
            f"{SAY('Gateway')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: um cluster de análise roda seis horas por noite e "
            f"pode ser interrompido. Qual a opção mais barata?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('Spot')} Instances — tolerante a interrupção, com "
            f"desconto de até noventa por cento. Para {SAY('EMR')}: use "
            f"{SAY('Spot')} nos nós de tarefa, e {SAY('on-demand')} nos nós "
            f"principais."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: como alertar o gestor quando o gasto previsto "
            f"passar de mil dólares no mês?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {BUDGETS} com alerta de {FORECASTED_COST}, e "
            f"notificação via S N S ou e-mail."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: a empresa tem instâncias Reservadas compradas há um "
            f"ano, mas mudou de família de instância. Como aproveitar o "
            f"desconto sem perder flexibilidade?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Migrar para {COMPUTE_SAVINGS_PLANS} na próxima renovação — "
            f"oferecem desconto equivalente, mas se aplicam automaticamente "
            f"a qualquer família, região, e até Fargate e Lambda, "
            f"eliminando o {LOCK_IN} da configuração específica da "
            f"Reservada."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: ambientes de desenvolvimento ficam ligados o tempo "
            f"todo, mas só são usados em horário comercial. Qual a forma "
            f"mais simples de cortar custo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Automação de início e parada agendados — por exemplo, "
            f"EventBridge Scheduler mais Lambda — ligando no início do "
            f"expediente e desligando ao final. Corta o custo de "
            f"computação em cerca de sessenta e cinco por cento, sem afetar "
            f"o armazenamento."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: duas instâncias {SAY('EC2')} na mesma {SAY('VPC')}, "
            f"em zonas diferentes, trocam grandes volumes de dados "
            f"continuamente. Isso gera custo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Sim. Tráfego entre zonas é cobrado por gigabyte em cada "
            f"direção, mesmo na mesma {SAY('VPC')}. Se a latência entre "
            f"zonas não for problema e o requisito de disponibilidade "
            f"permitir, colocar os dois na mesma zona elimina esse custo — "
            f"mas avalie o {SAY('trade-off')} de resiliência antes."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como obter rapidamente uma lista de problemas de "
            f"custo, segurança e limite de serviço, sem configurar nenhuma "
            f"ferramenta nova?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {TRUSTED_ADVISOR} — roda checagens automáticas "
            f"pré-configuradas nas categorias de custo, segurança, "
            f"performance, tolerância a falhas e limites de serviço, sem "
            f"necessidade de configuração adicional."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo treze. No próximo, vamos aprofundar "
            f"em containers: {SAY('ECS')}, {SAY('EKS')} e Fargate. Até a "
            f"próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
