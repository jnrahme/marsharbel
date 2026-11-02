# I18N STATUS

Audit at 2026-10-13 3:35 PM EDT, stage d5b67353. Pages = sitemap URLs per locale prefix (English = 153). Missing strings, localization correctness and per-locale build results come from `build-international.py --check` (passes on stage for all 12 locales) and the policy gate; per-locale string-gap counts are not yet measured, so the column says so rather than guess.

| Locale | Sitemap pages /153 | Nav coverage | Other work | Open PR | Build/test | Merge status |
|---|---|---|---|---|---|---|
| ar | 41 | marked on stage (#764,#749) | 23 leftover pages queued (T-008); native review not certified | none open | build --check OK on stage; strings gap not measured | merged on stage |
| de | 36 | marked on stage (#766); pinned 12 twins in #782 | finish_nav 13 pages queued (T-007) | #782 draft 8723ea64 | build --check OK on stage; strings gap not measured | merged on stage |
| ru | 20 | marked on stage (#773) | pinned travel twins pending source commit | none open | build --check OK on stage; strings gap not measured | merged on stage |
| fr | 26 | #783 merge approved 67eee959 | 4 authored hashes repinned by script | #783 | build --check OK on stage; strings gap not measured | not merged |
| es | 27 | merged on stage (#787) | native review not certified | none | build --check OK on stage; strings gap not measured | merged on stage |
| it | 23 | not started | after es | none | build --check OK on stage; strings gap not measured | not merged |
| pl | 23 | not started | after it | none | build --check OK on stage; strings gap not measured | not merged |
| pt | 24 | not started | after pl | none | build --check OK on stage; strings gap not measured | not merged |
| hi | 5 | not started (limited launch) | mark-as-English | none | build --check OK on stage; strings gap not measured | not merged |
| th | 5 | not started (limited launch) | mark-as-English | none | build --check OK on stage; strings gap not measured | not merged |
| zh-Hans | 15 | travel and film mirror families (no homepage) | Mirror-only ACTIVE locale (scrum ruling 3:49 PM): rule j applies to its mirrored families; config lists unchanged on purpose | none | build --check OK on stage; strings gap not measured | not merged (15 pages live) |

Rule (j): a page ships only when every active locale has it. Native review is not certified for any locale. Commit SHAs are in COMPLETED.md and the PR column. Worklists: /downloads/locale-links-worklist-87b40854.csv (87 rows), locale-links-deep-ar-de-ru-ae83ec61.csv (2172 rows).