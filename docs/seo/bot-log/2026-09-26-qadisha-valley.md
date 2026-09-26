# 2026-09-26 - /qadisha-valley places-cluster hub (content cycle)

## Task
Parent spec (4:07 AM, competitor lane): /qadisha-valley, the places-cluster hub - keywords "qadisha valley", "kadisha valley monasteries", "holy valley lebanon" (travel + heritage). Title and meta description per spec; outline H1 + 7 H2s + FAQ; internal links /bekaa-kafra /visit-annaya /saint-charbel-trail /saint-charbel-hermitage /saint-charbel-places-lebanon /history; Article + FAQPage + TouristAttraction schema via generator only. Fork ruling (5:35 AM): English standalone now; locales queued with the intl lane as keyed-template mirrors after the prayer mirror chain.

## Branch
seo/qadisha-valley off 0efb02c (nav-resync tip) - parent named the dependency ("build it after the nav re-sync bundle"). Stage tip at branch time: 194dd95 (nav-resync not yet merged).

## Facts and provenance
- UNESCO WH list 850: "Ouadi Qadisha (the Holy Valley) and the Forest of the Cedars of God (Horsh Arz el-Rab)", inscribed 1998, criteria (iii)(iv) - https://whc.unesco.org/en/list/850/
- Name/etymology (Aramaic "holy"), Nahr Qadisha ~35km from grotto below the Cedars, two branches Qannoubine + Qozhaya, Palaeolithic cave use, Mamluk campaigns 1268/1283, Asi al-Hadath mummies, Qozhaya tradition (St Hilarion, 4th c.; documented by Middle Ages; destroyed 16th c., rebuilt), Saydet Hawqa (late 13th c., 1150m), Mar Sarkis/Ras al-Nahr ("Watchful Eye", church 8th c.), Mar Lichaa (first mentioned 14th c., 4 rock-cut chapels, Maronite solitaries + Discalced Carmelites) - Wikipedia Qadisha_Valley (fetched, corroboration only; not cited on page).
- Patriarchal seat claim kept consistent with the site's own bekaa-kafra.html: twenty-four Maronite patriarchs, 1440-1823 (NOT Wikipedia's "500 years").
- Qannoubine today (narrow track carved into valley wall; nuns year-round) + Fr Hani Tawk quote "It's our roots here. Our Jerusalem, our Rome." - The National, 2022-04-15 (cited).
- 1610 Syriac-Garshuni Psalter, first book printed in the eastern Ottoman Empire - USEK Library, Hidden Treasures (cited).
- Deir es-Salib (cave church below Hadchit, Houlat branch; medieval wall paintings in situ) - JEMAHS 4(2-3) "Wall Paintings in the Qadisha Valley" (cited).
- Saint Charbel links kept to site claims: born Bekaa Kafra 1828 at the head of the valley; hermitage "high above the town of Bsharri and looking across the Qadisha Valley" (saint-charbel-places-lebanon.html); trail.
- Visiting: bases Bsharri (Qannoubine) / Ehden (Qozhaya); ~2 hours from Beirut; Qozhaya by car, Qannoubine on foot; spring-autumn; working monasteries.

## Media (rights-clean, per-image records in docs/seo/photo-rights-registry.md)
- Hero: qadisha-valley-aerial.webp (Evan Williams, CC BY-SA 4.0)
- qannoubine-church.webp (Hussein Sabboury, CC0)
- qozhaya-monastery.webp (Yellaban, public domain)
- mar-lichaa-monastery.webp (Eusebius, CC BY 3.0)
- Rejected after visual inspection: "The Monastery of Qozhaya, Kadisha Valley, Lebanon.jpg" (Argenberg, CC BY 4.0) - no monastery visible in frame; Commons title misdescribes content.

## Process
- New hand-authored page with full head resource set (font preloads + styles.css?v=20260922-1), hero-figure sibling after cta-row, existing component classes only, no hand-added JSON-LD.
- Baseline: 118 keys registered for qadisha-valley.html via check_i18n_policy.py's own extractor (max-merge, insertion-ordered, indent=2, ensure_ascii=False, no trailing newline). i18n policy passes.
- Sitemap: qadisha-valley entry added after bekaa-kafra (lastmod 2026-09-26, monthly, 0.8).
- apply_seo_tags.py run: touched only qadisha-valley.html (WebPage + BreadcrumbList + Article). Generator does NOT emit FAQPage/TouristAttraction/datePublished for new pages - spec asked for FAQPage + TouristAttraction; flagged to parent as a generator-extension follow-up (hand-adding JSON-LD is forbidden).
- FOUND + FIXED (nav-resync latent defect): nav-resync hand-edited the GENERATED saint-charbel-prayers.html; build-international.py --check flagged it stale and i18n:build reverted its nav. Fixed at the source: templates/mirrors/prayers.html (./story -> ./stories, 2 hrefs) + locales/en/mirrors/prayers.json ("Story for Children" -> "Saint Storybooks"), regenerated. English master now byte-identical to nav-resync's version; en/prayers.html + ar/prayers.html regenerated with the new nav (Arabic label unchanged, hrefs -> /stories). Integrator: merge nav-resync first, then this bundle.
- Full QA suite (scripts/qa/run_full_qa.sh): GREEN, exit 0 - 144 indexable pages match sitemap.
- Pixel review: desktop 1440x900 + mobile 390x844 full-page screenshots after scroll (reveal animations fired); hero, images, captions, FAQ, sources, footer all render correctly. Sticky header mid-stitch is the known capture artifact.

## Not done (follow-ups)
- Inbound cross-links from bekaa-kafra.html ("Pair It With the Qadisha Valley" section) and saint-charbel-places-lebanon.html deferred: nav-resync (pending) modifies those files; add after it merges.
- Places dropdown nav addition (all 69+ pages) not in spec - flagged to parent as an option.
- IndexNow: /qadisha-valley to be submitted at deploy (integrator).
