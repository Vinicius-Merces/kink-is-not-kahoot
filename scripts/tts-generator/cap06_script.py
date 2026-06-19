"""Roteiro tratado do Capitulo 6 (Alta disponibilidade e escalabilidade)."""

from glossary import SAY, EMPH, BRK, PHON

FAULT_TOLERANCE = PHON("fɔlt ˈtɑlərəns", "Fault Tolerance")
BULKHEAD = PHON("ˈbʌlkhɛd", "Bulkhead")
CIRCUIT_BREAKER = PHON("ˈsɜrkɪt ˈbreɪkɚ", "Circuit Breaker")
GRACEFUL_DEGRADATION = PHON("ˈɡreɪsfəl dɛɡrəˈdeɪʃən", "Graceful Degradation")
EXPONENTIAL_BACKOFF = PHON("ˌɛkspoʊˈnɛnʃəl ˈbækɔf", "exponential backoff")
JITTER = PHON("ˈdʒɪtɚ", "jitter")
VISIBILITY_TIMEOUT = PHON("ˌvɪzəˈbɪləti ˈtaɪmaʊt", "Visibility Timeout")
DEAD_LETTER_QUEUE = PHON("dɛd ˈlɛtɚ kju", "Dead-Letter Queue")
LONG_POLLING = PHON("lɔŋ ˈpoʊlɪŋ", "Long Polling")
FAN_OUT = PHON("fæn aʊt", "fan-out")
FILTER_POLICY = PHON("ˈfɪltɚ ˈpɑləsi", "filter policy")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo seis: alta disponibilidade e escalabilidade. Aqui vamos juntar "
            f"as peças de computação com a camada de mensageria que dá resiliência "
            f"de verdade à arquitetura."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    {
        "voice": "antonio",
        "text": (
            f"Primeiro, o vocabulário que muda a resposta na prova: alta "
            f"disponibilidade aceita um pequeno tempo de interrupção durante o "
            f"{SAY('failover')}, de segundos a minutos. {FAULT_TOLERANCE}, ou "
            f"tolerância a falhas, exige redundância ativa duplicada, operando o "
            f"tempo todo, sem nenhuma degradação perceptível — e custa "
            f"significativamente mais."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Existem padrões de arquitetura para aumentar a resiliência. O "
            f"{BULKHEAD} isola recursos por cliente ou função, para que a falha de "
            f"um não afete os outros. O {CIRCUIT_BREAKER} para de chamar um serviço "
            f"que está falhando repetidamente, evitando uma cascata de falhas pelo "
            f"sistema inteiro."
            f"{BRK(400)} E a {GRACEFUL_DEGRADATION} serve uma versão reduzida quando "
            f"um componente não crítico falha — por exemplo, mostrar um produto sem "
            f"recomendações personalizadas, em vez de quebrar a página toda."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Quando uma chamada falha, repetir na hora só piora — gera uma onda de "
            f"tentativas que sobrecarrega ainda mais o serviço. A prática correta é "
            f"o {EXPONENTIAL_BACKOFF}: aumentar o tempo de espera exponencialmente "
            f"entre tentativas, com um componente aleatório, o {JITTER}, para evitar "
            f"que todos os clientes tentem de novo no mesmo instante."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Vamos para a camada de desacoplamento. Arquiteturas resilientes não "
            f"fazem componentes se chamarem diretamente — elas usam mensageria para "
            f"absorver picos e isolar falhas."
            f"{BRK(400)} S Q S Standard desacopla com melhor esforço de ordem. S Q S "
            f"F I F O garante ordem exata e nenhuma duplicata, mas com throughput "
            f"menor. S N S é publicação e assinatura — todos os assinantes recebem a "
            f"mensagem."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} E o padrão favorito da prova: S N S fazendo {FAN_OUT} para "
            f"várias filas S Q S, uma por sistema consumidor. Um evento, processado "
            f"de forma independente por N sistemas diferentes."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    {
        "voice": "antonio",
        "text": (
            f"Pontos de prova sobre S Q S: o {VISIBILITY_TIMEOUT} esconde a mensagem "
            f"enquanto ela está sendo processada — se não for deletada a tempo, ela "
            f"reaparece, então o consumidor precisa ser idempotente."
            f"{BRK(400)} A {DEAD_LETTER_QUEUE} isola mensagens que falharam repetidas "
            f"vezes, sem travar o processamento das demais. E o {LONG_POLLING} reduz "
            f"custo e latência de detecção, esperando até vinte segundos por uma "
            f"mensagem antes de retornar vazio."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca",
        "text": (
            f"Um detalhe importante: S Q S não é publicação e assinatura. Uma "
            f"mensagem na fila é consumida por apenas um consumidor. Se vários "
            f"sistemas independentes precisam receber a mesma mensagem, S Q S "
            f"sozinho não resolve — é preciso S N S fazendo {FAN_OUT} para múltiplas "
            f"filas."
            f"{BRK(400)} E uma {FILTER_POLICY} no S N S permite que cada assinante "
            f"receba só as mensagens que interessam a ele, sem precisar filtrar no "
            f"próprio código."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Hora da revisão. Primeira: pedidos de um e-commerce devem ser "
            f"processados na ordem exata, sem duplicatas. Qual serviço?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"S Q S F I F O. Garante processamento exatamente uma vez e ordem dentro "
            f"do mesmo grupo de mensagens."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: upload de imagem precisa disparar três sistemas "
            f"independentes — thumbnail, moderação e indexação. Como fazer?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"S N S fazendo {FAN_OUT} para três filas S Q S, cada uma com seu próprio "
            f"consumidor. Cada sistema processa no seu próprio ritmo, sem que a falha "
            f"de um afete os outros."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"E a última: um serviço dependente está lento, e isso está derrubando o "
            f"sistema inteiro em cascata. Qual padrão de resiliência aplicar?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{CIRCUIT_BREAKER}. Ele para de chamar o serviço problemático após "
            f"detectar falhas repetidas, retornando erro imediatamente em vez de "
            f"esperar timeout a cada chamada."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo seis. No próximo, vamos falar de recuperação "
            f"de desastre. Até a próxima!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
