# 2026-09-25 - Batch 17: curated video testimonies on /testimonies

Parent spec 2026-09-25 2:34 PM (Joey's ask): curated video testimonies
section, youtube-nocookie lazy embeds, no hand-added schema (VideoObject
via generator when the technical-lane feature lands). All 9 videos verified
playable + embed-enabled by the competitor lane today.

## Shipped
- New "Video Testimonies" section on /testimonies, placed after the
  source-published accounts section (outside the baseline-testimonies
  markers that #144's static archive owns), closing the page.
- Featured lead: Deacon Michael Chirichella (US, cancer, 2026, 2:47).
- Lead grid: Yassine Jaber (Sunni Muslim witness, 31:15), Dafne Gutierrez
  at her Phoenix parish (7:18, linked to her miracle page).
- "Watch their stories" grid: Serrano (10:08), Eid podcast (33:08),
  Raymond Nader EN (7:01, linked), Nohad OTV Arabic (39:54, linked),
  Nohad + Saad MTV Arabic (31:38), Dafne Telemundo Spanish (4:20).
- One-line captions (who, what, where, duration); section-sub carries the
  honesty line: personal testimonies, not medical verification or official
  Church recognition; nocookie-until-play note.
- HTML comment for the intl lane: /ar leads Arabic items + Raymond AR
  version m9jEoRCK2jw; /es features Telemundo.
- i18n baseline refreshed for testimonies.html.

## QA
check_seo green (125), test_seo 14/14, i18n policy green, nav 0/80,
diff --check clean. Playwright: 9 iframes all youtube-nocookie, zero
console errors; featured embed render-verified with thumbnail (desktop +
mobile).
