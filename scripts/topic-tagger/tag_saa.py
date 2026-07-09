#!/usr/bin/env python3
"""
Rotulador de tópicos das questões SAA-C03 (campo `topics`).
Idempotente: pode rodar de novo após adicionar questões novas.
Uso: python3 scripts/topic-tagger/tag_saa.py
"""
import json, re, collections, sys, os

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

# tópico: (nome de exibição, [padrões regex case-insensitive; use (?-i:...) para case-sensitive])
TAXONOMY = {
 'iam': ('IAM e identidades', [r'\bIAM\b', r'AssumeRole', r'\bSTS\b', r'instance profile', r'permission boundar', r'Identity Center', r'\bSSO\b', r'federa', r'access key', r'menor privil[eé]gio', r'least privilege', r'usu[aá]rio raiz', r'\broot\b.{0,20}(conta|MFA|user)', r'MFA', r'pol[ií]tica.{0,20}(IAM|baseada em identidade|baseada em recurso)', r'resource-based polic', r'identity-based']),
 'ec2-compute': ('EC2 e computação', [r'\bEC2\b', r'\bAMI\b', r'instance store', r'placement group', r'\bSpot\b', r'Reserved Instance', r'inst[aâ]ncia reservada', r'Dedicated Host', r'user data', r'hibernat', r'tipo de inst[aâ]ncia', r'General Purpose|Memory Optimized|Compute Optimized|fam[ií]lia [MRCTX]\b', r'Compute Optimizer', r'\bBatch\b', r'Lightsail', r'Capacity Rebalanc', r'lifecycle hook', r'launch template|modelo de execu[cç][aã]o', r'Elastic Beanstalk|Beanstalk', r'\.ebextensions']),
 's3-storage': ('S3 e armazenamento', [r'\bS3\b', r'\bbucket', r'Glacier', r'classe de armazenamento', r'storage class', r'lifecycle', r'ciclo de vida', r'versionament', r'\bEBS\b', r'\bEFS\b', r'\bFSx\b', r'Object Lock', r'Intelligent[- ]Tiering', r'presigned|pr[eé]-assinad', r'multipart', r'Object Lambda', r'snapshot', r'\bgp[23]\b|\bio[12]\b|\bst1\b|\bsc1\b', r'Transfer Acceleration', r'Storage Lens', r'MFA Delete']),
 'vpc': ('VPC e redes', [r'\bVPC\b', r'sub-rede|subnet', r'\bNAT\b', r'Internet Gateway|\bIGW\b', r'security group|grupo de seguran[cç]a', r'\bNACL\b|network ACL', r'route table|tabela de rota', r'VPC [Ee]ndpoint|PrivateLink|Gateway Endpoint|Interface Endpoint', r'peering', r'Elastic IP', r'\bENI\b', r'[Ff]low [Ll]ogs', r'bastion', r'CIDR']),
 'databases': ('Bancos de dados', [r'\bRDS\b', r'Aurora', r'DynamoDB', r'ElastiCache', r'\bRedis\b', r'Memcached', r'\bDAX\b', r'Neptune', r'DocumentDB', r'Keyspaces', r'\bQLDB\b', r'Timestream', r'read replica|r[eé]plica de leitura', r'RDS Proxy', r'Performance Insights', r'Global Tables|tabelas globais', r'MemoryDB', r'PITR|point-in-time']),
 'high-availability': ('Alta disponibilidade e escalabilidade', [r'\bALB\b|\bNLB\b|\bELB\b|[Ll]oad [Bb]alancer|balanceador', r'Auto Scaling|\bASG\b', r'health check|verifica[cç][aã]o de sa[uú]de', r'target group|grupo de destino', r'sticky session|sess[aã]o pegajosa|afinidade', r'scaling polic|pol[ií]tica de escal', r'zona de disponibilidade|Availability Zone|multi-AZ|Multi-AZ']),
 'dr-backup': ('DR e backup', [r'disaster recovery|recupera[cç][aã]o de desastre', r'\bRPO\b', r'\bRTO\b', r'pilot light', r'warm standby', r'multi-site', r'AWS Backup', r'\bDRS\b|Elastic Disaster Recovery', r'backup e restaura|backup & restore']),
 'serverless': ('Serverless e mensageria', [r'Lambda(?!@Edge)', r'\bSQS\b', r'\bSNS\b', r'EventBridge', r'\bDLQ\b|dead-letter', r'fan-?out', r'fila\b|filas\b', r'serverless|sem servidor', r'Amplify', r'cold start', r'concorr[eê]ncia (provisionada|reservada)', r'visibility timeout|tempo limite de visibilidade', r'long polling', r'FIFO']),
 'security-services': ('Serviços de segurança', [r'\bKMS\b', r'CloudHSM', r'GuardDuty', r'Inspector', r'Macie', r'\bWAF\b', r'Shield', r'Firewall Manager', r'Secrets Manager', r'\bACM\b|Certificate Manager', r'Security Hub', r'Detective', r'Network Firewall', r'Nitro Enclaves', r'Parameter Store', r'criptograf', r'SSE-KMS|SSE-S3|SSE-C', r'envelope']),
 'monitoring': ('Monitoramento e observabilidade', [r'CloudWatch', r'CloudTrail', r'AWS Config\b', r'X-Ray', r'alarme|alarm', r'm[eé]trica', r'Logs Insights', r'Trusted Advisor', r'Health Dashboard', r'Synthetics', r'Service Map|mapa de servi[cç]o']),
 'migration': ('Migração e transferência', [r'Snowball|Snowcone|Snowmobile|fam[ií]lia Snow', r'DataSync', r'\bDMS\b', r'\bSCT\b', r'Storage Gateway|File Gateway|Volume Gateway|Tape Gateway|VTL', r'Transfer Family', r'\bMGN\b|Application Migration', r'on-premises', r'lift-and-shift|rehost|replataforma|replatform']),
 'analytics': ('Analytics e Big Data', [r'Kinesis', r'Firehose', r'\bGlue\b', r'Athena', r'Redshift', r'\bEMR\b', r'QuickSight', r'OpenSearch|Elasticsearch', r'\bMSK\b|Kafka', r'Lake Formation', r'data lake', r'Parquet', r'AppFlow', r'Managed.{0,10}Flink|Data Analytics', r'shard']),
 'cost': ('Otimização de custos', [r'custo', r'\bcost\b', r'Savings Plans', r'Cost Explorer', r'Budgets|or[cç]amento', r'Cost and Usage|\bCUR\b', r'pre[cç]o|pricing', r'billing|fatura', r'tag.{0,15}aloca[cç][aã]o', r'CAPEX|OPEX', r'mais barat|menor custo|econom']),
 'containers': ('Containers', [r'\bECS\b', r'\bEKS\b', r'Fargate', r'\bECR\b', r'cont[eê]iner|container', r'Kubernetes', r'App Runner', r'task definition|defini[cç][aã]o de task', r'\bpod\b']),
 'app-integration': ('APIs e integração', [r'API Gateway', r'Step Functions', r'AppSync', r'Amazon MQ', r'ActiveMQ|RabbitMQ', r'\bSWF\b', r'GraphQL', r'WebSocket', r'usage plan|plano de uso', r'throttling', r'exponential backoff|backoff exponencial|\bjitter\b', r'\bidempot']),
 'edge-dns': ('Route 53, CloudFront e borda', [r'Route ?53', r'CloudFront', r'Global Accelerator', r'edge location|localiza[cç][aã]o de borda', r'\bOAC\b|\bOAI\b|Origin Access', r'geolocaliza|geoproximi', r'Lambda@Edge', r'CloudFront Functions', r'hosted zone', r'registro (A|CNAME|alias)|pol[ií]tica de roteamento']),
 'hybrid-networking': ('Redes híbridas e edge computing', [r'Direct Connect|\bDX\b', r'Site-to-Site|VPN\b', r'Client VPN', r'Transit Gateway', r'Outposts', r'Local Zones?', r'Wavelength', r'\bBGP\b', r'\bVIF\b', r'h[ií]brid']),
 'ml-ai': ('Machine Learning e IA', [r'SageMaker', r'Rekognition', r'Comprehend', r'Textract', r'Polly', r'Transcribe', r'Translate\b', r'\bLex\b', r'Kendra', r'Personalize', r'Forecast', r'Bedrock', r'machine learning|aprendizado de m[aá]quina', r'intelig[eê]ncia artificial']),
 'governance': ('Organizations e governança', [r'Organizations', r'\bSCP\b|Service Control', r'(?-i:\bOUs?\b)|unidade organizacional', r'Control Tower', r'landing zone', r'AWS RAM|Resource Access Manager', r'Service Catalog', r'License Manager', r'multi ?-?conta|m[uú]ltiplas contas', r'organization trail|trilha da organiza[cç][aã]o', r'consolidated billing|fatura consolidada']),
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
            if p.search(ct): s += 4  # o serviço na resposta correta É o assunto da questão
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
        path = os.path.join(ROOT, f'data/exams/saa-c03/{lvl}.json')
        d = json.load(open(path, encoding='utf-8'))
        for q in d['questions']:
            q['topics'] = choose(score_topics(q))
            for t in q['topics']: stats[lvl][t] += 1
            if not q['topics']: untagged.append((lvl, q['id']))
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"{'tópico':22} ini  med  avc  total")
    for t in TAXONOMY:
        tot = sum(stats[l][t] for l in stats)
        print(f"{t:22} {stats['iniciante'][t]:>3} {stats['medio'][t]:>4} {stats['avancado'][t]:>4} {tot:>6}")
    print('SEM TÓPICO:', untagged if untagged else 0)
