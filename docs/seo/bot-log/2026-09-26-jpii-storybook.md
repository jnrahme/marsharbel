# Bot log - John Paul II storybook page (/jpii-story)

Date: 2026-09-26
Branch: seo/jpii-storybook (based on the pio-storybook tip f9e7ff7, fetched locally as pio-sb-tmp; that bundle is ahead in the integrator queue and this change requires it)

## What changed
- New page jpii-story.html: "The Story of John Paul II" - 11-page read-aloud storybook for children, following the Pio storybook pattern (same parameterized player, data-story="jpii"). Hero, player, per-page evidence panel, composite-scene disclosure, "What Young Hearts Can Learn" lesson cards, "True Dates" list, Research Basis links, IndexNow ping on load.
- storybook.js: getStoryId recognizes 'jpii'; JPII_STORY_EN (11 pages: bodies verbatim from the parent-supplied asset package pages.json; prayer + heart cards authored in the established child-friendly pattern); STORY_PAGES.jpii; VOICE_PACKS.jpii (kokoro-jpii, base ./media/storybook-jpii/en); 4 EVIDENCE_SOURCES entries (vaticanJPIIBiography, vaticanJPIIInaugural, vaticanJPIIWYD, domjp2Family); recommendedId chain extended (jpii recommends pio).
- media/storybook-jpii/images/page-01..11.webp (1280x720, 113-211KB) and media/storybook-jpii/en/page-01..11.mp3, copied from the parent-supplied asset package (jpii-storybook-assets-private-v1-221928a0.zip).
- sitemap.xml: /jpii-story entry (weekly, 0.9), matching the /pio-story pattern.
- locales/legacy-text-baseline.json: wording registered for jpii-story.html (83 entries) and storybook.js (323 entries) using the policy script's own extractors (Counter max-merge; root js via scripts/i18n/extract-js-text.mjs).

## Provenance
- Asset package: /downloads/jpii-storybook-assets-private-v1-221928a0.zip (parent-supplied, 11.4MB): 770-word story (~5:55), 11 page MP3s (Kokoro am_michael 0.94), 62 sentence FLACs (not shipped in this change), SRT, pages.json, source-notes.txt.
- illustrations are imaginative watercolor-like composites; the page carries the package's illustrationDisclosure line, same as the Pio storybook page.
- Source URLs re-verified reachable today (curl 200): Vatican canonization biographical profile (2014), Vatican WYD chronicle, 1978 inaugural homily, domjp2.pl/en/the-wojtyla-family.

## Verification
- python3 scripts/qa/check_i18n_policy.py - passed (no new legacy wording).
- python3 scripts/qa/check_seo.py - passed for jpii-story.html; stale-lastmod flags for pio/jpii/teresa/saints are pre-existing on this branch base (predates #206's lastmod bumps) and vanish on rebase.
- git diff --check - clean.
- node --check storybook.js - passed.
- scripts/apply_seo_tags.py ran; its edits to pio-story.html and the jpii/teresa datePublished bumps were reverted (not this bundle's files). On jpii-story.html it rewrote og:image/twitter:image to the default saint-charbel.jpg; restored to media/storybook-jpii/images/page-01.webp. It also fixed pio-story.html's stale og:title ("Saint Charbel Story for Kids") in its own working copy - that fix was reverted here since pio-story.html belongs to the pio-storybook bundle; flagged for the integrator.
- Playwright render (mobile 390x844, desktop 1440x900, local http server): /jpii-story.html loads with zero page errors, page 1 "A Boy in Wadowice" -> Next -> page 2 "A Family That Prayed", illustration ./media/storybook-jpii/images/page-01.webp, prayer/heart/evidence cards render, lesson cards render. Regressions: /story.html (Charbel) and /pio-story.html (Pio) load with zero page errors.
- Pixel review of mobile + desktop screenshots: layout, typography, evidence labels, and imagery all as intended; forgiveness page imagery is nongraphic.

## Flags
- Merge order: this change requires the pio-storybook commit f9e7ff7 (storybook.js parameterization). Per parent it joins the queue after prayer-hub merges.
- pio-story.html on the pending pio-storybook bundle has og:title/twitter:title saying "Saint Charbel Story for Kids" (copy-paste from the template). apply_seo_tags regenerates it correctly from the h1; fix belongs to a touch-up of that bundle.
- IndexNow: /jpii-story should be submitted after merge.
