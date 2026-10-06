# 2026-10-06 - News desk: Beirut altar consecration card (Douaihy & Hoayek)

Feature: new card `douaihy-hoayek-altar-consecration-2026-09` in the TOP section "News of Saint Charbel and the Lebanon Saints" on /news, placed by event date between el-paso-lebanese-festival-2026-10 and emmitsburg-shrine-anniversary-2026-09 (inside the i18n-news-desk block). Event: September 27, 2026 consecration of the altar of Blessed Patriarchs Estephan Douaihy and Elias Hoayek at St. George Maronite Cathedral, Beirut; relics deposited in the altar; Patriarch Al-Rahi presided; President Aoun attended. Closes the Sept 28 desk lead previously held as unverified.

Generator path (corrected after PR #630 feedback): the card lives in templates/news-desk/cards.html + keyed copy in locales/en/news-desk.json (consecration.*); news.html and src/pages/news.html carry the rendered output of scripts/build_news_desk.py; feed.xml rebuilt by scripts/build_feeds.py from news.html; sitemap.xml /news lastmod hand-bumped to 2026-10-06; scripts/qa/test_news_desk.py gained test_douaihy_hoayek_altar_card.

## Evidence gate
- Verification: NNA (nna-leb.gov.lb/en/news/225064, Sept 27), An-Nahar English (en.annahar.com/en/351845, Sept 27, homily quotes), L'Orient Today (article 1548831, Sept 27, relics). Three independent reports agree on date, venue, celebrant, relics, president's attendance.
- Title discipline: both patriarchs labeled Blessed, not Saint (Douaihy beatified 2024; Hoayek July 25, 2026). Card says so explicitly.
- Media-rights ledger: media/news/beirut-st-george-cathedral.webp - Lebnen18, Commons, CC BY-SA 3.0 (multi-licensed), verified on the file page; 960px thumb converted to WebP, no content edits; venue-context caption. Event photos from NNA/Annahar/L'Orient NOT reused (no verified license). Registered in docs/seo/photo-rights-registry.md (October 6 section).

## QA
- scripts/build_news_desk.py --check: pass (see run log). scripts/build_feeds.py --check: pass. node scripts/build-pages.mjs --check: 109 pages, 0 out of date.
- bash scripts/qa/prepush.sh: all static gates passed (exit 0), including build_news_desk.py --check. check_i18n_policy.py: pass. test_head_fragments.py: OK (counts unchanged, no new page). test_news_desk.py: 7 tests OK.
- Rendered check over local HTTP at 1280 and 390 with __MARSHARBEL_QA__ monitoring flag: card present, image loads, zero console/page errors; screenshots eyeballed.

## IndexNow URLs
- https://marsharbel.com/news
- https://marsharbel.com/feed.xml
