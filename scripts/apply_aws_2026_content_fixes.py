#!/usr/bin/env python3
"""Apply verified 2026 AWS fact corrections to canonical PT exam content.

The July 2025 AWS Free Tier redesign replaced the old generic 12-month-new-account
model used by two CLF-C02 questions. This migration keeps question IDs, domains,
correct indexes and option counts stable while updating only human-language content.

Official reference basis (verified 2026-08-17):
- New customers can choose a Free account plan lasting up to 6 months or until
  Free Tier credits are exhausted, whichever happens first.
- New customers receive USD 100 in credits and can earn up to USD 100 more.
- Eligible Always Free offers remain available within their monthly limits.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIXES = {
    ("clf-c02", "iniciante", "clf-ini-093"): {
        "text": "Um desenvolvedor backend criou uma nova conta AWS em 2026 e quer experimentar serviços sem correr o risco de cobranças inesperadas. Ele escolheu o plano gratuito, que utiliza créditos do AWS Free Tier e pode durar até seis meses ou até os créditos acabarem, o que ocorrer primeiro. Onde o usuário pode acompanhar o saldo de créditos, o período restante do plano gratuito e o uso elegível para evitar surpresas de faturamento?",
        "options": [
            "Na interface de regras do AWS Network Firewall.",
            "No painel de controle do AWS Systems Manager OpsCenter.",
            "No AWS Billing and Cost Management, incluindo os indicadores de Free Tier, créditos e informações do plano da conta.",
            "No catálogo de relatórios e acordos do AWS Artifact."
        ],
        "explanation": "O AWS Billing and Cost Management centraliza as informações do plano gratuito, saldo de créditos, período restante e dados de uso do Free Tier. No modelo atual, novos clientes podem usar um plano gratuito por até seis meses ou até esgotar os créditos, além de ofertas Always Free elegíveis dentro de seus limites.",
        "hint": "O acompanhamento do plano gratuito, créditos e consumo pertence ao painel de faturamento e gerenciamento de custos da conta.",
        "optionRationales": [
            "O AWS Billing and Cost Management centraliza as informações do plano gratuito, saldo de créditos, período restante e dados de uso do Free Tier.",
            "O AWS Artifact armazena relatórios de conformidade e acordos institucionais e não monitora créditos ou consumo do Free Tier.",
            "O Systems Manager OpsCenter centraliza itens de trabalho operacionais e troubleshooting, sem função de acompanhamento de créditos e plano gratuito.",
            "O AWS Network Firewall filtra tráfego de rede e não participa do gerenciamento de faturamento ou créditos da conta."
        ]
    },
    ("clf-c02", "medio", "clf-med-092"): {
        "text": "Um novo cliente AWS quer explorar os serviços em 2026 controlando o risco de cobranças inesperadas. Qual afirmação descreve corretamente o AWS Free Tier atual para novos clientes?",
        "options": [
            "Toda nova conta AWS recebe todos os serviços gratuitamente por exatamente 12 meses, sem limite de créditos.",
            "O uso gratuito é restrito exclusivamente a serviços de computação, armazenamento e rede.",
            "Novos clientes podem escolher um plano gratuito que dura até seis meses ou até os créditos do Free Tier acabarem, recebem créditos iniciais com possibilidade de obter créditos adicionais e também podem utilizar ofertas Always Free elegíveis dentro de seus limites.",
            "O Free Tier é composto apenas por descontos de Reserved Instances, volume e Spot."
        ],
        "explanation": "No AWS Free Tier atual, novos clientes podem escolher um plano gratuito que termina após até seis meses ou quando os créditos forem esgotados, o que ocorrer primeiro. A AWS concede créditos iniciais, permite obter créditos adicionais em atividades elegíveis e mantém ofertas Always Free para serviços participantes dentro de limites mensais.",
        "hint": "O modelo atual combina um plano gratuito temporário baseado em créditos com ofertas Always Free, e não o antigo modelo genérico de 12 meses.",
        "optionRationales": [
            "O programa atual não oferece todos os serviços gratuitamente por doze meses; o novo plano gratuito trabalha com créditos e prazo máximo de seis meses.",
            "O Free Tier inclui serviços de várias categorias e não está limitado apenas a computação, armazenamento e rede.",
            "Novos clientes podem escolher o plano gratuito de até seis meses ou até o esgotamento dos créditos, com créditos iniciais, oportunidades de créditos adicionais e ofertas Always Free elegíveis.",
            "Reserved Instances, Savings Plans, descontos por volume e Spot são mecanismos de preço para uso pago e não definem o AWS Free Tier."
        ]
    }
}


def apply_fix(cert: str, level: str, question_id: str, replacement: dict) -> bool:
    path = ROOT / "data" / "exams" / cert / f"{level}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    question = next((q for q in data.get("questions", []) if q.get("id") == question_id), None)
    if question is None:
        raise RuntimeError(f"Question not found: {cert}/{level}/{question_id}")

    original_structural = {
        "id": question.get("id"),
        "domain": question.get("domain"),
        "correct": question.get("correct"),
        "selectCount": question.get("selectCount"),
        "topics": question.get("topics"),
        "optionCount": len(question.get("options", [])),
    }

    changed = False
    for key, value in replacement.items():
        if question.get(key) != value:
            question[key] = value
            changed = True

    after_structural = {
        "id": question.get("id"),
        "domain": question.get("domain"),
        "correct": question.get("correct"),
        "selectCount": question.get("selectCount"),
        "topics": question.get("topics"),
        "optionCount": len(question.get("options", [])),
    }
    if original_structural != after_structural:
        raise RuntimeError(f"Structural invariant changed while fixing {question_id}: {original_structural} -> {after_structural}")

    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"updated: {path.relative_to(ROOT)}::{question_id}")
    else:
        print(f"current: {path.relative_to(ROOT)}::{question_id}")
    return changed


def main() -> int:
    changed = 0
    for (cert, level, question_id), replacement in FIXES.items():
        changed += int(apply_fix(cert, level, question_id, replacement))
    print(f"AWS 2026 fact corrections complete: {changed} file-question updates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
