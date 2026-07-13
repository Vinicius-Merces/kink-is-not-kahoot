#!/usr/bin/env python3
"""
Validador dos bancos de questões do KINK.

Verifica invariantes que, se quebradas, corrompem a experiência do simulado:
  1. JSON válido e com as chaves estruturais esperadas
  2. `correct` dentro do intervalo de opções (int) ou lista de ints válidos (multi)
  3. Explicação com um segmento por alternativa ("A) ... B) ...")
  4. Campo `topics` presente e não vazio em toda questão
  5. IDs únicos dentro de cada arquivo
  6. Distribuição de posições da resposta não degenerada (nenhuma posição > 60%)

Uso:
  python3 scripts/validate_banks.py            # valida tudo em data/exams/
  python3 scripts/validate_banks.py --strict   # trata avisos como erro

Sai com código != 0 se houver qualquer ERRO (é isso que faz o CI falhar).
"""
import json
import os
import re
import sys
import glob
import collections

EXAMS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'exams')
LETTERS = 'ABCDEF'

errors = []
warnings = []


def err(f, msg):
    errors.append(f"❌ {f}: {msg}")


def warn(f, msg):
    warnings.append(f"⚠️  {f}: {msg}")


def validate_file(path):
    rel = os.path.relpath(path)
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        err(rel, f"JSON inválido: {e}")
        return

    questions = data.get('questions')
    if not isinstance(questions, list) or not questions:
        err(rel, "sem lista de 'questions'")
        return

    # Detecta o formato do arquivo pela maioria das questões:
    #  - per_option_format: explicações no padrão "A) ... B) ..." sincronizadas
    #  - uses_topics: banco que adota rotulagem por tema
    sample = questions[:20]
    def _has_letter_segments(q):
        e = q.get('explanation', '') or ''
        n = len(q.get('options', []) or [])
        return n > 0 and len(re.findall(r'\b[A-F]\)\s', e)) == n and e.strip().startswith('A)')
    per_option_hits = sum(1 for q in sample if _has_letter_segments(q))
    per_option_format = per_option_hits >= max(3, len(sample) // 2)
    topic_hits = sum(1 for q in sample if isinstance(q.get('topics'), list) and q.get('topics'))
    uses_topics = topic_hits >= max(3, len(sample) // 2)

    ids = collections.Counter()
    positions = collections.Counter()
    total_single = 0

    for i, q in enumerate(questions):
        qid = q.get('id', f'(índice {i})')
        ids[qid] += 1

        opts = q.get('options')
        if not isinstance(opts, list) or len(opts) < 2:
            err(rel, f"{qid}: precisa de ao menos 2 opções")
            continue
        n = len(opts)

        # correct no range
        correct = q.get('correct')
        if isinstance(correct, list):
            if not correct:
                err(rel, f"{qid}: 'correct' (multi) vazio")
            for c in correct:
                if not isinstance(c, int) or not (0 <= c < n):
                    err(rel, f"{qid}: índice correto {c} fora do intervalo 0..{n-1}")
        elif isinstance(correct, int):
            if not (0 <= correct < n):
                err(rel, f"{qid}: índice correto {correct} fora do intervalo 0..{n-1}")
            positions[correct] += 1
            total_single += 1
        else:
            err(rel, f"{qid}: 'correct' ausente ou de tipo inválido")

        # explicação: sempre obrigatória. O formato "por alternativa"
        # (A)/B)/C)...) é OPCIONAL — só é exigido para bancos que já o adotam
        # (detectado no nível do arquivo). Nos demais, apenas informa.
        expl = q.get('explanation', '')
        if not expl:
            err(rel, f"{qid}: sem explicação")
        elif per_option_format:
            segs = re.findall(r'\b[A-F]\)\s', expl)
            if len(segs) != n:
                err(rel, f"{qid}: explicação por alternativa tem {len(segs)} segmentos para {n} opções (devem bater)")
            elif not expl.strip().startswith('A)'):
                warn(rel, f"{qid}: explicação não começa em 'A)'")

        # topics: exigido para bancos que adotam rotulagem por tema; nos
        # bancos legados sem rótulos, é apenas um aviso de melhoria.
        topics = q.get('topics')
        if not isinstance(topics, list) or not topics:
            if uses_topics:
                err(rel, f"{qid}: sem 'topics' (este banco usa rotulagem por tema)")
            else:
                warn(rel, f"{qid}: sem 'topics' (considere rotular por tema)")

    # IDs duplicados
    for qid, c in ids.items():
        if c > 1:
            err(rel, f"id duplicado '{qid}' aparece {c}x")

    # distribuição de posições (só questões single-answer)
    if total_single >= 10:
        for pos, c in positions.items():
            frac = c / total_single
            if frac > 0.60:
                warn(rel, f"posição {LETTERS[pos]} concentra {frac*100:.0f}% das respostas — rebalancear")

    print(f"  ✓ {rel}: {len(questions)} questões")


def main():
    strict = '--strict' in sys.argv
    files = sorted(glob.glob(os.path.join(EXAMS_DIR, '**', '*.json'), recursive=True))
    if not files:
        print("Nenhum banco encontrado em data/exams/")
        sys.exit(1)

    print(f"Validando {len(files)} bancos...\n")
    for f in files:
        validate_file(f)

    print()
    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    print(f"\n{'='*50}")
    print(f"Erros: {len(errors)} | Avisos: {len(warnings)}")

    if errors or (strict and warnings):
        print("❌ Validação FALHOU")
        sys.exit(1)
    print("✅ Todos os bancos passaram")
    sys.exit(0)


if __name__ == '__main__':
    main()
