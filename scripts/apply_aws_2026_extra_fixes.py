#!/usr/bin/env python3
"""Additional verified AWS 2026 content corrections.

Verified against current AWS Billing/Free Tier, Lambda, DynamoDB and AWS Budgets
primary documentation on 2026-08-17. Structural question fields are never changed.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIXES = {
    ("clf-c02", "avancado", "clf-avc-234"): {
        "text": "Uma empresa criou uma nova conta AWS após a mudança do AWS Free Tier de julho de 2025. Mesmo quando o plano gratuito de até seis meses termina ou os créditos são consumidos, alguns serviços continuam oferecendo limites mensais gratuitos. Qual alternativa descreve corretamente esse benefício?",
        "options": [
            "Todos os serviços de infraestrutura tornam-se permanentemente gratuitos depois que o plano gratuito termina.",
            "Ofertas Always Free continuam disponíveis dentro dos limites mensais definidos por serviço; por exemplo, AWS Lambda e Amazon DynamoDB mantêm franquias mensais gratuitas elegíveis.",
            "O plano gratuito reinicia automaticamente a cada ano e concede novamente seis meses sem cobrança.",
            "Após o fim dos créditos, a AWS converte automaticamente a conta para Savings Plans sem custo."
        ],
        "explanation": "O AWS Free Tier atual combina créditos e um plano gratuito de até seis meses para novos clientes com mais de 30 serviços que possuem ofertas Always Free. Essas ofertas continuam disponíveis dentro dos limites mensais específicos de cada serviço.",
        "hint": "Diferencie o plano temporário baseado em créditos das ofertas Always Free com franquias mensais contínuas.",
        "optionRationales": [
            "Serviços de infraestrutura não se tornam ilimitadamente gratuitos; uso fora de ofertas ou créditos aplicáveis segue a cobrança padrão.",
            "Ofertas Always Free permanecem disponíveis dentro de limites mensais definidos por serviço, separadamente do prazo do plano gratuito.",
            "O plano gratuito não reinicia anualmente; ele termina após até seis meses ou quando os créditos são consumidos, o que ocorrer primeiro.",
            "Savings Plans são compromissos de uso pagos e não são concedidos automaticamente quando os créditos terminam."
        ]
    },
    ("clf-c02", "avancado", "clf-avc-238"): {
        "text": "Uma startup escolheu o plano gratuito da AWS e quer ser avisada caso comece a gerar gastos além dos limites de uso gratuito ou dos créditos disponíveis. No AWS Budgets, qual template simplificado é apropriado para receber um alerta assim que houver gasto cobrável?",
        "options": [
            "Zero spend budget (orçamento de gasto zero).",
            "Savings Plans coverage budget.",
            "Reserved Instance utilization budget.",
            "Data transfer budget obrigatório para ativar o plano gratuito."
        ],
        "explanation": "O AWS Budgets oferece o template simplificado Zero spend budget para notificar quando os gastos ultrapassam os limites gratuitos aplicáveis. Ele complementa o acompanhamento de créditos e do plano gratuito no Billing and Cost Management.",
        "hint": "Procure o template cujo objetivo é avisar quando o gasto deixa de ser zero.",
        "optionRationales": [
            "O Zero spend budget é o template atual apropriado para alertar quando surgem gastos além dos limites gratuitos aplicáveis.",
            "Budgets de cobertura de Savings Plans acompanham cobertura de compromissos e não o saldo do Free Tier.",
            "Budgets de utilização de Reserved Instances acompanham utilização de reservas e não créditos do plano gratuito.",
            "Não existe exigência de criar um orçamento de transferência de dados para ativar o plano gratuito."
        ]
    },
    ("saa-c03", "iniciante", "saa-ini-276"): {
        "text": "Uma empresa está começando a usar AWS em 2026 e quer entender as ofertas Always Free, que continuam disponíveis dentro de limites mensais mesmo depois que o plano gratuito temporário ou os créditos iniciais terminam. Qual alternativa apresenta exemplos atuais desse benefício?",
        "options": [
            "Todos os serviços AWS ficam gratuitos sem limite enquanto a conta permanecer no plano gratuito.",
            "AWS Lambda oferece mensalmente 1 milhão de solicitações e 400.000 GB-segundos de computação gratuitos; o Amazon DynamoDB mantém 25 GB de armazenamento e 25 WCUs e 25 RCUs provisionadas dentro do nível gratuito.",
            "Qualquer instância EC2, qualquer banco RDS e qualquer volume S3 permanecem ilimitadamente gratuitos para sempre.",
            "As ofertas Always Free terminam no instante em que os créditos iniciais chegam a zero."
        ],
        "explanation": "A AWS mantém mais de 30 serviços com ofertas Always Free dentro de limites mensais. Entre os exemplos atuais, Lambda inclui 1 milhão de solicitações e 400.000 GB-segundos por mês, e DynamoDB Standard inclui 25 GB de armazenamento e 25 WCUs e 25 RCUs provisionadas.",
        "hint": "Always Free é uma franquia mensal contínua para serviços elegíveis, separada do prazo do plano gratuito e do saldo de créditos.",
        "optionRationales": [
            "O AWS Free Tier não torna todos os serviços ilimitadamente gratuitos; cada oferta tem regras e limites próprios.",
            "Lambda e DynamoDB possuem ofertas mensais gratuitas atuais e documentadas dentro de limites específicos.",
            "EC2, RDS e S3 não se tornam ilimitadamente gratuitos para sempre; uso fora das ofertas aplicáveis é cobrado.",
            "As ofertas Always Free são separadas do saldo de créditos do novo cliente e podem continuar disponíveis dentro de seus limites."
        ]
    }
}


def apply_one(cert, level, qid, replacement):
    path = ROOT / "data" / "exams" / cert / f"{level}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    q = next((item for item in data.get("questions", []) if item.get("id") == qid), None)
    if q is None:
        raise RuntimeError(f"Question not found: {cert}/{level}/{qid}")
    before = (q.get("id"), q.get("domain"), q.get("correct"), q.get("selectCount"), q.get("topics"), len(q.get("options", [])))
    changed = False
    for key, value in replacement.items():
        if q.get(key) != value:
            q[key] = value
            changed = True
    after = (q.get("id"), q.get("domain"), q.get("correct"), q.get("selectCount"), q.get("topics"), len(q.get("options", [])))
    if before != after:
        raise RuntimeError(f"Structural invariant changed while fixing {qid}")
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"updated: {path.relative_to(ROOT)}::{qid}")
    else:
        print(f"current: {path.relative_to(ROOT)}::{qid}")


def main():
    for key, replacement in FIXES.items():
        apply_one(*key, replacement)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
