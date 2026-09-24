# SEO bot work log - 2026-09-24 - content batch 1

date: 2026-09-24
task_id: content-batch-1-trail-patronage-movie-healing
change_type: new content pages (4) + internal links + sitemap + keyword map
risk_level: low (factual/devotional-tradition content; no miracle, testimony,
privacy, payment, canonical, or i18n-architecture changes)

## Evidence and plan

- Keyword map: docs/seo/keyword-map-2026-09-24.md (research method, cluster
  coverage, opportunity scores, batch plan, evidence URLs).
- Demand evidence: live rankings checked 2026-09-21 ("saint charbel prayer"
  ~#6, "mar charbel rosary" ~#5); public SERP research 2026-09-24. Search
  Console access still pending; no volumes invented.

## Prepared in this batch (PR proposed; merge goes through the integrator lane)

| Page | Target intent | Key sources |
|---|---|---|
| /saint-charbel-trail | saint charbel trail / darb mar charbel | darbmarcharbel.org, lebanontraveler.com |
| /saint-charbel-patron-saint | what is saint charbel the patron saint of | vaticanstate.va saint-of-the-day, ewtnmission.com, Paul VI canonization homily |
| /saint-charbel-movie | saint charbel movie / mar charbel movie | elcinema.com, blogbaladi.com, cinemacitybeirut.com, thebeiruter.com, rottentomatoes.com, EWTN on demand |
| /saint-charbel-prayer-for-healing | saint charbel prayer for healing / for the sick | saintcharbel.com, vaticanstate.va |

Internal links added (one edit point each): visit-annaya.html (trail tip),
news.html (movie card), saint-charbel-prayers.html (healing guide note),
history.html (patronage card). All four new pages link back into the prayer,
visit, history, and news cluster.

## Editorial review notes

- Patronage page distinguishes formal recognition from devotional custom, per
  site rules; no Vatican decree is claimed for healing patronage.
- Healing prayer page: prayers labeled as original site compositions; no
  outcome promises; holy oil described as devotional aid, not medicine.
- Movie page states what is confirmed (2026 Lebanon release, cast, director)
  and what is not (international/streaming) as of 2026-09-24.
- Trail page reports section status as of launch reporting and directs readers
  to the official site for current conditions.
- No doctrinal, miracle, or testimony content in this batch; the standing
  Joey-review gate is not triggered. "saint charbel miracles 2025/2026" remains
  queued behind that review.

## Verification (local, 2026-09-24)

- python3 scripts/qa/check_seo.py: no new errors vs clean-stage baseline
  (baseline itself fails on /it /pl /pt non-reciprocal hreflang - pre-existing,
  addressed by the in-flight homepage i18n/head repair PR).
- python3 scripts/qa/check_i18n_policy.py: batch files pass after registering
  the four new standalone English pages in locales/legacy-text-baseline.json,
  the same mechanism as the approved 2026-09-21 standalone-page batch. The two
  remaining failures (index.html, testimony-review.html) are pre-existing on
  clean stage and belong to other in-flight work.
- python3 -m unittest scripts/qa: 31 tests, same 3 pre-existing failures as
  clean-stage baseline (homepage managed-block repair in flight); zero new.
- npm run build:navigation: new pages synced to shared primary nav.
- npm run qa:dead-code: clean.
- git diff --check: clean.
- Browser render check (Playwright chromium, local static server): all four
  pages render with correct H1, zero console errors, no mobile horizontal
  overflow at 390px; desktop and mobile screenshots taken.
- Not run locally: full Playwright quality suite and Apache route checks
  (environment limits); CI on the PR runs qa, browser-quality, and dead-code
  gates before merge.

## Measurement and next review

- Expected metric: indexing of the 4 new canonical URLs; impressions/clicks by
  query class once Search Console access lands; CTR at positions 4-20.
- next_review_date: 2026-10-24
- rollback_reference: remove the 4 page files, 4 sitemap entries, and the 4
  single-point internal links listed above.
