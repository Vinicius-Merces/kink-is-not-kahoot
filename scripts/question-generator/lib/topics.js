// Constantes de apoio à geração: rótulos de nível, prefixos de ID e tópicos
// de foco por domínio (usados para variar o conteúdo gerado entre lotes).

const LEVEL_LABELS = {
    iniciante: 'Iniciante (fundamentos, terminologia básica e conceitos introdutórios)',
    medio: 'Intermediário (cenários de aplicação prática e comparação entre serviços)',
    avancado: 'Avançado (cenários complexos, otimização e arquiteturas multi-serviço)'
};

// Prefixo de nível usado nos IDs das perguntas (ex: clf-ini-013)
const ID_PREFIXES = {
    iniciante: 'ini',
    medio: 'med',
    avancado: 'avc'
};

// Tópicos sugeridos por domínio, usados para variar o foco de cada lote
// gerado e reduzir a chance de questões repetitivas.
const FOCUS_TOPICS = {
    // CLF-C02
    'cloud-concepts': [
        'AWS Well-Architected Framework (os 6 pilares)',
        'Modelos de implantação: nuvem pública, privada e híbrida',
        'Vantagens da nuvem: elasticidade, agilidade e economia de escala global',
        'CapEx vs OpEx',
        'Infraestrutura global da AWS: Regiões, Zonas de Disponibilidade, Edge Locations e Local Zones',
        'Estratégias de migração para a nuvem (os 6 Rs)',
        'AWS Cloud Adoption Framework (CAF)',
        'Modelos de serviço: IaaS, PaaS e SaaS',
        'Disponibilidade, escalabilidade e elasticidade',
        'AWS Trusted Advisor (visão geral)',
        'Agilidade de negócio e time to market na nuvem',
        'Sustentabilidade na nuvem AWS'
    ],
    'security-compliance': [
        'IAM: usuários, grupos, roles e políticas',
        'Modelo de Responsabilidade Compartilhada',
        'Boas práticas de segurança da conta root e MFA',
        'AWS Organizations e Service Control Policies (SCPs)',
        'AWS Shield e proteção contra DDoS',
        'AWS WAF (Web Application Firewall)',
        'Amazon GuardDuty e detecção de ameaças',
        'AWS KMS e criptografia de dados em repouso e em trânsito',
        'AWS Artifact e relatórios de conformidade',
        'AWS Config para auditoria de configurações',
        'Security Groups vs Network ACLs',
        'AWS Secrets Manager e Systems Manager Parameter Store',
        'AWS CloudTrail para auditoria de chamadas de API',
        'Princípio do menor privilégio (least privilege)'
    ],
    'technology-services': [
        'Amazon EC2: tipos de instância e modelos de cobrança',
        'Amazon S3: classes de armazenamento e ciclo de vida',
        'Amazon VPC: sub-redes, gateways e roteamento',
        'Amazon RDS e bancos de dados relacionais gerenciados',
        'Amazon DynamoDB e bancos NoSQL',
        'AWS Lambda e computação serverless',
        'Elastic Load Balancing (ALB, NLB, CLB)',
        'Amazon CloudFront e CDN',
        'Amazon Route 53 e DNS',
        'Amazon ECS, EKS e containers',
        'AWS Auto Scaling',
        'Amazon SNS e Amazon SQS',
        'AWS Elastic Beanstalk',
        'Comparação entre Amazon EFS, EBS e S3',
        'AWS Outposts e serviços híbridos'
    ],
    'billing-pricing-support': [
        'AWS Pricing Calculator',
        'AWS Cost Explorer',
        'AWS Budgets e alertas de custo',
        'Planos de suporte AWS (Basic, Developer, Business, Enterprise)',
        'Modelos de precificação do EC2 (On-Demand, Reserved, Spot, Savings Plans)',
        'AWS Organizations e consolidated billing',
        'AWS Cost and Usage Report',
        'AWS Free Tier',
        'Tags de alocação de custos',
        'AWS Marketplace',
        'TCO (Total Cost of Ownership) e AWS Pricing Calculator'
    ],

    // SAA-C03
    'secure-architectures': [
        'IAM avançado: roles entre contas e federação de identidade',
        'AWS Organizations e SCPs em arquiteturas multi-conta',
        'Segurança de VPC: Security Groups, NACLs, VPC Endpoints e PrivateLink',
        'AWS KMS: chaves gerenciadas pelo cliente vs pela AWS',
        'Criptografia de dados em S3, RDS e EBS',
        'AWS Secrets Manager vs Parameter Store',
        'AWS WAF, Shield Advanced e proteção de aplicações',
        'AWS IAM Identity Center (SSO)',
        'Amazon Cognito para autenticação de aplicações',
        'Proteção de dados em trânsito (TLS e AWS Certificate Manager)',
        'Arquiteturas de rede segura: bastion hosts, NAT Gateway, VPN e Direct Connect'
    ],
    'resilient-architectures': [
        'Multi-AZ vs Multi-Region',
        'Amazon RDS Multi-AZ e Read Replicas',
        'Auto Scaling Groups e health checks',
        'Elastic Load Balancing e failover',
        'Versionamento e replicação cross-region no Amazon S3',
        'Amazon Route 53: roteamento de failover e health checks',
        'Estratégias de disaster recovery (backup/restore, pilot light, warm standby, multi-site)',
        'Amazon SQS para desacoplamento e resiliência',
        'AWS Backup',
        'Amazon DynamoDB Global Tables',
        'RTO e RPO',
        'AWS Step Functions para orquestração resiliente'
    ],
    'high-performing-architectures': [
        'Amazon CloudFront e otimização de entrega de conteúdo',
        'Amazon ElastiCache (Redis e Memcached)',
        'Tipos de volume EBS (gp3, io2, st1, sc1) e desempenho',
        'Amazon S3 Transfer Acceleration e multipart upload',
        'Read Replicas do Amazon RDS para escalabilidade de leitura',
        'Amazon DynamoDB DAX e modos de capacidade',
        'AWS Global Accelerator',
        'Escolha de tipos de instância EC2 por carga de trabalho',
        'Amazon EMR e processamento de big data',
        'Placement groups no EC2',
        'Enhanced Networking e instâncias otimizadas para rede',
        'Otimização de performance em arquiteturas serverless com AWS Lambda'
    ],
    'cost-optimized-architectures': [
        'Modelos de compra do EC2 (On-Demand, Reserved, Spot, Savings Plans)',
        'Classes de armazenamento e políticas de ciclo de vida do Amazon S3',
        'Right-sizing de instâncias e recursos',
        'AWS Compute Optimizer',
        'Auto Scaling para otimização de custos',
        'AWS Cost Explorer e AWS Budgets',
        'Arquiteturas serverless para redução de custos operacionais',
        'Amazon S3 Intelligent-Tiering',
        'Uso de Spot Instances em workloads tolerantes a falhas',
        'AWS Trusted Advisor (verificações de custo)',
        'Custos de transferência de dados entre regiões e Zonas de Disponibilidade'
    ],

    // DVA-C02
    'development-aws-services': [
        'AWS Lambda: handlers, layers, variáveis de ambiente e concorrência',
        'Amazon API Gateway (REST e HTTP APIs)',
        'Amazon DynamoDB: modelagem de dados e índices secundários (GSI/LSI)',
        'AWS SDK e AWS CLI no desenvolvimento de aplicações',
        'Arquiteturas orientadas a eventos com Amazon SQS, SNS e EventBridge',
        'AWS Step Functions',
        'Amazon S3: operações programáticas e presigned URLs',
        'AWS AppSync e GraphQL',
        'Amazon Cognito (user pools e identity pools)',
        'Containers: Amazon ECS, ECR e Fargate',
        'AWS Serverless Application Model (SAM)',
        'Idempotência e tratamento de erros em integrações com serviços AWS'
    ],
    'security': [
        'IAM roles para aplicações (instance profiles do EC2 e execution roles do Lambda)',
        'AWS Secrets Manager e Parameter Store no código da aplicação',
        'AWS KMS: criptografia de dados na aplicação',
        'Amazon Cognito: autenticação e autorização de usuários',
        'Políticas IAM de menor privilégio para desenvolvedores',
        'Criptografia em trânsito (HTTPS/TLS) em APIs',
        'AWS WAF integrado a API Gateway/CloudFront',
        'Gestão segura de credenciais (evitar hardcoding)',
        'AWS Certificate Manager em aplicações',
        'Segurança em pipelines de CI/CD'
    ],
    'deployment': [
        'CI/CD com AWS CodeCommit, CodeBuild, CodeDeploy e CodePipeline',
        'Estratégias de implantação: blue/green, canary e rolling',
        'AWS Elastic Beanstalk: ambientes e configurações',
        'Infraestrutura como código com AWS SAM e AWS CDK',
        'AWS CloudFormation: templates, stacks e change sets',
        'Versionamento e aliases de funções AWS Lambda',
        'Amazon ECS: task definitions, services e deployments',
        'Rollback de implantações com falha',
        'Gestão de ambientes (dev, staging, produção) e parametrização'
    ],
    'troubleshooting-optimization': [
        'Amazon CloudWatch: métricas, alarmes, logs e dashboards',
        'AWS X-Ray para rastreamento distribuído',
        'Depuração de funções Lambda (logs, timeouts e cold starts)',
        'Otimização de performance do DynamoDB (throttling e hot partitions)',
        'Tratamento de erros e retries com backoff exponencial',
        'AWS CloudTrail para diagnóstico de chamadas de API',
        'Monitoramento de filas SQS e dead-letter queues (DLQ)',
        'Otimização de custo e performance do AWS Lambda (memória vs tempo de execução)',
        'Troubleshooting de permissões IAM (erros de Access Denied)',
        'AWS Health Dashboard'
    ]
};

// Seleciona um subconjunto rotativo de tópicos de foco para variar os lotes
function pickFocusTopics(domainId, batchIndex, count) {
    const topics = FOCUS_TOPICS[domainId];
    if (!topics || topics.length === 0) return [];
    const size = Math.min(count, topics.length, 6);
    const start = (batchIndex * size) % topics.length;
    const picked = [];
    for (let i = 0; i < size; i++) {
        picked.push(topics[(start + i) % topics.length]);
    }
    return picked;
}

module.exports = { LEVEL_LABELS, ID_PREFIXES, FOCUS_TOPICS, pickFocusTopics };
