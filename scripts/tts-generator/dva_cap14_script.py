"""Roteiro DVA-C02 Capitulo 14 — Troubleshooting, otimizacao e tabela mestre."""

from glossary import SAY, EMPH, BRK, PHON

XRAY = PHON("ɛks reɪ", "X-Ray")
DAX = PHON("dæks", "DAX")
ELASTICACHE = PHON("ɪˈlæstɪkæʃ", "ElastiCache")
LAZY_LOADING = PHON("ˈleɪzi ˈloʊdɪŋ", "lazy loading")
WRITE_THROUGH = PHON("raɪt θru", "write-through")
PROVISIONED = PHON("prəˈvɪʒənd kənˈkɜrənsi", "Provisioned Concurrency")
BUCKET_KEYS = PHON("ˈbʌkət kiz", "S3 Bucket Keys")
LONG_POLLING = PHON("lɔŋ ˈpoʊlɪŋ", "long polling")
CODEGURU = PHON("koʊd ˈɡuru ˈproʊfaɪlɚ", "CodeGuru Profiler")
HANDLER = PHON("ˈhændlɚ", "handler")
VISIBILITY = PHON("ˌvɪzəˈbɪləti ˈtaɪmaʊt", "visibility timeout")
PRESIGNED = PHON("priˈsaɪnd ju ɑr ɛl", "presigned URL")
ENVELOPE = PHON("ˈɛnvəloʊp ɪnˈkrɪpʃən", "envelope encryption")
GSI = PHON("dʒi ɛs aɪ", "GSI")
DLQ = PHON("di ɛl kju", "DLQ")
CHANGE_SET = PHON("tʃeɪndʒ sɛt", "Change Set")
SAM_LOCAL = PHON("sæm ˈloʊkəl", "sam local")
IMMUTABLE = PHON("ɪˈmjutəbəl", "immutable")
CORS = PHON("kɔrz", "CORS")
FILTER_POLICIES = PHON("ˈfɪltɚ ˈpɑləsiz", "filter policies")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo quatorze, o último: troubleshooting, otimização e a "
            f"tabela mestre — o {SAY('DVA')} inteiro em uma página. Na última "
            f"semana antes da prova, revise ESTE capítulo diariamente."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Dicionario de erros ----
    {
        "voice": "antonio",
        "text": (
            f"O dicionário de erros. Provisioned throughput exceeded no "
            f"{SAY('DynamoDB')}: capacidade ou hot partition — backoff, chave "
            f"melhor, on-demand ou {DAX}. Quatro dois nove no {SAY('API')} "
            f"Gateway: throttling — backoff e ajustar limites. Cinco zero "
            f"dois: resposta malformada da Lambda proxy. Cinco zero quatro: "
            f"integração passou dos vinte e nove segundos — padrão assíncrono. "
            f"Task timed out na Lambda: timeout baixo ou dependência lenta — "
            f"investigue com {XRAY}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Lambda em {SAY('VPC')} sem acessar {SAY('API')} "
            f"externa: sem saída para internet — NAT Gateway com rota. Access "
            f"denied com {SAY('SSE')} {SAY('KMS')} no {SAY('S3')}: falta "
            f"{SAY('KMS')} decrypt na ROLE. Mensagens {SAY('SQS')} duplicadas: "
            f"{VISIBILITY} curto e consumidor não idempotente. E erro de "
            f"{CORS} no navegador: preflight sem o allow origin — habilite "
            f"{CORS} na {SAY('API')} ou no bucket."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Otimizacao ----
    {
        "voice": "francisca",
        "text": (
            f"As respostas-padrão de otimização. Leitura repetitiva: CACHE — "
            f"{ELASTICACHE} com {LAZY_LOADING} ou {WRITE_THROUGH} mais "
            f"{SAY('TTL')}, {DAX} no {SAY('DynamoDB')}, cache do {SAY('API')} "
            f"Gateway — inclusive por header quando o conteúdo varia por "
            f"cliente. Lambda lenta: mais memória — que é mais {SAY('CPU')} — "
            f"conexões FORA do {HANDLER} para reuso entre invocações, e "
            f"{PROVISIONED} para cold start. Para DESCOBRIR o gargalo em "
            f"produção: {CODEGURU} ou {XRAY}."
        ),
    },
    {
        "voice": "francisca",
        "text": (
            f"{BRK(400)} Custo: {SAY('HTTP')} {SAY('API')} em vez de REST "
            f"quando não precisa dos extras, {BUCKET_KEYS} com {SAY('SSE')} "
            f"{SAY('KMS')}, {LONG_POLLING} no {SAY('SQS')}, e {FILTER_POLICIES} "
            f"no {SAY('SNS')} para não entregar o que seria descartado."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Tabela mestre ----
    {
        "voice": "antonio",
        "text": (
            f"A tabela mestre — decore cada linha. Credenciais seguras: role — "
            f"instance profile, task role, execution role. Eliminar cold "
            f"start: {PROVISIONED}. Limitar concorrência para proteger o "
            f"downstream: reserved. Deploy gradual de Lambda: alias com pesos "
            f"mais CodeDeploy. Processo acima de vinte e nove segundos atrás "
            f"de {SAY('API')}: assíncrono com duzentos e dois. Consulta por "
            f"atributo não-chave: {GSI} com Query — nunca Scan."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Escrita concorrente: condition expression e "
            f"optimistic locking. Upload direto do cliente: {PRESIGNED}. "
            f"Criptografar acima de quatro kilobytes: {ENVELOPE}. Rotação "
            f"automática: Secrets Manager. Login de usuários: Cognito User "
            f"Pool; cliente acessando {SAY('AWS')} direto: Identity Pool. "
            f"Poison messages: {DLQ} com max receive count. Workflow "
            f"multi-etapas: Step Functions. Ver mudanças antes do update: "
            f"{CHANGE_SET}. Testar Lambda local: {SAM_LOCAL}. Filtrar traces: "
            f"{XRAY} annotations. E deploy {SAY('Beanstalk')} com rollback "
            f"rápido: {IMMUTABLE} ou blue green."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Checkpoint final ----
    {
        "voice": "francisca",
        "text": (
            f"Checkpoint final. Primeira: qual o roteiro de diagnóstico de uma "
            f"{SAY('API')} serverless lenta?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{XRAY} acha o segmento lento. Se é a Lambda: memória, reuso de "
            f"conexões, cold start. Se é o {SAY('DynamoDB')}: chave, índices, "
            f"{DAX}. Se é a integração: cache do {SAY('API')} Gateway."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: três formas de reduzir custo numa {SAY('API')} REST de "
            f"leitura intensa?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Cache no stage do {SAY('API')} Gateway, cache de dados com {DAX} "
            f"ou {ELASTICACHE}, e avaliar {SAY('HTTP')} {SAY('API')}."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": f"E terceira: o que revisar na véspera da prova?{BRK(800)}",
    },
    {
        "voice": "antonio",
        "text": (
            f"Os números: quinze minutos de Lambda, vinte e nove segundos de "
            f"{SAY('API')} Gateway, quatro kilobytes do {SAY('KMS')}, "
            f"{SAY('RCU')} de quatro kilobytes e {SAY('WCU')} de um, duzentos "
            f"e cinquenta e seis kilobytes do {SAY('SQS')}, e trinta segundos "
            f"de {VISIBILITY} — mais a tabela mestre."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Parabéns — você chegou ao fim da trilha {SAY('DVA')} dash C zero "
            f"dois! Agora é simulado até bater oitenta por cento com "
            f"consistência. Boa prova!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
