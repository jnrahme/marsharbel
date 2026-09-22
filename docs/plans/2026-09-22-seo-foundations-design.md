# SEO and publishing setup

Status: SEO implementation prepared for reviewed release. Infrastructure migration below remains proposed.

## Recommended architecture

Use feature branches for changes, `stage` for a separate password-protected staging website, and `main` for production at https://marsharbel.com. Today Hostinger deploys `stage` directly to production; migrate deliberately after the separate environment is validated. Do not change the current branch mapping before its replacement works.

Require PR checks before merging. Deploy one tested revision at a time, verify public files after deployment, keep a known good release and test rollback. Confirm hosting capabilities before choosing an atomic release mechanism or changing providers. Keep credentials out of Git and enable MFA for owner accounts.

## SEO first pass

Observed on 2026-09-22: four public editorial pages absent from the sitemap; the shop planning page indexable; /index duplicates the homepage; www also serves the site. The existing canonical tags already prefer HTTPS without www. Search Console verification files exist, but current ownership, sitemap submission, and indexing status have not been confirmed.

Implemented changes:

- Add four omitted editorial pages to the sitemap and keep unfinished shop/account tools out of search.
- Preserve authored canonical/noindex metadata after JavaScript executes; consolidate www and explicit index URLs. Use absolute URL paths in extension redirects.
- Preserve authored structured data and descriptions when regenerating metadata; escape attribute values and support checkouts under `/tmp`.
- Add a homepage WebSite graph, neutral site description and explicit biography heading.
- Remove hreflang annotations for runtime-only translations that canonicalize to English. Keep the visitor language selector and English/x-default annotations. Reviewed, independently indexable translations are future work.
- Preload the hero image; serve smaller homepage WebP previews with intrinsic dimensions. Original media stays available. The two previews shrink from 739,028 to 178,112 bytes (about 76%).
- Keep content visible without JavaScript and avoid hiding above-fold text for reveal effects; respect reduced-motion preferences for those transitions.
- Add CI checks for sitemap coverage, canonicals, headings, image alt attributes, local references, JSON-LD syntax and browser-rendered metadata. Extend deployment verification to sitemap/robots and optimized previews.

## Validation on 2026-09-22

- 42 indexable pages pass static and rendered metadata checks; 7 private/unfinished pages retain noindex in the browser. Tracking parameters preserve the canonical URL. Homepage heading remains visible with JavaScript disabled.
- All 1,254 local references inspected resolve. Every indexable page has one H1 and image alt attributes.
- Eight Python regression/deployment-verifier tests pass; generator remains repeatable and preserves authored graphs/noindex.
- Apache: six redirect cases (including www, nested HTML paths and query preservation), six successful routes, and a genuine 404 pass. Google verification files remain reachable. The gallery shares its name with a media directory; its existing special rewrite is retained.
- 125 Playwright quality tests across five viewport sizes pass. Dead-code checks pass.
- Full application QA passed in the first run. A later concurrent run failed three timing-sensitive voice-player assertions; the complete checklist suite passed when rerun in isolation. Speech synthesis sanitization tests skip because the environment has no voices. GitHub CI remains a separate release gate.
- Local mobile Lighthouse: initial 79 performance / 100 accessibility / 100 best practices / 100 SEO; optimized run 95 / 100 / 100 / 100, LCP 2.8s, CLS 0.054, TBT 0ms. Lab results vary and are not production field data or ranking guarantees. LCP still exceeds the 2.5s good threshold; font/CSS loading and hosting delivery remain performance opportunities.
- Search Console opens signed out in the available in-app browser. Index coverage, ownership and traffic were not verified. No sitemap submission or indexing request has been claimed.

## Next steps

1. Establish separate staging and validate the deployment/rollback process there.
2. Verify Google Search Console ownership and inspect indexed pages, canonical selection and sitemap status. Record the first 28-day baseline for clicks, impressions, query positions and top pages.
3. Review and release the first SEO changes through the checked pipeline. Inspect important URLs after release.
4. Prioritize accurate, sourced Saint Charbel prayer/novena/biography pages and useful Rosary guides using actual search queries. Do not invent authority, miracle verification, search volume or affiliations.
5. Audit mobile performance and returning-browser behavior. Review multilingual rendering before expanding language targeting; current query-string translations need a separate indexing audit.
6. Review search performance monthly against comparable periods. Ranking improvement is an outcome to measure, not a guaranteed release result.

References: [Google SEO guidance](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), [Search Console setup](https://developers.google.com/search/docs/monitor-debug/search-console-start).
