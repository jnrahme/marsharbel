# Site-wide photo audit - 2026-09-25

Standing rule (Joey, via parent, 2026-09-25 9:08 PM): real photos on every page where they belong, site-wide. Every new page ships with real, rights-clean images by default. This audit is the backlog; batches run through the integrator like the editorial retrofit.

## Method
Scanned all 150 HTML pages: word count (boilerplate stripped) vs <img>/<video>/embed count. Flagged: content pages over 400 words with zero media. Excluded: legal pages (privacy-policy, terms-of-service - photos do not belong), the 4 saint/blessed pages (photos shipped in the seo/saints-photos bundle), localized pages (media lands with the intl lane, not one-off edits).

## Result: 35 English content pages need photos

### Priority 1 - core pages, highest site prominence (nav, homepage, hubs)
1. prayer-library.html (4,015 words) - hub of the whole prayer section
2. miracles/index.html (1,560) - miracles hub
3. saint-charbel-novena.html (1,411)
4. saint-charbel-prayer-for-healing.html (1,274)
5. saint-charbel-miracles-2026.html (1,271)
6. saint-charbel-prayers.html (1,213)
7. visit-annaya.html (1,162)
8. saint-charbel-feast-day.html (1,151)
9. saint-charbel-oil.html (1,064)
10. saint-charbel-tomb.html (1,033)

### Priority 2 - prayer intentions + Lebanon places
11. saint-charbel-prayer-for-a-miracle.html (1,027)
12. saint-charbel-around-the-world.html (984)
13. maronite-history.html (920)
14. saint-charbel-prayer-for-students.html (896)
15. saint-charbel-prayer-for-anxiety.html (885)
16. saint-charbel-prayer-for-depression.html (869)
17. saint-charbel-prayer-for-family.html (861)
18. saint-charbel-prayer-for-the-sick.html (857)
19. saint-charbel-prayer-for-addiction.html (856)
20. saint-charbel-places-lebanon.html (854)
21. saint-charbel-prayer-for-pregnancy.html (854)
22. saint-charbel-quotes.html (848)
23. saint-charbel-relics.html (834)
24. 22nd-of-the-month.html (819)
25. saint-charbel-hermitage.html (811)
26. saint-charbel-patron-saint.html (719)
27. how-did-saint-charbel-die.html (640)
28. rosary-visual-guide.html (606)
29. history.html (567)

### Priority 3 - light treatment / judgement calls
30. news.html (984) - hub; consider thumbnails per card rather than hero
31. rosary-minibook.html (454) - printable; may intentionally stay light

### Excluded
- privacy-policy.html, terms-of-service.html (legal text; photos do not belong)
- st-maroun / st-nimatullah / st-rafqa / blessed-fulton-sheen (photos in the pending saints-photos bundle)
- ~65 localized pages (fr/ar/es/pt/de/it/el/pl): media lands via the intl lane's generated pages, not hand edits

## Batch plan
- Batches of ~5 pages, P1 first, one bundle per batch through the integrator.
- Sourcing: Wikimedia Commons public-domain / CC with per-image provenance in docs/seo/photo-rights-registry.md (same standard as the saints batch): monastery of Annaya, tomb, hermitage, oil, feast-day crowds, Qadisha valley, etc.
- Medium honesty: photographs captioned as photographs; icons/portraits labeled as such.
- No CSS additions; reuse hero-figure / photo-card components. Generator re-stamps SEO tags per batch. Full QA + Playwright render + pixel inspection per batch.
- Progress tracked here and in docs/seo/bot-log/ per batch.

Status: 0/35 pages complete (saints-photos bundle pending integrator covers 5 more pages separately).
