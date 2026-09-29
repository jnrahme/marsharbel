# 2026-09-29 - New page: /saint-charbel-chaplet (AEO re-audit spec)

## What shipped
- saint-charbel-chaplet.html (en-first): answer-first hero (structure + opening prayer named), 6 sections, 6-step bead-by-bead guide, both traditional prayers in full, 5-question FAQ, Sources.
- prayer-library.html: finder card (keywords: chaplet beads red white blue father of truth 22nd).
- sitemap.xml entry (indent normalized after test_seo caught the regex-sensitive line), apply_seo_tags.py registry entry, baseline per-file update (2 files).
- Generator-filled JSON-LD: WebPage+Breadcrumb+Article (datePublished 2026-09-29), FAQPage. No hand-added JSON-LD.

## Evidence gate
### Claim/source matrix
- Bead structure (medal + 1 white bead; five sets of three: 3 red, 1 white, 1 blue; 5 black dividers; 21 beads total) - St. Joseph Maronite Church Phoenix + battlebeads (identical); mariereine (French) corroborates 21 beads + medal + color meanings.
- Color meanings (red = vows of poverty/chastity/obedience; white = Eucharist; blue = Our Lady) - all three sources agree.
- Order of prayers (white bead: Father of Truth; black: Our Father; each colored set: 3 Hail Marys by theme; medal: Prayer to Obtain Graces) - Phoenix + battlebeads identical.
- Father of Truth = the Maronite liturgy prayer Charbel was praying when struck at the altar Dec 16, 1898; kept repeating it until death Dec 24 - mariereine + battlebeads; consistent with our /history account (stroke during the Divine Liturgy).
- charbel.app PDF cross-check: structure matches but their Father of Truth is TRUNCATED (ends "accept my prayer. Amen", drops the mercy/scale/nails passage) and their closing prayer is abbreviated. Page uses the full traditional text from Phoenix/battlebeads. No charbel.app text used.
- Wording variant noted: "nails and the lance" (battlebeads) vs "the nail and the lance" (Phoenix). Page uses "nails" (plural), the more common rendering.
- 22nd-of-the-month pairing and July novena pairing - site's own pages.
- NOT asserted: any claim that the monastery of Annaya formally publishes this chaplet (sources show the devotion in Maronite parish use; the page says "the prayer tradition that surrounds his shrine", no stronger claim).

### Media-rights ledger
- media/news/saint-charbel-portrait.webp (existing site asset, already rights-recorded, reused as hero). No new media; no suitable rights-clean chaplet-beads photograph exists on Commons (checked 2026-09-29).

### Translation-parity note
- en-first only; hreflang x-default + en. Locale mirrors via the mirror pipeline later; baseline updated per-file.

## QA
- build-home-css, i18n:check/test, check_seo (206 pages), check_i18n_policy, nav-sync (106 pages, 0 drift), dead_code, diff --check, test_seo+test_prayer_mirror+test_i18n (60 tests OK - the prayer-mirror key-count drift is fixed on current stage by #342), testimony-security, site-smoke, 8 rosary/story suites: PASS.
- Rendered review: desktop 1440 + phone 390 full-page captures + prayer-library card element shots, pixel-inspected.
- Test-assisted fix: test_missing_sitemap_entry_fails caught my first sitemap insert (unindented line broke the test's entry-removal regex); indent normalized. Same cosmetic nit exists in the pending st-estephan-nehme bundle (st-nimatullah line) - valid XML, no check fails there, flagged to integrator for normalization on merge.

## Sources (page)
- stjosephphoenix.org/st-sharbel/prayers/chaplet-of-st-sharbel (Maronite parish; structure + both prayers, fetched).
- mariereine.com (French tradition; fetched 2026-09-29).
- battlebeads.com/stchar.html (independent instruction corroboration; fetched. NOTE: its biography paragraph has a wrong birth year - cited for chaplet instructions only).
