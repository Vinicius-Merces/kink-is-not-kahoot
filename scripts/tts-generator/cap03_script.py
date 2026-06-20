"""Roteiro tratado do Capitulo 3 (Armazenamento) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON, GATEWAY

MULTIPART_UPLOAD = PHON("ˈmʌltipɑrt ˈʌploʊd", "Multipart Upload")
LIFECYCLE = PHON("ˈlaɪfsaɪkəl", "Lifecycle")
VERSIONING = PHON("ˈvɜrʒənɪŋ", "Versioning")
DELETE_MARKER = PHON("dɪˈlit ˈmɑrkɚ", "delete marker")
MFA_DELETE = PHON("ɛm ɛf eɪ dɪˈlit", "MFA Delete")
OBJECT_LOCK = PHON("ˈɑbdʒɛkt lɑk", "Object Lock")
GOVERNANCE_MODE = PHON("ˈɡʌvɚnəns moʊd", "Governance")
COMPLIANCE_MODE = PHON("kəmˈplaɪəns moʊd", "Compliance")
BUCKET_POLICY = PHON("ˈbʌkɪt ˈpɑləsi", "Bucket Policy")
BLOCK_PUBLIC_ACCESS = PHON("blɑk ˈpʌblɪk ˈæksɛs", "Block Public Access")
PRESIGNED_URLS = PHON("priˈsaɪnd ˌjuˈɑrˈɛlz", "Presigned URLs")
PRESIGNED_URL = PHON("priˈsaɪnd ˌjuˈɑrˈɛl", "Presigned URL")
BUCKET_OWNER_ENFORCED = PHON("ˈbʌkɪt ˈoʊnɚ ɪnˈfɔrst", "Bucket Owner Enforced")
THROTTLING = PHON("ˈθrɑtlɪŋ", "throttling")
EVENT_NOTIFICATIONS = PHON("ɪˈvɛnt ˌnoʊtəfəˈkeɪʃənz", "Event Notifications")
BATCH_OPERATIONS = PHON("bætʃ ˌɑpəˈreɪʃənz", "Batch Operations")
TRANSFER_ACCELERATION = PHON("ˈtrænsfɚ ækˌsɛləˈreɪʃən", "Transfer Acceleration")
WEBSITE_HOSTING = PHON("ˈwɛbsaɪt ˈhoʊstɪŋ", "Website Hosting")
PERFORMANCE_MODE = PHON("pɚˈfɔrməns moʊd", "Performance Mode")
THROUGHPUT_MODE = PHON("ˈθruːpʊt moʊd", "Throughput Mode")
BURSTING = PHON("ˈbɜrstɪŋ", "Bursting")
ELASTIC = PHON("ɪˈlæstɪk", "Elastic")
FILE_GATEWAY = PHON("faɪl ˈɡeɪtweɪ", "File Gateway")
VOLUME_GATEWAY = PHON("ˈvɑljum ˈɡeɪtweɪ", "Volume Gateway")
TAPE_GATEWAY = PHON("teɪp ˈɡeɪtweɪ", "Tape Gateway")
VIRTUAL_TAPE_LIBRARY = PHON("ˈvɜrtʃuəl teɪp ˈlaɪbrɛri", "Virtual Tape Library")
TRANSFER_FAMILY = PHON("ˈtrænsfɚ ˈfæməli", "Transfer Family")
SNOW_FAMILY = PHON("snoʊ ˈfæməli", "Snow Family")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo três: armazenamento. A maioria das questões de "
            f"armazenamento da prova envolve {SAY('S3')}, então vamos cobri-lo em "
            f"profundidade antes de comparar com {SAY('EFS')} e {SAY('FSx')}."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- S3 fundamentos ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('S3')} é um armazenamento de objetos: arquivos imutáveis "
            f"endereçados por bucket e chave. Um objeto pode ter até cinco "
            f"terabytes; para arquivos maiores que cem megabytes, a prática "
            f"recomendada é o {MULTIPART_UPLOAD}, que é paralelo e retomável, e "
            f"obrigatório acima de cinco gigabytes."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Quatro números para gravar: a durabilidade é de onze "
            f"noves, projetada para sobreviver à perda de duas zonas de "
            f"disponibilidade simultâneas, exceto na classe One Zone. A "
            f"disponibilidade varia por classe — Standard tem acordo de noventa e "
            f"nove vírgula noventa e nove por cento."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A consistência é forte, de leitura após escrita, para "
            f"todos os objetos, desde dois mil e vinte — não existe mais "
            f"consistência eventual no {SAY('S3')}. E o namespace de nomes de "
            f"bucket é global na {SAY('AWS')}, embora o bucket em si resida numa "
            f"região específica."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Classes ----
    {
        "voice": "francisca",
        "text": (
            f"Agora as classes de armazenamento. A regra de ouro: não confunda "
            f"acesso raro com acesso lento."
            f"{BRK(300)} Standard é para acesso frequente, diário ou semanal. "
            f"Intelligent-Tiering é quando o padrão de acesso é desconhecido ou "
            f"imprevisível — ele move o objeto entre camadas automaticamente."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(300)} Standard-IA e One Zone-IA são para acesso infrequente, "
            f"mas com recuperação em milissegundos — a diferença é que One Zone "
            f"fica em apenas uma zona de disponibilidade, e custa vinte por cento "
            f"menos, sendo ideal para dados recriáveis. As duas têm cobrança "
            f"mínima de trinta dias de armazenamento."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E aqui vem a parte que mais confunde: Glacier Instant "
            f"Retrieval também recupera em milissegundos, apesar do nome Glacier — "
            f"para arquivos acessados raramente, tipo uma vez por trimestre. "
            f"Glacier Flexible Retrieval leva de minutos a até doze horas. E "
            f"Glacier Deep Archive, a classe mais barata de todas, leva de doze a "
            f"quarenta e oito horas, e exige mínimo de cento e oitenta dias de "
            f"armazenamento — ideal para compliance de sete a dez anos."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Quatro armadilhas de classe para gravar: padrão "
            f"desconhecido aponta para Intelligent-Tiering, não para I A. Arquivo "
            f"instantâneo pode ser Glacier Instant — nem todo Glacier é lento. "
            f"Classes I A cobram mínimo de trinta dias, então arquivos de vida "
            f"curta saem mais caros que Standard. E Glacier Deep Archive tem mínimo "
            f"de cento e oitenta dias — deletar antes cobra a diferença."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Lifecycle ----
    {
        "voice": "francisca",
        "text": (
            f"Uma {LIFECYCLE} Policy automatiza a movimentação entre classes, ou "
            f"a exclusão de objetos. É a resposta padrão para reduzir custo de "
            f"armazenamento de logs ao longo do tempo."
            f"{BRK(400)} Um exemplo típico: nos primeiros trinta dias, o log fica "
            f"em Standard, para análise frequente. Dos trinta aos noventa dias, "
            f"vai para Standard-IA. Dos noventa aos trezentos e sessenta e cinco "
            f"dias, vai para Glacier Flexible, como arquivo. E depois de um ano, "
            f"expira e é deletado, respeitando o prazo legal."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(500)} Atenção: não é possível transitar de Standard para "
            f"Standard-IA antes de trinta dias de armazenamento, e as transições "
            f"entre classes Glacier também têm restrições. E a {LIFECYCLE} não "
            f"muda retroativamente objetos que já existiam antes da regra ser "
            f"criada, a menos que você use {BATCH_OPERATIONS}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Replicacao ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre replicação: o {SAY('S3')} suporta replicação assíncrona entre "
            f"buckets, mas exige {VERSIONING} ativo nos dois lados."
            f"{BRK(400)} C R R, replicação entre regiões, serve para recuperação "
            f"de desastre em outra região, compliance multi-região, e reduzir "
            f"latência global — mas cobra transferência de dados entre regiões. "
            f"S R R, replicação na mesma região, serve para consolidar logs de "
            f"vários buckets ou testes, sem esse custo de transferência."
            f"{BRK(400)} Em ambos os casos, a replicação só começa para objetos "
            f"novos — objetos antigos exigem {SAY('S3')} Batch Replication."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Versionamento e Object Lock ----
    {
        "voice": "francisca",
        "text": (
            f"Com {VERSIONING} ativo, cada versão de um objeto coexiste no "
            f"bucket. Deletar um objeto insere apenas um {DELETE_MARKER}, em vez "
            f"de remover de fato — para recuperar, basta deletar esse marcador."
            f"{BRK(400)} O {MFA_DELETE} exige autenticação multifator para apagar "
            f"versões ou desativar o {VERSIONING}, protegendo contra exclusão "
            f"acidental ou maliciosa."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E o {OBJECT_LOCK}, modelo W O R M, impede deleção ou "
            f"modificação por um período. No modo {GOVERNANCE_MODE}, usuários com "
            f"permissão especial ainda podem remover. No modo {COMPLIANCE_MODE}, "
            f"{EMPH('ninguém, nem o usuário root')}, pode remover durante o "
            f"período — exigido por reguladores rígidos, como a S E C americana."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Seguranca em camadas ----
    {
        "voice": "antonio",
        "text": (
            f"O {SAY('S3')} tem múltiplas camadas de controle de acesso, e todas "
            f"precisam estar alinhadas para uma requisição funcionar."
            f"{BRK(400)} A {BUCKET_POLICY} é uma política baseada em recurso, "
            f"valendo para qualquer entidade — usuários {SAY('IAM')}, outras "
            f"contas, ou o público. A política {SAY('IAM')} define o que aquele "
            f"usuário ou role pode fazer."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A lista de controle de acesso, ou A C L, é legada — "
            f"evite, e mantenha desabilitada com a opção {BUCKET_OWNER_ENFORCED}. "
            f"O {BLOCK_PUBLIC_ACCESS} é uma camada extra de segurança que bloqueia "
            f"qualquer configuração que tornaria o bucket público, mesmo que uma "
            f"política permita por engano. E {PRESIGNED_URLS} dão acesso "
            f"temporário a um objeto privado sem expor credenciais — a U R L "
            f"expira depois de um tempo definido."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Encryption ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre criptografia em repouso: S S E dash S três é o padrão, "
            f"gerenciado pela {SAY('AWS')}, transparente, sem custo extra, mas não "
            f"auditável por chave."
            f"{BRK(400)} S S E dash K M S usa uma chave do K M S, gerenciada ou "
            f"sua própria — e {EMPH('toda utilização da chave gera um evento no CloudTrail')}, "
            f"respondendo à pergunta de quem acessou o quê."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} S S E dash C usa uma chave do próprio cliente, fora da "
            f"{SAY('AWS')} — raro, só para regulação que proíbe isso. E "
            f"criptografia do lado do cliente significa que o dado já chega "
            f"criptografado na {SAY('AWS')}, para o compliance mais rígido "
            f"possível."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} Um detalhe de performance: cada operação com S S E dash K "
            f"M S chama a A P I do K M S, que tem limite de taxa. Em workloads de "
            f"alto throughput, isso pode gerar {THROTTLING}, ou seja, limitação, "
            f"do K M S. Considere S S E dash S três, que não chama o K M S, ou "
            f"aumente o limite do K M S."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Notifications, Performance, Website Hosting ----
    {
        "voice": "francisca",
        "text": (
            f"{EVENT_NOTIFICATIONS} disparam ações em resposta a eventos de "
            f"objeto — Lambda, S Q S, S N S ou EventBridge. O caso clássico: "
            f"processar uma imagem ao fazer upload, onde uma Lambda redimensiona e "
            f"salva em outro bucket."
            f"{BRK(400)} Já {BATCH_OPERATIONS} executam ações em massa sobre "
            f"objetos existentes: copiar, invocar Lambda, restaurar do Glacier, "
            f"usando uma lista de objetos como entrada."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Sobre performance: o {SAY('S3')} suporta milhares de "
            f"operações por segundo por prefixo — distribuir objetos em prefixos "
            f"diferentes aumenta o throughput proporcionalmente. {TRANSFER_ACCELERATION} "
            f"usa os pontos de borda do CloudFront para acelerar upload de "
            f"clientes distantes do bucket. E {SAY('S3')} Select executa S Q L "
            f"simples no servidor, buscando só a parte necessária de um objeto "
            f"grande, reduzindo dados transferidos."
        ),
    },
    {"voice": "antonio", "text": BRK(800)},
    {
        "voice": "francisca",
        "text": (
            f"E sobre {WEBSITE_HOSTING}: o padrão recomendado é bucket privado, "
            f"com {BLOCK_PUBLIC_ACCESS} ativado, mais CloudFront com {SAY('OAC')}. "
            f"O {SAY('OAC')} permite que só o CloudFront acesse o bucket — sem "
            f"tornar nada público — e ainda adiciona C D N, H T T P S e proteção "
            f"contra D D o S automaticamente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Grande decisao S3/EBS/EFS/FSx ----
    {
        "voice": "antonio",
        "text": (
            f"Agora a grande decisão entre tipos de armazenamento."
            f"{BRK(300)} {SAY('S3')} é objeto, acesso ilimitado por A P I — pense "
            f"em data lake e backup. {SAY('EBS')} é bloco, conectado a uma única "
            f"instância numa única zona — pense no disco da sua {SAY('EC2')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {SAY('EFS')} é arquivo, protocolo N F S, montado em "
            f"milhares de instâncias Linux ao mesmo tempo, com escala automática, "
            f"em múltiplas zonas. {SAY('FSx')} for Windows é arquivo S M B com "
            f"integração ao Active Directory."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {SAY('FSx')} for Lustre é para computação de alta "
            f"performance, com integração direta ao {SAY('S3')} como camada de "
            f"dados. {SAY('FSx')} for NetApp ONTAP atende múltiplos protocolos — N "
            f"F S, S M B e i S C S I no mesmo sistema, bom para migração de NetApp "
            f"local. E {SAY('FSx')} for OpenZFS atende migração de workloads Z F "
            f"S, com latência sub-milissegundo."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- EFS detalhado ----
    {
        "voice": "francisca",
        "text": (
            f"Aprofundando no {SAY('EFS')}: é um N F S gerenciado que escala "
            f"automaticamente, sem pré-provisionar capacidade — cobra por "
            f"gigabyte armazenado."
            f"{BRK(400)} Tem dois {PERFORMANCE_MODE}s: General Purpose, o padrão, "
            f"com menor latência; e Max I O, para acesso paralelo intenso em big "
            f"data."
            f"{BRK(400)} E dois {THROUGHPUT_MODE}s: {BURSTING}, que escala "
            f"conforme o tamanho do sistema de arquivos; e {ELASTIC}, que escala "
            f"independente do tamanho — recomendado atualmente. Tem também classe "
            f"One Zone, mais barata, e suporta {LIFECYCLE} para mover arquivos "
            f"não acessados para uma classe I A."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Storage Gateway ----
    {
        "voice": "antonio",
        "text": (
            f"Por fim, o Storage {GATEWAY}, a ponte híbrida. Quando o cenário "
            f"descreve um data center que precisa continuar acessando dados "
            f"localmente, enquanto eles residem na nuvem, a resposta é Storage "
            f"{GATEWAY} — não DataSync, que é só para migração pontual."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {FILE_GATEWAY} expõe N F S ou S M B, com cache local "
            f"dos arquivos mais usados, sincronizando para o {SAY('S3')} em "
            f"qualquer classe. Há também uma variante {SAY('FSx')} {FILE_GATEWAY} "
            f"para acesso Windows com Active Directory."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {VOLUME_GATEWAY} expõe um disco i S C S I, com backup "
            f"automático para o {SAY('S3')} — em modo cached, com os dados de fato "
            f"no {SAY('S3')} e cache local, ou em modo stored, com os dados "
            f"localmente e backup no {SAY('S3')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} E o {TAPE_GATEWAY} simula uma {VIRTUAL_TAPE_LIBRARY} via "
            f"i S C S I, para softwares de backup legados — o software acredita "
            f"que está gravando em fitas físicas, mas os dados vão para o "
            f"{SAY('S3')} ou Glacier, sem precisar trocar nenhum software."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Para não confundir os três serviços de transferência: o DataSync é "
            f"para transferência agendada ou única, migrando dados de N F S, S M "
            f"B ou até outra nuvem para a {SAY('AWS')} — não é acesso permanente, "
            f"é movimento pontual de dados."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Storage {GATEWAY} é integração híbrida permanente, com "
            f"acesso local contínuo. {TRANSFER_FAMILY} fornece endpoints S F T P, "
            f"F T P ou F T P S gerenciados, para parceiros externos que enviam "
            f"arquivos direto para o {SAY('S3')} ou {SAY('EFS')}. E a "
            f"{SNOW_FAMILY} usa dispositivos físicos — Snowball, Snowcone e "
            f"Snowmobile — para migração offline, quando a conexão de internet é "
            f"lenta demais para o volume de dados."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"O material escrito ainda traz um laboratório prático de duas horas, "
            f"por centavos, onde você ativa {VERSIONING}, configura uma "
            f"{LIFECYCLE} rule completa, gera uma {PRESIGNED_URL}, "
            f"e monta um {SAY('EFS')} compartilhado entre duas instâncias. Vale a "
            f"pena fazer com o computador na mão."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: logs de auditoria que devem ser retidos "
            f"sete anos, acesso praticamente nunca, menor custo possível. Qual a "
            f"classe?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Glacier Deep Archive, com uma {LIFECYCLE} rule automática — a "
            f"classe de menor custo do {SAY('S3')}. A latência de até quarenta e "
            f"oito horas é aceitável para auditoria rara."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: cinquenta instâncias {SAY('EC2')} Linux precisam ler e "
            f"escrever os mesmos arquivos de configuração simultaneamente. Qual "
            f"serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('EFS')} — sistema de arquivos N F S gerenciado, multi-zona, "
            f"montado em quantas instâncias for necessário, com escala automática "
            f"de capacidade. {SAY('EBS')} seria impossível, porque conecta a "
            f"apenas uma instância por vez. E o {SAY('S3')} não tem semântica de "
            f"arquivo, não é POSIX."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: a questão exige auditar quem acessou a chave de "
            f"criptografia de um bucket. Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"S S E dash K M S com uma Customer Managed Key, mais CloudTrail. "
            f"Cada uso da chave gera um evento no CloudTrail com quem fez, quando "
            f"e de qual I P. S S E dash S três não tem essa auditabilidade "
            f"granular."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: um data center local precisa continuar acessando arquivos "
            f"via N F S, mas os dados devem residir no {SAY('S3')}. Qual "
            f"serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Storage {GATEWAY}, especificamente o {SAY('S3')} {FILE_GATEWAY}. "
            f"Apresenta interface N F S ou S M B localmente, com cache, "
            f"sincronizando de fato com o {SAY('S3')}. DataSync não serve, porque "
            f"é migração, não acesso permanente."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: por que One Zone-IA pode ser a resposta certa, mesmo sendo "
            f"menos resiliente que Standard-IA?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Quando o dado é facilmente recriável — um thumbnail derivado de um "
            f"original, ou logs que já existem no sistema primário. A resiliência "
            f"extra de múltiplas zonas é desperdício de custo para algo "
            f"regenerável, e One Zone-IA custa vinte por cento menos."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: um sistema legado usa backup em fita física. Como migrar "
            f"para a nuvem sem trocar o software de backup?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Storage {GATEWAY}, especificamente o {TAPE_GATEWAY}. Ele apresenta "
            f"uma {VIRTUAL_TAPE_LIBRARY} via i S C S I para o software existente, "
            f"que acredita estar gravando em fitas — mas os dados vão para "
            f"{SAY('S3')} ou Glacier. Zero mudança de software."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: como servir um site estático do {SAY('S3')} sem tornar "
            f"o bucket público, com H T T P S e cache global?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"CloudFront com {SAY('OAC')}, mantendo o {BLOCK_PUBLIC_ACCESS} "
            f"ativado no bucket. O {SAY('OAC')} permite que só o CloudFront "
            f"acesse o bucket, via uma política específica — o bucket nunca fica "
            f"exposto diretamente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo três. No próximo, vamos para {SAY('VPC')} e "
            f"redes. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
