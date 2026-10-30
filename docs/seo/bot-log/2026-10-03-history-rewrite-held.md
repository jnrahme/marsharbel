# 2026-10-03 /history rewrite - built, HELD (not integrated)
- Source copy: growth reviewer final v2 (Oct 3). Built into src/pages/history.html, 3,300 words, answer-first (answer block 55 words), quick facts table, 8 sections, status table, 9 FAQ (hand-mirrored in FAQPage JSON-LD), 10 sources, internal links.
- Facts corrected against primary sources before building: Paul VI 1977 homily says ordained 1859, then 16 years of community life at Annaya and 23 alone, died at 70 (so "47 years at Annaya" and "16 community years after joining at 23" were wrong and are not printed); drive from Beirut is about 90 minutes per /visit-annaya (draft said an hour); Leo XIV Dec 1, 2025 quotes confirmed at vatican.va.
- Dropped as unverified: "Annaya means hermit", hermitage altitude 1,400 m, "highest inhabited village" (now "one of the highest"), father's burial near Byblos and August date, canonization-miracle name/illness (sources disagree; saintcharbel.com names Mariam Awad, not cross-checked with the Church record).
- Schema: WebPage and Person are generator-owned (apply_seo_tags: Person adds birthDate 1828, deathDate 1898-12-24, sameAs). FAQPage hand-mirrored.
- Catalog: locales/en/history-copy.json (191 strings, exact counts).
- Photos: see docs/seo/photo-rights-registry.md 2026-10-03.
- German twin and other locales need full re-translation (i18n lane, after #538).
- IndexNow (after integration): https://marsharbel.com/history
