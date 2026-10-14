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
