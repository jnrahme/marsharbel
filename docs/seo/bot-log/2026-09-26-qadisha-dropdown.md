# 2026-09-26 - /qadisha-valley Places dropdown + inbound cross-link (follow-up bundle)

## Task
Parent 5:45 AM: add /qadisha-valley to the Places dropdown site-wide (cluster hub) + inbound cross-links from bekaa-kafra and saint-charbel-places-lebanon, once nav-resync lands. Integrator 5:48 process feedback applied: edit partials/primary-navigation.html + sync-navigation.mjs write mode, never hand-edit page navs; full QA suite before shipping.

## Preconditions
Verified on origin/stage: nav-resync landed as #234 (squash 1e5b642, partials/primary-navigation.html carries Story -> /stories), qadisha-valley page landed as #236 (54dcd16). Branch seo/qadisha-dropdown off fresh origin/stage.

## Changes
- partials/primary-navigation.html: "Qadisha Valley" added to the Places dropdown after Bekaa Kafra; scripts/sync-navigation.mjs (write mode) propagated to all 96 managed pages (root + mysteries/ + miracles/, ../ prefixes handled by the sync).
- templates/mirrors/prayers.html + locales/{en,ar,es,fr,pt}/mirrors/prayers.json: same item added at the GENERATOR source (new slot header.qadishaValley) so the prayer-mirror pages stay consistent for BOTH sync-navigation --check and build-international --check. Labels: en "Qadisha Valley", ar "وادي قاديشا" (per UNESCO whc.unesco.org/ar/list/850 + Arabic Wikipedia), es "Valle de Qadisha", fr "Vallée de Qadisha", pt "Vale de Qadisha" (proper noun; es/fr/pt translate "Valley" per their catalog style, ar transliterates per its style). Regenerated: saint-charbel-prayers.html, en/prayers.html, ar/prayers.html, es/oraciones.html, fr/prieres.html, pt/oracoes.html.
- bekaa-kafra.html: "Pair It With the Qadisha Valley" section - first sentence now links the Qadisha to ./qadisha-valley.
- saint-charbel-places-lebanon.html: NO edit needed - a body link to ./qadisha-valley already exists on stage (Bekaa Kafra visiting paragraph); skipped to avoid double-linking the same target on one page.
- locales/legacy-text-baseline.json: re-registered via check_i18n_policy.py's extractor (99 new keys: the "Qadisha Valley" label across managed pages + anchor splits), max-merge, insertion-ordered format preserved.

## Verification
- sync-navigation --check: 96 pages, 0 out of sync.
- build-international --check: green (8 languages, 48 guides, 7 language homepages).
- check_i18n_policy: green.
- Full QA suite: GREEN - run in chunks because the full script now exceeds the 120s bash window (build-home-css, i18n, SEO, feeds, testimony baseline+static; testimony-security; site-smoke; all 6 rosary sub-suites individually green).
- Pixel review: desktop dropdown on qadisha-valley (active state on the new item), mysteries/joyful-1 subdirectory dropdown (../ hrefs work), ar/prayers RTL nav (label verified in markup), mobile 390 - all clean. Screenshots in the parent report.

## Notes
- The prayer-mirror pages now carry the Qadisha Valley dropdown item in all 5 mirror locales; remaining locales without mirror catalogs are unaffected (their pages are generated from other templates).
- IndexNow: no new URLs in this bundle (nav/content change only).
