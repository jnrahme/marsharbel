# Qadisha Valley: English and Arabic keyed mirror

## Scope
English `/qadisha-valley` remains the master. `/ar/qadisha-valley` reproduces the nine sections, four licensed images, ten subheadings, all citations and the existing top language selector through one keyed template. The next locale mirrors should add full catalogs and routes, not a second template or a hand-authored catalog topic.

## Correction
The English master said the Qadisha Valley, Cedars and Charbel's birthplace were "three World Heritage neighbors within a fifteen-minute drive." UNESCO inscription 850 covers the Qadisha Valley and Cedars of God, not Bekaa Kafra as a third listed property; a precise drive time also lacked support. Both catalogs now distinguish the nearby birthplace from the inscription and qualify travel time. Source: https://whc.unesco.org/en/list/850/

## Build and checks
`locales/registry.json` owns authored routes. `scripts/i18n/qadisha_mirror.py` renders both pages, validates complete catalogs and escapes copy at the boundary; build outputs reciprocal hreflang, sitemap and locale selector routes. Existing English Annaya correction remains verified by `qadisha_copy.validate`. Unsupported destinations stay on their real English URLs. SEO generator skips authored mirrors to avoid replacing their metadata or schema. No frozen baseline expansion.

`npm run i18n:check`, `npm run i18n:test`, `python3 scripts/qa/check_seo.py`, SEO regression tests, and 20 focused Playwright tests passed across phone, tablet and desktop. Full QA and whole-suite Playwright were interrupted by the tool time cap while still running and are not claimed complete. Native Apache/LiteSpeed and deployed-route checks remain for integration. Reviewed full-page desktop and mobile screenshots of the Arabic page after font/layout adjustment; images, captions, sections, FAQ, sources and footer remain readable with no horizontal overflow. No deployment or stage merge from this branch.
