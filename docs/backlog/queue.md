# Work queue

Copied from `Projects/Marsharbel/throughput-plan.md` section 8 (joey-projects-vault main, Nov 25 2026). Status column is owned by Instinct; the seven CI rows reflect tonight's merges/PRs.

## Queue

Format (one row per item; Instinct owns status):
`| ID | Type | Item | Why (data) | Locales | Size | Status | PR |`
Types: CI, SEO, LOC (locale), BOOK, BOOK-TR (book translation), PIPE (pipeline), FIX. Status: ready → in-pr → merged → measured | blocked(<check>) | dropped. Size S ≤ 100 lines, M ≤ 300.

| ID | Type | Item | Why (data) | Locales | Size | Status | PR |
|---|---|---|---|---|---|---|---|
| Q-001 | CI | Sitemap lastmod robust to squash merges (C1) | #941 push QA red; #951 date refresh | n/a | M | merged | [#952](https://github.com/jnrahme/marsharbel/pull/952) |
| Q-002 | CI | Deploy admission retries transient API errors (C2) | #951 deploy failed on API read | n/a | S | merged | [#954](https://github.com/jnrahme/marsharbel/pull/954) |
| Q-003 | CI | Fix qa-shard 5/8 alt-text assertion family + rebalance (C3) | 7 failed runs; #950 | n/a | M | ready | |
| Q-004 | CI | Rebalance/fix qa-shard 6/8 (C3) | 5 failed runs | n/a | M | in-pr | [#957](https://github.com/jnrahme/marsharbel/pull/957) |
| Q-005 | CI | Flaky ledger artifact + daily summary (C5) | bq shards 1,2,6,7,8 failed 5× each | n/a | S | in-pr | [#955](https://github.com/jnrahme/marsharbel/pull/955) |
| Q-006 | CI | `scripts/qa/affected.sh` local fast path (C7) | local full gate 45–75 min | n/a | M | in-pr | [#956](https://github.com/jnrahme/marsharbel/pull/956) |
| Q-007 | CI | Post-merge regeneration of sitemap/manifest/search-index (C4; revive #881 idea) | conflict churn | n/a | M | merged | [#953](https://github.com/jnrahme/marsharbel/pull/953) |
| Q-008 | FIX | Lowercase /zh-hans → 301 /zh-Hans/ (from 9:04 brief) | slash URL 301→404 | zh-Hans | S | ready | |
| Q-009 | SEO | Homepage title/meta + intro for "saint charbel"/"st charbel"/"mar charbel" | / pos 11.4, 864 impr, CTR 0.7%; "mar charbel" 501 impr pos 12.4 | all 12 | S | ready | |
| Q-010 | SEO | /ar/ homepage title/meta (Arabic queries) | /ar/ 574 impr pos 9.3 CTR 0.5% | ar | S | ready | |
| Q-011 | SEO | /ar/saint-charbel-chaplet title/meta + how-to answer | 373 impr pos 7.3 CTR 0.3% | ar | S | ready | |
| Q-012 | SEO | /saint-charbel-tomb title/meta + visiting info answer | 235 impr pos 5.6 CTR 0.4% | en (+LOC items) | S | ready | |
| Q-013 | SEO | /how-did-saint-charbel-die title/meta + direct answer box | 195 impr pos 6.0, 0 clicks | en | S | ready | |
| Q-014 | SEO | /charbel-film-premiere title/meta; link to movie page | 153 impr pos 9.4, 0 clicks | en | S | ready | |
| Q-015 | SEO | /ar/feast-day title/meta | 130 impr pos 7.6, 0 clicks | ar | S | ready | |
| Q-016 | SEO | /videos title/meta + VideoObject check | 348 impr pos 6.3 CTR 1.1% | en | S | ready | |
| Q-017 | SEO | /music title/meta | 201 impr pos 7.4 CTR 1.5% | en | S | ready | |
| Q-018 | SEO | /fr/prieres + /fr/neuvaine titles/meta, internal links from /fr/22-du-mois | 216 & 158 impr pos ~9 | fr | S | ready | |
| Q-019 | SEO | /it/preghiere title/meta + links from /it/il-22-del-mese (pos 3.2) | 178 impr pos 9.8 | it | S | ready | |
| Q-020 | SEO | /pl/nowenna title/meta + links from /pl/22-dnia-miesiaca (pos 2.2) | 177 impr pos 11.7 | pl | S | ready | |
| Q-021 | SEO | /ru/ homepage title/meta | 171 impr pos 9.8 CTR 0.6% | ru | S | ready | |
| Q-022 | SEO | /es/novena: FAQ answers for "novena completa a san charbel" | 644 impr pos 8.5; query pos 8.0 | es | S | ready | |
| Q-023 | SEO | Movie page: protect + extend (where-to-watch by country, link out to film premiere/saint pages); no #948 rebuild | 135 clicks / 3,546 impr pos 6.1 | en | S | ready | |
| Q-024 | LOC | Movie page in fr/es/it/de/pl/pt/ru/ar (map existing /fr/charbel-film-premiere; add missing) | winner page, no mapped variants | 11 | M | ready | |
| Q-025 | LOC | Oil page in all locales | 43 clicks / 887 impr pos 4.9; no mapped variants | 11 | M | ready | |
| Q-026 | LOC | Healing prayer page in all locales | 340 impr pos 7.8; no mapped variants | 11 | M | ready | |
| Q-027 | LOC | How-did-he-die page in all locales | 195 impr EN; no variants | 11 | M | ready | |
| Q-028 | LOC | Tomb page in all locales | 235 impr EN; no variants | 11 | M | ready | |
| Q-029 | LOC | Chaplet, litany, feast-day in fr/es/pt/it/de/pl/ru | /ar/ chaplet 373 impr; missing in 7+ locales | 7–10 | M | ready | |
| Q-030 | LOC | 22nd-of-month, novena, prayers, pilgrimage, visit-annaya in hi/th/zh-Hans | strong in it/fr/pl (pos 2.2–4.8); missing hi/th/zh | 3 | M | ready | |
| Q-031 | LOC | Map unmapped locale equivalents into same-page-manifest + hreflang | e.g. /fr/charbel-film-premiere not mapped | all | S | ready | |
| Q-032 | SEO | es: San Charbel *listones* (Mexico tradition) page + en version | Mexico 424 impr; documented tradition | es, en (+LOC) | M | ready | |
| Q-033 | SEO | pt (Brazil): oração/novena snippet + oil page priority | Brazil 210 impr pos 9.8; pt 4 clicks | pt | S | ready | |
| Q-034 | SEO | en: Philippines relic-tour/oil intent section | Philippines 613 impr pos 6.2 CTR 2.1% | en | S | ready | |
| Q-035 | SEO | Internal links: winners → near-winners (movie, oil, 22nd → tomb, how-he-died, chaplet, litany) | §1.4 | all | S | ready | |
| Q-036 | SEO | Schema audit on near-winners (Article/FAQ/VideoObject validity; respect #939 decision) | near-winner list | all | S | ready | |
| Q-037 | FIX | Revive #847 as fresh PR: VideoObject uploadDate with timezone | stale draft, real fix | all | S | ready | |
| Q-038 | FIX | Revive #849 as fresh PR: heading 200% text overflow | stale draft, a11y | all | S | ready | |
| Q-039 | FIX | Revive #757 as fresh PR: nav row gap | stale draft | all | S | ready | |
| Q-040 | BOOK-TR | Maroun book → 11 locales | EN-only book | 11 | M | ready | |
| Q-041 | BOOK-TR | Rafqa book → 11 locales | EN-only | 11 | M | ready | |
| Q-042 | BOOK-TR | Hardini book → 11 locales | EN-only | 11 | M | ready | |
| Q-043 | BOOK-TR | Charbel v2 book → 11 locales | EN-only | 11 | M | ready | |
| Q-044 | BOOK-TR | Francis book → 11 locales | EN-only; /francis-story 146 impr pos 8.1 | 11 | M | ready | |
| Q-045 | BOOK-TR | Marina, Massabki, Sergius-Bacchus books → 11 locales (one PR each) | EN-only | 11 | M×3 | ready | |
| Q-046 | BOOK-TR | Pio, JPII, Mother Teresa, Therese, Anthony books (one PR each) | EN-only | 11 | M×5 | ready | |
| Q-047 | BOOK-TR | Joseph, Peter, Jude, Magdalene, Augustine, "story" books (one PR each) | EN-only | 11 | M×6 | ready | |
| Q-048 | BOOK-TR | Rosary books joyful set → hi, ru, th, zh-Hans | missing 4 locales | 4 | M | ready | |
| Q-049 | BOOK-TR | Rosary luminous set → hi, ru, th, zh-Hans | same | 4 | M | ready | |
| Q-050 | BOOK-TR | Rosary sorrowful set → hi, ru, th, zh-Hans | same | 4 | M | ready | |
| Q-051 | BOOK-TR | Rosary glorious set → hi, ru, th, zh-Hans | same | 4 | M | ready | |
| Q-052 | PIPE | `scripts/pipeline/` runner skeleton + provider adapter + budget guard ($0) | §6 | n/a | M | ready | |
| Q-053 | PIPE | Glossaries per locale (names, prayers, Maronite terms) | §6 | 12 | M | ready | |
| Q-054 | PIPE | Back-translation diff + claim↔evidence checker | §6 | n/a | M | ready | |
| Q-055 | BOOK | Nicholas of Myra (6 Dec) — 12 locales; art sign-off by Joey | seed #22 | 12 | M | ready | |
| Q-056 | BOOK | Juan Diego (9 Dec) — 12 locales; art sign-off by Joey | seed #23; Mexico | 12 | M | ready | |
| Q-057 | BOOK | Lucy (13 Dec) | seed #24 | 12 | M | ready | |
| Q-058 | BOOK | John of the Cross (14 Dec) | seed #14 | 12 | M | ready | |
| Q-059 | BOOK | Elizabeth Ann Seton (4 Jan) | seed #8 | 12 | M | ready | |
| Q-060 | BOOK | André Bessette (6 Jan) | seed #25 | 12 | M | ready | |
| Q-061 | BOOK | Stephen Douayhy (Maronite) | seed #1 | 12 | M | ready | |
| Q-062 | BOOK | Estephan Nehme (Lebanese) | seed #3 | 12 | M | ready | |
| Q-063 | BOOK | Carlo Acutis | seed #18 | 12 | M | ready | |
| Q-064 | BOOK | Lorenzo Ruiz (Philippines) | seed #33 | 12 | M | ready | |
| Q-065 | SEO | Weekly GSC/GA4 export into relay (Instinct supplies data; L4) | Ryze disconnected | n/a | S | ready | |
| Q-066 | SEO | Stories hub (`stories.html`) localized + linked from each saint page | stories.html no mapped variants | 11 | M | ready | |

Remaining seed saints (§5.5) become BOOK items as the book loop reaches them. Each `M×N` row is N separate PRs.
