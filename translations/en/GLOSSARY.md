# CloudPath English terminology glossary

This glossary is the translation contract for CloudPath study content. It keeps terminology consistent across exam banks, CloudArena, study guides and UI.

AWS product and framework names should normally remain in their official English form rather than being translated creatively.

## Core cloud terms

| PT source concept | CloudPath EN standard |
|---|---|
| computação em nuvem | cloud computing |
| nuvem pública | public cloud |
| nuvem privada | private cloud |
| nuvem híbrida | hybrid cloud |
| agilidade | agility |
| elasticidade | elasticity |
| escalabilidade | scalability |
| alta disponibilidade | high availability |
| tolerância a falhas | fault tolerance |
| economia de escala | economies of scale |
| despesa de capital | capital expenditure (CapEx) |
| despesa operacional | operating expense (OpEx) |
| pagamento conforme o uso | pay-as-you-go |
| sob demanda | on demand |

## AWS global infrastructure

| PT source concept | CloudPath EN standard |
|---|---|
| Região AWS | AWS Region |
| Zona de Disponibilidade | Availability Zone |
| Localização de Borda | Edge Location |
| ponto de presença | point of presence |
| Local Zone | Local Zone |
| residência de dados | data residency |

Capitalize official AWS infrastructure terms when referring to AWS concepts: `Region`, `Availability Zone`, `Edge Location`.

## Security and identity

| PT source concept | CloudPath EN standard |
|---|---|
| Modelo de Responsabilidade Compartilhada | AWS Shared Responsibility Model |
| segurança da nuvem | security OF the cloud |
| segurança na nuvem | security IN the cloud |
| princípio do menor privilégio | principle of least privilege |
| autenticação multifator | multi-factor authentication (MFA) |
| usuário root | root user |
| função do IAM | IAM role |
| usuário do IAM | IAM user |
| grupo do IAM | IAM group |
| política de controle de serviço | Service Control Policy (SCP) |
| política baseada em recurso | resource-based policy |
| limite de permissões | permissions boundary |

Prefer `IAM role`, not `IAM Role`, in prose unless it begins a title/label.

## AWS Well-Architected Framework

Official pillar names:

- Operational Excellence
- Security
- Reliability
- Performance Efficiency
- Cost Optimization
- Sustainability

Use `AWS Well-Architected Framework` in full on first mention when natural. Keep official pillar capitalization.

## AWS Cloud Adoption Framework

Use `AWS Cloud Adoption Framework (AWS CAF)` on first mention when natural.

Official perspective names:

- Business
- People
- Governance
- Platform
- Security
- Operations

## Migration strategies

| PT source concept | CloudPath EN standard |
|---|---|
| Rehospedar | Rehost / Rehosting |
| Lift-and-Shift | Lift-and-Shift |
| Replataformar | Replatform / Replatforming |
| Refatorar / Rearquitetar | Refactor / Re-architect |
| Recomprar | Repurchase / Repurchasing |
| Reter | Retain / Retaining |
| Retirar | Retire / Retiring |

When the source explicitly names the strategy, prefer forms such as `Rehosting (Lift-and-Shift)` to preserve exam-recognition vocabulary.

## Service models

- Infrastructure as a Service (IaaS)
- Platform as a Service (PaaS)
- Software as a Service (SaaS)
- Function as a Service (FaaS)

Do not expand an acronym differently from its industry-standard name.

## Product names

Keep official product capitalization and spelling, including:

- Amazon EC2
- Amazon S3
- Amazon VPC
- Amazon RDS
- Amazon DynamoDB
- Amazon CloudFront
- Amazon Route 53
- Amazon GuardDuty
- AWS IAM / AWS Identity and Access Management
- AWS CloudTrail
- Amazon CloudWatch
- AWS WAF
- AWS Shield Standard
- AWS Shield Advanced
- AWS Organizations
- AWS Trusted Advisor
- AWS Pricing Calculator
- AWS Cost Explorer
- AWS Budgets
- AWS Compute Optimizer
- AWS Systems Manager
- AWS KMS
- AWS Secrets Manager

## Editorial rules

1. Preserve the technical intent of the Portuguese source; do not simplify away exam-relevant qualifiers.
2. Preserve option order. The structural builder controls answer identity and the correct index.
3. Do not add or remove caveats merely to make English shorter.
4. Prefer natural professional English over literal Portuguese syntax.
5. Keep AWS service names official and unchanged.
6. Use `practice exam` for `simulado` in product/UI prose. Use `exam` when discussing the real AWS certification exam itself.
7. Use `question bank` for `banco de questões`.
8. Use `answer option` for `alternativa` when clarity requires it.
9. Use `explanation` for the general answer explanation.
10. Preserve staged `optionRationales` order exactly as the canonical source; do not infer or repair source ordering during translation.

## Narration boundary

This glossary does not authorize translation or regeneration of prerecorded narration. Narration remains a separate future localization phase.
