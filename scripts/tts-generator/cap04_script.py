"""Roteiro tratado do Capitulo 4 (VPC e Redes) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

STATEFUL = PHON("ˈsteɪtfəl", "stateful")
STATELESS = PHON("ˈsteɪtləs", "stateless")
SUBNET = PHON("ˈsʌbnɛt", "subnet")
ROUTE_TABLE = PHON("ɹut ˈteɪbəl", "Route Table")
INTERNET_GATEWAY = PHON("ˈɪntɚnɛt ˈɡeɪtweɪ", "Internet Gateway")
NAT_GATEWAY = PHON("næt ˈɡeɪtweɪ", "NAT Gateway")
NAT_INSTANCE = PHON("næt ˈɪnstəns", "NAT Instance")
EGRESS_ONLY = PHON("ˈiɡrɛs ˈoʊnli", "Egress-Only")
GATEWAY_ENDPOINT = PHON("ˈɡeɪtweɪ ˈɛndpɔɪnt", "Gateway Endpoint")
INTERFACE_ENDPOINT = PHON("ˈɪntɚfeɪs ˈɛndpɔɪnt", "Interface Endpoint")
PRIVATELINK = PHON("ˈpraɪvətlɪŋk", "PrivateLink")
PEERING = PHON("ˈpɪrɪŋ", "Peering")
TRANSIT_GATEWAY = PHON("ˈtrænzɪt ˈɡeɪtweɪ", "Transit Gateway")
SITE_TO_SITE_VPN = PHON("saɪt tu saɪt vi pi ɛn", "Site-to-Site VPN")
DIRECT_CONNECT = PHON("dɪˈrɛkt kəˈnɛkt", "Direct Connect")
ROUTING_POLICY = PHON("ˈrutɪŋ ˈpɑləsi", "routing policy")
WEIGHTED = PHON("ˈweɪtɪd", "Weighted")
LATENCY_POLICY = PHON("ˈleɪtənsi", "Latency")
FAILOVER = PHON("ˈfeɪloʊvɚ", "Failover")
GEOLOCATION = PHON("ˌdʒioʊloʊˈkeɪʃən", "Geolocation")
GEOPROXIMITY = PHON("ˌdʒioʊprɑkˈsɪməti", "Geoproximity")
MULTIVALUE = PHON("ˈmʌltivælju", "Multivalue Answer")
TRAFFIC_FLOW = PHON("ˈtræfɪk floʊ", "Traffic Flow")
GLOBAL_ACCELERATOR = PHON("ˈɡloʊbəl əkˈsɛləreɪtɚ", "Global Accelerator")
FLOW_LOGS = PHON("floʊ lɑɡz", "Flow Logs")
NETWORK_FIREWALL = PHON("ˈnɛtwɜrk ˈfaɪrwɔl", "Network Firewall")
BASTION_HOST = PHON("ˈbæstʃən hoʊst", "Bastion Host")
SESSION_MANAGER = PHON("ˈsɛʃən ˈmænɪdʒɚ", "Session Manager")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quatro: {SAY('VPC')} e redes. Este é o domínio com mais "
            f"armadilhas conceituais da prova. Entender a fundo o caminho que um "
            f"pacote percorre dentro e fora da {SAY('VPC')} resolve a maioria das "
            f"questões."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Anatomia da VPC ----
    {
        "voice": "antonio",
        "text": (
            f"Uma {SAY('VPC')} é uma rede logicamente isolada dentro de uma "
            f"região, definida por um bloco de endereços, por exemplo dez ponto "
            f"zero ponto zero ponto zero barra dezesseis. Dentro dela, as "
            f"{SUBNET}s são criadas em zonas de disponibilidade específicas — uma "
            f"{SUBNET} nunca cruza duas zonas."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Uma {SUBNET} pública tem rota para um {INTERNET_GATEWAY} "
            f"na tabela de rotas. Uma {SUBNET} privada não tem essa rota direta, e "
            f"usa um {NAT_GATEWAY} para saída."
            f"{BRK(400)} A {ROUTE_TABLE} define para onde vai o tráfego de cada "
            f"bloco de destino — cada {SUBNET} está associada a exatamente uma "
            f"{ROUTE_TABLE}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E um detalhe que cai na prova: a {SAY('AWS')} reserva "
            f"cinco endereços I P por {SUBNET} — o primeiro para a rede, o "
            f"segundo para o roteador da {SAY('VPC')}, o terceiro para D N S, o "
            f"quarto reservado para uso futuro, e o último para broadcast. Um "
            f"bloco barra vinte e quatro tem duzentos e cinquenta e seis "
            f"endereços, mas só duzentos e cinquenta e um são utilizáveis."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Security Group x NACL ----
    {
        "voice": "francisca",
        "text": (
            f"Agora a comparação mais cobrada de redes: Security Group contra "
            f"{SAY('NACL')}. Memorize bem essas diferenças."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O Security Group atua em nível de instância. É "
            f"{STATEFUL} — o tráfego de retorno é permitido automaticamente, "
            f"mesmo sem regra de saída explícita. Só tem regras de permitir, nunca "
            f"de negar. E pode referenciar outro Security Group como origem ou "
            f"destino, eliminando a necessidade de saber I Ps fixos."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Já o {SAY('NACL')} atua em nível de {SUBNET}, afetando "
            f"todas as instâncias dentro dela. É {STATELESS} — é preciso liberar "
            f"ida {EMPH('e')} volta explicitamente. Permite tanto permitir quanto "
            f"negar, avaliadas em ordem numérica crescente até a primeira regra "
            f"que casar. É o único mecanismo nativo de {SAY('VPC')} que bloqueia "
            f"um I P específico."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Atenção às regras efêmeras: se um cliente externo faz "
            f"uma requisição H T T P na porta oitenta, a resposta sai por uma "
            f"porta efêmera aleatória, entre mil e vinte e quatro e sessenta e "
            f"cinco mil. O {SAY('NACL')} de saída precisa permitir essa faixa, "
            f"senão a resposta é descartada — mesmo que a entrada tenha sido "
            f"permitida. É o cenário clássico de o Security Group está certo, mas "
            f"o {SAY('NACL')} está bloqueando o retorno."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- IGW / NAT Gateway / Egress-Only ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre os gateways de saída: o {INTERNET_GATEWAY} é bidirecional, "
            f"dando às {SUBNET}s públicas acesso de entrada e saída à internet."
            f"{BRK(300)} O {NAT_GATEWAY} é só de saída: instâncias privadas "
            f"iniciam conexões à internet, mas a internet não inicia conexão com "
            f"elas. É gerenciado pela {SAY('AWS')} e redundante na zona."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} A {NAT_INSTANCE} é a versão legada — uma {SAY('EC2')} "
            f"própria fazendo essa função — não escala automaticamente e exige "
            f"gestão manual, evite em novos designs. E o {EGRESS_ONLY} "
            f"{INTERNET_GATEWAY} é o equivalente do {NAT_GATEWAY}, mas para "
            f"tráfego I P v seis."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Confundir {NAT_GATEWAY} com {INTERNET_GATEWAY} é erro "
            f"clássico. Se o enunciado descreve uma instância privada que precisa "
            f"baixar atualizações da internet, mas não pode ser acessada de fora, "
            f"a resposta é {NAT_GATEWAY}. Se descreve uma instância pública "
            f"acessível externamente, é {INTERNET_GATEWAY}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- VPC Endpoints ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre acesso privado a serviços da {SAY('AWS')}: o "
            f"{GATEWAY_ENDPOINT} é uma entrada na tabela de rotas, totalmente "
            f"{EMPH('grátis')}, mas só funciona para {SAY('S3')} e "
            f"{SAY('DynamoDB')}."
            f"{BRK(400)} Já o {INTERFACE_ENDPOINT}, que usa {PRIVATELINK}, cria "
            f"uma interface de rede com I P privado na {SUBNET}, cobrindo a "
            f"maioria dos outros serviços — mas cobra por hora e por gigabyte "
            f"processado."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Sinal prático de custo: se o tráfego para "
            f"{SAY('S3')} ou {SAY('DynamoDB')} sai de uma {SUBNET} privada e o "
            f"enunciado pede menor custo, troque o caminho via {NAT_GATEWAY} por "
            f"um {GATEWAY_ENDPOINT} gratuito. Para qualquer outro serviço, é "
            f"{INTERFACE_ENDPOINT}, que ainda reduz o custo de {NAT_GATEWAY} "
            f"mesmo cobrando seu próprio preço."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Conectividade (tabela grande) ----
    {
        "voice": "francisca",
        "text": (
            f"Agora a tabela de conectividade entre redes — vamos passar por "
            f"todos os cenários."
            f"{BRK(300)} Duas {SAY('VPC')}s conversando: {PEERING}, que "
            f"{EMPH('não é transitivo')} e exige blocos sem sobreposição."
            f"{BRK(300)} Muitas {SAY('VPC')}s mais conexão local: "
            f"{TRANSIT_GATEWAY}, a resposta quando o {PEERING} viraria uma teia "
            f"impossível de gerenciar."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Instância privada acessando {SAY('S3')} ou "
            f"{SAY('DynamoDB')} sem internet: {GATEWAY_ENDPOINT}, grátis."
            f"{BRK(300)} Instância privada acessando outros serviços da "
            f"{SAY('AWS')}: {INTERFACE_ENDPOINT}, via {PRIVATELINK}."
            f"{BRK(300)} Expor seu próprio serviço para outras contas sem usar "
            f"{PEERING}: {PRIVATELINK} como Endpoint Service — o consumidor não "
            f"vê sua {SAY('VPC')} inteira, só o serviço específico exposto."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Conexão local rápida de criar: {SITE_TO_SITE_VPN}, "
            f"criptografada via I P Sec, sobe em minutos."
            f"{BRK(300)} Link dedicado de alta largura: {DIRECT_CONNECT}, "
            f"privado, mas leva semanas para provisionar e {EMPH('não é criptografado por padrão')} "
            f"— combine com V P N sobre o Direct Connect para criptografia."
            f"{BRK(300)} E se você quer Direct Connect, mas não pode esperar "
            f"semanas: suba a V P N imediatamente como solução temporária, e "
            f"migre para Direct Connect quando ele estiver disponível."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Peering detalhado ----
    {
        "voice": "antonio",
        "text": (
            f"Aprofundando no {PEERING}: ele cria uma conexão ponto a ponto "
            f"entre duas {SAY('VPC')}s, na mesma conta ou em contas diferentes, "
            f"na mesma região ou entre regiões."
            f"{BRK(400)} Três pontos de atenção: não é transitivo — se A precisa "
            f"conversar com C através de B, é preciso um {PEERING} direto entre A "
            f"e C. Os blocos de endereço não podem se sobrepor. E cada lado "
            f"precisa atualizar sua própria tabela de rotas apontando para a "
            f"conexão."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Transit Gateway ----
    {
        "voice": "francisca",
        "text": (
            f"Quando o número de {SAY('VPC')}s cresce, o número de conexões "
            f"{PEERING} necessárias para conectar todas entre si cresce de forma "
            f"quadrática — rapidamente inviável."
            f"{BRK(400)} O {TRANSIT_GATEWAY} resolve isso atuando como um "
            f"roteador regional central: cada {SAY('VPC')}, V P N ou Direct "
            f"Connect se conecta uma única vez a ele, e ele roteia entre todos. "
            f"Suporta até políticas de roteamento e segmentação entre grupos de "
            f"{SAY('VPC')}s."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Route 53 routing policies ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos para o Route cinquenta e três, o D N S gerenciado da "
            f"{SAY('AWS')}. As políticas de roteamento definem como ele responde "
            f"a consultas."
            f"{BRK(300)} Simple é um registro sem lógica nenhuma. {WEIGHTED} "
            f"divide por pesos, por exemplo setenta e trinta — usado em testes A "
            f"B e migração gradual de tráfego."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {LATENCY_POLICY} direciona para a região de menor "
            f"latência medida. {FAILOVER} usa um primário monitorado, com health "
            f"check, e um secundário assumindo se ele falhar — base de qualquer "
            f"site de recuperação de desastre."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {GEOLOCATION} roteia por país ou continente do usuário "
            f"— usado para restrição legal de conteúdo. {GEOPROXIMITY} é parecido, "
            f"mas com um viés ajustável de proximidade geográfica, e exige o "
            f"recurso {TRAFFIC_FLOW}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {MULTIVALUE} retorna até oito registros saudáveis "
            f"aleatoriamente — um balanceamento D N S simples com health check, "
            f"que não substitui um balanceador de carga real, mas ajuda. E "
            f"I P-based roteia conforme o bloco de I P do cliente, por exemplo "
            f"direcionando clientes de um provedor específico para um servidor "
            f"dedicado."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Os health checks do Route cinquenta e três monitoram "
            f"endpoints, ou outros health checks combinados, ou alarmes do "
            f"CloudWatch. Eles são a base do roteamento {FAILOVER} — sem health "
            f"check, o Route cinquenta e três não sabe quando trocar para o "
            f"secundário."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- CloudFront vs Global Accelerator ----
    {
        "voice": "antonio",
        "text": (
            f"CloudFront contra {GLOBAL_ACCELERATOR} — a distinção é cache "
            f"contra não-cache."
            f"{BRK(400)} CloudFront faz cache de conteúdo nos pontos de borda, só "
            f"H T T P e H T T P S — pense em conteúdo estático global, streaming "
            f"de vídeo, redução de carga na origem, e proteção contra D D o S na "
            f"borda. O {SAY('OAC')} protege um {SAY('S3')} privado, servindo "
            f"apenas via CloudFront."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {GLOBAL_ACCELERATOR} não faz cache — é um atalho de "
            f"rede que usa o backbone privado da {SAY('AWS')} em vez da internet "
            f"pública. Suporta T C P {EMPH('e')} U D P. Pense em jogos, voz sobre "
            f"I P, I o T, I P estático global com dois I Ps anycast fixos, e "
            f"failover entre regiões em segundos — muito mais rápido que esperar "
            f"o T T L do D N S expirar."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Quando os dois aparecem juntos na mesma questão: se o "
            f"conteúdo é cacheável, como H T M L, imagem ou vídeo, é CloudFront. "
            f"Se o protocolo não é H T T P, como jogos e voz, ou a aplicação "
            f"precisa de I P fixo com menor latência sem cache, é "
            f"{GLOBAL_ACCELERATOR}. Os dois não competem — atacam problemas "
            f"diferentes."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Flow Logs / Network Firewall ----
    {
        "voice": "antonio",
        "text": (
            f"{FLOW_LOGS} de {SAY('VPC')} capturam metadados de tráfego I P — "
            f"origem, destino, porta, protocolo, aceito ou rejeitado — entrando e "
            f"saindo de interfaces, {SUBNET}s ou {SAY('VPC')}s inteiras, indo "
            f"para CloudWatch Logs ou {SAY('S3')}. Use para auditoria de "
            f"segurança e para descobrir por que um tráfego está sendo bloqueado."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Já o A W S {NETWORK_FIREWALL} é um firewall "
            f"{STATEFUL} gerenciado para a {SAY('VPC')} inteira — inspeciona até "
            f"a camada de aplicação, com regras compatíveis com Suricata. Use "
            f"quando Security Group e {SAY('NACL')} não bastam, como bloquear "
            f"domínios específicos ou inspecionar o conteúdo do pacote."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Bastion vs Session Manager ----
    {
        "voice": "francisca",
        "text": (
            f"Para acessar instâncias em {SUBNET}s privadas sem expô-las à "
            f"internet, existem duas abordagens."
            f"{BRK(400)} O {BASTION_HOST} é uma {SAY('EC2')} pública com S S H ou "
            f"R D P exposto, idealmente restrito por I P — é legado, mas ainda "
            f"aparece em ambientes que não migraram."
            f"{BRK(400)} O {SAY('SSM')} {SESSION_MANAGER} é a resposta preferida "
            f"hoje: {EMPH('nenhuma porta de entrada aberta')}, usando o agente S S "
            f"M mais credenciais {SAY('IAM')} — totalmente auditável via "
            f"CloudTrail."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito ainda traz um laboratório prático de três "
            f"horas, por cerca de um dólar — lembre de deletar o {NAT_GATEWAY} ao "
            f"final — onde você recria a {SAY('VPC')} do zero, adiciona um "
            f"{GATEWAY_ENDPOINT}, conecta via Session Manager, e protege um "
            f"bucket com CloudFront e {SAY('OAC')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: um jogo multiplayer com U D P precisa "
            f"de latência mínima global e I P fixo. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{GLOBAL_ACCELERATOR}. Suporta T C P e U D P, fornece I Ps anycast "
            f"estáticos, e usa o backbone privado da {SAY('AWS')} para menor "
            f"latência."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: como bloquear um I P atacante específico vindo da "
            f"internet?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('NACL')} com regra de negar para esse I P de origem. Security "
            f"Group não suporta regra de negar explícito — só permite, ou "
            f"simplesmente não inclui a regra."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: quarenta {SAY('VPC')}s e um data center local precisam "
            f"se comunicar entre si. Qual a solução escalável?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{TRANSIT_GATEWAY} — hub centralizado que evita criar dezenas de "
            f"conexões individuais de {PEERING}. Cada {SAY('VPC')} e a conexão "
            f"local se conectam uma vez ao {TRANSIT_GATEWAY}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: a aplicação precisa de conectividade privada e "
            f"criptografada com o ambiente local, e precisa estar funcionando "
            f"ainda hoje. Qual a opção?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SITE_TO_SITE_VPN} — sobe em minutos, criptografada via I P Sec. "
            f"{DIRECT_CONNECT} é mais estável e com mais largura de banda, mas "
            f"leva semanas para provisionar, não atendendo urgência."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: usuários no Brasil devem ver conteúdo diferente dos "
            f"usuários nos Estados Unidos, por exigência legal. Qual política de "
            f"roteamento?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Route cinquenta e três com {GEOLOCATION}. Diferente de "
            f"{LATENCY_POLICY}, que escolhe pela menor latência sem considerar "
            f"legalidade, {GEOLOCATION} roteia deterministicamente por país do "
            f"solicitante."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: como dar acesso S S H a uma {SAY('EC2')} privada sem abrir "
            f"nenhuma porta no Security Group?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('SSM')} {SESSION_MANAGER} — usa o agente instalado na "
            f"instância mais credenciais {SAY('IAM')}, sem porta vinte e dois "
            f"aberta nem {BASTION_HOST}. Todo acesso é auditável via CloudTrail."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: por que duas {SAY('VPC')}s com {PEERING} A com B, e B "
            f"com C, não conseguem rotear tráfego direto de A para C?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{PEERING} não é transitivo. Cada conexão é estritamente ponto a "
            f"ponto. Para A se comunicar com C, é preciso um {PEERING} direto "
            f"entre eles, ou migrar para {TRANSIT_GATEWAY}, que roteia entre "
            f"todas as {SAY('VPC')}s conectadas."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo quatro. No próximo, vamos falar de bancos "
            f"de dados: {SAY('RDS')}, Aurora e {SAY('DynamoDB')}. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
