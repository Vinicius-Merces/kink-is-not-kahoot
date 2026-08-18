# CloudPath i18n Architecture

## Goal

Add English support without rewriting CloudPath, duplicating pages or degrading the current premium UI. Portuguese remains the source locale while English is introduced incrementally behind a shared runtime and validation contract.

Narration assets are intentionally outside this migration until a later dedicated phase.

## Current architecture

CloudPath remains a Vanilla JS application with Node/Express/Socket.IO and Firebase. Internationalization is layered onto the existing product rather than used as a reason to migrate frameworks.

### Runtime

`js/i18n.js` owns:

- supported locales: `pt-BR` and `en`
- persistent locale selection
- `?lang=` override support
- Portuguese fallback
- `<html lang>` updates
- semantic translation keys
- text, placeholder, `aria-label` and `title` translation
- compact PT/EN navigation switcher
- modular catalog composition through deep merge
- page adapter registration

### Bootstraps

There are two guarded entry points:

- `js/branding.js` boots i18n on the landing/home surface
- `js/nav-menu.js` boots i18n on internal pages that share the primary navigation

Both use guards so a page may safely contain both entry points without loading the runtime twice.

### Catalog layout

Catalogs are split by product surface instead of growing into a single monolithic JSON file:

```text
locales/
├── pt-BR/
│   ├── ui.json
│   └── simulator.json
└── en/
    ├── ui.json
    └── simulator.json
```

`ui.json` contains shared UI/home/navigation vocabulary. `simulator.json` contains the practice-exam interface. The runtime deep-merges the files for the active locale.

The validator requires each supported locale to expose the same catalog files and the same final flattened key set.

## Implemented surfaces

### Home

`js/i18n-home.js` maps the existing premium landing DOM to semantic keys without rebuilding the markup.

Covered surfaces include:

- loading state
- hero and status badges
- AWS globe accessibility copy and legend
- teacher/student cards
- room-code form
- metrics
- study/exam banners
- CloudArena marketing/demo section
- feature cards
- About section
- login modal
- metadata
- footer

Decorative DOM elements are preserved rather than replaced. The adapter is also compatible with the separate Orbital Studio creator-credit change: if that link is present, only the surrounding creator copy is localized and the link remains intact.

### Shared navigation

`js/i18n-shared.js` covers:

- navigation landmark label
- mobile menu label and expanded state
- Study / Quizzes / Performance groups
- item labels and hints
- logout
- internal-page language switcher placement

### Practice exams

`js/i18n-simulados.js` begins the interface/content separation for Simulados.

Translated interface surfaces include:

- page heading and mode selectors
- configuration labels
- question-count controls
- Exam Mode / Study Mode controls
- real-exam controls
- pause/review/report/navigation actions
- option-layout controls
- result-section headings
- finish confirmation
- live teacher-room shell
- dynamic progress labels, review marks and multiple-answer hints

The adapter preserves live counters and uses idempotent DOM updates so MutationObserver-driven localization cannot translate itself in a loop.

Question text, answer options, explanations and domain/topic names remain Portuguese until the exam-bank content migration. This is deliberate: UI translation and study-content translation are separate layers.

## Accessibility improvements included

The home login modal now gains:

- Escape to close
- keyboard focus trapping
- focus placement when opened
- focus restoration for Escape-driven close

Locale switching also updates accessible navigation and control labels.

## CloudArena stable identity contract

The existing CloudArena overlay still links answer metadata by literal `matchText`, which prevents safe content translation.

The migration contract is:

```text
<questionId>:option:<index>
```

Example:

```text
clf-ini-001:option:2
```

`scripts/prepare_arena_option_ids.py` validates and can enrich current overlays with stable `optionId` values while retaining `matchText` during the transition.

The server resolver has not yet been switched away from `matchText`; that will happen after current overlays are safely enriched and validated.

## CI contract

`.github/workflows/validate-banks.yml` now validates:

- JavaScript syntax for the i18n runtime/adapters and internal navigation bootstrap
- existing question banks
- existing CloudArena overlays
- CloudArena stable option-ID contract
- PT/EN catalog-file parity
- PT/EN translation-key parity
- non-empty translation leaves
- frontend references to unknown i18n keys

This turns missing locale work into a build failure instead of a silent runtime fallback.

## Narration boundary

`assets/narracao/**` is excluded from this migration phase.

The English UI may explicitly communicate that current narrated chapters are in Portuguese. No narration audio is translated, regenerated or replaced in this branch.

## Next slices

1. Finish Simulados dynamic runtime messages and result chrome without translating question-bank content yet.
2. Add locale-aware exam-bank schema/parity validation.
3. Pilot translated exam content with CLF-C02 while preserving question IDs, correct indexes and domain IDs.
4. Enrich CloudArena overlays with stable option IDs and change server resolution from `matchText` to `optionId`.
5. Translate CloudArena UI/metadata against stable IDs.
6. Extract long study-track content from giant HTML files into locale-specific content sources.
7. Add indexable English routes/metadata/hreflang after the bilingual product flow is stable.

## Non-goals

This work does not:

- migrate CloudPath to React, Next.js or another framework
- redesign the current premium interface
- duplicate pages into `*-en.html`
- translate narration assets
- mass-translate question banks before identity/parity safeguards exist
- remove current Portuguese content as the source locale
