"""Roteiro tratado do Capitulo 17 (Redes avancadas e conectividade hibrida) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

TRANSIT_GATEWAY = PHON("ˈtrænzɪt ˈɡeɪtweɪ", "Transit Gateway")
PRIVATELINK = PHON("ˈpraɪvətlɪŋk", "PrivateLink")
PEERING = PHON("ˈpɪrɪŋ", "Peering")
ATTACHMENT = PHON("əˈtætʃmənt", "attachment")
TGW_ROUTE_TABLES = PHON("ti dʒi dʌbəlju ɹut ˈteɪbəlz", "TGW Route Tables")
TGW_ROUTE_TABLE = PHON("ti dʒi dʌbəlju ɹut ˈteɪbəl", "route table do TGW")
MULTICAST = PHON("ˈmʌltikæst", "Multicast")
PRIVATE_VIF = PHON("ˈpraɪvət vɪf", "Private VIF")
PUBLIC_VIF = PHON("ˈpʌblɪk vɪf", "Public VIF")
TRANSIT_VIF = PHON("ˈtrænzɪt vɪf", "Transit VIF")
LAG = PHON("læɡ", "LAG")
LINK_AGGREGATION_GROUP = PHON("lɪŋk ˌæɡrɪˈɡeɪʃən ɡrup", "Link Aggregation Group")
DIRECT_CONNECT_GATEWAY = PHON("dɪˈrɛkt kəˈnɛkt ˈɡeɪtweɪ", "Direct Connect Gateway")
ECMP = PHON("i si ɛm pi", "ECMP")
BGP = PHON("bi dʒi pi", "BGP")
ENDPOINT_SERVICE = PHON("ˈɛndpɔɪnt ˈsɜrvɪs", "Endpoint Service")
VPC_SHARING = PHON("vi pi si ˈʃɛrɪŋ", "VPC Sharing")
RAM = PHON("ɛs eɪ ɛm", "RAM")
NETWORK_FIREWALL = PHON("ˈnɛtwɜrk ˈfaɪrwɔl", "Network Firewall")
FQDN = PHON("ɛf kju di ɛn", "FQDN")
DEEP_PACKET_INSPECTION = PHON("dip ˈpækɪt ɪnˈspɛkʃən", "deep packet inspection")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dezessete: redes avançadas e conectividade "
            f"híbrida. O capítulo quatro introduziu {TRANSIT_GATEWAY}, V P "
            f"N e Direct Connect. Aqui aprofundamos cada um, especialmente "
            f"cenários de múltiplas {SAY('VPCs')}, contas e regiões."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Transit Gateway ----
    {
        "voice": "francisca",
        "text": (
            f"O {TRANSIT_GATEWAY} é um roteador regional central: cada "
            f"{SAY('VPC')}, V P N ou Direct Connect se conecta a ele via "
            f"um {ATTACHMENT}, e as {TGW_ROUTE_TABLES} — não as da "
            f"{SAY('VPC')} — decidem quem enxerga quem."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Cada {ATTACHMENT} é associado a uma "
            f"{TGW_ROUTE_TABLE}, "
            f"permitindo segmentar — por exemplo, {SAY('VPCs')} de produção "
            f"não vendo {SAY('VPCs')} de desenvolvimento, mesmo conectadas "
            f"ao mesmo {TRANSIT_GATEWAY}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {SAY('peering')} entre {TRANSIT_GATEWAY}s de "
            f"regiões diferentes mantém o tráfego no {SAY('backbone')} "
            f"privado da {SAY('AWS')}, criptografado. O {MULTICAST} é "
            f"suportado entre {SAY('subnets')} de {SAY('VPCs')} anexadas — "
            f"caso de uso de nicho, mas que aparece como diferencial. E o "
            f"compartilhamento via A W S {RAM} permite que um "
            f"{TRANSIT_GATEWAY} criado numa conta de rede central seja "
            f"usado por outras contas da organização."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Armadilha importante: {SAY('VPC')} {PEERING} não "
            f"é transitivo, mas {TRANSIT_GATEWAY} é. Se A está conectada "
            f"com B por {PEERING}, e B está conectada com C, A "
            f"{EMPH('não consegue')} alcançar C através de B. Para dezenas "
            f"de {SAY('VPCs')} precisando se comunicar, sem criar uma "
            f"malha gigante de conexões, a resposta é {TRANSIT_GATEWAY}, "
            f"que roteia entre todos os {ATTACHMENT}s."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Direct Connect VIF types ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre os tipos de interface virtual do Direct Connect: o "
            f"{PRIVATE_VIF} acessa recursos dentro de uma {SAY('VPC')}, "
            f"com I Ps privados, como se estivesse na mesma rede. O "
            f"{PUBLIC_VIF} acessa serviços públicos da {SAY('AWS')}, como "
            f"{SAY('S3')}, usando seus {SAY('endpoints')} públicos, mas "
            f"pela conexão dedicada, sem passar pela internet."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {TRANSIT_VIF} conecta a um "
            f"{DIRECT_CONNECT_GATEWAY} associado a um ou mais "
            f"{TRANSIT_GATEWAY}s, para alcançar múltiplas {SAY('VPCs')} ou "
            f"regiões por uma única conexão física. O {LAG}, "
            f"{LINK_AGGREGATION_GROUP}, agrupa múltiplas conexões físicas "
            f"numa só conexão lógica, dando mais throughput e redundância. "
            f"E o {DIRECT_CONNECT_GATEWAY} permite que uma conexão alcance "
            f"{SAY('VPCs')} em múltiplas regiões através de "
            f"{PRIVATE_VIF}s ou {TRANSIT_VIF}s."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- VPN ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre V P N: cada conexão {SAY('Site-to-Site')} vem com dois "
            f"túneis I P Sec para redundância — o ideal é configurar o "
            f"roteador local para usar ambos, via {ECMP} ou {BGP} com "
            f"prioridades."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {BGP} dinâmico permite {SAY('failover')} "
            f"automático de rotas entre os túneis, detectando o caminho "
            f"mais curto. Roteamento estático exige atualização manual. "
            f"Uma V P N acelerada usa a rede global da {SAY('AWS')} para "
            f"reduzir latência até o {SAY('endpoint')} V P N. E o padrão "
            f"comum: Direct Connect como link primário, mais V P N "
            f"{SAY('Site-to-Site')} como {SAY('failover')} automático via "
            f"{BGP}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- PrivateLink ----
    {
        "voice": "antonio",
        "text": (
            f"Interface {SAY('Endpoints')}, do capítulo quatro, permitem "
            f"{EMPH('consumir')} serviços da {SAY('AWS')} de forma "
            f"privada. O {PRIVATELINK} também permite que {EMPH('você')} "
            f"exponha um serviço seu para outras {SAY('VPCs')} ou contas, "
            f"sem {PEERING}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O fluxo: na sua {SAY('VPC')}, um {SAY('NLB')} na "
            f"frente da aplicação, com um {ENDPOINT_SERVICE} associado a "
            f"ele, exigindo aprovação manual ou automática de cada "
            f"assinatura. Na {SAY('VPC')} do cliente, um Interface "
            f"{SAY('Endpoint')} cria uma interface privada que acessa seu "
            f"serviço por I P privado."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Quando usar {PRIVATELINK} em vez de {PEERING}: o "
            f"{PEERING} expõe toda a faixa de endereços da {SAY('VPC')} ao "
            f"par. O {PRIVATELINK} expõe {EMPH('apenas o serviço específico')} "
            f"atrás do {SAY('NLB')}, sem rotas de {SAY('VPC')}, sem risco "
            f"de sobreposição de endereços, e com controle granular de "
            f"quem pode se conectar. Para {SAY('SaaS')} multi-cliente, ou "
            f"compartilhar um serviço com parceiros sem expor a rede "
            f"inteira, a resposta é {PRIVATELINK}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- VPC Sharing ----
    {
        "voice": "antonio",
        "text": (
            f"O A W S Resource Access Manager permite que uma conta "
            f"proprietária compartilhe {SAY('subnets')} de sua {SAY('VPC')} "
            f"com outras contas da organização, no que se chama "
            f"{VPC_SHARING}. As contas participantes lançam recursos — "
            f"{SAY('EC2')}, {SAY('RDS')} — nessas {SAY('subnets')}, mas não "
            f"podem gerenciar a {SAY('VPC')} em si — útil para times de "
            f"aplicação que não devem administrar a rede, mantendo um "
            f"único bloco de endereços centralizado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- 4 camadas de seguranca ----
    {
        "voice": "francisca",
        "text": (
            f"As quatro camadas de segurança de rede: Security Group, "
            f"nível de instância, só permite, {EMPH('stateful')}. Network "
            f"{SAY('ACL')}, nível de {SAY('subnet')}, permite e nega, "
            f"{EMPH('stateless')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} A W S {SAY('WAF')}, camada sete, protege "
            f"{SAY('ALB')}, CloudFront e API Gateway contra S Q L "
            f"injection e X S S. E o A W S {NETWORK_FIREWALL}, nível de "
            f"{SAY('VPC')}, faz inspeção {EMPH('stateful')} de pacotes, "
            f"detecção e prevenção de intrusão, e filtragem por domínio, "
            f"com regras compatíveis com Suricata."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Quando a prova quer {NETWORK_FIREWALL}: "
            f"Security Group e {SAY('NACL')} filtram por I P, porta e "
            f"protocolo. {SAY('WAF')} entende H T T P. Nenhum dos três faz "
            f"{DEEP_PACKET_INSPECTION} ou bloqueia tráfego de saída por "
            f"domínio. Quando o enunciado menciona detecção e prevenção de "
            f"intrusão, inspeção de {SAY('payload')}, ou controle de saída "
            f"por domínio para toda a {SAY('VPC')}, a resposta é A W S "
            f"{NETWORK_FIREWALL}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito traz um laboratório de uma hora, por dez "
            f"centavos de dólar, onde você cria duas {SAY('VPCs')} com "
            f"blocos diferentes, conecta as duas via {TRANSIT_GATEWAY}, e "
            f"testa conectividade entre instâncias usando o Session "
            f"Manager."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (5 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: vinte {SAY('VPCs')} de "
            f"departamentos diferentes precisam se comunicar, com "
            f"possibilidade de isolar algumas — financeiro não vendo "
            f"marketing, por exemplo. Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{TRANSIT_GATEWAY} com múltiplas {TGW_ROUTE_TABLES} — cada "
            f"departamento associado a uma {SAY('route table')} que só "
            f"propaga as rotas permitidas, em vez de uma malha de "
            f"{PEERING}s, não-transitiva e inviável em escala."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: a empresa quer acessar {SAY('VPCs')} em três "
            f"regiões diferentes através de uma única conexão Direct "
            f"Connect. Qual a configuração?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{DIRECT_CONNECT_GATEWAY} associado a {TRANSIT_VIF}s, "
            f"conectados a {TRANSIT_GATEWAY}s em cada região — o {SAY('DX Gateway')} "
            f"estende o alcance da conexão física para múltiplas regiões."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: a conexão Direct Connect principal precisa de "
            f"{SAY('failover')} automático se o circuito físico cair. Qual "
            f"a opção mais simples?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"V P N {SAY('Site-to-Site')} como {SAY('backup')}, com "
            f"{BGP} configurado para assumir automaticamente as rotas "
            f"quando o Direct Connect cair — ambos anunciam as mesmas "
            f"rotas, e o roteador escolhe o caminho de menor custo "
            f"enquanto disponível."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: uma empresa de {SAY('software')} quer oferecer sua A "
            f"P I para clientes em {SAY('VPCs')} deles, sem expor a faixa "
            f"de endereços da própria {SAY('VPC')}. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {PRIVATELINK}, com um {ENDPOINT_SERVICE} na frente de "
            f"um {SAY('NLB')} — expõe apenas o serviço específico via "
            f"interface privada na {SAY('VPC')} do cliente, sem "
            f"{PEERING} e sem expor a rede inteira."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como bloquear que qualquer instância na "
            f"{SAY('VPC')} acesse domínios fora de uma lista aprovada?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {NETWORK_FIREWALL}, com regras de filtragem por "
            f"domínio, posicionado na rota de saída da {SAY('VPC')}. "
            f"Security Group e {SAY('NACL')} não filtram por {FQDN}, e o "
            f"{SAY('WAF')} só atua em tráfego H T T P de entrada."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dezessete. No próximo, vamos falar "
            f"de machine learning e inteligência artificial na "
            f"{SAY('AWS')}. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
