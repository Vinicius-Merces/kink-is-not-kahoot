# English exam banks

This directory is reserved for translated CloudPath exam content.

Portuguese remains the canonical source under:

```text
data/exams/<certification>/<level>.json
```

English banks are introduced incrementally under:

```text
data/exams-en/<certification>/<level>.json
```

Example:

```text
data/exams/clf-c02/iniciante.json       # canonical PT source
data/exams-en/clf-c02/iniciante.json    # English translation
```

## Translation invariants

A translation may change human-language content only. It must preserve:

- question `id`
- question count
- domain `id`
- each question's `domain`
- `correct` indexes
- `selectCount`
- `topics`
- number and order of answer options
- non-name domain metadata

Question text, option text, explanations and domain display names may be translated.

Run:

```bash
python3 scripts/validate_exam_locale_parity.py
```

Once a certification is considered complete, CI can require all three levels with:

```bash
python3 scripts/validate_exam_locale_parity.py --require-cert clf-c02
```

Do not place narration files here. Narration remains a separate future localization phase.
