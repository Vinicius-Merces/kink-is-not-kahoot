"""Roteiro tratado do Capitulo 5 (Bancos de dados - RDS, Aurora, DynamoDB)."""

from glossary import SAY, EMPH, BRK, PHON

READ_REPLICA = PHON("rid rɪˈplɪkə", "Read Replica")
MULTI_AZ = PHON("ˈmʌlti eɪ zɛd", "Multi-AZ")
FAILOVER = PHON("ˈfeɪloʊvɚ", "failover")
BACKTRACK = PHON("ˈbæktræk", "Backtrack")
GLOBAL_DATABASE = PHON("ˈɡloʊbəl ˈdeɪtəbeɪs", "Global Database")
PARTITION_KEY = PHON("pɑrˈtɪʃən ki", "partition key")
SORT_KEY = PHON("sɔrt ki", "sort key")
HOT_PARTITION = PHON("hɑt pɑrˈtɪʃən", "hot partition")
ON_DEMAND = PHON("ɑn dɪˈmænd", "on-demand")
PROVISIONED = PHON("prəˈvɪʒənd", "provisioned")
LAZY_LOADING = PHON("ˈleɪzi ˈloʊdɪŋ", "lazy loading")
WRITE_THROUGH = PHON("raɪt θru", "write-through")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo cinco: bancos de dados. É o domínio mais denso da prova, então "
            f"vamos com calma."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    {
        "voice": "antonio",
        "text": (
            f"A primeira pergunta que você deve se fazer não é qual banco é melhor, e "
            f"sim qual banco se encaixa no padrão de acesso, consistência e escala "
            f"descritos no enunciado."
            f"{BRK(400)} {SAY('RDS')} é S Q L relacional tradicional. Aurora é S Q L "
            f"compatível com performance superior na {SAY('AWS')}. {SAY('DynamoDB')} é "
            f"N o S Q L de chave-valor, com latência baixa em qualquer escala. E "
            f"Redshift é para data warehouse, consultas analíticas pesadas."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Agora a pegadinha número um do exame: {MULTI_AZ} contra {READ_REPLICA}. "
            f"Grave assim: {EMPH('Multi A Z é disponibilidade')}. {EMPH('Read Replica é performance de leitura')}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} O {MULTI_AZ} replica de forma síncrona para um standby "
            f"invisível, que não atende tráfego nenhum. Se o primário cai, o "
            f"{FAILOVER} é automático, e o endereço de conexão não muda."
            f"{BRK(400)} Já a {READ_REPLICA} replica de forma assíncrona, e atende "
            f"tráfego de leitura de verdade. Se o primário cair, ela não assume "
            f"sozinha — é preciso promovê-la manualmente."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"A Aurora tem diferenciais que a prova adora. O armazenamento é "
            f"distribuído automaticamente em seis cópias, por três zonas de "
            f"disponibilidade, com {FAILOVER} em cerca de trinta segundos — bem mais "
            f"rápido que o {SAY('RDS')} tradicional."
            f"{BRK(400)} E o Aurora {GLOBAL_DATABASE} replica entre regiões diferentes "
            f"com atraso menor que um segundo, e promove a região secundária em menos "
            f"de um minuto. É a resposta padrão quando o cenário pede recuperação de "
            f"desastre agressiva para um banco relacional."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Quando funções Lambda esgotam o limite de conexões do banco em picos de "
            f"tráfego, a resposta é o {SAY('RDS')} Proxy: ele faz o pool de conexões "
            f"reais e as compartilha entre as chamadas, sem cada invocação abrir uma "
            f"conexão nova."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Vamos para o {SAY('DynamoDB')}. Cada item tem uma {PARTITION_KEY}, e "
            f"opcionalmente uma {SORT_KEY}. No modo {ON_DEMAND}, você paga por "
            f"requisição, ideal para carga imprevisível. No modo {PROVISIONED}, mais "
            f"barato por unidade, você define a capacidade, ideal para carga "
            f"previsível."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(500)} E aqui vai uma armadilha clássica: Query usa a chave de "
            f"partição para buscar direto, rápido e barato. Scan percorre a tabela "
            f"inteira, item por item — lento e caro, mesmo com filtro, porque o "
            f"filtro só é aplicado depois de ler tudo."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Um problema de modelagem muito cobrado é a {HOT_PARTITION}: quando "
            f"muitos itens compartilham a mesma chave de partição, ou um pequeno "
            f"grupo de chaves recebe tráfego desproporcional, aquela partição física "
            f"fica sobrecarregada — mesmo com capacidade total disponível na tabela."
            f"{BRK(400)} A solução não é aumentar a capacidade. A solução é redesenhar "
            f"a chave de partição para ter mais variedade, distribuindo melhor a "
            f"carga."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Outros recursos importantes do {SAY('DynamoDB')}: T T L expira itens "
            f"automaticamente, sem custo extra — perfeito para limpar sessões antigas. "
            f"Streams captura mudanças e dispara uma Lambda. E Global Tables replica "
            f"a tabela entre regiões, com leitura e escrita em todas elas "
            f"simultaneamente."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Por fim, o ElastiCache. Redis tem estruturas ricas, como sorted sets, "
            f"perfeito para ranking em tempo real, além de persistência e replicação. "
            f"Memcached é mais simples, multi-thread, sem persistência — dado "
            f"totalmente descartável."
            f"{BRK(400)} Dois padrões de cache valem lembrar: {LAZY_LOADING}, onde o "
            f"dado só entra no cache na primeira leitura, e {WRITE_THROUGH}, onde toda "
            f"escrita no banco também atualiza o cache."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: relatórios noturnos estão derrubando a "
            f"performance do app de produção. Como resolver sem mudar a lógica de "
            f"escrita?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Direcionar as queries de relatório para uma {READ_REPLICA}. O app de "
            f"escrita continua apontando para o primário, sem nenhuma mudança."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: uma tabela {SAY('DynamoDB')} usa o I D do cliente como chave de "
            f"partição, mas um cliente gigante gera oitenta por cento do tráfego. O "
            f"que acontece, e como corrigir?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Isso é uma {HOT_PARTITION}. A correção é redesenhar a chave para ter "
            f"mais variedade, por exemplo combinando o I D do cliente com um sufixo "
            f"de distribuição, espalhando a carga entre mais partições."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: ranking em tempo real de um jogo com milhões de jogadores. "
            f"Qual a solução?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"ElastiCache Redis com sorted sets — estrutura nativa para ranking "
            f"ordenado, com leitura e escrita em sub-milissegundo."
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
