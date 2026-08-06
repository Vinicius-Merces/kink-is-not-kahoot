"""Roteiro tratado do Capitulo 5 (Bancos de dados) - cobertura completa."""

from glossary import SAY, EMPH, BRK, PHON

PARAMETER_GROUPS = PHON("pəˈræmɪtɚ ɡrups", "Parameter Groups")
OPTION_GROUPS = PHON("ˈɑpʃən ɡrups", "Option Groups")
MAINTENANCE_WINDOW = PHON("ˈmeɪntənəns ˈwɪndoʊ", "Maintenance Window")
READ_REPLICA = PHON("rid rɪˈplɪkə", "Read Replica")
MULTI_AZ = PHON("ˈmʌlti eɪ zɛd", "Multi-AZ")
FAILOVER = PHON("ˈfeɪloʊvɚ", "failover")
READER_ENDPOINT = PHON("ˈridɚ ˈɛndpɔɪnt", "reader endpoint")
GLOBAL_DATABASE = PHON("ˈɡloʊbəl ˈdeɪtəbeɪs", "Global Database")
BACKTRACK = PHON("ˈbæktræk", "Backtrack")
PARALLEL_QUERY = PHON("ˈpærəlɛl ˈkwɪri", "Parallel Query")
RDS_PROXY = PHON("ɑr di ɛs ˈprɑksi", "RDS Proxy")
PARTITION_KEY = PHON("pɑrˈtɪʃən ki", "Partition Key")
SORT_KEY = PHON("sɔrt ki", "Sort Key")
ON_DEMAND = PHON("ɑn dɪˈmænd", "on-demand")
PROVISIONED = PHON("prəˈvɪʒənd", "Provisioned")
GLOBAL_TABLES = PHON("ˈɡloʊbəl ˈteɪbəlz", "Global Tables")
LAST_WRITER_WINS = PHON("læst ˈraɪtɚ wɪnz", "last-writer-wins")
TRANSACTIONS = PHON("trænˈzækʃənz", "Transactions")
HOT_PARTITION = PHON("hɑt pɑrˈtɪʃən", "hot partition")
SORTED_SETS = PHON("ˈsɔrtɪd sɛts", "sorted sets")
CLUSTER_MODE = PHON("ˈklʌstɚ moʊd", "Cluster Mode")
LAZY_LOADING = PHON("ˈleɪzi ˈloʊdɪŋ", "Lazy Loading")
WRITE_THROUGH = PHON("raɪt θru", "Write-Through")
SPECTRUM = PHON("ˈspɛktrəm", "Spectrum")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo cinco: bancos de dados. É o domínio mais denso da prova, "
            f"com a maior taxa de questões de cenário. Não existe o melhor banco "
            f"— existe o banco certo para o padrão de acesso, consistência e "
            f"escala descritos no enunciado."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Qual banco (12 linhas) ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos passar rapidamente pelo cardápio completo de bancos da "
            f"{SAY('AWS')}."
            f"{BRK(300)} S Q L relacional tradicional, tipo E R P ou e-commerce: "
            f"{SAY('RDS')}, com MySQL, PostgreSQL, MariaDB, Oracle ou S Q L "
            f"Server. S Q L com performance e disponibilidade superiores: "
            f"Aurora, compatível com MySQL ou PostgreSQL. Carga intermitente que "
            f"precisa escalar a zero: Aurora Serverless versão dois."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} N o S Q L chave-valor com latência baixa em qualquer "
            f"escala: {SAY('DynamoDB')}. Cache sub-milissegundo na frente de "
            f"outro banco: ElastiCache, Redis ou Memcached. {SAY('DynamoDB')} com "
            f"cache de microssegundos sem mudar código: {SAY('DAX')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Data warehouse, consultas analíticas pesadas e "
            f"colunares: Redshift. Grafos, para recomendação ou detecção de "
            f"fraude por relacionamento: Neptune. Séries temporais de I o T e "
            f"métricas: Timestream."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Documentos J S O N compatíveis com MongoDB: DocumentDB. "
            f"Ledger imutável com histórico verificável: Q L D B. E cache de "
            f"banco totalmente gerenciado e durável, com Multi A Z nativo: "
            f"MemoryDB for Redis."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- RDS fundamentos ----
    {
        "voice": "francisca",
        "text": (
            f"Sobre fundamentos operacionais do {SAY('RDS')}: backups "
            f"automatizados combinam snapshot diário e logs de transação, com "
            f"retenção de zero a trinta e cinco dias, suportando restauração para "
            f"qualquer ponto no tempo dentro da janela."
            f"{BRK(400)} Snapshots manuais são retidos indefinidamente até serem "
            f"deletados manualmente — independentes da retenção automática."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} {PARAMETER_GROUPS} configuram parâmetros do motor, como "
            f"o número máximo de conexões — algumas mudanças exigem reinício. "
            f"{OPTION_GROUPS} habilitam recursos específicos do motor, como "
            f"criptografia transparente do Oracle."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Criptografia em repouso precisa ser definida na "
            f"criação do banco — {EMPH('não pode ser ativada depois')} num banco "
            f"já existente, sem fazer snapshot e restaurar com criptografia "
            f"habilitada. E a {MAINTENANCE_WINDOW} é quando patches obrigatórios "
            f"acontecem — em {MULTI_AZ}, o patch ocorre primeiro no standby, "
            f"depois faz {FAILOVER}."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Multi-AZ vs Read Replica ----
    {
        "voice": "antonio",
        "text": (
            f"Agora a pegadinha número um da prova: {MULTI_AZ} contra "
            f"{READ_REPLICA}. Grave assim: {EMPH('Multi A Z é disponibilidade')}. "
            f"{EMPH('Read Replica é performance de leitura')}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {MULTI_AZ} replica de forma síncrona, para um standby "
            f"invisível, sem acesso direto — ele não atende tráfego nenhum. Se o "
            f"primário cai, o {FAILOVER} é automático, leva de um a dois minutos, "
            f"e o {SAY('endpoint')} D N S permanece o mesmo."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {READ_REPLICA} replica de forma assíncrona, podendo "
            f"atrasar, e atende tráfego de leitura de verdade — apps leem dela "
            f"diretamente. Se o primário cair, ela {EMPH('não assume sozinha')} "
            f"— é preciso promovê-la manualmente a banco independente. E só a "
            f"{READ_REPLICA} pode ser entre regiões diferentes, servindo de base "
            f"para recuperação de desastre."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Resumindo: {MULTI_AZ} resolve o banco caiu. "
            f"{READ_REPLICA} resolve relatórios pesados demais. E sim, você pode "
            f"ter as duas juntas — uma {READ_REPLICA} pode ter seu próprio "
            f"{MULTI_AZ}, e o primário pode ter {MULTI_AZ} mais várias "
            f"{READ_REPLICA}s simultaneamente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Aurora ----
    {
        "voice": "antonio",
        "text": (
            f"A Aurora tem diferenciais que a prova adora. O armazenamento é "
            f"distribuído automaticamente em seis cópias, por três zonas de "
            f"disponibilidade, com auto-cura de blocos corrompidos, crescendo "
            f"até cento e vinte e oito terabytes sem intervenção."
            f"{BRK(400)} Suporta até quinze {READ_REPLICA}s, com um "
            f"{READER_ENDPOINT} que já balanceia entre elas automaticamente — uma "
            f"única string de conexão, sem gerenciar qual réplica usar. E o "
            f"{FAILOVER} leva cerca de trinta segundos, muito mais rápido que o "
            f"{SAY('RDS')} tradicional."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O Aurora {GLOBAL_DATABASE} replica entre regiões com "
            f"atraso menor que um segundo, e promove a região secundária em "
            f"menos de um minuto — resposta padrão para banco relacional com "
            f"recuperação de desastre agressiva e multi-região."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O {BACKTRACK}, disponível no MySQL, rebobina o banco "
            f"para um ponto no tempo sem precisar restaurar de um snapshot — "
            f"recuperação rápida de um erro humano, como um DROP TABLE "
            f"acidental. E o Aurora {PARALLEL_QUERY} empurra processamento "
            f"analítico para a camada de armazenamento, acelerando consultas "
            f"pesadas sem precisar de um data warehouse separado."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- RDS Proxy ----
    {
        "voice": "francisca",
        "text": (
            f"Quando funções Lambda, ou aplicações com muitas conexões "
            f"efêmeras, acessam o {SAY('RDS')} ou Aurora diretamente, cada "
            f"invocação pode abrir uma conexão nova — esgotando rápido o limite "
            f"do banco."
            f"{BRK(400)} O {RDS_PROXY} fica entre a aplicação e o banco, fazendo "
            f"pool e multiplexação de conexões, reduzindo drasticamente o número "
            f"de conexões reais — e também acelera o {FAILOVER}, mantendo as "
            f"conexões do proxy enquanto o banco reconecta."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- DynamoDB ----
    {
        "voice": "antonio",
        "text": (
            f"Vamos para o {SAY('DynamoDB')}: N o S Q L de chave-valor "
            f"totalmente gerenciado, com latência de milissegundos consistente "
            f"em qualquer escala. Cada item tem uma {PARTITION_KEY}, e "
            f"opcionalmente uma {SORT_KEY}, formando juntas a chave primária."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} No modo {ON_DEMAND}, você paga por requisição — mais "
            f"caro por unidade, mas sem precisar prever capacidade, ideal para "
            f"carga imprevisível. No modo {PROVISIONED}, você define a "
            f"capacidade, mais barato por unidade — combine com Auto Scaling "
            f"para absorver picos."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} O índice secundário global, ou {SAY('GSI')}, permite "
            f"consultar por uma chave diferente da original, e pode ser criado a "
            f"qualquer momento. Já o índice secundário local, {SAY('LSI')}, usa "
            f"a mesma {PARTITION_KEY} com uma {SORT_KEY} alternativa, mas "
            f"{EMPH('precisa ser criado já na criação da tabela')} — não pode ser "
            f"adicionado depois."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O {SAY('DAX')} é um cache in-memory de microssegundos "
            f"na frente do {SAY('DynamoDB')}, compatível com a mesma A P I, sem "
            f"mudar código. {GLOBAL_TABLES} dão réplicas multi-região "
            f"ativo-ativo, com leitura e escrita em todas as regiões, resolvendo "
            f"conflitos pela regra {LAST_WRITER_WINS}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O T T L expira itens automaticamente, sem custo de "
            f"escrita ou exclusão — perfeito para limpar sessões antigas. "
            f"Streams captura mudanças e dispara uma Lambda, base de arquiteturas "
            f"orientadas a evento. {TRANSACTIONS} oferecem operações A C I D "
            f"multi-item, tudo ou nada, em até cem itens por transação. E o P I T "
            f"R restaura a tabela para qualquer segundo nos últimos trinta e "
            f"cinco dias."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},
    {
        "voice": "antonio",
        "text": (
            f"{BRK(300)} Uma armadilha clássica: Query usa a {PARTITION_KEY} "
            f"para buscar direto — rápido, previsível e barato. Scan percorre a "
            f"tabela inteira, item por item — lento e caro, mesmo com filtro, "
            f"porque o filtro só é aplicado {EMPH('depois')} de ler tudo. Se a "
            f"questão menciona performance ruim numa tabela grande, a resposta "
            f"envolve modelar a chave corretamente, ou criar um {SAY('GSI')} — "
            f"nunca adicionar um filtro ao Scan."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Hot Partition ----
    {
        "voice": "francisca",
        "text": (
            f"O problema de modelagem mais cobrado é a {HOT_PARTITION}. O "
            f"{SAY('DynamoDB')} distribui dados e capacidade entre partições "
            f"físicas baseado na {PARTITION_KEY}. Se muitos itens compartilham a "
            f"mesma chave, ou um pequeno grupo de chaves recebe tráfego "
            f"desproporcional, aquela partição fica sobrecarregada — mesmo com "
            f"capacidade total disponível na tabela."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} A solução padrão é redesenhar a chave para ter alta "
            f"cardinalidade — por exemplo, incluindo um sufixo aleatório ou o I D "
            f"do usuário — distribuindo a carga entre mais partições. "
            f"{EMPH('Aumentar a capacidade provisionada não resolve')} — o "
            f"problema é distribuição, não capacidade total."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- ElastiCache ----
    {
        "voice": "antonio",
        "text": (
            f"Sobre ElastiCache: Redis tem estruturas ricas — listas, sets, "
            f"{SORTED_SETS}, hashes — com persistência, replicação e {MULTI_AZ} "
            f"com {FAILOVER} automático. Ranking ou leaderboard é sinônimo de "
            f"{SORTED_SETS}. Suporta também publicação e assinatura, scripts "
            f"Lua, e {CLUSTER_MODE} para sharding horizontal."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Memcached é mais simples: cache chave-valor, "
            f"multi-thread, usando múltiplos núcleos por nó. Sem persistência "
            f"nem replicação — o dado é puramente descartável. Escala "
            f"horizontalmente de forma simples, adicionando nós."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Dois padrões de cache valem lembrar: {LAZY_LOADING}, "
            f"onde o dado só entra no cache na primeira leitura — simples, mas a "
            f"primeira leitura é sempre um cache miss. E {WRITE_THROUGH}, onde "
            f"toda escrita no banco também atualiza o cache — sempre atualizado, "
            f"mas pode escrever dados que nunca serão lidos."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Redshift ----
    {
        "voice": "antonio",
        "text": (
            f"Por fim, Redshift: otimizado para O L A P, consultas analíticas "
            f"complexas sobre grandes volumes — não para transações O L T P de "
            f"alto volume. Usa armazenamento colunar, compressão agressiva e "
            f"distribuição entre nós."
            f"{BRK(400)} O Redshift {SPECTRUM} permite consultar dados direto no "
            f"{SAY('S3')}, sem carregá-los no cluster. E o Redshift Serverless "
            f"elimina a gestão de cluster, escalando automaticamente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"O material escrito traz um laboratório prático de duas horas e "
            f"meia, no Free Tier, onde você força um {FAILOVER} de {MULTI_AZ} e "
            f"observa o {SAY('endpoint')} não mudar, promove uma "
            f"{READ_REPLICA}, compara o custo de Query contra Scan no "
            f"{SAY('DynamoDB')}, e compara a latência do Redis com o "
            f"{SAY('DynamoDB')} para o mesmo dado."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint completo (7 perguntas) ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: relatórios noturnos estão derrubando a "
            f"performance do app de produção. Como resolver sem mudar a lógica "
            f"de escrita?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Direcionar as queries de relatório para uma {READ_REPLICA}. O app "
            f"de escrita continua apontando para o primário, inalterado. "
            f"{MULTI_AZ} não ajudaria — o standby não atende tráfego de leitura."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: o banco precisa sobreviver automaticamente à queda de "
            f"uma zona, sem mudar a string de conexão da aplicação. Qual "
            f"recurso?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{MULTI_AZ}. {FAILOVER} automático em um a dois minutos, e o "
            f"{SAY('endpoint')} D N S permanece o mesmo — a {SAY('AWS')} reaponta "
            f"internamente."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: funções Lambda estão esgotando o limite de conexões do "
            f"{SAY('RDS')} em picos de tráfego. Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{RDS_PROXY} — faz pool de conexões reais e as multiplexa entre as "
            f"invocações, evitando que cada chamada abra uma conexão nova "
            f"diretamente no banco."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quarta: ranking em tempo real de um jogo com milhões de "
            f"jogadores, atualizado a cada partida. Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"ElastiCache Redis com {SORTED_SETS} — estrutura nativa para "
            f"ranking ordenado, atualizando e consultando em sub-milissegundo, "
            f"sem reordenar manualmente."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Quinta: uma tabela {SAY('DynamoDB')} usa o I D do cliente como "
            f"chave de partição, mas um cliente gigante gera oitenta por cento "
            f"do tráfego. O que acontece, e como corrigir?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Isso é uma {HOT_PARTITION}. A correção é redesenhar a chave para "
            f"maior cardinalidade — por exemplo, combinando o I D do cliente com "
            f"um sufixo de distribuição, espalhando a carga entre mais "
            f"partições."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Sexta: a aplicação precisa expirar automaticamente itens de "
            f"sessão depois de vinte e quatro horas, sem custo adicional de "
            f"processamento. Qual recurso?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"T T L do {SAY('DynamoDB')} — define um atributo de expiração, e o "
            f"item é removido automaticamente em segundo plano, sem consumir "
            f"capacidade de leitura ou escrita."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: você precisa de recuperação de desastre entre "
            f"regiões para um banco relacional, com R P O de segundos e R T O de "
            f"menos de um minuto. Qual a opção?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Aurora {GLOBAL_DATABASE} — replicação entre regiões com atraso "
            f"tipicamente abaixo de um segundo, e promoção da região secundária "
            f"em menos de um minuto. {READ_REPLICA} entre regiões do "
            f"{SAY('RDS')} tem atraso maior e promoção manual mais lenta."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo cinco. No próximo, vamos falar de alta "
            f"disponibilidade e escalabilidade. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
