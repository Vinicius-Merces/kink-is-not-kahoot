"""Roteiro tratado do Capitulo 3 (Armazenamento - S3, EFS, FSx, Storage Gateway)."""

from glossary import SAY, BRK, PHON, GATEWAY

LIFECYCLE = PHON("ˈlaɪfsaɪkəl", "lifecycle")
VERSIONING = PHON("ˈvɜrʒənɪŋ", "versioning")
OBJECT_LOCK = PHON("ˈɑbdʒɛkt lɑk", "Object Lock")
COMPLIANCE_MODE = PHON("kəmˈplaɪəns moʊd", "Compliance")
MULTIPART_UPLOAD = PHON("ˈmʌltipɑrt ˈʌploʊd", "Multipart Upload")
TRANSFER_ACCELERATION = PHON("ˈtrænsfɚ ækˌsɛləˈreɪʃən", "Transfer Acceleration")
BUCKET_POLICY = PHON("ˈbʌkɪt ˈpɑləsi", "bucket policy")
BLOCK_PUBLIC_ACCESS = PHON("blɑk ˈpʌblɪk ˈæksɛs", "Block Public Access")
PRESIGNED_URL = PHON("priˈsaɪnd ˌjuˈɑrˈɛl", "presigned URL")
FILE_GATEWAY = PHON("faɪl ˈɡeɪtweɪ", "File Gateway")
VOLUME_GATEWAY = PHON("ˈvɑljum ˈɡeɪtweɪ", "Volume Gateway")
TAPE_GATEWAY = PHON("teɪp ˈɡeɪtweɪ", "Tape Gateway")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo três: armazenamento. Vamos cobrir {SAY('S3')} em profundidade, "
            f"e como ele se compara a {SAY('EFS')} e {SAY('FSx')}."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    {
        "voice": "antonio",
        "text": (
            f"O {SAY('S3')} é um armazenamento de objetos: arquivos imutáveis guardados "
            f"por bucket e chave. Tem durabilidade de onze noves, ou seja, "
            f"noventa e nove vírgula novecentos e noventa e nove por cento — "
            f"projetado para sobreviver à perda de duas zonas de disponibilidade "
            f"simultâneas."
            f"{BRK(400)} E desde dois mil e vinte, todo objeto no {SAY('S3')} tem "
            f"consistência forte de leitura após escrita: não existe mais aquela "
            f"espera de consistência eventual."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Vamos para as classes de armazenamento — e aqui a regra de ouro é: não "
            f"confunda acesso raro com acesso lento."
            f"{BRK(400)} Standard é para acesso frequente. Intelligent-Tiering é quando "
            f"você não sabe o padrão de acesso — ele move o objeto entre camadas "
            f"automaticamente. Standard-IA e One Zone-IA são para acesso raro, mas com "
            f"recuperação imediata."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E aqui vem a parte que costuma confundir: Glacier Instant "
            f"Retrieval também é recuperação em milissegundos, apesar do nome Glacier. "
            f"Já o Glacier Flexible Retrieval leva minutos a horas, e o Glacier Deep "
            f"Archive, o mais barato de todos, leva de doze a quarenta e oito horas — "
            f"ideal para compliance de longo prazo, tipo sete a dez anos."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Para automatizar essa movimentação entre classes, existe a {LIFECYCLE} "
            f"policy: você define regras como, por exemplo, mover para Standard-IA aos "
            f"trinta dias, para Glacier aos noventa dias, e expirar, ou seja, deletar, "
            f"depois de um ano."
            f"{BRK(400)} Atenção: classes de acesso infrequente têm cobrança mínima de "
            f"trinta dias de armazenamento — então arquivos de vida muito curta podem "
            f"sair mais caros do que ficar em Standard."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Sobre segurança do {SAY('S3')}: o {BLOCK_PUBLIC_ACCESS} é uma camada de "
            f"segurança que bloqueia qualquer configuração que tornaria o bucket "
            f"público, mesmo que alguém configure isso por engano depois."
            f"{BRK(400)} E para dar acesso temporário a um objeto privado sem mexer em "
            f"política nenhuma, existe a {PRESIGNED_URL}: uma U R L assinada que expira "
            f"depois de um tempo definido."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Sobre criptografia: o padrão é o S S E dash S três, transparente e sem "
            f"custo extra. Quando a prova menciona auditar quem usou a chave de "
            f"criptografia, a resposta é S S E dash K M S com uma chave gerenciada pelo "
            f"cliente: todo uso da chave fica registrado no CloudTrail."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Com o {VERSIONING} ativado, cada versão de um objeto coexiste no bucket — "
            f"deletar só adiciona um marcador, sem remover de fato. E o {OBJECT_LOCK} "
            f"em modo {COMPLIANCE_MODE} impede que absolutamente ninguém, nem o usuário "
            f"root, delete ou modifique um objeto durante o período definido. É a "
            f"resposta certa para exigências regulatórias rígidas."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Agora a grande decisão entre tipos de armazenamento."
            f"{BRK(400)} {SAY('S3')} é objeto, acesso ilimitado por A P I — pense em "
            f"data lake e backup. {SAY('EBS')} é bloco, conectado a uma única instância "
            f"— pense no disco da sua {SAY('EC2')}. {SAY('EFS')} é arquivo, no protocolo "
            f"N F S, montado simultaneamente em milhares de instâncias Linux ao mesmo "
            f"tempo, com escala automática de capacidade."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Já o {SAY('FSx')} for Windows atende protocolo S M B com "
            f"integração ao Active Directory. E o {SAY('FSx')} for Lustre é para "
            f"computação de alta performance, com integração direta ao {SAY('S3')} como "
            f"camada de dados."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Por fim, o Storage {GATEWAY} — a ponte híbrida. Quando o cenário descreve "
            f"um data center que precisa continuar acessando dados localmente, enquanto "
            f"eles moram na nuvem, é Storage {GATEWAY}, não DataSync."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O {FILE_GATEWAY} expõe N F S ou S M B com cache local, "
            f"sincronizando para o {SAY('S3')}. O {VOLUME_GATEWAY} expõe um disco i S C "
            f"S I com backup automático. E o {TAPE_GATEWAY} simula fitas físicas para "
            f"softwares de backup legados, sem precisar trocar nenhum software."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: logs que precisam ficar guardados por sete "
            f"anos, acesso praticamente nunca, menor custo possível. Qual a "
            f"classe?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Glacier Deep Archive, com uma {LIFECYCLE} policy automática. É a classe "
            f"mais barata do {SAY('S3')}, e a latência de recuperação de até "
            f"quarenta e oito horas é aceitável para auditoria rara."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: cinquenta instâncias {SAY('EC2')} Linux precisam ler e escrever "
            f"os mesmos arquivos ao mesmo tempo. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{SAY('EFS')}. Sistema de arquivos N F S gerenciado, multi zona, montado "
            f"em quantas instâncias forem necessárias. O {SAY('EBS')} não serve, porque "
            f"conecta a apenas uma instância por vez."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: a empresa precisa servir um site estático do {SAY('S3')} sem "
            f"tornar o bucket público. Como fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"CloudFront com {SAY('OAC')}, mantendo o {BLOCK_PUBLIC_ACCESS} ativado no "
            f"bucket. O {SAY('OAC')} permite que só o CloudFront acesse o bucket, "
            f"através de uma política específica — o bucket nunca fica exposto "
            f"diretamente."
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
