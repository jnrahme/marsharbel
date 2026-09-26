# 2026-09-26 - Qadisha cluster: Qannoubine + Qozhaya monastery pages

## Task
Parent 4:08 PM (competitor-lane backlog specs): build /qannoubine-monastery and /qozhaya-monastery per the cluster pattern - thin SERPs (Wikipedia + travel blogs, no devotional authority page), same opening as the Qadisha hub. Article + FAQPage + TouristAttraction schema, internal links up to the hub pages.

## Pages built
- qannoubine-monastery.html: "Qannoubine, the Fortress-Convent of the Patriarchs" - name ("the monastery" par excellence), patriarchal seat 1440-1823 (24 governed, 17 buried, 1909 Syriac stele in St Marina's cave chapel), the Coronation of the Virgin fresco (Douaihy's commission, Boutros the Cypriot, 1781 Moussa Dib restoration, 15 patriarchs), St Marina tradition, the year-round nuns, walking access. Sources: LebanonUntravelled, SyriacPress parts 1-2, UNESCO listing 850.
- qozhaya-monastery.html: "Qozhaya, Saint Anthony's House" - dedication + "treasure of life" etymology (attributed as current scholarly reading), 4th-century origins (attributed), the printing press and the 1610 Qozhaya Psalter (al-Rizzi, Pasquale Eli, Yuseph ibn Amima, Nov 10 1610 colophon, Syriac+Garshuni, first book printed in the eastern Ottoman Empire), LMO mother house from 1708 (1695 founding, 300+ monks peak), what to see, visiting by car. Sources: USEK exhibition + Hidden Treasures, typographie.org, Wikipedia overview.

## Accuracy calls (verified against sources, not the spec)
- Patriarch counts: 24 governed (site-consistent with hub/bekaa-kafra), 17 buried (SyriacPress: 26 officially resided, 17 lived and buried). The spec's "24 buried there" was NOT written - the governed/buried distinction is preserved.
- The 1584 press date is presented as monastery tradition; the documented first book is the 1610 Psalter (USEK: the 1585 catalogued edition has no surviving copy; Dandini saw no press in 1596). The page title keeps the spec's "first printing press" hook; body and FAQ carry the precise claim.
- Wikipedia's "Patriarch Sergius Rizzi" error not repeated - al-Rizzi was a Maronite College alumnus, later Archbishop of Damascus.
- St Marina and the 4th-century founding are phrased as tradition, not fact.

## Architecture (cluster pattern, full nav membership)
- Travel dropdown: both pages added after Qadisha Valley - partial + sync-navigation.mjs (97 pages) + hand-updated mirror templates (prayers.html, qadisha.html) + new catalog keys header.qannoubineMonastery / header.qozhayaMonastery in 11 mirror catalogs (en/ar/fr/es/pt/it/de/pl, Arabic: دير قنوبين / دير قزحيا) + i18n:build.
- apply_seo_tags.py BUG FIX: places_stems() still matched `>Places<` after the #262 Places->Travel rename, silently disabling TouristAttraction generation for any new dropdown page. One-line fix to `>Travel<`. Existing pages were unaffected (authored blocks always win). Flagged for the integrator.
- JSON-LD generator-owned: WebPage + BreadcrumbList + Article + FAQPage (6 Q&A each) + TouristAttraction on both new pages; apply_seo_tags.py touched 0 other files.
- Sitemap: 2 new entries after qadisha-valley (148 indexable pages).
- Baseline: merged (snapshot update for synced pages + partial entry + 2 new entries; nothing dropped).

## Verification
- check_i18n_policy GREEN; check_seo GREEN (148 pages); sync-navigation --check 0 out of sync.
- Full QA chunked ALL GREEN (chunk1 build-home-css/i18n/seo/feeds/testimony; chunk2 testimony-security/site-smoke; chunk3 six rosary sub-suites).
- Pixel review: both pages full-page mobile top-to-bottom - nav with Travel active + aria-current, hero images with attribution captions, all sections well-set, no overflow. Desktop hero bands verified.

## Branch note
Built on feat/qadisha-cluster-pages off origin/stage 6089c18 (post-#270). A mid-build base mistake (work begun on the old batch-2 branch, whose base predated #264's trailing-slash normalization) was caught and redone cleanly: full reset to 6089c18, all changes re-applied by script, generated mirrors rebuilt via i18n:build rather than carried over.

## Follow-ons
- 7-locale mirrors with Arabic priority (parent coordinates intl regeneration): mirror template + en catalog keys would follow the qadisha conversion pattern.
- Noto Arabic webfont self-hosting remains queued behind this merge.
