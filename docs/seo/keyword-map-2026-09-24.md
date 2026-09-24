# Saint Charbel keyword map - 2026-09-24

Owner: content pipeline (SEO bot). Method: public keyword and SERP research
(Search Console access pending). No search volumes are invented here; demand is
inferred from live Google rankings already earned ("saint charbel prayer" ~#6,
"mar charbel rosary" ~#5, checked 2026-09-21), competitor coverage, and the
presence of dedicated SERP results. Every candidate lists its evidence URL.

## Coverage: what the site already answers

| Query class | Owner page(s) |
|---|---|
| saint charbel prayer / prayers | /saint-charbel-prayers, /prayer-library |
| mar charbel rosary / how to pray the rosary | /rosary-visual-guide, /rosary-intro, /mysteries/* |
| saint charbel novena | /saint-charbel-novena |
| saint charbel feast day | /saint-charbel-feast-day |
| 22nd of the month saint charbel | /22nd-of-the-month |
| visit annaya / annaya monastery | /visit-annaya |
| saint charbel miracles | /miracles |
| saint charbel news / movie (news angle) | /news |
| saint charbel story / biography / history | /story, /history, /en/biography + 7 locales |
| saint charbel testimony | /testimonies |

## Gap clusters and opportunity scores

Scoring follows docs/SEO-BOT-24-7-OPERATING-PLAN.md:
priority = (impact * confidence) / max(1, effort + risk), 0-5 scale.

### Cluster: pilgrimage and places (beyond Annaya)

1. **saint charbel trail / darb mar charbel** - NEW PAGE (batch 1)
   Intent: learn + visit. Lebanon's first official long-distance pilgrimage
   trail launched 2025-07-20; section A1 Annaya-Mayfouq open. Fresh topic with
   thin, recent competition; strong fit with /visit-annaya.
   Evidence: https://darbmarcharbel.org/ ,
   https://www.lebanontraveler.com/en/magazine/darb-mar-charbel-trail/
   impact 4, confidence 5, effort 2, risk 1 -> priority 10.0

2. **saint charbel places in lebanon / bekaa kafra** - DRAFTED 2026-09-24 (batch 2)
   Intent: learn + visit. Birthplace village, Saint's Cave, route Bekaa Kafra
   to Annaya. Overlaps trail page; may merge into it or become its own guide
   once trail page performance is visible.

### Cluster: identity and patronage

3. **what is saint charbel the patron saint of** - NEW PAGE (batch 1)
   Intent: learn. Direct question SERP; competitor charbel.app ranks with a
   nuanced answer. Honest treatment (devotional custom vs formal decree) is a
   differentiator and matches site rules.
   Evidence: https://vaticanstate.va/en/state-and-government/general-informations/saint-of-the-day/2303-july-24-saint-charbel-makhlouf.html ,
   https://ewtnmission.com/dailysaint/st-charbel-makhlouf/ ,
   https://charbel.app/saints/saint-charbel-patron-saint
   impact 4, confidence 5, effort 1, risk 1 -> priority 10.0

4. **saint charbel quotes** - DRAFTED 2026-09-24 (batch 2)
   Intent: learn. High misattribution risk across the web; authentic material
   exists (homilies/proverbs tradition, "Love Is a Radiant Light", Skandar).
   Only publish with traceable sourcing and labeled devotional reports.
   Evidence: https://en.wikiquote.org/wiki/Charbel_Makhlouf ,
   https://cenaclepress.com/en-us/products/love-is-a-radiant-light

### Cluster: media

5. **saint charbel movie / mar charbel movie / charbel film** - NEW PAGE (batch 1)
   Intent: learn + watch. "Charbel" (2026, dir. Nadim Mehanna) released in
   Lebanon in 2026; international/streaming status unconfirmed. /news covers
   the news angle; an evergreen explainer owns the navigational query.
   Evidence: https://elcinema.com/en/work/2098722 ,
   https://www.cinemacitybeirut.com/Browsing/Movies/Details/f-A000004219 ,
   https://www.thebeiruter.com/article/the-film-about-saint-rafqa/2418 ,
   https://www.rottentomatoes.com/m/charbel
   impact 4, confidence 4, effort 1, risk 1 -> priority 8.0

### Cluster: prayer by need

6. **saint charbel prayer for healing / for the sick** - NEW PAGE (batch 1)
   Intent: pray. Long-tail of the proven "saint charbel prayer" demand;
   existing pages hold prayer texts but none answers "how do I pray for a sick
   person with Saint Charbel". Devotional tradition only, no outcome promises.
   Evidence: site ranking for "saint charbel prayer" (~#6, 2026-09-21);
   competitor: https://charbel.app/prayers/saint-charbel-prayer-for-the-sick
   impact 4, confidence 4, effort 1, risk 2 -> priority 5.3

7. **saint charbel miracles 2025 / 2026** - BLOCKED: needs Joey review
   Known gap since 2026-09-21. Doctrinally sensitive (recent miracle claims);
   per standing rules this content is flagged for Joey review before merge.
   Draft only after his direction on sourcing standard.

### Cluster: worldwide devotion

8. **san charbel mexico / saint charbel around the world** - DRAFTED 2026-09-24 (batch 3)
   Intent: learn. Large Spanish-language devotion (Catedral San Charbel,
   listones tradition). English explainer first; any Spanish-language page is a
   new-language decision reserved for Joey.
   Evidence: https://catedralsancharbel.mx/ ,
   https://desdelafe.mx/noticias/iglesia-en-mexico/los-listones-de-san-charbel-una-tradicion-que-inicio-en-mexico/

### Cluster: papal visit (event demand)

9. **pope leo xiv saint charbel annaya december 2025** - DRAFTED 2026-09-24 (batch 2)
   Intent: learn. Primary source available (Vatican transcript of the
   2025-12-01 visit and prayer at the tomb). Evergreen recap page; check
   overlap with /news first.
   Evidence: http://www.vatican.va/content/leo-xiv/en/speeches/2025/december/documents/20251201-libano-san-charbel.html

## Batch plan

- Batch 1 (this PR): saint-charbel-trail, saint-charbel-patron-saint,
  saint-charbel-movie, saint-charbel-prayer-for-healing. All factual or
  devotional-tradition content; no miracle claims; normal QA gate applies.
- Batch 2 (drafted 2026-09-24, stacked on batch 1): /pope-leo-xiv-annaya-visit,
  /saint-charbel-quotes, /saint-charbel-places-lebanon. Miracles 2025/2026 only
  after Joey's review.
- Seasonal: the 22nd-of-the-month pilgrimage drives a monthly traffic
  spike (next: October 22, 2026). Batch 7 refreshed /22nd-of-the-month with
  an FAQ section + FAQPage schema and linked the novena page into the
  monthly rhythm. July brings the feast novena window (July 15-23) and the
  feast itself (July 24 / third Sunday of July) - plan a June refresh of
  /saint-charbel-novena and /saint-charbel-feast-day ahead of it.
- Batch 3 (drafted 2026-09-24, stacked on batches 1-2):
  /saint-charbel-around-the-world. Next: reassess with Search Console data
  when access lands; miracles 2025/2026 still parked for Joey's review.

## Measurement

- Per page: indexing in Search Console, impressions/clicks by query class,
  CTR at positions 4-20, internal click-through to prayer and visit pages.
- Review date for batch 1 pages: 2026-10-24 (or first Search Console export).
- Rollback: delete the page file and sitemap entry; internal links are in
  single, listed edit points per source page.
