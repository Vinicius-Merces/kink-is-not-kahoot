"""Roteiro tratado do Capitulo 7 (Disaster Recovery) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

RPO = PHON("ɑr pi oʊ", "RPO")
RTO = PHON("ɑr ti oʊ", "RTO")
BACKUP_AND_RESTORE = PHON("ˈbækʌp ænd rɪˈstɔr", "Backup and Restore")
PILOT_LIGHT = PHON("ˈpaɪlət laɪt", "Pilot Light")
WARM_STANDBY = PHON("wɔrm ˈstændbaɪ", "Warm Standby")
MULTI_SITE_ACTIVE_ACTIVE = PHON("ˈmʌlti saɪt ˈæktɪv ˈæktɪv", "Multi-site Active/Active")
AWS_BACKUP = PHON("eɪ dʌbəlju ɛs ˈbækʌp", "AWS Backup")
DRS = PHON("di ɑr ɛs", "DRS")
CLOUDENDURE = PHON("klaʊd ɪnˈdjʊr", "CloudEndure")
GLOBAL_DATABASE = PHON("ˈɡloʊbəl ˈdeɪtəbeɪs", "Global Database")
BACKUP_PLANS = PHON("ˈbækʌp plænz", "Backup Plans")
BACKUP_VAULT_LOCK = PHON("ˈbækʌp vɔlt lɑk", "Backup Vault Lock")
WORM = PHON("wɜrm", "WORM")
CROSS_REGION_COPY = PHON("krɔs ˈridʒən ˈkɑpi", "Cross-Region Copy")
CROSS_ACCOUNT_COPY = PHON("krɔs əˈkaʊnt ˈkɑpi", "Cross-Account Copy")
BACKUP_AUDIT_MANAGER = PHON("ˈbækʌp ˈɔdɪt ˈmænɪdʒɚ", "Backup Audit Manager")
RESILIENCE_HUB = PHON("rɪˈzɪljəns hʌb", "Resilience Hub")
FAULT_INJECTION_SERVICE = PHON("fɔlt ɪnˈdʒɛkʃən ˈsɜrvɪs", "Fault Injection Service")
CHAOS_ENGINEERING = PHON("ˈkeɪɑs ˌɛndʒəˈnɪrɪŋ", "Chaos Engineering")
GAME_DAYS = PHON("ɡeɪm deɪz", "Game Days")
GAME_DAY = PHON("ɡeɪm deɪ", "Game Day")
RUNBOOK = PHON("ˈrʌnbʊk", "runbook")
RANSOMWARE = PHON("ˈrænsəmwɛr", "ransomware")
COMPLIANCE_MODE = PHON("kəmˈplaɪəns moʊd", "Compliance")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo sete: recuperação de desastre, ou Disaster Recovery. "
            f"Vamos falar de dois números que definem toda a estratégia, e das "
            f"quatro abordagens possíveis, da mais barata à mais cara."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- RPO / RTO ----
    {
        "voice": "francisca",
        "text": (
            f"{RPO}, o objetivo de ponto de recuperação, responde: quanto de "
            f"dado eu posso perder? Ele olha para o passado, e depende de "
            f"quando foi o último backup ou replicação."
            f"{BRK(400)} {RTO}, o objetivo de tempo de recuperação, responde: "
            f"quanto tempo eu posso ficar fora do ar? Ele olha para o futuro, e "
            f"depende de quanto tempo leva para restabelecer o serviço. "
            f"{EMPH('Quanto menores os dois, mais cara a estratégia')}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- 4 estrategias ----
    {
        "voice": "antonio",
        "text": (
            f"Existem quatro estratégias clássicas, da mais barata à mais cara."
            f"{BRK(400)} {BACKUP_AND_RESTORE}: só backups e snapshots copiados "
            f"para outra região. No desastre, você reconstrói tudo do zero com "
            f"CloudFormation. {RPO} de horas, {RTO} de horas a dias — a mais "
            f"barata."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {PILOT_LIGHT}: os dados replicam continuamente na "
            f"região de recuperação, mas a aplicação está desligada, só pronta "
            f"— imagens e templates preparados. Você liga os servidores no "
            f"momento do desastre. {RPO} de minutos, {RTO} de uma a duas horas."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {WARM_STANDBY}: uma versão funcional completa, em "
            f"capacidade mínima, já rodando na região de recuperação. No "
            f"desastre, você só redireciona o tráfego e escala. {RPO} de "
            f"segundos a minutos, {RTO} de minutos."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E {MULTI_SITE_ACTIVE_ACTIVE}: duas ou mais regiões em "
            f"produção plena, simultaneamente. Se uma cai, a outra absorve "
            f"automaticamente. {RPO} e {RTO} praticamente zero — mas é a "
            f"estratégia mais cara das quatro."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Como não confundir {PILOT_LIGHT} com {WARM_STANDBY}: "
            f"no {PILOT_LIGHT}, a aplicação {EMPH('não está rodando')} na "
            f"recuperação — só os dados estão vivos, e ela não atende nenhuma "
            f"requisição até você acender os servidores. No {WARM_STANDBY}, a "
            f"aplicação {EMPH('já está rodando')}, em versão reduzida, e "
            f"poderia atender uma requisição agora mesmo."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Servicos por estrategia ----
    {
        "voice": "antonio",
        "text": (
            f"Agora os serviços que implementam cada estratégia."
            f"{BRK(300)} Backups centralizados e entre regiões, de múltiplos "
            f"serviços: {AWS_BACKUP}, com planos, vault e cópia entre regiões."
            f"{BRK(300)} Replicar servidores continuamente, com {RPO} de "
            f"segundos e {RTO} de minutos: A W S Elastic Disaster Recovery, ou "
            f"{DRS}, que replica bloco a bloco."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Banco relacional com atraso menor que um segundo "
            f"entre regiões: Aurora {GLOBAL_DATABASE}. {SAY('DynamoDB')} "
            f"multi-região ativo-ativo: Global Tables. Replicação de objetos "
            f"{SAY('S3')} entre regiões: {SAY('CRR')}, Cross-Region "
            f"Replication."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Redirecionamento de tráfego no momento do desastre: "
            f"Route cinquenta e três {SAY('failover')}, ou Global Accelerator. "
            f"E reconstrução rápida de infraestrutura: CloudFormation — "
            f"pré-requisito para {PILOT_LIGHT} e {BACKUP_AND_RESTORE}."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Três armadilhas de D R para gravar: {EMPH('Multi A Z protege contra falha de zona, não de região inteira')} "
            f"— se a região inteira ficou indisponível, Multi A Z não resolve. "
            f"Snapshots e imagens precisam ser copiados para {EMPH('outra')} "
            f"região — o que ficou na região que falhou não ajuda em nada. E "
            f"se o enunciado pede menor custo com {RTO} de vinte e quatro "
            f"horas, a resposta é {BACKUP_AND_RESTORE} — não complique "
            f"desnecessariamente com uma estratégia mais cara."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- AWS Backup ----
    {
        "voice": "antonio",
        "text": (
            f"Aprofundando no {AWS_BACKUP}: ele centraliza e automatiza "
            f"backups de {SAY('EC2')}, {SAY('EBS')}, {SAY('RDS')}, Aurora, "
            f"{SAY('DynamoDB')}, {SAY('EFS')}, {SAY('FSx')} e Storage Gateway "
            f"— em vez de configurar backup serviço por serviço."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {BACKUP_PLANS} definem frequência, janela, retenção "
            f"e regras de transição para armazenamento frio. O "
            f"{BACKUP_VAULT_LOCK}, modo {WORM}, impede até o administrador de "
            f"deletar backups antes do prazo — proteção contra {RANSOMWARE} e "
            f"exclusão maliciosa."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {CROSS_REGION_COPY} e {CROSS_ACCOUNT_COPY} copiam "
            f"backups automaticamente para outra região ou conta — essencial "
            f"para D R de região e isolamento contra comprometimento de conta. "
            f"E o {BACKUP_AUDIT_MANAGER} avalia se os planos atendem aos "
            f"requisitos de compliance definidos."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- DRS ----
    {
        "voice": "francisca",
        "text": (
            f"O {DRS}, sucessor do {CLOUDENDURE}, instala um agente leve nos "
            f"servidores de origem — locais, de outra nuvem, ou {SAY('EC2')} — "
            f"que replica continuamente as alterações de disco, bloco a bloco, "
            f"para uma área de staging de baixo custo na {SAY('AWS')}."
            f"{BRK(400)} Durante um desastre, o {DRS} lança instâncias "
            f"{SAY('EC2')} completas a partir dessa réplica em minutos — "
            f"diferente de um backup tradicional, que exigiria restaurar e "
            f"reconfigurar do zero."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Resilience Hub ----
    {
        "voice": "antonio",
        "text": (
            f"O A W S {RESILIENCE_HUB} avalia uma aplicação contra metas de "
            f"{RPO} e {RTO} definidas, simulando cenários de falha — zona "
            f"fora do ar, região fora do ar, falha de componente — e apontando "
            f"lacunas específicas, como: este {SAY('RDS')} não tem Multi A Z, "
            f"o que viola o {RTO} de cinco minutos definido. Ele gera "
            f"recomendações de remediação concretas."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Chaos Engineering ----
    {
        "voice": "francisca",
        "text": (
            f"Uma estratégia de D R documentada, mas nunca testada, é apenas "
            f"uma suposição, não uma garantia."
            f"{BRK(400)} O A W S {FAULT_INJECTION_SERVICE} permite injetar "
            f"falhas controladas em produção — terminar instâncias, simular "
            f"latência de rede, esgotar C P U — para validar que os "
            f"mecanismos de auto-healing e {SAY('failover')} realmente "
            f"funcionam. Essa prática se chama {CHAOS_ENGINEERING}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Os {GAME_DAYS} são exercícios programados onde o "
            f"time simula um desastre real e segue o {RUNBOOK} de D R para "
            f"medir o {RTO} de verdade — em vez de confiar apenas na "
            f"documentação."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório prático de duas horas, "
            f"por cerca de cinquenta centavos, onde você cria um plano no "
            f"{AWS_BACKUP} com cópia entre regiões e cronometra o {RTO} real, "
            f"simula um {PILOT_LIGHT} subindo uma stack na região B, e "
            f"configura {SAY('failover')} do Route cinquenta e três entre "
            f"duas regiões."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: {RPO} de cinco minutos, {RTO} de uma "
            f"hora, orçamento apertado. Qual estratégia?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{PILOT_LIGHT}. Dados replicando continuamente garantem o {RPO} "
            f"de minutos, e a infraestrutura desligada mantém o custo baixo. "
            f"Um {RTO} de uma a duas horas para acender a infraestrutura é "
            f"viável."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: sistema de pagamentos global, zero tempo de "
            f"inatividade tolerado. Qual estratégia?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{MULTI_SITE_ACTIVE_ACTIVE}. Duas ou mais regiões em produção "
            f"plena, com Route cinquenta e três ou Global Accelerator "
            f"distribuindo o tráfego entre elas."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: um ambiente de recuperação que já atende requisições "
            f"de teste, em capacidade reduzida. Qual estratégia?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{WARM_STANDBY}. A aplicação já está rodando na região de "
            f"recuperação — isso a diferencia do {PILOT_LIGHT}, onde ela está "
            f"desligada."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: por que fizemos backup na mesma região não é uma "
            f"estratégia válida quando a região inteira cai?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Se toda a região está indisponível, qualquer recurso "
            f"armazenado nela — incluindo backups e snapshots — também fica "
            f"inacessível. D R de região exige cópia em {EMPH('outra')} "
            f"região."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: como o {DRS} se diferencia do {AWS_BACKUP}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{AWS_BACKUP} tira snapshots periódicos, com {RPO} em horas. O "
            f"{DRS} replica continuamente bloco a bloco para a região de "
            f"recuperação, permitindo {RPO} de segundos e {RTO} de minutos — é "
            f"o sucessor do {CLOUDENDURE} para migração completa de "
            f"servidores."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: a empresa teme que um atacante comprometa a conta e "
            f"delete os backups antes de exigir resgate. Como proteger?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BACKUP_VAULT_LOCK} em modo {COMPLIANCE_MODE} — torna os "
            f"backups imutáveis por um período, impedindo exclusão mesmo por "
            f"um administrador ou root comprometido. Combine com "
            f"{CROSS_ACCOUNT_COPY} para isolar os backups numa conta separada."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como validar que a estratégia de D R realmente "
            f"atinge o {RTO} prometido, sem esperar um desastre real?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {RESILIENCE_HUB} para avaliar a arquitetura contra as "
            f"metas de {RPO} e {RTO}, e A W S {FAULT_INJECTION_SERVICE} para "
            f"injetar falhas controladas e medir o comportamento real do "
            f"{SAY('failover')} num {GAME_DAY}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo sete. No próximo, vamos falar de "
            f"computação serverless: Lambda e containers. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
