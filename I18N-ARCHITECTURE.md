# CloudPath internationalization architecture

## Goal

Make CloudPath natively bilingual without duplicating pages or changing the current premium visual language.

Initial locales:

- `pt-BR` - current source language and fallback
- `en` - English product version

Narration assets are explicitly outside this migration phase. Existing files under `assets/narracao/` remain untouched until a dedicated audio/TTS phase.

## Runtime

`js/i18n.js` is the single locale runtime.

It provides:

- persistent locale selection through `cloudpath_locale_v1`
- optional URL override with `?lang=pt-BR` or `?lang=en`
- fallback to `pt-BR`
- automatic `<html lang>` updates
- metadata translation for the main product surface
- key-based translation through `data-i18n`
- placeholder, `aria-label` and `title` translation
- `cloudpath:i18nready` and `cloudpath:localechange` events
- a compact PT/EN selector mounted in the existing navigation

The runtime is bootstrapped by `js/branding.js`, which is already shared by the product. This avoids adding a new script tag manually to every page during Phase 0.

## Catalogs

UI catalogs live in:

```text
locales/
├── pt-BR/
│   └── ui.json
└── en/
    └── ui.json
```

All locale catalogs must contain exactly the same leaf keys. CI enforces this with `scripts/validate_i18n.py`.

Example:

```html
<button data-i18n="common.login">Entrar</button>
<input data-i18n-placeholder="quiz.roomCode" placeholder="Código da sala">
<button data-i18n-aria-label="common.close" aria-label="Fechar">×</button>
```

No runtime text-search or Portuguese-string replacement should be introduced. Every migrated string gets an explicit semantic key.

## Content migration order

1. Shared navigation, authentication, modals and common UI
2. Home page
3. Progress and quiz management surfaces
4. Practice exam shell
5. CloudArena UI shell
6. Exam question banks and explanations
7. Study guides
8. Narration and TTS behavior in a separate project phase

This order keeps the current product functional while large content sets are translated in controlled batches.

## Exam data contract

Translated question banks must preserve these invariants across locales:

- same certification ID
- same question ID
- same domain ID
- same difficulty bucket
- same correct option index during the transition
- same number and ordering of options during the transition

A translated question must never change the answer key.

Future target layout:

```text
data/exams/
├── pt-BR/
│   ├── clf-c02/
│   ├── saa-c03/
│   ├── dva-c02/
│   └── dea-c01/
└── en/
    ├── clf-c02/
    ├── saa-c03/
    ├── dva-c02/
    └── dea-c01/
```

The current `data/exams/<cert>/` layout remains the production source until the locale-aware server loader is introduced.

## CloudArena option identity

### Current risk

CloudArena overlays currently bind metadata to the Portuguese option text through `matchText`.

That relationship is language-dependent and must not be used as the final identity mechanism.

### Stable migration ID

Phase 0 defines:

```text
<questionId>:option:<zero-based-index>
```

Example:

```text
clf-ini-001:option:2
```

`scripts/prepare_arena_option_ids.py` validates the current relationship and can enrich overlay files while preserving backwards compatibility:

```bash
python3 scripts/prepare_arena_option_ids.py --write
```

During the transition an overlay option may contain both fields:

```json
{
  "optionId": "clf-ini-001:option:2",
  "matchText": "Troca de despesas de capital (CapEx) por despesas variáveis (OpEx)",
  "stage": "correct"
}
```

`matchText` must only be removed after the server endpoint resolves CloudArena options by stable ID/index and PT/EN bank parity is covered by CI.

## Validation

Local command:

```bash
npm run validate
```

Individual checks:

```bash
npm run validate:i18n
npm run validate:arena-ids
```

GitHub Actions now validates:

- question banks
- current CloudArena overlays
- stable option-ID migration contract
- PT/EN UI catalog parity

## Non-goals for Phase 0

Phase 0 does not:

- translate narration audio
- duplicate HTML pages
- change framework
- redesign the current UI
- translate the full exam bank yet
- translate the large study-guide documents yet
- remove `matchText` from production before the server migration is ready

The purpose of this phase is to make the English rollout safe before touching the mass content.
