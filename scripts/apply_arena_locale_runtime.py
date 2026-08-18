#!/usr/bin/env python3
"""Make the CloudArena API locale-aware after ready EN overlays exist."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SERVER=ROOT/'server.js'

HELPER_MARKER="const arenaCache = new Map();\n"
HELPER="""const arenaCache = new Map();

const TOPIC_LABELS_EN = {
    'iam': 'IAM and identities', 'ec2-compute': 'EC2 and compute', 's3-storage': 'S3 and storage',
    'vpc': 'VPC and networking', 'databases': 'Databases',
    'high-availability': 'High availability and scalability', 'dr-backup': 'Disaster recovery and backup',
    'serverless': 'Serverless and messaging', 'security-services': 'Security services',
    'monitoring': 'Monitoring and observability', 'migration': 'Migration and transfer',
    'analytics': 'Analytics and Big Data', 'cost': 'Cost optimization', 'containers': 'Containers',
    'app-integration': 'APIs and integration', 'edge-dns': 'Route 53, CloudFront and edge',
    'hybrid-networking': 'Hybrid networking and edge computing', 'ml-ai': 'Machine Learning and AI',
    'governance': 'Organizations and governance', 'sdk-cli': 'SDK, CLI and credentials',
    'lambda': 'AWS Lambda', 'api-gateway': 'API Gateway', 'dynamodb': 'DynamoDB',
    's3-dev': 'S3 for developers', 'messaging': 'Messaging and Step Functions',
    'security-dev': 'IAM, KMS and secrets', 'cognito': 'Cognito', 'cicd': 'CI/CD (CodeSuite)',
    'cloudformation-sam': 'CloudFormation and SAM', 'beanstalk': 'Elastic Beanstalk',
    'troubleshooting': 'Troubleshooting and optimization',
    'de-fundamentals': 'Data engineering fundamentals', 'streaming': 'Streaming ingestion (Kinesis and MSK)',
    'batch-ingestion': 'Batch ingestion and migration', 'glue-etl': 'AWS Glue and Data Catalog',
    'datalake-s3': 'Data Lake on S3', 'redshift': 'Amazon Redshift', 'athena': 'Amazon Athena',
    'emr': 'Amazon EMR and Spark', 'orchestration': 'Pipeline orchestration',
    'dataops': 'Data operations and quality', 'data-security': 'Data security and governance',
    'nosql-stores': 'NoSQL data stores'
};

function hasReadyEnglishArena(certId) {
    try {
        const overlayPath = path.join(__dirname, 'data', 'cloudarena', 'breakdowns-en', `${certId}.json`);
        if (!fs.existsSync(overlayPath)) return false;
        const overlay = JSON.parse(fs.readFileSync(overlayPath, 'utf8'));
        const overlayMeta = overlay._translation || {};
        if (overlayMeta.locale !== 'en' || overlayMeta.sourceLocale !== 'pt-BR' || overlayMeta.status !== 'ready') {
            return false;
        }
        for (const level of ['iniciante', 'medio', 'avancado']) {
            const bankPath = path.join(__dirname, 'data', 'exams-en', certId, `${level}.json`);
            if (!fs.existsSync(bankPath)) return false;
            const bank = JSON.parse(fs.readFileSync(bankPath, 'utf8'));
            const meta = bank._translation || {};
            if (meta.locale !== 'en' || meta.sourceLocale !== 'pt-BR' || meta.status !== 'ready') return false;
        }
        return true;
    } catch (error) {
        console.error(`[CloudArena] falha ao validar conteúdo EN ${certId}:`, error.message);
        return false;
    }
}
"""

OLD_CACHE="""    if (arenaCache.has(certId)) {
        return res.json(arenaCache.get(certId));
    }
"""
NEW_CACHE="""    const requestedLocale = String(req.query.locale || '').trim().toLowerCase().startsWith('en') ? 'en' : 'pt-BR';
    const useEnglish = requestedLocale === 'en' && hasReadyEnglishArena(certId);
    const contentLocale = useEnglish ? 'en' : 'pt-BR';
    const localeFallback = requestedLocale === 'en' && !useEnglish;
    const cacheKey = `${certId}:${contentLocale}`;
    if (arenaCache.has(cacheKey)) {
        return res.json(arenaCache.get(cacheKey));
    }
"""
OLD_OVERLAY="const overlayPath = path.join(__dirname, 'data', 'cloudarena', 'breakdowns', `${certId}.json`);"
NEW_OVERLAY="const overlayDir = contentLocale === 'en' ? 'breakdowns-en' : 'breakdowns';\n        const overlayPath = path.join(__dirname, 'data', 'cloudarena', overlayDir, `${certId}.json`);"
OLD_BANK="const bankPath = path.join(__dirname, 'data', 'exams', certId, `${level}.json`);"
NEW_BANK="const bankDir = contentLocale === 'en' ? 'exams-en' : 'exams';\n            const bankPath = path.join(__dirname, 'data', bankDir, certId, `${level}.json`);"
OLD_ATTACK="""                    attackName: (firstTopic && TOPIC_LABELS[firstTopic]) || firstTopic
                        || domainNames.get(q.domain) || 'Nuvem',
"""
NEW_ATTACK="""                    attackName: (firstTopic && (contentLocale === 'en' ? TOPIC_LABELS_EN[firstTopic] : TOPIC_LABELS[firstTopic]))
                        || domainNames.get(q.domain) || firstTopic || (contentLocale === 'en' ? 'Cloud' : 'Nuvem'),
"""
OLD_PAYLOAD="""        const payload = { success: true, certId, totalBank, pools };
        arenaCache.set(certId, payload);
"""
NEW_PAYLOAD="""        const payload = { success: true, certId, requestedLocale, locale: contentLocale, localeFallback, totalBank, pools };
        arenaCache.set(cacheKey, payload);
"""

def replace_once(text, old, new, label):
    count=text.count(old)
    if count!=1: raise RuntimeError(f'{label}: expected one marker, found {count}')
    return text.replace(old,new,1)

def main():
    text=SERVER.read_text(encoding='utf-8')
    if 'hasReadyEnglishArena(certId)' in text:
        print('server.js: locale-aware CloudArena already applied'); return 0
    text=replace_once(text,HELPER_MARKER,HELPER,'helper')
    text=replace_once(text,OLD_CACHE,NEW_CACHE,'cache')
    text=replace_once(text,OLD_OVERLAY,NEW_OVERLAY,'overlay path')
    text=replace_once(text,OLD_BANK,NEW_BANK,'bank path')
    text=replace_once(text,OLD_ATTACK,NEW_ATTACK,'attack label')
    text=replace_once(text,OLD_PAYLOAD,NEW_PAYLOAD,'payload cache')
    SERVER.write_text(text,encoding='utf-8'); print('patched server.js: CloudArena locale-aware runtime enabled'); return 0
if __name__=='__main__': raise SystemExit(main())
