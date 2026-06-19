"""Roteiro tratado do Capitulo 4 (VPC e Redes)."""

from glossary import SAY, EMPH, BRK, PHON, GATEWAY, ENDPOINT

STATEFUL = PHON("ˈsteɪtfəl", "stateful")
STATELESS = PHON("ˈsteɪtləs", "stateless")
SUBNET = PHON("ˈsʌbnɛt", "subnet")
ROUTE_TABLE = PHON("ɹut ˈteɪbəl", "route table")
PEERING = PHON("ˈpɪrɪŋ", "peering")
TRANSIT_GATEWAY = PHON("ˈtrænzɪt ˈɡeɪtweɪ", "Transit Gateway")
PRIVATELINK = PHON("ˈpraɪvətlɪŋk", "PrivateLink")
FLOW_LOGS = PHON("floʊ lɑɡz", "Flow Logs")
ROUTING_POLICY = PHON("ˈrutɪŋ ˈpɑləsi", "routing policy")
FAILOVER = PHON("ˈfeɪloʊvɚ", "failover")
GLOBAL_ACCELERATOR = PHON("ˈɡloʊbəl əkˈsɛləreɪtɚ", "Global Accelerator")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quatro: {SAY('VPC')} e redes. Esse é o domínio com mais "
            f"armadilhas conceituais da prova — vamos destrinchar cada uma."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    {
        "voice": "antonio",
        "text": (
            f"Uma {SAY('VPC')} é uma rede isolada dentro de uma região, definida por um "
            f"bloco de endereços. Dentro dela, as {SUBNET}s ficam em zonas de "
            f"disponibilidade específicas — uma {SUBNET} nunca cruza duas zonas."
            f"{BRK(400)} Uma {SUBNET} pública tem rota para um Internet {GATEWAY}. Uma "
            f"{SUBNET} privada não tem essa rota direta, e depende de um N A T "
            f"{GATEWAY} para sair para a internet."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Agora a comparação mais cobrada de redes: Security Group contra N A C L."
            f"{BRK(400)} O Security Group atua em nível de instância, é {STATEFUL} — "
            f"ou seja, o tráfego de retorno é liberado automaticamente — e só tem "
            f"regras de permitir, nunca de negar."
            f"{BRK(400)} Já o N A C L atua em nível de {SUBNET}, é {STATELESS} — "
            f"precisa liberar ida e volta manualmente — e permite tanto permitir quanto "
            f"negar. É o único jeito nativo de bloquear um I P específico."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Um detalhe que pega muita gente: se um cliente externo faz uma "
            f"requisição na porta oitenta, a resposta sai por uma porta efêmera "
            f"aleatória. Se o N A C L de saída não libera essa faixa de portas, a "
            f"resposta é descartada, mesmo que a entrada tenha sido permitida."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Não confunda Internet {GATEWAY} com N A T {GATEWAY}. O Internet "
            f"{GATEWAY} é bidirecional, dá acesso de entrada e saída para "
            f"{SUBNET}s públicas. O N A T {GATEWAY} é só de saída: a instância "
            f"privada inicia conexões para a internet, mas a internet não consegue "
            f"iniciar conexão com ela."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Para acesso privado a serviços da {SAY('AWS')}, existem dois tipos de "
            f"{ENDPOINT}. O Gateway {ENDPOINT} é gratuito, mas só funciona para "
            f"{SAY('S3')} e {SAY('DynamoDB')}. O Interface {ENDPOINT}, que usa "
            f"{PRIVATELINK}, cobre praticamente todos os outros serviços, mas tem "
            f"custo por hora."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Um sinal prático de custo: se o cenário fala em tráfego para "
            f"{SAY('S3')} saindo de uma {SUBNET} privada, e pede o menor custo, a "
            f"resposta quase sempre é trocar o caminho via N A T {GATEWAY} por um "
            f"Gateway {ENDPOINT} — que não cobra nada."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Sobre conectar VPCs entre si: o {PEERING} cria uma conexão ponto a "
            f"ponto, mas {EMPH('não é transitivo')}. Se A está conectada com B, e B "
            f"está conectada com C, A não consegue alcançar C automaticamente."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Quando o número de VPCs cresce e o {PEERING} viraria uma "
            f"teia gigante, a resposta é o {TRANSIT_GATEWAY}: um roteador central "
            f"onde cada VPC se conecta uma única vez, e ele cuida de rotear entre "
            f"todas."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Sobre conectividade com o ambiente local da empresa: a V P N "
            f"site-to-site sobe em minutos, é criptografada, mas passa pela internet "
            f"pública. O Direct Connect é um link físico dedicado, mais estável e "
            f"rápido, mas leva semanas para ser provisionado, e não é criptografado "
            f"por padrão."
            f"{BRK(400)} Se o cenário precisa de conectividade urgente, a resposta é "
            f"V P N. Se precisa de link dedicado de longo prazo, é Direct Connect — "
            f"os dois podem coexistir, com a V P N como backup."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"No Route cinquenta e três, as {ROUTING_POLICY}s mais importantes são: "
            f"Weighted, para dividir tráfego por peso, como num teste A B; Latency, "
            f"para direcionar à região de menor latência; {FAILOVER}, com um primário "
            f"e um secundário monitorados por health check; e Geolocation, para "
            f"restrições legais por país."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"E para fechar: CloudFront contra {GLOBAL_ACCELERATOR}. CloudFront faz "
            f"cache de conteúdo nas bordas — pense em conteúdo estático e vídeo. O "
            f"{GLOBAL_ACCELERATOR} não faz cache: é um atalho pela rede privada da "
            f"{SAY('AWS')}, suporta T C P e U D P, e oferece I P fixo global — ótimo "
            f"para jogos e voz, onde cache não ajuda."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: como bloquear um I P atacante específico "
            f"vindo da internet?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"N A C L com uma regra de negar para aquele I P. Security Group não tem "
            f"regra de negar explícito."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: quarenta VPCs e um data center local precisam se comunicar. "
            f"Qual a solução escalável?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{TRANSIT_GATEWAY}. Um hub central evita criar dezenas de conexões "
            f"individuais de {PEERING}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: um jogo multiplayer com U D P precisa de latência mínima "
            f"global e I P fixo. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{GLOBAL_ACCELERATOR}. Suporta T C P e U D P, e fornece I Ps anycast "
            f"fixos usando o backbone privado da {SAY('AWS')}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo quatro. No próximo, vamos falar de bancos de "
            f"dados: {SAY('RDS')}, Aurora e {SAY('DynamoDB')}. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
