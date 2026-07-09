#!/usr/bin/env python3
"""
Rotulador de tópicos das questões DVA-C02 (campo `topics`).
Idempotente. Uso: python3 scripts/topic-tagger/tag_dva.py
"""
import json, re, collections, os

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

TAXONOMY = {
 'sdk-cli': ('SDK, CLI e credenciais', [r'\bSDK\b', r'\bCLI\b', r'credencia', r'access key', r'IMDS|metadata service', r'instance profile', r'exponential backoff|backoff exponencial', r'\bjitter\b', r'\bretry|retentativa', r'pagina[cç]|paginator', r'--profile|\bprofile\b.{0,20}(nomeado|named|aws)', r'\bidempot', r'vari[aá]ve(l|is) de ambiente.{0,30}(AWS|credencia)']),
 'lambda': ('AWS Lambda', [r'Lambda(?!@Edge)', r'cold start', r'concorr[eê]ncia (provisionada|reservada)|Provisioned Concurrency|Reserved Concurrency', r'\balias\b', r'\blayer', r'event source mapping', r'/tmp\b', r'Destinations', r'execution role|fun[cç][aã]o de execu[cç][aã]o', r'\$LATEST|vers[aã]o publicada', r'invoca[cç][aã]o (s[ií]ncrona|ass[ií]ncrona)']),
 'api-gateway': ('API Gateway', [r'API Gateway', r'usage plan|plano de uso', r'API [Kk]ey', r'\bstage\b|est[aá]gio da API', r'canary', r'authorizer|autorizador', r'\b(429|502|504)\b', r'mapping template', r'integra[cç][aã]o proxy|proxy integration', r'WebSocket', r'HTTP API|REST API', r'29 ?segundos|29s']),
 'dynamodb': ('DynamoDB', [r'DynamoDB', r'\bRCU\b|\bWCU\b', r'unidade de (leitura|escrita)|capacity unit', r'\bGSI\b|\bLSI\b|[ií]ndice secund[aá]rio', r'condition expression|express[aã]o de condi[cç][aã]o', r'optimistic|otimista', r'\bDAX\b', r'Streams', r'\bTTL\b', r'BatchGetItem|BatchWriteItem', r'\bScan\b|\bQuery\b', r'partition key|sort key|chave de parti[cç][aã]o|chave de classifica', r'transa[cç]|TransactWrite']),
 's3-dev': ('S3 para desenvolvedores', [r'\bS3\b', r'\bbucket', r'presigned|pr[eé]-assinad', r'multipart', r'SSE-KMS|SSE-S3|SSE-C', r'Bucket Keys', r'event notification|notifica[cç][aã]o de evento', r'\bCORS\b', r'Transfer Acceleration']),
 'messaging': ('Mensageria e Step Functions', [r'\bSQS\b', r'\bSNS\b', r'EventBridge', r'Step Functions', r'visibility timeout|tempo limite de visibilidade', r'long polling', r'FIFO', r'fan-?out', r'\bDLQ\b|dead-letter', r'Express|Standard.{0,20}workflow|state machine|m[aá]quina de estados', r'task token', r'MessageGroupId|dedupl', r'ActiveMQ|RabbitMQ|Amazon MQ', r'Retry|Catch.{0,30}(estado|state)']),
 'security-dev': ('IAM, KMS e segredos', [r'\bKMS\b', r'GenerateDataKey', r'envelope', r'Secrets Manager', r'Parameter Store', r'\bSTS\b', r'AssumeRole', r'\bIAM\b', r'criptograf', r'\bACM\b|Certificate Manager', r'rota[cç][aã]o.{0,25}(segredo|credencia|autom)', r'menor privil[eé]gio|least privilege', r'pol[ií]tica.{0,20}(IAM|recurso)']),
 'cognito': ('Cognito', [r'Cognito', r'[Uu]ser [Pp]ool', r'[Ii]dentity [Pp]ool', r'\bJWT\b', r'ID token|access token|refresh token', r'Hosted UI', r'federa', r'convidad|guest|n[aã]o autenticad']),
 'containers': ('Containers e ECR', [r'\bECS\b', r'\bECR\b', r'Fargate', r'\bEKS\b', r'task definition|defini[cç][aã]o de task', r'task role|execution role.{0,30}(task|ECS)|Task Execution', r'cont[eê]iner|container', r'\bdocker\b', r'get-login-password', r'image scanning|lifecycle polic.{0,20}(ECR|imagem)']),
 'cicd': ('CI/CD (CodeSuite)', [r'CodePipeline', r'CodeBuild', r'CodeDeploy', r'CodeCommit', r'buildspec', r'appspec', r'blue/?green', r'in-place', r'Canary10Percent|Linear10Percent|deployment config', r'hook', r'pipeline', r'aprova[cç][aã]o manual|manual approval', r'artefato|artifact', r'ValidateService|BeforeAllowTraffic|AfterAllowTraffic|BeforeInstall|AfterInstall']),
 'cloudformation-sam': ('CloudFormation e SAM', [r'CloudFormation', r'\bSAM\b', r'template', r'\bstack\b', r'change set|conjunto de altera', r'\bdrift\b', r'!Ref|Fn::|GetAtt|ImportValue|!Sub|FindInMap', r'sam (local|build|deploy|package)', r'Transform.{0,20}Serverless', r'DeletionPolicy', r'StackSets', r'stack policy', r'Outputs|Export']),
 'monitoring': ('Observabilidade', [r'CloudWatch', r'CloudTrail', r'X-Ray', r'annotation|anota[cç][aã]o', r'sampling|amostragem', r'\bdaemon\b|UDP 2000', r'metric filter|filtro de m[eé]trica', r'subscription filter', r'alarme|alarm', r'Logs Insights', r'high-resolution|alta resolu[cç][aã]o', r'segment|subsegment', r'service map|mapa de servi[cç]o', r'm[eé]trica custom|PutMetricData']),
 'beanstalk': ('Elastic Beanstalk', [r'Beanstalk', r'\.ebextensions', r'all at once|rolling|immutable|traffic splitting', r'swap.{0,25}(URL|CNAME)|troca de CNAME', r'worker environment|ambiente worker', r'cron\.yaml', r'Managed Platform Updates', r'saved configuration']),
 'troubleshooting': ('Troubleshooting e otimização', [r'throttl', r'ProvisionedThroughputExceeded', r'Task timed out|tempo limite excedido', r'AccessDenied|acesso negado', r'\b(4\d\d|5\d\d)\b.{0,30}erro|erro.{0,10}\b(4\d\d|5\d\d)\b', r'lentid[aã]o|lat[eê]ncia (alta|elevada)', r'otimiza|melhorar (o desempenho|a performance)', r'diagnostic|depurar|debug', r'ElastiCache|lazy loading|write-through', r'cache']),
}

COMPILED = {k: [re.compile(p, re.I) for p in pats] for k, (n, pats) in TAXONOMY.items()}

def score_topics(q):
    text = q['text']
    ci = q['correct'] if isinstance(q['correct'], list) else [q['correct']]
    ct = ' '.join(q['options'][i] for i in ci)
    wt = ' '.join(o for i, o in enumerate(q['options']) if i not in ci)
    sc = {}
    for t, pats in COMPILED.items():
        s = 0
        for p in pats:
            if p.search(text): s += 3
            if p.search(ct): s += 4
            if p.search(wt): s += 1
        if s: sc[t] = s
    return sc

def choose(sc):
    if not sc: return []
    strong = sorted([t for t, s in sc.items() if s >= 4], key=lambda t: -sc[t])
    if strong: return strong[:3]
    best = max(sc.values())
    return sorted([t for t, s in sc.items() if s == best], key=lambda t: -sc[t])[:2]

if __name__ == '__main__':
    stats = collections.defaultdict(collections.Counter)
    untagged = []
    for lvl in ['iniciante', 'medio', 'avancado']:
        path = os.path.join(ROOT, f'data/exams/dva-c02/{lvl}.json')
        d = json.load(open(path, encoding='utf-8'))
        for q in d['questions']:
            q['topics'] = choose(score_topics(q))
            for t in q['topics']: stats[lvl][t] += 1
            if not q['topics']: untagged.append((lvl, q['id'], q['text'][:80]))
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"{'tópico':20} ini  med  avc  total")
    for t in TAXONOMY:
        tot = sum(stats[l][t] for l in stats)
        print(f"{t:20} {stats['iniciante'][t]:>3} {stats['medio'][t]:>4} {stats['avancado'][t]:>4} {tot:>6}")
    print('SEM TÓPICO:', len(untagged))
    for u in untagged[:10]: print('  ', u)
