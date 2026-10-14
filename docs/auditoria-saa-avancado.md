# Auditoria pedagógica SAA-C03 — Avançado

Escopo: `data/exams/saa-c03/avancado.json` (235 questões). Alterações de conteúdo só após revisão técnica individual, preservando IDs, gabaritos válidos, explicações e compatibilidade com CloudArena.

## Diagnóstico inicial
- 163/235 (69,4%) têm a alternativa correta empatada como a mais longa ou sendo a mais longa.
- 71/235 (30,2%) têm alternativa correta com comprimento >= 2x a média das demais.
- Prioridade de revisão por desproporção: saa-avc-222, saa-avc-120, saa-avc-193, saa-avc-174, saa-avc-114, saa-avc-180, saa-avc-124, saa-avc-122, saa-avc-113, saa-avc-199, saa-avc-215, saa-avc-011.

## Critérios de revisão
1. Manter uma única resposta inequivocamente correta, ou o número explicitamente exigido em questões multirresposta.
2. Distratores tecnicamente plausíveis, próximos em granularidade e no mesmo universo de serviços/decisões da correta.
3. Evitar pistas por comprimento, linguagem absoluta, nível de detalhe ou alternativas absurdas.
4. Enunciados devem especificar restrições suficientes para distinguir serviços AWS parecidos.
5. Preservar explicações didáticas na correção, sem antecipá-las nas alternativas.
6. Validar alinhamento entre opções, índice de resposta, explicações e overlays CloudArena após qualquer mudança.
7. Não alterar o banco médio nem publicar a branch em produção até a aprovação.

## Medição reprodutível
Executar `python3 scripts/audit_saa_advanced.py` para imprimir indicadores e a fila de revisão.

## Checkpoint confirmado em 14/10/2026

**Auditoria em andamento: 102 de 235 questões revisadas. A branch ainda não está pronta para revisão final das 235.**

O histórico anterior mencionava uma revisão local completa que não chegou ao GitHub. Na retomada, a branch remota ainda estava em `1843ab3`. Esse trabalho local não foi contabilizado como concluído. As revisões abaixo foram reconstruídas e salvas incrementalmente na própria branch `audit/advanced-question-bank`.

### Cobertura efetivamente recuperada

- Revisadas individualmente: `saa-avc-001` a `saa-avc-101`, exceto `004`, que já não existia; também `saa-avc-215` e `saa-avc-222`. Total: **102**.
- Revisão inclui enunciado, alternativas, gabarito, explicação, `optionRationales`, `hint`, referências exatas e justificativas `finalBlow` da Arena.
- O registro por ID está em `docs/auditoria-saa-avancado-registro.json`.
- Pendentes: `102–214`, `216–221` e `223–236`. Total: **133**, incluindo as 12 multirresposta `225–236`.
- Próximo lote: `102–126`. Não recomeçar a auditoria nos primeiros IDs.
- Os 235 IDs e os índices de gabarito foram preservados. Correções técnicas foram aplicadas ao conteúdo e às restrições dos cenários, sem mudar os índices.
- Os overlays de outros níveis permanecem semanticamente idênticos aos de `1843ab3`. Os demais bancos não foram alterados.

### Correções técnicas relevantes neste checkpoint

| IDs | Problema corrigido |
| --- | --- |
| 006 | FIFO não garante sozinho efeitos de negócio exatamente uma vez; consumidores precisam de idempotência. |
| 012 | Savings Plans são compromissos de gasto; não equivalem a descontos por faixas de volume. |
| 013 | A SaaS assume uma role no cliente e gera o ExternalId exclusivo; o cenário anterior invertia o fluxo. |
| 014, 067 | Desabilitar KMS não invalida instantaneamente plaintext nem data keys em cache. |
| 026 | ACM não emite certificados de uma CA configurada em modo short-lived; integração com workloads explicitada. |
| 027 | Permissions boundary precisa ser obrigatória e protegida; concessões diretas a sessões têm ressalvas. |
| 030 | Registro de conteúdo delimitado a shell nativo; túneis SSH/port forwarding não têm a mesma cobertura. |
| 035 | Contexto MFA delimitado a credenciais IAM; não generalizado à federação. |
| 040, 065 | Retenção por versão do Object Lock e carência do Vault Lock Compliance esclarecidas. |
| 041 | Snapshot não oferece mínimo downtime absoluto; janela de suspensão de escritas explicitada. |
| 043 | DNS Firewall associa regras à VPC, não uma allowlist independente diretamente à sub-rede. |
| 047, 051, 054, 099, 215 | Removidas ambiguidades com alternativas também defensáveis, explicitando restrições arquiteturais. |
| 051 | Acesso direto cross-account exige resource policy, IAM da consumidora e autorização KMS. |
| 069 | Entrega de logs ALB por service principal usa SourceOrgId/SourceArn; PrincipalOrgID não representa essa origem. |
| 071 | Expiração de sessão de conta não força novo MFA se a sessão do portal continua válida. |
| 079 | CRR não replica configuração/transições Lifecycle; destino precisa de configuração própria. |
| 090 | Tiers 0/1 de réplicas Serverless v2 acompanham capacidade do writer; não há independência universal. |
| 095, 096 | Readiness checks não comprovam capacidade real; FIS não torna toda ação de falha reversível. |
| 098 | Condições/transações regionais em MREC não criam exclusão mútua global; ownership/modelagem corrigidos. |
| 100 | Failover típico não é garantia absoluta de menos de 35 segundos. |
| 101 | Corrigida premissa de MSK provisionado em uma única AZ; RF, ISR e acks agora coerentes. |
| 215 | A explicação de Elastic Resize ainda descrevia aumento permanente; corrigida junto ao cenário. |

### Validação executada

| Verificação | Resultado |
| --- | --- |
| `python3 scripts/validate_banks.py` | 0 erros; 443 avisos preexistentes fora deste escopo. |
| `python3 scripts/validate_arena.py` | Todos os overlays válidos; eliminadas as 120 divergências iniciais de referências/gabarito. |
| `python3 scripts/validate_saa_advanced_audit.py` | 102 revisadas com referências, gabarito, reasonWrong, rationales e explicações consistentes. |
| `python3 scripts/validate_saa_advanced_audit.py --require-complete` | Retorna 2 intencionalmente: faltam 133 revisões. Não é um selo de conclusão. |
| `git diff --check` | Sem erros de whitespace. |
| Comparação com `1843ab3` | IDs e gabaritos preservados; nenhuma alternativa/enunciado duplicado; questões fora do registro sem alteração; overlays fora do avançado preservados. |

Esses testes são estruturais. A avaliação técnica e pedagógica foi individual; os scripts não demonstram, sozinhos, a unicidade de uma resposta. Ainda falta a conferência final do fluxo executável da Arena e das questões multirresposta. Nenhum merge na main ou comando de deploy foi executado.

### Indicadores parciais de tamanho

Recorte reprodutível: somente as **223 questões de resposta única**, medindo caracteres e incluindo empates no critério de maior alternativa. Não comparar diretamente estes números com o diagnóstico histórico de 235 questões sem igualar o recorte e a versão.

| Indicador | Início desta retomada (`1843ab3`) | Checkpoint atual |
| --- | ---: | ---: |
| Correta é a maior ou empata como maior | 149 | 119 |
| Correta tem pelo menos 2x a média das incorretas | 65 | 38 |

Os valores ainda incluem 121 questões de resposta única pendentes. O tamanho é um sinal de revisão, não um objetivo para preenchimento artificial de alternativas.

### Referências oficiais utilizadas nas correções críticas

- [ExternalId e acesso de terceiros](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html)
- [Desabilitar chaves KMS e efeitos sobre data keys](https://docs.aws.amazon.com/kms/latest/developerguide/enabling-keys.html)
- [Modos de CA e certificados short-lived](https://docs.aws.amazon.com/privateca/latest/userguide/short-lived-certificates.html)
- [Chaves globais de condição IAM e MFA](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html)
- [Secrets Manager cross-account](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_examples_cross.html)
- [Associação DNS Firewall à VPC](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-vpc-associating-rule-group.html)
- [Logs ALB: SourceOrgId e SourceArn](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html)
- [Sessões e permission sets](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsets.html)
- [Vault Lock e carência](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html)
- [Cobertura do Network Access Analyzer](https://docs.aws.amazon.com/vpc/latest/network-access-analyzer/how-network-access-analyzer-works.html)
- [O que o S3 replica](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-what-is-isnot-replicated.html)
- [Escala de réplicas Aurora Serverless v2](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html)
- [Modos de consistência das Global Tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html)
- [Configuração MSK: replication factor, ISR e acks](https://docs.aws.amazon.com/msk/latest/developerguide/msk-configuration-properties.html)
