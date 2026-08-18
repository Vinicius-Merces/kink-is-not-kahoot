# English exam banks

This directory contains only **complete, buildable English exam banks**.

Portuguese remains the canonical source under:

```text
data/exams/<certification>/<level>.json
```

Final English banks live under:

```text
data/exams-en/<certification>/<level>.json
```

Incomplete translations must **not** be placed here.

## Staged translation workflow

Large banks are translated safely in batches under:

```text
translations/en/<certification>/<level>/*.json
```

Example for CLF-C02 Beginner:

```text
translations/en/clf-c02/domains.json
translations/en/clf-c02/iniciante/001-010.json
translations/en/clf-c02/iniciante/011-020.json
translations/en/clf-c02/iniciante/021-030.json
```

Each batch is keyed by stable question ID and may contain human-language fields only:

- `text`
- `options`
- `explanation`
- `hint`, when present in the PT source
- `optionRationales`, when present in the PT source

Structural fields such as `correct`, `domain`, `topics`, `selectCount` and question IDs are intentionally absent from staging batches. The builder always copies those fields from the canonical PT bank.

Validate all current staging targets with:

```bash
python3 scripts/validate_exam_translation_staging.py
```

Check one target and print its current coverage with:

```bash
python3 scripts/build_exam_translation.py clf-c02 iniciante --check
```

A partial staging set is valid, but it cannot produce a final bank.

When coverage reaches 100%, require completeness first:

```bash
python3 scripts/build_exam_translation.py clf-c02 iniciante --require-complete
```

Then build the final ready bank:

```bash
python3 scripts/build_exam_translation.py clf-c02 iniciante --write
```

Only `--write` creates:

```text
data/exams-en/clf-c02/iniciante.json
```

and only when every canonical question has a structurally valid English translation.

## Final-bank invariants

A completed English bank may change human-language content only. It must preserve:

- question `id`
- question count
- domain `id`
- each question's `domain`
- `correct` indexes
- `selectCount`
- `topics`
- number and order of answer options
- non-name domain metadata

Domain display names may be translated through the staged domain map.

Validate built EN banks against the PT source with:

```bash
python3 scripts/validate_exam_locale_parity.py
```

Once a certification is considered complete, CI can require all three levels and `status=ready` with:

```bash
python3 scripts/validate_exam_locale_parity.py --require-cert clf-c02
```

## Content-quality boundary

The canonical banks contain some `optionRationales` arrays whose ordering may not visually correspond to the `correct` index. The current Simulados runtime returns question text, answer options, the correct index and the general explanation; it does not currently use `optionRationales` in the answer-check/result flow.

For that reason, translation staging preserves the source `optionRationales` order instead of silently reordering editorial metadata during localization. Any cleanup of that source content should be a separate, explicit content-quality change.

## Narration

Do not place narration files here. `assets/narracao/**` remains a separate future localization phase.
