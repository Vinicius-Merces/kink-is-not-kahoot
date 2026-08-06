"""Roteiro tratado do Capitulo 21 (Cenarios integrados) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

ELASTICACHE = PHON("ɪˈlæstɪkæʃ", "ElastiCache")
STICKY_SESSIONS = PHON("ˈstɪki ˈsɛʃənz", "sticky sessions")
FIREHOSE = PHON("ˈfaɪɚhoʊz", "Firehose")
PARQUET = PHON("ˈpɑrkɛt", "Parquet")
LIFT_AND_SHIFT = PHON("lɪft ænd ʃɪft", "lift-and-shift")
REHOST = PHON("ri hoʊst", "rehost")
MGN = PHON("ɛm dʒi ɛn", "MGN")
SCT = PHON("ɛs si ti", "SCT")
DMS = PHON("di ɛm ɛs", "DMS")
CDC = PHON("si di si", "CDC")
SNOWBALL = PHON("ˈsnoʊbɔl", "Snowball")
COGNITO = PHON("kɑɡˈnitoʊ", "Cognito")
WAF = PHON("wɑf", "WAF")
GLOBAL_TABLES = PHON("ˈɡloʊbəl ˈteɪbəlz", "Global Tables")
WORM = PHON("wɜrm", "WORM")
SCP = PHON("ɛs si pi", "SCP")
GATEWAY_ENDPOINT = PHON("ˈɡeɪtweɪ ˈɛndpɔɪnt", "Gateway Endpoint")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo vinte e um: cenários integrados — pensando como a prova. "
            f"Os capítulos anteriores ensinam os serviços. Este capítulo treina "
            f"a leitura de arquiteturas: como traduzir os requisitos de um "
            f"enunciado em serviços {SAY('AWS')}, e por que as alternativas "
            f"tentadoras falham. São cinco cenários completos."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Cenario 1: e-commerce com picos sazonais ----
    {
        "voice": "antonio",
        "text": (
            f"Primeiro cenário: loja virtual com tráfego dez vezes maior na "
            f"Black Friday. Os requisitos são: sem downtime, sessões de usuários "
            f"não podem se perder quando uma instância morre, imagens lentas para "
            f"usuários de outros estados, e o banco não pode perder pedidos em "
            f"falha de zona."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Traduzindo cada requisito. Tráfego dez vezes maior na "
            f"Black Friday significa elasticidade horizontal — Auto Scaling Group "
            f"multi-zona atrás de um {SAY('ALB')}. Sessões não podem se perder "
            f"quando a instância morre significa estado fora da instância — "
            f"{ELASTICACHE} Redis ou {SAY('DynamoDB')} para sessões, nunca memória "
            f"local."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Imagens lentas para usuários distantes significa "
            f"conteúdo estático na borda — {SAY('S3')} como origem mais "
            f"CloudFront com cache nas edge locations. E banco não pode perder "
            f"pedidos em falha de zona significa failover automático do banco — "
            f"{SAY('RDS')} Multi-{SAY('AZ')}, com Read Replicas apenas se "
            f"houver menção a relatórios ou leitura pesada."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} As alternativas tentadoras neste cenário: {STICKY_SESSIONS} "
            f"parecem resolver o problema de sessão, mas quando a instância morre "
            f"a sessão morre junto — são conveniência de roteamento, não "
            f"resiliência. Scale-up, colocar uma instância maior, atende o pico "
            f"mas mantém o ponto único de falha. E Read Replica no lugar de "
            f"Multi-{SAY('AZ')} confunde performance com disponibilidade — réplica "
            f"não tem failover automático."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Cenario 2: analytics near real-time ----
    {
        "voice": "antonio",
        "text": (
            f"Segundo cenário: milhares de eventos por minuto devem ficar "
            f"consultáveis em {SAY('SQL')} em poucos minutos, com o mínimo de "
            f"infraestrutura gerenciada e custo de consulta baixo. O time não "
            f"quer administrar servidores nem clusters."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A arquitetura: Kinesis Data {FIREHOSE} entregando para o "
            f"{SAY('S3')} com buffer de cerca de sessenta segundos. O {FIREHOSE} "
            f"converte os dados nativamente para o formato {PARQUET} e faz "
            f"particionamento por data — menos dados escaneados, custo de consulta "
            f"menor. Depois, o Glue Data Catalog registra o schema, e o Athena "
            f"consulta os dados com {SAY('SQL')} diretamente no {SAY('S3')}, "
            f"pagando por terabyte escaneado, sem servidor."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} As tentadoras aqui: Kinesis Data Streams mais consumidor "
            f"em {SAY('EC2')} funciona, mas viola o mínimo de gerenciamento — "
            f"você mantém o consumidor. Carregar tudo num {SAY('RDS')} é um banco "
            f"{SAY('OLTP')} para análise de logs — caro e lento. Redshift "
            f"provisionado vinte e quatro horas por dia só se o volume e a "
            f"frequência justificarem; para consulta ocasional, o Athena vence "
            f"em custo."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Cenario 3: migracao com prazo apertado ----
    {
        "voice": "antonio",
        "text": (
            f"Terceiro cenário: contrato do data center vence em seis meses. "
            f"Quarenta servidores VMware, um banco Oracle crítico que não pode "
            f"parar mais que minutos, trezentos terabytes de arquivos frios e "
            f"link de duzentos megabits. Durante a transição, sistemas locais e "
            f"migrados precisam conversar com segurança."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A arquitetura: para os quarenta servidores com prazo "
            f"curto, {LIFT_AND_SHIFT} com o {SAY('AWS')} {MGN}, o Application "
            f"Migration Service — replicação contínua e cutover rápido. Para o "
            f"Oracle sem parar, migração heterogênea quase sem downtime com "
            f"{SCT} para converter o schema, mais {DMS} com full load e {CDC} "
            f"para replicação contínua."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Para os trezentos terabytes com link de duzentos "
            f"megabits: matematicamente, essa transferência levaria meses pela "
            f"rede — a família {SNOWBALL} com dispositivo físico é a resposta. "
            f"E para a conectividade híbrida segura durante a transição, "
            f"{SAY('VPN')} Site-a-Site de imediato; Direct Connect se a transição "
            f"se estender."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} As tentadoras: DataSync para os trezentos terabytes "
            f"ignora a matemática da banda — a regra prática é que mais de uma "
            f"semana pela rede leva à família Snow. Dump e restore do Oracle "
            f"gera horas de downtime — o requisito 'minutos' força {CDC}. E "
            f"refatorar para serverless em seis meses é a alternativa bonita "
            f"que estoura o prazo — {REHOST} primeiro, modernize depois."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Cenario 4: API serverless global ----
    {
        "voice": "antonio",
        "text": (
            f"Quarto cenário: {SAY('API')} mobile com usuários em três continentes, "
            f"tráfego imprevisível — zero à noite, picos ao meio-dia. Login "
            f"obrigatório, proteção contra bots e injeção, e latência de leitura "
            f"de milissegundos de um catálogo acessado globalmente."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A arquitetura: tráfego imprevisível que cai a zero "
            f"aponta direto para o trio serverless — {SAY('API')} Gateway mais "
            f"Lambda mais {SAY('DynamoDB')}. Para usuários em três continentes, "
            f"{SAY('API')} Gateway edge-optimized com CloudFront e {SAY('DynamoDB')} "
            f"{GLOBAL_TABLES} para replicação multi-região automática do catálogo."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Para o login, {COGNITO} User Pool mais um autorizador no "
            f"{SAY('API')} Gateway, gerando {SAY('JWT')} gerenciado. Para bots e "
            f"injeção, {SAY('AWS')} {WAF} com managed rules e rate-based rules "
            f"associado à distribuição CloudFront ou à {SAY('API')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} As tentadoras: {SAY('ALB')} mais {SAY('EC2')} mais Auto "
            f"Scaling atende, mas paga capacidade ociosa à noite — tráfego "
            f"imprevisível com vales é o gatilho do serverless. Shield Standard "
            f"sozinho não filtra injeção — ele é proteção de D D o S nas camadas "
            f"três e quatro; a camada sete é o {WAF}. E replicar {SAY('RDS')} "
            f"entre continentes para catálogo chave-valor é usar o martelo errado "
            f"— {GLOBAL_TABLES} faz isso nativamente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Cenario 5: compliance financeiro ----
    {
        "voice": "antonio",
        "text": (
            f"Quinto cenário: fintech regulada. Registros de transação imutáveis "
            f"por sete anos — nem admins podem apagar. Toda chamada de {SAY('API')} "
            f"auditada em todas as contas da organização. Chaves de criptografia "
            f"com uso rastreável. Regiões fora do Brasil bloqueadas para todos. "
            f"E acesso aos dados sem tráfego pela internet."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A arquitetura: para imutabilidade absoluta por sete anos, "
            f"{SAY('S3')} Object Lock em modo Compliance — modelo {WORM}. Para "
            f"auditoria de toda a organização, CloudTrail organization trail. "
            f"Para criptografia auditável, S S E dash K M S com Customer Managed "
            f"Key — cada uso da chave gera um evento no CloudTrail."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Para bloquear regiões fora do Brasil para todos, "
            f"{SCP} na unidade organizacional com condição "
            f"'aws colon RequestedRegion' — nenhuma política I A M por conta "
            f"consegue esse guardrail acima do I A M. E para acesso privado "
            f"aos serviços sem tráfego pela internet, {GATEWAY_ENDPOINT} para "
            f"{SAY('S3')} e {SAY('DynamoDB')}, mais Interface Endpoints para os "
            f"demais serviços."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} As tentadoras do cenário de compliance: Object Lock em "
            f"modo Governance cai no 'nem admins' — usuários com a permissão de "
            f"bypass conseguem remover a retenção; apenas o modo Compliance é "
            f"absoluto. Bucket policy negando delete parece imutável, mas policies "
            f"são editáveis por quem tem permissão. E {SAY('IAM')} policy negando "
            f"regiões precisa ser replicada em cada conta — {SCP} resolve no nível "
            f"da organização de uma vez."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- O metodo em 4 passos ----
    {
        "voice": "antonio",
        "text": (
            f"Por fim, o método em quatro passos para levar para a prova. "
            f"{BRK(400)} Primeiro: sublinhe os requisitos não-funcionais — "
            f"disponível? barato? menor esforço? mais rápido? compliance? "
            f"São eles que decidem entre duas alternativas tecnicamente corretas."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Segundo: traduza cada frase do cenário em um serviço "
            f"candidato. Terceiro: elimine as alternativas que violam qualquer "
            f"requisito — uma única violação já elimina. Quarto: entre as "
            f"sobreviventes, escolha a de menor esforço operacional. Na dúvida, "
            f"serviço gerenciado vence autogerenciado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão rápida. Primeira: 'sessões não podem se perder quando "
            f"uma instância morre' — qual a resposta padrão e por que "
            f"{STICKY_SESSIONS} não é?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Externalizar o estado em {ELASTICACHE} ou {SAY('DynamoDB')}. "
            f"{STICKY_SESSIONS} prendem o usuário à instância — quando ela morre, "
            f"a sessão morre junto. É conveniência de roteamento, não resiliência."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: que frases do enunciado gritam 'serverless' em vez de "
            f"{SAY('EC2')} mais Auto Scaling?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"'Tráfego imprevisível ou esporádico', 'zero em certos períodos', "
            f"'pagar apenas pelo uso', 'mínimo esforço operacional'. Tráfego alto "
            f"e constante, por outro lado, pode favorecer {SAY('EC2')} com "
            f"Savings Plans."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: dois requisitos apontam serviços diferentes para o mesmo "
            f"problema. Qual critério desempata na prova?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O requisito não-funcional explícito do enunciado: mais barato, "
            f"menor esforço, mais rápido, menor latência. O S A A quase sempre "
            f"pede 'a solução que atende com menor X' — esse X é o desempate. "
            f"Na dúvida, gerenciado vence autogerenciado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo vinte e um e a trilha completa do {SAY('SAA')} "
            f"dash C zero três! Você tem os conceitos, os padrões e o método "
            f"de leitura da prova. Agora é hora do simulado completo. Boa sorte!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
