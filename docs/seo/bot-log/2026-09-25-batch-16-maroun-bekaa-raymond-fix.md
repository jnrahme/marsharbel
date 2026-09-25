# 2026-09-25 - Batch 16: St Maroun + Bekaa Kafra + raymond-nader date correction

Parent 2026-09-25 2:13 PM: factual correction on /miracles/raymond-nader -
1995 is the Family of Saint Sharbel's founding; official ecclesial recognition
was 2010 (source: familyofsaintsharbel.org, Raymond Nader's experience page).
Folded into this bundle per parent. Remaining competitor-parity items
(St Maroun, Bekaa Kafra) built generator-clean in the same batch.

## Shipped
- /st-maroun: the hermit of Cyrrhus (c. 350-410, some say 423). Sourced from
  the Eparchy of Saint Maron's history series (Theodoret's Religious History
  as principal source, Chrysostom letter c. 406, disciples, death and the
  disputed body, only Catholic church named for a person) + the eparchy's
  feast page (Feb 9). No invented facts; quotes attributed to Theodoret.
- /bekaa-kafra: Lebanon's highest village (~1,800m, Becharreh), Charbel's
  birthplace - Makhlouf home, baptism church (7th-13th c.), prayer grotto,
  access roads, visiting notes. Sources: LebanonUntravelled, Discover
  Lebanon, saintcharbel.com; birth facts consistent with our /history.
- history.html: birthplace linked to /bekaa-kafra; 2 new cluster cards
  (St Maroun, Bekaa Kafra) in the saints section.
- /miracles/raymond-nader correction: body + FAQ + JSON-LD FAQ answer now
  read founding 1995, formal recognition as ecclesial community 2010 after
  nine years of Church observation (verified against the cited source).
- sitemap +2; i18n baseline registered for all 4 touched files.

## Generator-clean
New pages authored with title/canonical/description only; apply_seo_tags.py
built the meta/WebPage blocks. Visible FAQ sections without hand-added
FAQPage (generator feature request stands with technical lane).

## QA
check_seo green (126 indexable), test_seo 14/14, check_i18n_policy green,
sync-navigation 0/81, diff --check clean, sitemap_lastmod refreshed
(history lastmod). Playwright: both new pages clean desktop renders,
zero console errors; bekaa mobile spot check.
