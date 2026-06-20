"""Roteiro tratado do Capitulo 16 (Route 53 e CloudFront em profundidade) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

ALIAS = PHON("ˈeɪliəs", "Alias")
CNAME = PHON("si neɪm", "CNAME")
APEX = PHON("ˈeɪpɛks", "apex")
PRIVATE_HOSTED_ZONE = PHON("ˈpraɪvət ˈhoʊstɪd zoʊn", "Private Hosted Zone")
CALCULATED_HEALTH_CHECK = PHON("ˈkælkjəleɪtɪd hɛlθ tʃɛk", "Calculated Health Check")
FAILOVER = PHON("ˈfeɪloʊvɚ", "failover")
ROUTING_POLICY = PHON("ˈrutɪŋ ˈpɑləsi", "routing policy")
CACHE_BEHAVIOR = PHON("kæʃ bɪˈheɪvjɚ", "Cache behavior")
INVALIDATION = PHON("ɪnˌvælɪˈdeɪʃən", "invalidação")
OAC = PHON("oʊ eɪ si", "OAC")
OAI = PHON("oʊ eɪ aɪ", "OAI")
ORIGIN_ACCESS_CONTROL = PHON("ˈɔrədʒɪn ˈæksɛs kənˈtroʊl", "Origin Access Control")
ORIGIN_ACCESS_IDENTITY = PHON("ˈɔrədʒɪn ˈæksɛs aɪˈdɛntɪti", "Origin Access Identity")
SIGV4 = PHON("sɪɡ vi fɔr", "SigV4")
SIGNED_URL = PHON("saɪnd ˌjuˈɑrˈɛl", "Signed URL")
SIGNED_COOKIES = PHON("saɪnd ˈkʊkiz", "Signed Cookies")
GEO_RESTRICTION = PHON("ˈdʒioʊ rɪˈstrɪkʃən", "Geo Restriction")
CLOUDFRONT_FUNCTIONS = PHON("klaʊdfrʌnt ˈfʌŋkʃənz", "CloudFront Functions")
LAMBDA_EDGE = PHON("ˈlæmdə ɛdʒ", "Lambda@Edge")
VIEWER_REQUEST = PHON("ˈvjuɚ rɪˈkwɛst", "viewer request")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo dezesseis: Route cinquenta e três e CloudFront em "
            f"profundidade. O capítulo quatro já cobriu as políticas de "
            f"roteamento e a comparação com {SAY('Global Accelerator')}. "
            f"Aqui vamos além: tipos de registro, health checks compostos, "
            f"e os detalhes de cache e segurança do CloudFront."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Alias vs CNAME ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre tipos de registro: o {ALIAS} é uma extensão da "
            f"{SAY('AWS')} que aponta para recursos {SAY('AWS')} — "
            f"{SAY('ALB')}, CloudFront, site no {SAY('S3')} — de graça, sem "
            f"cobrança de consulta, e funciona no {APEX} da zona, como "
            f"{SAY('exemplo.com')} sem subdomínio."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Já o {CNAME} é o padrão D N S, apontando para "
            f"outro nome — mas {EMPH('não pode ser usado no apex')} da "
            f"zona, porque não pode coexistir com os registros N S e S O A "
            f"da raiz. E a {PRIVATE_HOSTED_ZONE} é uma zona D N S resolvida "
            f"apenas dentro de {SAY('VPCs')} associadas, para nomes "
            f"internos, sem expor nada à internet."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Sinal prático: apontar o domínio raiz, sem "
            f"{SAY('www')}, para um balanceador ou CloudFront só é possível "
            f"com um registro {ALIAS} — {CNAME} não é permitido no "
            f"{APEX}. Se o enunciado menciona domínio raiz mais recurso da "
            f"{SAY('AWS')}, a resposta quase certamente envolve {ALIAS}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Health checks ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre health checks do Route cinquenta e três: o tipo "
            f"básico verifica um I P ou domínio diretamente, via H T T P, H "
            f"T T P S ou T C P, com verificadores globais distribuídos "
            f"avaliando a porcentagem de respostas saudáveis."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {CALCULATED_HEALTH_CHECK} combina o status de "
            f"até duzentos e cinquenta e seis outros health checks, com "
            f"lógica E, OU ou NÃO — por exemplo, saudável se pelo menos "
            f"duas de três regiões estiverem de pé. E o tipo CloudWatch "
            f"Alarm reflete o estado de um alarme — útil para monitorar "
            f"recursos que o Route cinquenta e três não alcança "
            f"diretamente, como o {SAY('RDS')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Grave este mantra: {SAY('failover')} automático é "
            f"health check {EMPH('mais')} {ROUTING_POLICY} {SAY('failover')}. "
            f"Health checks por si só não redirecionam tráfego — eles só "
            f"marcam um registro como saudável ou não. É a política de "
            f"roteamento {SAY('failover')} que usa esse status para decidir "
            f"entre o primário e o secundário."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- CloudFront cache ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre cache e invalidação no CloudFront: o {CACHE_BEHAVIOR} "
            f"define regras por padrão de caminho — barra imagens, barra A "
            f"P I — controlando origem, T T L, e quais cabeçalhos, "
            f"{SAY('cookies')} e parâmetros são encaminhados."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O T T L, mínimo, padrão e máximo, define quanto "
            f"tempo o objeto fica na borda antes de revalidar com a "
            f"origem — pode ser sobrescrito pelos cabeçalhos "
            f"{SAY('Cache-Control')} da origem. A {INVALIDATION} força a "
            f"remoção de objetos do cache antes do T T L expirar — os "
            f"primeiros mil caminhos por mês são grátis, depois é cobrado. "
            f"E uma alternativa mais barata é o versionamento do nome do "
            f"arquivo, que propaga instantaneamente sem custo de "
            f"{INVALIDATION}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- OAC vs OAI ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre acesso privado ao {SAY('S3')}: o {OAC}, "
            f"{ORIGIN_ACCESS_CONTROL}, é a opção atual — suporta S S E dash "
            f"K M S no bucket, todos os métodos H T T P, incluindo "
            f"{SAY('uploads')} via CloudFront, e assinatura {SIGV4} "
            f"completa. É a opção recomendada pela {SAY('AWS')} para "
            f"qualquer distribuição nova."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Já o {OAI}, {ORIGIN_ACCESS_IDENTITY}, é legado — "
            f"ainda funciona, mas {EMPH('não suporta S S E dash K M S')} "
            f"nem todos os métodos. Se a questão menciona bucket "
            f"criptografado com K M S, {OAI} não atende — precisa do {OAC}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Signed URL vs Cookies ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre conteúdo restrito: para acesso a um único arquivo, "
            f"como o link de download de um P D F, use {SIGNED_URL} — uma "
            f"sequência de busca com assinatura e expiração, válida para "
            f"aquele objeto."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Para acesso a múltiplos arquivos, como todos os "
            f"vídeos de um curso após o login, use {SIGNED_COOKIES} — o "
            f"navegador envia o {SAY('cookie')} em toda requisição "
            f"seguinte, sem precisar assinar cada U R L. E para restringir "
            f"por país, use a {GEO_RESTRICTION} da distribuição — não "
            f"precisa de U R L ou {SAY('cookie')} assinado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Lambda@Edge vs CloudFront Functions ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre personalização na borda: {CLOUDFRONT_FUNCTIONS} são "
            f"JavaScript leve, executando em microssegundos, milhões de "
            f"requisições por segundo, rodando apenas em {VIEWER_REQUEST} "
            f"ou resposta. Ideal para manipulações simples — reescrever U R "
            f"Ls, normalizar cabeçalhos."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Já o {LAMBDA_EDGE} são funções Lambda completas, "
            f"com mais recursos e tempo de execução, podendo rodar nas "
            f"quatro fases da requisição e acessar rede externa. Use "
            f"quando precisar de lógica mais pesada — por exemplo, chamar "
            f"uma A P I externa antes de servir o conteúdo."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório de uma hora, custo "
            f"mínimo, onde você protege um bucket privado com CloudFront "
            f"mais {OAC}, confirma que o acesso direto ao {SAY('S3')} "
            f"falha, e gera uma {SIGNED_URL} com expiração de cinco "
            f"minutos."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (5 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: por que não é possível usar um "
            f"registro {CNAME} para apontar o domínio raiz, sem "
            f"subdomínio, para um {SAY('ALB')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{CNAME} não pode coexistir com os registros N S e S O A "
            f"obrigatórios no {APEX} da zona. A solução é um registro "
            f"{ALIAS}, extensão da {SAY('AWS')} sem essa restrição, e sem "
            f"custo de consulta."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: como configurar o Route cinquenta e três para "
            f"considerar uma região fora do ar somente se duas de três "
            f"health checks regionais falharem?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Um {CALCULATED_HEALTH_CHECK}, combinando os três health "
            f"checks individuais com um limiar — saudável se pelo menos "
            f"dois estiverem bem."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: um bucket {SAY('S3')} com criptografia S S E dash "
            f"K M S precisa ser origem de uma distribuição CloudFront "
            f"privada. O {OAI} funciona?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Não. {OAI} não suporta buckets com S S E dash K M S. É "
            f"necessário usar {OAC}, que suporta {SIGV4} completo, "
            f"incluindo K M S."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: uma plataforma de cursos online precisa liberar "
            f"acesso a centenas de vídeos para um aluno logado, sem "
            f"assinar cada U R L individualmente. Qual mecanismo?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SIGNED_COOKIES} — um conjunto de {SAY('cookies')} assinados "
            f"é emitido após o login, e enviado automaticamente pelo "
            f"navegador em todas as requisições seguintes, sem gerar uma U "
            f"R L assinada por arquivo."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: você precisa rejeitar requisições sem um "
            f"cabeçalho customizado, com latência mínima e altíssimo "
            f"volume, direto na borda. {LAMBDA_EDGE} ou "
            f"{CLOUDFRONT_FUNCTIONS}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{CLOUDFRONT_FUNCTIONS} — para validações leves de "
            f"cabeçalhos e U R Ls, com latência de microssegundos e custo "
            f"menor. {LAMBDA_EDGE} seria excesso de engenharia para essa "
            f"lógica simples."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo dezesseis. No próximo, vamos "
            f"aprofundar em redes avançadas e conectividade híbrida. Até a "
            f"próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
