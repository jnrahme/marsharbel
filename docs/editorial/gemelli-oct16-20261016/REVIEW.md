# Gemelli October 16 news-value update

Audience benefit: replace yesterday's health update with today's source-backed report, keeping translated home summaries current. Intended outcome is accurate reading and source follow-through. No measured traffic or growth result is claimed.

Source: https://www.vaticannews.va/en/pope/news/2026-10/pope-leo-xiv-day-four-health-update-gemelli-hospital.html

Scope: six existing English news-desk values, exact source href and datetime, generated source-page blocks, stable keyed news/home bindings and reviewed translation packet. Existing film lead, Gemelli anchor, Aoun/LBC paragraph, photo and licence stay unchanged.

Translations: all 11 supplied locale deltas (66 values) are retained at locales/gemelli-oct16-translations.json. Existing render destinations remain home EN plus ar/de/es/fr/hi/it/pl/pt/ru/th and news EN/AR. This is not a new locale-page release. zh-Hans values are retained as intake only.

Local checks:
- News desk: 28 tests pass; generation check passes.
- Mirror structure: 6 pass; locale mirror policy: 7 pass; exact-master: 5 pass.
- Full international build and check pass (12 languages, 44 guides, 11 homes).
- Source build for touched index/news: 2 pages, 0 stale. Full source check exceeded the local 100-second timeout, not an assertion failure; full CI is required.
- International generation needed a second pass for manifest source-hash ordering; subsequent full check passes.
- I18n policy initially failed because the isolated worktree lacked acorn. Existing project node_modules linked locally; rerun passes. No dependency or baseline changed.
- Rendered 13 affected HTML destinations at 390/768/1280, zero overflow and JS exceptions. Corrected initial screenshot alignment from section-bottom to actual Gemelli card, then inspected EN/AR mobile and desktop pixels.
- Two production-only Arabic v3 fonts are absent locally, producing 404s on AR home/news. Exact live font URLs return 200 font/woff2. Live font decoding and rendered checks remain required after deployment.

No main merge, automatic-promotion action, locale registry expansion, photo replacement or test weakening. Independent Scrum ruling, complete real CI, main-agent release decision, live byte/user-path/pixel verification and overwrite checks remain mandatory.

## CI correction, 13:29 ET
Exact-head CI on 2cbb8bf9 found omitted generated derivatives: feed.xml and 11 search-index locale excerpts. Existing feed and search generators were run without changes to assertions or build configuration. Feed check, five feed tests and search-index complete check now pass (410 pages, 12 locales, zero stale excerpts). This new head requires fresh independent review and full CI; the earlier review does not cover it automatically.
