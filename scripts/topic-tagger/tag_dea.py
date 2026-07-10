#!/usr/bin/env python3
"""
Rotulador de tópicos das questões DEA-C01 (campo `topics`).
Diferente dos demais: PRESERVA tags existentes (curadas manualmente) e
rotula apenas questões novas sem o campo. Uso: python3 scripts/topic-tagger/tag_dea.py
"""
import json, re, collections, os
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
TAXONOMY = {
 'de-fundamentals': ('Fundamentos de engenharia de dados', [r'ETL\b|ELT\b', r'data lake.{0,30}warehouse|warehouse.{0,30}data lake', r'schema-on-', r'colunar|linha a linha', r'Avro|Parquet.{0,40}(compara|vs)', r'small files|arquivos pequenos', r'Iceberg|table format']),
 'streaming': ('Ingestão streaming (Kinesis e MSK)', [r'Kinesis', r'Firehose', r'\bMSK\b|Kafka', r'\bshard', r'fan-?out', r'IteratorAge', r'Managed.{0,10}Flink', r'partition key.{0,40}(stream|shard)', r'streaming|tempo real']),
 'batch-ingestion': ('Ingestão batch e migração', [r'\bDMS\b', r'\bCDC\b|change data capture', r'AppFlow', r'DataSync', r'Snowball|fam[ií]lia Snow', r'Transfer Family', r'\bSCT\b']),
 'glue-etl': ('AWS Glue e Data Catalog', [r'\bGlue\b', r'Crawler', r'Data Catalog', r'DataBrew', r'Job Bookmark', r'Schema Registry', r'\bDPU\b|worker type|G\.[12]X']),
 'datalake-s3': ('Data Lake no S3', [r'\bS3\b', r'\bbucket', r'lifecycle|ciclo de vida', r'Intelligent[- ]Tiering', r'particionamento|parti[cç][aã]o|prefixo', r'classe de armazenamento|Glacier', r'compaction|compacta']),
 'redshift': ('Amazon Redshift', [r'Redshift', r'DISTSTYLE|DISTKEY|SORT KEY|sort key', r'\bCOPY\b|\bUNLOAD\b', r'Spectrum', r'\bWLM\b', r'Concurrency Scaling', r'materialized view', r'data shar', r'VACUUM|ANALYZE']),
 'athena': ('Amazon Athena', [r'Athena', r'\bCTAS\b', r'workgroup', r'partition projection', r'federated quer', r'dados escaneados|bytes escaneados', r'result reuse']),
 'emr': ('Amazon EMR e Spark', [r'\bEMR\b', r'Spark', r'\bHive\b', r'EMRFS', r'n[oó]s? (task|core|primary)', r'broadcast join', r'cluster transiente']),
 'orchestration': ('Orquestração de pipelines', [r'Step Functions', r'\bMWAA\b|Airflow', r'\bDAG', r'EventBridge.{0,30}(agend|regra|Scheduler)', r'Glue Workflow', r'Retry|Catch', r'Map\b.{0,30}(estado|state)', r'backfill', r'orquestra']),
 'dataops': ('Operações e qualidade de dados', [r'Data Quality|DQDL', r'CloudWatch', r'alarme|alarm', r'IteratorAge', r'STL_LOAD_ERRORS|MAXERROR', r'idempot', r'monitorar|observabilidade', r'lag|atraso', r'skew', r'linhagem']),
 'data-security': ('Segurança e governança de dados', [r'Lake Formation', r'LF-Tags', r'\bKMS\b', r'Macie', r'Secrets Manager', r'criptograf', r'data filter|row-level|column-level|coluna.{0,30}(mascar|permiss)', r'mascaramento|masking', r'cross-account', r'VPC [Ee]ndpoint|PrivateLink', r'CloudTrail', r'Block Public Access', r'menor privil[eé]gio']),
 'nosql-stores': ('DynamoDB e data stores', [r'DynamoDB', r'\bDAX\b', r'Streams do DynamoDB|DynamoDB Streams', r'on-demand.{0,30}(capacidade|modo)', r'export.{0,20}S3', r'chave-valor', r'PITR']),
}
COMPILED = {k: [re.compile(p, re.I) for p in pats] for k,(n,pats) in TAXONOMY.items()}
def score(q):
    text=q['text']; ci=q['correct'] if isinstance(q['correct'],list) else [q['correct']]
    ct=' '.join(q['options'][i] for i in ci); wt=' '.join(o for i,o in enumerate(q['options']) if i not in ci)
    sc={}
    for t,pats in COMPILED.items():
        s=0
        for p in pats:
            if p.search(text): s+=3
            if p.search(ct): s+=4
            if p.search(wt): s+=1
        if s: sc[t]=s
    return sc
def choose(sc):
    if not sc: return []
    strong=sorted([t for t,s in sc.items() if s>=4], key=lambda t:-sc[t])
    if strong: return strong[:3]
    best=max(sc.values())
    return sorted([t for t,s in sc.items() if s==best], key=lambda t:-sc[t])[:2]
if __name__=='__main__':
    for lvl in ['iniciante','medio','avancado']:
        path=os.path.join(ROOT,f'data/exams/dea-c01/{lvl}.json')
        d=json.load(open(path,encoding='utf-8'))
        novos=0
        for q in d['questions']:
            if not q.get('topics'):
                q['topics']=choose(score(q)); novos+=1
        json.dump(d,open(path,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
        sem=sum(1 for q in d['questions'] if not q.get('topics'))
        print(f"{lvl}: {len(d['questions'])} questões | rotuladas agora: {novos} | sem tópico: {sem}")
