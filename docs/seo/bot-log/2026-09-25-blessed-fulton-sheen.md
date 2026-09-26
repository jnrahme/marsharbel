# 2026-09-25 - Blessed Fulton Sheen page + /saints hub + news card (Joey's 6:00-6:03 PM orders)

Ordered by Joey via WhatsApp: full page for Blessed Fulton Sheen (beatified
yesterday, Sept 24 2026), a news card, a /saints hub kicking off a standing
saints series, and Saints as a top-level nav tab.

## Shipped
- blessed-fulton-sheen.html: editorial-quality page. He is BLESSED, never
  called a saint - hero, At a Glance status line, "What Beatification
  Means" section, and FAQ all keep the beatified-vs-canonized distinction.
  Grounded in Vatican News (Sept 23 2026: Pope Leo's General Audience
  tribute, Louvain/Washington studies, Life Is Worth Living 1952-1957,
  1953 Emmy, Rochester 1966, died December 1979; March 25 2026: venerable
  2012, miracle decree 2019) and Catholic Register/OSV News (Sept 24 2026:
  declaration, ~50,000 attendance, Tagle presiding, Engstrom miracle 2010,
  mandible relic). 5 YouTube talks embedded (oEmbed-verified 200 today,
  CatholicClips channel, nocookie lazy iframes, exact oEmbed caption
  titles, topic summaries, fallback watch links) + official archive link
  (fultonsheen.com/full-video-audio-library). No hero image: no
  rights-cleared Sheen photo available.
- 3 of Joey's 8 video IDs dropped (oEmbed 404): YRZJeHI8aiw, L-vrnkla2T8,
  YL77iqiRMy0 ("The Celebrity Priest Who Couldn't Be Bought") - reported.
- saints.html: hub for the series. Whole-card clickable cards with status
  tags (Canonized 1977 / Saint 4th-5th c. / Canonized 2004 / Canonized 2001
  / Beatified September 24 2026), Saint Charbel card pointing to his story,
  "How This Series Works" section. Adding a future saint = one card.
- news.html: dated whole-card item (September 24, 2026 - Beatification) at
  top, linking both sources + the new page; footer date updated.
- Nav: "Saints" top-level tab between Miracles and Prayer (direct link,
  Gallery pattern), partials/primary-navigation.html + sync-navigation
  across 84 pages. testimony-review.html left unsynced per standing
  practice (tool page outside editorial scope).
- sitemap + feed.xml rebuilt; baselines registered for all changed pages.

## QA
check_seo green (132 indexable, +2 new), test_seo 15/15 (generator
repeatability on both new pages - generator stamped their JSON-LD),
i18n policy green, sync-navigation green (except testimony-review by
design), news thumbs + feeds checks green, diff --check clean. Playwright
desktop + mobile: hero, At a Glance, talks grid (YouTube thumbs loading),
saints hub, news card, mobile nav all render correctly; only console
notice is the site-wide compute-pressure permissions policy line.
