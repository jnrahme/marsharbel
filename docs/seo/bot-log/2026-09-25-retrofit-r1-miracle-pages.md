# 2026-09-25 - Retrofit R1: 5 miracle child pages to editorial-quality standard

Joey's 4:31 PM voice note (via parent): apply marsharbel-editorial-quality to
every article/news/information page. R1 = the miracle child pages (parent's
priority order). Retrofit = enhance, not rewrite (pages date from batch 13).

## Applied per page
- "At a Glance" fact box after the hero (Who/When/Where/Status), built from
  existing components (card update + kicker - no CSS changes). Status rows
  carry the claim/status distinctions verbatim from each page's evidence
  sections (bishop's recognition vs Vatican declaration; private revelation
  vs ecclesial recognition 2010; register entry vs under study).
- Watch sections: "Prefer to read?" text summary + YouTube fallback watch
  links with durations (skill: video adds first-hand witness; readers who
  do not play still get the content).
- Sources tightened: publisher - title - what it supports (dates where
  certain; no invented dates).
- Same-day oEmbed verification for all 7 embedded videos (200s, titles
  match captions) per marsharbel-video-media.
- No hand-added JSON-LD touched; hand-authored Article blocks preserved.

## QA
check_seo green (130), test_seo 15/15, i18n policy green (baseline refreshed
for 5), sync-navigation 0/82, diff --check clean. Playwright: fact boxes +
fallback links present on all 5, zero console errors, desktop + mobile
screenshots inspected.
