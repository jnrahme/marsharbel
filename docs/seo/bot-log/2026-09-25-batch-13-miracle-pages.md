# 2026-09-25 - Batch 13: individual miracle pages (competitor-parity priority 1)

Specs from parent 2026-09-25 1:23 PM (competitor lane): 5 child pages under
/miracles/, shared template (H1, summary, person before / what happened /
evidence / Church treatment / pilgrims today / FAQ / sources), Article +
FAQPage + BreadcrumbList schema, hero + inline images, attributed claims,
Church-approved vs reported distinguished, no promises. 7-locale rollout
flagged to parent separately (Arabic priority via intl lane pipeline).

## Shipped (English masters)
- miracles/nohad-el-shami.html - 1993 dream-surgery healing behind the 22nd;
  testimony framing (never tribunal-examined); links 22nd page, hermitage, oil
- miracles/dafne-gutierrez.html - Phoenix 2016 blindness healing; Dr Borik
  medical committee quoted; eparchial (not Vatican) recognition stated plainly
- miracles/canonization.html - the three Church-approved miracles (Kamari,
  Obeid 1950; Awad 1967); approval process explained
- miracles/raymond-nader.html - 1994 hermitage experience + hand print;
  private-revelation framing (experience not declared; Family of Saint
  Sharbel IS Church-approved); Dr Hokayem findings
- miracles/latest-register-entries.html - living page: Jan 2026 two healings
  (links miracles-2026), Oct 2025 Ishaac + Nehme, Naples vessel "under study"
- Hub (miracles.html): card titles link child pages + intro list of all five

## Tooling (flagged for technical-lane review)
Added miracles/ subdir support mirroring mysteries/ precedent:
scripts/i18n/catalog.py public_html_files, scripts/qa/check_i18n_policy.py
snapshot glob, scripts/sync-navigation.mjs pages + aliases (Miracles nav
active state). All additive; check_seo canonical logic already handles subdirs.

## Images
Site assets only (portrait, v1 artwork, trail, walk) with accurate captions;
no new rights-restricted material. Hero + layout matches pope-visit page.

## QA
check_seo green (119 pages, incl. link guard), i18n policy green, nav sync
0/74, diff --check clean, Playwright clean all 5 pages + hub (desktop+mobile,
zero console errors). Baseline registered via policy script's extractor.
