# Mobile performance and international discovery

These changes are local and require Joey's review and explicit approval before pushing or merging into `stage`. Stage currently publishes to the public Hostinger website.

## Implementation

- Serve the existing Cormorant Garamond and Manrope fonts locally, with their original Unicode subsets and OFL licenses. Preload the Latin subsets.
- Serve AVIF homepage images with WebP fallbacks, preserving the original JPEG for sharing metadata and existing links.
- Reserve header space for the language selector and batch reveal layout measurements to prevent avoidable layout work.
- Defer homepage scripts in their original order.
- Generate the smaller `home.css` from `styles.css` and homepage/runtime sources. `npm run build:home-css` regenerates it; QA fails if it is stale. Other pages retain the full stylesheet.
- Add substantive Arabic and French introductory pages at `/ar` and `/fr`, with self-canonicals, reciprocal language links, sitemap entries, and visible language navigation. Arabic is right-to-left. Both pages work without JavaScript. These are initial translations for editorial review, not a translation of every linked resource. Linked resources explicitly disclose their English origin and automatic translation/audio limitations.
- Include all new image and font assets in deployment verification.

## Reproduce verification

Start a production-like local server:

```sh
node scripts/dev-server.mjs --port=4191 --compress
```

Compression is optional and mirrors Hostinger's existing gzip delivery. The regular preview at port 4190 is uncompressed; do not compare scores from these two server modes as though compression were a newly deployed improvement.

```sh
PORT=4191 BASE_URL=http://localhost:4191 npm run qa
PORT=4191 BASE_URL=http://localhost:4191 npm run quality:e2e -- --workers=2
python3 -m unittest discover -s scripts/qa -p 'test_*.py'
python3 scripts/qa/verify_deployment.py --base-url http://localhost:4191 --attempts 1
npx lighthouse http://localhost:4191/ --quiet --chrome-flags='--headless' --only-categories=performance,accessibility,best-practices,seo --output=json --output-path=/tmp/marsharbel-mobile-review.json
```

Use the explicit port to avoid testing a different existing preview. Measure Lighthouse separately from browser test suites. Local scores are lab measurements, not a guarantee of the live score or field Core Web Vitals. After approval and deployment, check the live website again.

## International search follow-through

The live robots file permits crawling and its sitemap currently contains 42 public URLs. The proposed sitemap contains 44. The traffic-by-country dashboard is a record of requests, not a geographic search restriction.

Before publishing, review the French and Arabic wording. After publishing, confirm sitemap processing and inspect the new canonical URLs in Search Console. Monitor impressions and clicks by country, language-related query, and page. Extend the translated content with reviewed biography, prayers, and Annaya visitor information according to actual search demand; do not publish large batches of unreviewed machine translations or invent search-volume claims.

Google recommends separate URLs for language versions and language annotations: https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites

Speed, indexing eligibility, and translations help discovery; none guarantees rankings or visitor numbers. Local audits cannot prove access from every country or network.

## Verified final results (local, 2026-09-22)

- Two consecutive final mobile Lighthouse runs: performance 100, accessibility 100, best practices 100, SEO 100; LCP 1.9 s, CLS 0. Both used port 4191 with gzip. Earlier intermediate versions varied between 98 and 100; these results do not guarantee a permanent live score.
- Full QA suite passed against port 4191. Speech-synthesis sanitization checks skipped because this environment has no installed voices.
- 125 responsive browser quality tests passed against the same preview, across five screen sizes.
- Eight Python regression tests passed. Runtime SEO verified 44 public pages, seven noindex pages, reciprocal language annotations, non-JavaScript translated content, and returning to English after selecting French.
- Arabic/French and homepage layout/accessibility spot checks passed at 390 and 1440 pixels. Homepage computed styling matches the full stylesheet at both widths.
- 97 frontend files verified against the local preview. All app-manifest icons and service-worker precache URLs return 200.
- App icons now use smaller versioned PNGs. The service-worker cache is updated and includes home.css. The manifest no longer describes the independent site as official.

Final reports: `/tmp/marsharbel-mobile-icons.json` and `/tmp/marsharbel-mobile-icons-repeat.json`. Nothing in this change set has been pushed or deployed; the live site must be measured after approval and deployment.
