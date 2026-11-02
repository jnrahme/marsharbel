# 2026-11-02 Commemoration of the Faithful Departed - implementation review

Status: RECONSTRUCTED 2026-10-30 against fresh stage f6e3ac1c (original 2026-10-26 bundle inaccessible; rebuilt verbatim from the recorded production transcript and the verbatim desk pack; no old QA carried over - all gates rerun on this head).

## Scope
- Source-faithful Maronite Commemoration of the Faithful Departed for Monday 2026-11-02 (Brooklyn Eparchy of Saint Maron 2026 desk calendar PDF: "Commemoration of the Faithful Departed / Monday / 2", Heb 10:11-18, Jn 17:1-8, no named saint). Re-verified 2026-10-30 against the live PDF.
- Text-only commemoration: no saint identity, no book, no art/placeholder. Explicit `kind:'commemoration'` + `commemoration` identity; `book:null` required; builder rejects saint identity/book/art on commemorations.
- 11 locale packs (en ar fr es pt it de pl ru hi th) mirror EN per existing editorial policy; `translationStatus` records "Agent-authored mirrored copy; independent review pending; no native-human review claimed".
- infoUrl: the Brooklyn Eparchy of Saint Maron 2026 desk calendar PDF (owning calendar's exact public source; re-verified 2026-10-30, November page 94). Replaces the desk-candidate Catholic.org AllSouls link to avoid any cross-calendar rite mismatch. Localized CTAs point to the commemoration in the 2026 Maronite calendar. No cross-calendar equivalence claim in copy.
- Expiry behavior preserved: the builder enforces a max 7-day span (8 dated entries); the retained window is 2026-10-26..2026-11-02. Only 2026-10-25 was pruned on insert (identical semantics to the original 2026-10-26 run); the 2026-10-26..2026-11-01 entries are semantically unchanged.

## Changes
- scripts/build_saint_of_day.py: kind support ('saint' default, 'commemoration' text-only), identity requirement, art/book rejection, `home-saint-info--text` marker class on the text-only card.
- scripts/i18n/refresh_saint_home_bindings.py: commemorations skip the book/portrait binding requirement.
- styles.css: scoped text-only commemoration card block (`.home-saint-day>a.home-saint-info.home-saint-info--text`), no portrait/halo pseudo-element, column layout. home.css regenerated.
- scripts/qa/test_saint_of_day.py: 3 new tests - text-only without saint identity (no plate/pair/img, marker class present), rejection of invented saint/book/art, rejection of unknown kind and missing commemoration identity.
- Data: locales/*/saint-of-day.json (11 packs), locales/saint-of-day.json manifest entry with source URL list and honest translation status; locales/*/home-copy.json + locales/en/saint-of-day-copy.json via generators; locales/en/home-bindings.json re-pinned.
- Regenerated: index.html + 11 locale homepages, same-page-manifest.js (ar2 home-equivalence candidateFileSha256 refreshed to the new ar/index.html hash), sitemap.xml.

## Verification (all run on this head, 2026-10-30)
- python3 -m unittest discover -s scripts/qa -p test_saint_of_day.py: 20 tests OK (incl. 3 new commemoration tests).
- node scripts/qa/test_saint_day_runtime.cjs: PASS (four NY clocks over two window units, midnight swap, minute/visibility refresh, no duplicate clone, fail-closed).
- python3 scripts/i18n/refresh_saint_home_bindings.py --check: OK.
- node scripts/build-pages.mjs --check --pages=index.html: 0 out of date.
- node scripts/build-home-css.mjs --check: matches sources.
- python3 scripts/qa/check_i18n_policy.py: passed.
- python3 scripts/qa/check_seo.py: passed, 423 indexable pages match sitemap and metadata rules.
- python3 scripts/build-same-page-control.py --check: 424 canonical pages, 0 stale.
- Source re-verification: Brooklyn 2026 desk calendar PDF re-fetched 2026-10-30, November page confirms the commemoration, readings and weekday.
- PENDING this run: Playwright saint-of-day spec (--grep 2026-11-02, phone+laptop) and rendered screenshot proof (en/ar/de at 390/768/1440). Will be attached with the candidate report; do not merge before they pass.
