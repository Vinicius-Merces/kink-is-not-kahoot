"""Roteiro tratado do Capitulo 11 (Migracao) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

REHOST = PHON("ˈrihoʊst", "Rehost")
LIFT_AND_SHIFT = PHON("lɪft ænd ʃɪft", "lift-and-shift")
REPLATFORM = PHON("riˈplætfɔrm", "Replatform")
REPURCHASE = PHON("riˈpɜrtʃəs", "Repurchase")
REFACTOR = PHON("riˈfæktɚ", "Refactor")
RETIRE = PHON("rɪˈtaɪr", "Retire")
RETAIN = PHON("rɪˈteɪn", "Retain")
RELOCATE = PHON("ˈrɛloʊkeɪt", "Relocate")
ASSESS = PHON("əˈsɛs", "Assess")
MOBILIZE = PHON("ˈmoʊbəlaɪz", "Mobilize")
MIGRATE_MODERNIZE = PHON("ˈmaɪɡreɪt ˈmɑdɚnaɪz", "Migrate and Modernize")
APPLICATION_DISCOVERY_SERVICE = PHON("ˌæplɪˈkeɪʃən dɪˈskʌvəri ˈsɜrvɪs", "Application Discovery Service")
MIGRATION_HUB = PHON("maɪˈɡreɪʃən hʌb", "Migration Hub")
MGN = PHON("ɛm dʒi ɛn", "MGN")
SCT = PHON("ɛs si ti", "SCT")
FULL_LOAD = PHON("fʊl loʊd", "Full Load")
CDC = PHON("si di si", "CDC")
SNOWCONE = PHON("snoʊkoʊn", "Snowcone")
SNOWBALL_EDGE = PHON("ˈsnoʊbɔl ɛdʒ", "Snowball Edge")
SNOWMOBILE = PHON("ˈsnoʊmoʊbil", "Snowmobile")
TRANSFER_FAMILY = PHON("ˈtrænsfɚ ˈfæməli", "Transfer Family")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo onze: migração. Questões desse domínio descrevem um "
            f"cenário local — volume de dados, link de rede, tolerância a "
            f"tempo de inatividade — e pedem o serviço ou estratégia certa. "
            f"O ponto de partida é sempre: o que está sendo movido, e quanto "
            f"tempo ou largura de banda há disponível."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- 7 Rs ----
    {
        "voice": "francisca",
        "text": (
            f"Vamos pelos sete erres, as estratégias de migração."
            f"{BRK(300)} {REHOST}, ou {LIFT_AND_SHIFT}: move a aplicação como "
            f"está, sem mudanças — para migração rápida, prazo curto, usando "
            f"o {MGN} como ferramenta típica."
            f"{BRK(300)} {REPLATFORM}: pequenas otimizações sem mudar a "
            f"arquitetura principal — por exemplo, trocar um banco "
            f"auto-gerenciado por {SAY('RDS')}, sem reescrever a aplicação."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {REPURCHASE}: substitui por um produto {SAY('SaaS')} "
            f"— por exemplo, trocar um C R M local por Salesforce, "
            f"abandonando o código legado."
            f"{BRK(300)} {REFACTOR}, ou re-arquitetar: reconstrói a "
            f"aplicação aproveitando recursos nativos da nuvem — maior "
            f"investimento, mas maior ganho, como transformar um monólito em "
            f"microsserviços."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} {RETIRE}: desliga o que não é mais necessário — "
            f"parte comum de qualquer avaliação de portfólio, já que dez a "
            f"vinte por cento dos sistemas legados tipicamente não precisam "
            f"migrar."
            f"{BRK(300)} {RETAIN}: mantém localmente por ora, por "
            f"dependências complexas ou compliance."
            f"{BRK(300)} E {RELOCATE}: move máquinas virtuais inteiras para "
            f"a {SAY('AWS')} sem modificação — por exemplo, VMware Cloud on "
            f"{SAY('AWS')} — quando a infraestrutura de virtualização em si "
            f"precisa ser preservada."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Fases ----
    {
        "voice": "antonio",
        "text": (
            f"O framework da {SAY('AWS')} organiza uma migração em larga "
            f"escala em três fases."
            f"{BRK(300)} {ASSESS}: avaliar o portfólio, calcular o custo "
            f"total de propriedade, usando o A W S {APPLICATION_DISCOVERY_SERVICE} "
            f"para descobrir dependências e padrões de uso automaticamente."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} {MOBILIZE}: construir a {SAY('landing zone')}, "
            f"treinar equipes, e definir o plano de migração por onda. "
            f"{BRK(300)} E {MIGRATE_MODERNIZE}: executar e otimizar de fato."
            f"{BRK(400)} O A W S {MIGRATION_HUB} centraliza o acompanhamento "
            f"do progresso de todas as migrações — D M S, {MGN}, S M S — num "
            f"único painel."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Servicos por cenario ----
    {
        "voice": "francisca",
        "text": (
            f"Agora os serviços por cenário."
            f"{BRK(300)} Migrar banco de dados com replicação contínua: D M "
            f"S, mais {SCT} se a engine mudar — quase sem tempo de "
            f"inatividade, o banco continua no ar."
            f"{BRK(300)} Migrar servidores ou máquinas virtuais para "
            f"{SAY('EC2')}: {MGN}, o Application Migration Service — "
            f"{LIFT_AND_SHIFT} com replicação contínua."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Mover arquivos N F S ou S M B locais para "
            f"{SAY('S3')} ou {SAY('EFS')}: DataSync — transferência agendada "
            f"ou contínua, com verificação de integridade."
            f"{BRK(300)} Volume de dados enorme, link lento: {SAY('Snow Family')} "
            f"— regra prática: se pela rede levaria mais de uma semana, use "
            f"dispositivo físico."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Parceiros enviando arquivos via S F T P: "
            f"{TRANSFER_FAMILY} — S F T P ou F T P S gerenciado sobre "
            f"{SAY('S3')}. E acesso híbrido permanente, onde o ambiente "
            f"local continua acessando a nuvem: Storage {SAY('Gateway')}, com "
            f"suas variantes de arquivo, volume e fita."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- DMS modos ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre os modos do D M S: {FULL_LOAD} copia o snapshot atual "
            f"das tabelas — usado isoladamente só se o banco pode ficar "
            f"parado durante a cópia."
            f"{BRK(300)} {FULL_LOAD} mais {CDC}, Change Data Capture, copia "
            f"o snapshot e depois replica continuamente as mudanças — quase "
            f"sem tempo de inatividade no momento do corte."
            f"{BRK(300)} E {CDC} apenas, quando o snapshot inicial já foi "
            f"feito por outro meio, e só falta sincronizar as mudanças "
            f"recentes."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Sinal prático: se a engine de origem e destino são "
            f"diferentes — por exemplo, Oracle para Aurora PostgreSQL — o D "
            f"M S por si só {EMPH('não converte o esquema')}. É necessário o "
            f"{SCT}, Schema Conversion Tool, antes, para converter "
            f"procedimentos, tipos e funções específicas da engine de "
            f"origem."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Snow Family ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre a {SAY('Snow Family')}, qual escolher: o {SNOWCONE} tem "
            f"cerca de oito terabytes, para computação de borda leve, em "
            f"espaços reduzidos, podendo ser enviado pelo correio."
            f"{BRK(300)} O {SNOWBALL_EDGE} tem cerca de oitenta terabytes, "
            f"para migração de grandes volumes com processamento na borda. E "
            f"o {SNOWMOBILE}, uma carreta, migra exabytes — um data center "
            f"inteiro, cenário raro, mas que aparece como maior volume "
            f"possível."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Armadilha entre DataSync, Storage {SAY('Gateway')} "
            f"e {SAY('Snow Family')}: DataSync é transferência de dados via "
            f"rede, pontual ou agendada, de A para B. Storage {SAY('Gateway')} "
            f"é integração híbrida permanente, continuando a acessar "
            f"localmente. E {SAY('Snow Family')} é quando a rede é o fator "
            f"limitante — transporte físico é mais rápido que a rede."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito traz um laboratório conceitual de uma "
            f"hora, com Free Tier, onde você configura uma task D M S em "
            f"modo {FULL_LOAD} mais {CDC}, cria uma tarefa de DataSync entre "
            f"dois buckets, e calcula mentalmente quanto tempo quinhentos "
            f"terabytes levariam por um link de cem megabits por segundo, "
            f"comparando com o prazo do {SNOWBALL_EDGE}."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (6 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: quinhentos terabytes de dados, "
            f"link de cem megabits por segundo, prazo de três semanas. Qual "
            f"a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SNOWBALL_EDGE}. Pela rede levaria mais de um ano — o "
            f"dispositivo físico é a única opção viável dentro do prazo."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: migrar Oracle local para Aurora PostgreSQL com "
            f"mínimo tempo de inatividade. Como?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SCT} para converter o esquema, mais D M S com replicação "
            f"contínua, {CDC}. O D M S mantém os bancos sincronizados até o "
            f"momento do corte."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: a empresa quer migrar duzentos servidores VMware "
            f"locais para {SAY('EC2')}, com o mínimo de reconfiguração. Qual "
            f"serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{MGN}, o Application Migration Service — instala um agente "
            f"leve, replica continuamente os servidores, e permite o corte "
            f"com pouco tempo de inatividade, sem reescrever a aplicação."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: parceiros externos precisam enviar arquivos via S F T "
            f"P direto para um bucket {SAY('S3')}. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {TRANSFER_FAMILY} — fornece {SAY('endpoints')} S F T P, "
            f"F T P S ou F T P gerenciados, armazenando os arquivos "
            f"recebidos direto no {SAY('S3')} ou {SAY('EFS')}, sem precisar "
            f"manter um servidor F T P."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: antes de migrar, a empresa precisa entender as "
            f"dependências entre trezentos servidores locais, sem instalar "
            f"nada manualmente em cada um. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"A W S {APPLICATION_DISCOVERY_SERVICE} — coleta dados de "
            f"configuração, uso e dependências de rede automaticamente, via "
            f"agente leve ou modo sem agente, alimentando o planejamento de "
            f"ondas de migração."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: uma aplicação legada será substituída por um "
            f"produto {SAY('SaaS')} de mercado, em vez de migrada. Qual dos "
            f"sete erres é esse?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{REPURCHASE} — abandona o código legado e adota um produto "
            f"{SAY('SaaS')} equivalente, eliminando a necessidade de migrar "
            f"ou manter a aplicação original."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo onze. No próximo, vamos falar de "
            f"analytics: Athena, Glue, Kinesis e Redshift. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
