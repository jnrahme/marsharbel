# 2026-09-29 - New page: /st-estephan-nehme (Lebanese saints pillar 1 of 4)

## What shipped
- st-estephan-nehme.html (en-first): answer-first hero (53 words), 8 body sections, 6-question FAQ, Sources.
- media/saints/st-estephan-nehme.webp (tomb photo, 610x404, converted from Commons JPEG).
- saints.html: hub card "Beatified 2010" with the same image + rights caption.
- sitemap.xml entry; apply_seo_tags.py SAINT_STEMS registration; legacy-text-baseline.json per-file update (saints.html, st-estephan-nehme.html only).
- Generator-filled JSON-LD: WebPage+Breadcrumb+Article (datePublished 2026-09-29), FAQPage (6 Q&A), Person. No hand-added JSON-LD.
- Spec note: no "For children" section - held until storybooks exist.

## Evidence gate
### Claim/source matrix (load-bearing claims)
- Born March 1889, Lehfed, youngest of seven; Our Lady of Grace school - Zenit 2010-06-10. (Wikipedia infobox says March 8; a French mirror says March 7 - month only asserted, conflict avoided.)
- Badger's Fountain - Zenit; framed on-page as "a tale from his childhood."
- Entered Kfifan novitiate 1905, two years after father's death - Zenit.
- First vows Aug 23, 1907, name Estephan - Zenit + saint-charbel.com.
- Lay brother, never a priest; monasteries Mayfouk/Houb/Kettara/Jbeil; solemn vows Apr 13, 1924 at Houb - stephremchurch chronology + saint-charbel.com.
- WWI famine food distribution - Wikipedia (cited) + Zenit ("lived through the adversities of WWI").
- "God sees me" - Zenit (verbatim "God sees me").
- "school of sanctity" / disciple of the land - Zenit.
- Died Aug 30, 1938 at Kfifan, aged 49 - Vatican decree PDF 2010-03-27 (dates) + Zenit.
- Body found intact March 10, 1951 - stephremchurch chronology; Zenit corroborates "body remains intact."
- Cause submitted 2001; Venerable Dec 17, 2007 - saint-charbel.com + ixtheo decretum super virtutibus record.
- Miracle: healing of Sister Marina Nehme (his niece, a Maronite religious) - Wikipedia/newsaints; Vatican decree PDF confirms a miracle through his intercession (unnamed). On-page deliberately does NOT name the diagnosis: sources conflict (osteosarcoma vs degenerative vertebral disease). Fine print included: "accounts retold beyond it vary, and we do not add to them."
- Beatified June 27, 2010 at Kfifan; Angelo Amato, prefect of the Congregation for the Causes of Saints, on behalf of Benedict XVI; president + Patriarch Sfeir + tens of thousands - Daily Star via maronite-heritage + yalibnan/AFP.
- Benedict XVI Angelus June 27, 2010 quote - vatican.va (verified verbatim, page 200).
- Feast Aug 30 - Wikipedia infobox + sancteo.

### Media-rights ledger
- media/saints/st-estephan-nehme.webp: source File:Tombe Estephan Nehmé.jpg, Wikimedia Commons, author Duneir, license CC BY-SA 4.0. Caption carries author + license on both the page and the hub card.
- REJECTED: File:Stéphane Nehmé.jpg (portrait) - uploader "la lumière de dieu blogspot" claims CC BY-SA 4.0 on what is likely the order's official portrait; provenance unreliable under the rights bar.

### Translation-parity note
- en-first only; no locales this batch. hreflang block is x-default + en (same as sibling saint pages). Locale mirrors flow through the mirror pipeline later; baseline updated per-file so intl lane inherits a clean snapshot.

## QA
- build-home-css, i18n:check, i18n:test, check_seo (206 pages), check_i18n_policy, sync-navigation (106 pages, 0 out of sync), dead_code, site-smoke, testimony-security, 8 rosary/story suites: PASS.
- test_seo/test_prayer_mirror/test_i18n (60 tests): 1 pre-existing failure on clean origin/stage 03ae5ae - test_keys_and_urls... expects 133 keys in locales/en/mirrors/prayers.json, file has 134 (intl-lane drift, not this batch).
- Rendered review: desktop 1440 + phone 390 full-page captures of the new page and saints.html hub, plus hub-card element shot; pixel-inspected. Known capture artifact: sticky nav overlays mid-page in fullPage shots (pre-existing site behavior, flagged to parent separately 2026-09-29).

## Sources (page)
- press.vatican.va bollettino 2010-03-27 (0182.pdf) - miracle decree (verified content).
- vatican.va Angelus 2010-06-27 (verified 200 + quote).
- zenit.org 2010-06-10 (fetched).
- maronite-heritage.com/June27-2010.php (Daily Star, ceremony).
- saint-charbel.com/blessed-brother-estephan (chronology corroboration).

## Integrator refresh (2026-10-01)
Fresh Vatican decree PDF confirms a miracle through intercession, not the submitted scientific-characterization wording; removed that overstatement and distinguished the named patient in contemporary reporting. Fresh Zenit/Angelus/Daily Star mirror checked. Commons146760961 confirms Duneir own work/CC BY-SA4.0; source and license links plus WebP conversion/no-crop notice added on page/hub. Frozen baseline unchanged; English copy tracked in scoped saint-pillars catalog. Hero figure moved outside CTA row.
