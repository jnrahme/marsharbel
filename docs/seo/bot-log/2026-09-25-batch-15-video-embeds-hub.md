# 2026-09-25 - Batch 15: miracle video embeds + /videos hub

Parent spec 2026-09-25 2:08 PM (Joey's direct ask, voice note 2:04 PM per parent):
embed 1-2 verified videos per miracle page in the story flow; new /videos hub
with Documentaries / The Movie / 6-Part Film / Miracles / Annaya & the
Hermitage / Relic Tours; Our Film slot reserved but NOT published (gated on
Joey's visual review); youtube-nocookie iframes; no hand-added schema
(generator-clean rule from batch-14 process fix).

## Shipped
- /videos hub: 23 embeds across 6 sections, each section intro links the
  relevant pages (miracles hub + child pages, visit-annaya, hermitage,
  relics); Our Film slot present as an HTML comment only; fine-print note on
  third-party hosting + youtube-nocookie privacy behavior
- Miracle pages: Watch sections placed next to their story content -
  nohad (2 embeds: 15:54 primary + 5:01 archival), dafne (2: 19:01 + 7:18
  Phoenix parish), canonization (1: 6:00 archival 1965), raymond (1: 7:01 +
  comment noting AR version m9jEoRCK2jw for the intl lane), register (1:
  2:20 Tablet coverage)
- miracles.html hub links the new videos page
- sitemap +1 (/videos, monthly, 0.8); i18n baseline registered for all 7
  touched pages via the policy script's own extractor
- CSP: frame-src https://www.youtube-nocookie.com added to netlify.toml
  (separate commit; parent-approved 2:08 PM as the required enabler of
  Joey's explicit YouTube-embeds request; no other directives touched)
- Skipped yYK9Oexw8eo per spec (login-required, dead embed)

## Generator-clean rule applied
No hand-added JSON-LD anywhere. videos.html authored with title + canonical +
description; apply_seo_tags.py generated the full meta/WebPage block.
VideoObject schema requested from the technical lane as a generator feature
(via parent).

## QA
check_seo green (125 indexable), test_seo 13/13 (incl. repeatability),
check_i18n_policy green (acorn installed per package.json - it was missing
from local node_modules), sync-navigation 0/80, diff --check clean,
sitemap_lastmod current. Playwright: videos hub 23 iframes, nohad 2,
register 1, all youtube-nocookie, zero console errors, desktop + mobile
renders verified (embed thumbnails load).
