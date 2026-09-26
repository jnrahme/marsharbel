# 2026-09-26 - generator extension: FAQPage + TouristAttraction schema

## Task
Parent 5:45 AM: extend apply_seo_tags.py for FAQPage + TouristAttraction - the reason qadisha-valley and future places pages ship without them (hand-added JSON-LD is forbidden, so the generator owns the fix).

## Design
- FAQPage: parsed from a page's "Frequently Asked Questions" section. TWO authored formats covered: h3 question + p answer (bekaa-kafra/qadisha style) and bold-led paragraphs "<p><strong>Q?</strong> A</p>" (saint-charbel-pilgrimage style). Answers are stripped to visible text (links keep their anchor text), entities resolved, whitespace collapsed.
- TouristAttraction: data-driven membership - pages in the nav partial's Places dropdown (partials/primary-navigation.html), so future cluster pages pick it up automatically. Fields: name (page title), description, url, image, containedInPlace Country Lebanon.
- Ownership rule: an existing FAQPage or TouristAttraction block (authored or previously generated) always wins - the generator never duplicates or rewrites it. ~12 pages already carry authored FAQPage blocks (e.g. how-did-saint-charbel-die, prayer-for-* pages); they are untouched. This also makes the generator naturally idempotent (rerun = 0 files).
- Only indexable, generator-managed pages (skips noindex, i18n-generated, authored-@graph pages).

## Output (this run)
- FAQPage added to 12 pages: bekaa-kafra, qadisha-valley, blessed-fulton-sheen, st-anthony-of-padua, st-augustine-of-hippo, st-francis-of-assisi, st-john-chrysostom, st-john-paul-ii, st-maroun, st-padre-pio, st-teresa-of-calcutta, saint-charbel-pilgrimage (bold-format).
- TouristAttraction added to 5 pages: bekaa-kafra, visit-annaya, saint-charbel-places-lebanon, saint-charbel-hermitage, saint-charbel-trail.
- qadisha-valley got FAQPage only: TouristAttraction membership is read from the Places dropdown, and the dropdown bundle (7cf2cdb) had not merged at build time. The next generator run after that merge adds it automatically - no code change needed.

## Verification
- Every JSON-LD block on every changed page parses (json.loads).
- Idempotency: second generator run updated 0 files.
- Full QA suite green (chunked; suite exceeds the 120s bash window): build-home-css, i18n check+test, check_seo + test_seo, feeds, testimony baseline/static, testimony-security, site-smoke, all 6 rosary sub-suites.
- No nav, sitemap, baseline, or i18n changes in this bundle (schema-only + script).
