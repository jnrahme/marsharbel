# English Letters display and homepage entry, September 25, 2026

## Changed

Renamed the English visitor-facing Testimonies page and navigation entry to Letters. Added a homepage letter field that grows as readers type and carries the draft in same-tab storage to the existing private submission form. No draft text enters the URL. Readers complete their name and consent there; failed submissions retain the draft, edits on the second page update the saved draft, and confirmed intake clears it. Publication remains subject to human editorial review. The `/testimonies` and `/submit-testimony` URLs, database tables, moderation behavior, and voice-testimony feature names remain unchanged.

The source-published historical/ministry accounts remain labeled as accounts rather than letters sent to this site. New English display strings are cataloged separately from the frozen legacy baseline in `locales/en/letters-display.json`. Existing non-English pages were not translated. The Arabic miracles-section testimony entry is a separate factual account, not a reader submission label.

## Why and expected impact

This follows the site's preferred Letters language and makes writing from the homepage easy on mobile. The same indexed archive URL and attribution boundaries are retained. This is a UX and display change, not a claim of improved rankings or a live-publishing change.

## Checks and next

CI QA components passed in two bounded batches because the combined rosary suite exceeds the execution window of a single shell command: home CSS freshness, 25 i18n tests, SEO metadata/sitemap, feeds, static archive, submission security, site smoke, and rosary tests. The long checklist suite passed separately. The new home-to-submit browser regression covers 390px and 1366px, empty validation, textarea growth, prefill, reload, storage failure, and draft retention/clearance across failed and successful mocked intake. Navigation sync: 82 pages and zero drift. Desktop/mobile homepage and Letters hero screenshots were inspected; live deployment is still pending integration.

After merging, translate the English new-label catalog and review the 7 translated homepages and Arabic miracles entry in context. Check the real intake configuration separately before promising that letters can currently be sent.
