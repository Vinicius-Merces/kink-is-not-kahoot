"""Roteiro tratado do Capitulo 20 (AWS Well-Architected Framework) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

OPERATIONAL_EXCELLENCE = PHON("ˌɑpəˈreɪʃənəl ˈɛksələns", "Operational Excellence")
SECURITY_PILLAR = PHON("sɪˈkjʊrəti", "Security")
RELIABILITY = PHON("rɪˌlaɪəˈbɪləti", "Reliability")
PERFORMANCE_EFFICIENCY = PHON("pɚˈfɔrməns ɪˈfɪʃənsi", "Performance Efficiency")
PERFORMANCE = PHON("pɚˈfɔrməns", "Performance")
COST_OPTIMIZATION = PHON("kɔst ˌɑptəməˈzeɪʃən", "Cost Optimization")
SUSTAINABILITY = PHON("səˌsteɪnəˈbɪləti", "Sustainability")
WELL_ARCHITECTED_TOOL = PHON("wɛl ˈɑrkɪtɛktɪd tul", "Well-Architected Tool")
TRUSTED_ADVISOR = PHON("ˈtrʌstɪd ədˈvaɪzɚ", "Trusted Advisor")
FAULT_TOLERANCE = PHON("fɔlt ˈtɑlərəns", "Fault Tolerance")
SERVICE_LIMITS = PHON("ˈsɜrvɪs ˈlɪmɪts", "Service Limits")
GRAVITON = PHON("ˈɡrævɪtɑn", "Graviton")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo vinte, o último: A W S Well-Architected Framework. "
            f"Este é o capítulo guarda-chuva da prova — ele não introduz "
            f"serviços novos, mas dá uma lente de leitura para qualquer "
            f"questão de cenário."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    {
        "voice": "antonio",
        "text": (
            f"Quando o enunciado descreve uma arquitetura e pergunta qual "
            f"a melhor solução, ele está, na prática, pedindo para "
            f"identificar qual pilar está sendo testado — e a resposta "
            f"certa é quase sempre a que resolve esse pilar sem "
            f"sacrificar demais os outros."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- 6 pilares ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos pelos seis pilares."
            f"{BRK(300)} {OPERATIONAL_EXCELLENCE}: operar e monitorar "
            f"sistemas, melhorando processos continuamente. A pergunta "
            f"chave: como saberemos que algo quebrou, e como automatizamos "
            f"a resposta?"
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {SECURITY_PILLAR}: proteger dados, sistemas e "
            f"ativos via gestão de risco. A pergunta chave: quem pode "
            f"acessar o quê, e os dados estão protegidos em repouso e em "
            f"trânsito?"
            f"{BRK(300)} {RELIABILITY}: recuperação de falhas, "
            f"escalonamento dinâmico de demanda. A pergunta chave: o "
            f"sistema se recupera sozinho de uma falha de zona ou "
            f"instância?"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {PERFORMANCE_EFFICIENCY}: uso eficiente de "
            f"recursos conforme a demanda evolui. A pergunta chave: "
            f"estamos usando o tipo certo de recurso para essa carga de "
            f"trabalho?"
            f"{BRK(300)} {COST_OPTIMIZATION}: evitar gastos desnecessários "
            f"e entender para onde o dinheiro vai. A pergunta chave: "
            f"estamos pagando por capacidade ociosa quando algo "
            f"{SAY('serverless')} ou {SAY('Spot')} resolveria?"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} E {SUSTAINABILITY}: minimizar os impactos "
            f"ambientais das cargas de trabalho na nuvem. A pergunta "
            f"chave: podemos reduzir consumo de energia escolhendo "
            f"regiões ou instâncias mais eficientes?"
        ),
    },
    {"voice": "antonio", "text": BRK(800)},
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Mantra para gravar: a palavra-chave do enunciado "
            f"aponta o pilar. Mínimo esforço operacional aponta para "
            f"{OPERATIONAL_EXCELLENCE} — pense gerenciado ou "
            f"{SAY('serverless')}. Criptografado, menor privilégio, "
            f"auditoria, aponta para {SECURITY_PILLAR}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Sobrevive à perda de uma zona, ou {SAY('RPO')} e "
            f"{SAY('RTO')}, aponta para {RELIABILITY}. Mais rápido, menor "
            f"latência, aponta para {PERFORMANCE_EFFICIENCY}. Mais "
            f"barato, reduzir custo, aponta para {COST_OPTIMIZATION}. "
            f"{EMPH('Quando duas opções parecem tecnicamente corretas, o pilar destacado no enunciado decide o desempate')}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Well-Architected Tool vs Trusted Advisor ----
    {
        "voice": "antonio",
        "text": (
            f"Duas ferramentas valem conhecer: a {WELL_ARCHITECTED_TOOL} "
            f"é gratuita — guia você por um questionário sobre sua carga "
            f"de trabalho à luz dos seis pilares, e gera um relatório de "
            f"riscos, alto ou médio, com recomendações específicas."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {TRUSTED_ADVISOR} faz verificações "
            f"automatizadas em tempo real, agrupadas em cinco categorias: "
            f"{COST_OPTIMIZATION}, {PERFORMANCE}, "
            f"{SECURITY_PILLAR}, {FAULT_TOLERANCE} e {SERVICE_LIMITS}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} No plano de suporte {SAY('Basic')} ou "
            f"{SAY('Developer')}, você só vê um subconjunto de checagens "
            f"de {SECURITY_PILLAR} e {SERVICE_LIMITS}. Cobertura completa "
            f"das cinco categorias exige plano {SAY('Business')} ou "
            f"{SAY('Enterprise')}, que também libera acesso programático "
            f"via A P I."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um exercício de vinte minutos, "
            f"gratuito: pense numa arquitetura simples — uma "
            f"{SAY('t2.micro')} numa única zona, com banco MySQL na mesma "
            f"instância, sem {SAY('backups')} automatizados. Para cada um "
            f"dos seis pilares, identifique pelo menos um risco, e proponha "
            f"a melhoria mínima usando os serviços vistos nesta trilha."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (6 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da última revisão. Primeira: a questão pede a solução "
            f"que minimiza o esforço operacional da equipe para hospedar "
            f"uma A P I — entre {SAY('EC2')} com Auto Scaling e Lambda "
            f"mais API Gateway. Qual pilar está em jogo, e qual tende a "
            f"ser a resposta?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{OPERATIONAL_EXCELLENCE}. Mínimo esforço operacional é a "
            f"palavra-chave clássica para soluções {SAY('serverless')} ou "
            f"gerenciadas — Lambda mais API Gateway tende a ser a "
            f"resposta, pois elimina correção de falhas, planejamento de "
            f"capacidade e gestão de servidores."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: duas soluções atendem igualmente bem ao requisito "
            f"funcional, mas uma usa Reservadas e outra {SAY('Spot')} para "
            f"um {SAY('job')} de lote tolerante a interrupções. Qual "
            f"pilar decide, e qual vence?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{COST_OPTIMIZATION}. Para cargas tolerantes a interrupção, "
            f"{SAY('Spot')} vence por custo significativamente menor — "
            f"Reservadas fazem sentido para cargas previsíveis e "
            f"contínuas, não para {SAY('jobs')} de lote flexíveis."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: qual ferramenta gratuita gera um relatório de "
            f"riscos alto ou médio, de uma carga de trabalho específica, "
            f"à luz dos seis pilares?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {WELL_ARCHITECTED_TOOL} — questionário guiado por "
            f"carga de trabalho, sem custo adicional, disponível em "
            f"qualquer plano de suporte."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: um cliente no plano de suporte {SAY('Basic')} quer "
            f"usar o {TRUSTED_ADVISOR} para ver todas as checagens de "
            f"{FAULT_TOLERANCE} e performance da conta. Isso é "
            f"possível?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Não. No plano {SAY('Basic')} ou {SAY('Developer')}, o "
            f"{TRUSTED_ADVISOR} expõe apenas um subconjunto de checagens "
            f"de {SECURITY_PILLAR} e {SERVICE_LIMITS}. Cobertura completa "
            f"das cinco categorias exige plano {SAY('Business')} ou "
            f"{SAY('Enterprise')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: uma arquitetura roda em uma única zona, e o "
            f"enunciado destaca {SAY('RPO')} de cinco minutos e "
            f"{SAY('RTO')} de uma hora. Qual pilar está sendo avaliado, e "
            f"o que isso sinaliza sobre a resposta esperada?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{RELIABILITY}. Números de {SAY('RPO')} e {SAY('RTO')} "
            f"sinalizam que a resposta precisa de uma estratégia de "
            f"recuperação de desastre concreta — Multi A Z ou "
            f"multi-região com {SAY('backups')} ou replicação que atendam "
            f"a essas metas, não apenas fazer {SAY('backup')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: a empresa quer reduzir a pegada de carbono de "
            f"suas cargas de trabalho, sem trocar de provedor de nuvem. "
            f"Qual pilar trata disso, e que tipo de ação se encaixa?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SUSTAINABILITY}. Ações típicas: escolher regiões com "
            f"matriz energética mais limpa, usar instâncias mais "
            f"eficientes, como {GRAVITON}, desligar recursos ociosos, e "
            f"adotar arquiteturas {SAY('serverless')} que escalam a zero."
        ),
    },
    {"voice": "antonio", "text": BRK(1500)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"E assim encerramos os vinte capítulos da nossa trilha de "
            f"estudos para o exame Solutions Architect Associate. "
            f"Parabéns por chegar até aqui — revise os pontos que mais "
            f"pegaram, refaça os laboratórios práticos, e boa sorte na "
            f"prova!"
        ),
    },
    {"voice": "francisca", "text": BRK(2000)},
]
