# International publishing and search operations

## Current implementation

Forty static reading guides cover five topics in eight languages: English, Arabic, French, Spanish, Portuguese, Italian, German and Polish. Seven localized homepages complement the existing English homepage. All new content is stored in keyed `locales/<code>/common.json` and `pages.json` catalogs; `locales/registry.json` owns languages, routes and topic structure. See `locales/README.md` for the editing workflow and `AGENTS.md` for mandatory engineering rules.

Run `npm run i18n:build` after editing catalogs. `npm run i18n:check` verifies reproducible output and rejects newly hardcoded legacy wording; `npm run i18n:test` exercises invalid catalogs and safe rendering. These checks run in full QA. Missing translations never silently fall back to English. Generated pages use a small shared stylesheet and no JavaScript, webfont downloads, analytics tags or third-party scripts.

Equivalent guides have reciprocal eight-language hreflang and an English x-default. Related legacy English interactive experiences are linked separately rather than falsely declared exact translations. Homepage alternates connect all eight languages. Visitors choose their language; there is no forced country/IP redirect.

`/ar` and `/fr` keep their published canonical URLs. All locale directories disable DirectorySlash and directory indexing, and root rewrite rules preserve their homepages. English `/en` redirects to `/`; its guides have their own `/en/...` routes. Verify Apache/LiteSpeed behavior locally and again on Hostinger after deployment.

The legacy interactive experiences are not fully catalog-migrated. Their pre-existing wording is frozen in `locales/legacy-text-baseline.json`; new or changed wording must migrate to catalogs. The JavaScript guard is heuristic and does not replace review of dynamic or inline-script text.

## Editorial review completed by the assistant

User direction on 22 September 2026: do not block on external reviewers; use authoritative research and best judgment for all eight languages’ wording. A human/native-speaker review has not been claimed.

Reviewed each resource for language consistency, factual dates, source attribution, names, theological framing, and promises of outcomes. Prayers address God and ask for the saint's intercession. Original devotional prayers and the nine-day reflection series are labeled as original site material, not official liturgy or a reproduction of the monastery's traditional novena. No modern prayer translation has been copied wholesale. The Rosary guides explain the structure and link to traditional prayer texts.

Source comparison caught an inconsistency on the monastery biography page: its prose says January 5, 1965, while its timeline and the papal canonization homily support December 5, 1965 for beatification. Our guides use December 5. Primary-source cross-checking takes precedence over copying a single page.

The Rosary's weekly distribution is presented as customary and adaptable. Annaya guides direct visitors to current monastery information instead of asserting fixed travel conditions or schedules.

Sources consulted 22 September 2026:
- Monastery biography: https://saintcharbel.com/saint-charbel-biography/
- Monastery hermitage: https://saintcharbel.com/the-hermitage/
- Monastery and current celebrations: https://saintcharbel.com/
- Monastery traditional novena: https://saintcharbel.com/novena-of-saint-charbel-en/
- Paul VI's canonization homily: https://www.vatican.va/content/paul-vi/fr/homilies/1977/documents/hf_p-vi_hom_19771009.html
- Vatican Rosary guide: https://www.vatican.va/special/rosary/documents/misteri_fr.html
- Vatican News French prayer reference: https://www.vaticannews.va/fr/priere/rosaire.html

## Before publishing a new batch

1. Rebuild: `python3 scripts/build-international.py`.
2. Check metadata, sitemap, reciprocal alternates, and local links: `python3 scripts/qa/check_seo.py`.
3. Run Python checks: `python3 -m unittest discover -s scripts/qa -p 'test_*.py'`.
4. Run the full QA suite with an explicitly selected preview port: `PORT=4191 BASE_URL=http://127.0.0.1:4191 npm run qa`.
5. Run responsive international browser checks: `PORT=4191 BASE_URL=http://127.0.0.1:4191 npx playwright test tests/international.spec.js --workers=3`.
6. Against an Apache/LiteSpeed preview, run `python3 scripts/qa/check_language_routes.py http://127.0.0.1:4192`. The Node preview does not implement Apache redirect rules.
7. Inspect mobile screenshots and run mobile Lighthouse under consistent conditions.
8. Joey reviews the pages locally and explicitly approves the push. Stage currently publishes the public website.
9. After the authorized deployment, run `python3 scripts/qa/verify_deployment.py --help` and invoke its live verification with the approved checkout. Also run `python3 scripts/qa/check_language_routes.py https://marsharbel.com`.

## Bing setup: prepared, not verified yet

The marsharbel.com property has been added to Bing Webmaster Tools under the personal Google sign-in. The public ownership meta tag is in the local homepage. It has not been deployed, so Bing verification is pending.

After the approved batch is live, return to https://www.bing.com/webmasters/ and verify the homepage meta tag. Submit https://marsharbel.com/sitemap.xml from the verified property. This method does not require granting Bing access to all Google Search Console properties.

## IndexNow: prepared, no submission made

`indexnow-key.txt` is a public ownership proof, not a private credential. `python3 scripts/submit-indexnow.py` previews the sitemap payload without network submission. After publication approval and successful live verification, run `python3 scripts/submit-indexnow.py --submit`. The script checks that the key and frontend files are deployed and URLs resolve directly before notifying IndexNow. Prefer `--url https://marsharbel.com/...` for only changed pages on later releases.

IndexNow does not submit URLs to Google and cannot guarantee inclusion in any search engine. Reference: https://www.indexnow.org/documentation

## Weekly measurement workflow

Use Search Console Performance > Search results, Web search, and compare equal 28-day periods. Export Countries, Queries, and Pages separately. Record date range, property, filters, clicks, impressions, CTR, and average position. Keep account exports outside the public web repository.

Use `python3 scripts/report-search-countries.py Countries.csv --previous PreviousCountries.csv` to summarize country coverage and change. Without a prior export, omit `--previous`. The script reads only local CSV files and sends nothing externally. Keep original exports for auditing; query anonymization means visible query rows may not sum to headline totals.

Group pages by each language route and English URLs. Investigate indexing before interpreting traffic. A few impressions or a single click are early signals, not an established audience. Hosting requests include automated traffic and are not substitutes for organic-search metrics.

No scheduled monitor or visitor analytics collection has been enabled. A 90-day traffic outcome cannot be measured on release day. All eight requested languages are included in this local batch. Use Search Console data to prioritize further content and countries; language availability does not guarantee indexing, rankings or traffic.

## Earlier two-language verification (superseded by the eight-language checks below)

- 54 indexable pages match sitemap, metadata, links, and reciprocal language annotations.
- 12 Python tests passed, including localized metadata preservation and a deliberately broken reciprocal language link.
- Full existing QA passed; speech-synthesis sanitization skipped because the test environment has no installed voices.
- All 195 responsive browser tests passed, including 70 international page/navigation/accessibility checks across five viewport configurations.
- Nine Apache route checks passed; 109 frontend files matched the checkout when fetched from the local Apache server. This is local server verification, not a new live deployment.
- Arabic and French prayer pages each scored 100 for mobile Lighthouse performance, accessibility, best practices, and SEO; LCP 1.1 seconds and CLS 0. These are local lab measurements.
- Arabic and French phone screenshots inspected; no clipping or horizontal overflow detected.
- Dead-code and whitespace checks passed. IndexNow preview and payload validation passed without submitting requests.
- Existing port 4190 preview verified to serve the current language homepages and prayer guides.

Google accepted indexing requests for the already-published /ar and /fr introductions. The new resource URLs were not submitted because they are not yet published. No changes were pushed to stage in this batch.

## International implementation references

- Google localized-page guidance: https://developers.google.com/search/docs/specialty/international/localized-versions
- W3C language declarations: https://www.w3.org/International/questions/qa-html-language-declarations

Language annotations use reciprocal, fully qualified alternate URLs; every generated page declares its actual language and writing direction. Topic links preserve the selected content across languages. A page being technically eligible for indexing does not establish indexing or search traffic.

## Eight-language verification — 22 September 2026

- Eight complete catalogs generate 40 guides and seven localized homepages; the existing English homepage remains in place.
- Catalog parity, plain-text validation, route/source validation, output freshness and the frozen legacy wording policy pass.
- All 31 Python tests pass, including deliberately invalid catalogs, hardcoded page/template messages, unsafe source links, escaping, SEO and missing/stale deployed files.
- All 440 responsive browser checks pass across five screen sizes. After moving the legacy navigation's accessible label into the catalog-generated block, all 40 affected navigation checks pass again.
- Full existing QA passes. Speech-synthesis sanitization is skipped because no voices are installed in the test environment.
- SEO validation passes for 89 indexable URLs. All 143 Apache language route checks pass. The local Apache server serves 145 frontend files matching the checkout. These are local checks, not a new deployment.
- Mobile Lighthouse measures 100 performance, accessibility, best practices and SEO for the homepage and representative Arabic/German prayer guides. Homepage LCP is 1.8 seconds; both guides are 1.1 seconds. All have zero CLS. These lab scores do not guarantee field performance or rankings.
- Arabic, German and Spanish mobile screenshots and the expanded homepage language menu have been inspected. Language targets on legacy pages are at least 44px high and wrap without horizontal overflow.
- Dead-code, JavaScript syntax and whitespace checks pass. IndexNow payload preview completes without submitting requests.
- Local port 4190 serves the current work. Nothing in this eight-language batch has been pushed; Bing ownership verification and publishing the new URLs remain pending local review and explicit approval.

The catalogs cover the new international reading resources. Legacy interactive experiences remain a documented migration backlog; do not represent this rollout as complete whole-site localization.

## UI correction — 22 September 2026

Joey rejected the additional language menus because the app already has a top language selector. The homepage footer list and five in-content language lists have been removed from the generator, along with their unused styles. The existing top selector and its locale routing remain. Standalone guides retain their single header language control. This supersedes the earlier expanded-menu design and tap-target test; regression coverage now checks that existing pages have exactly one selector and no extra language menus. SEO metadata, sitemap entries and translated guide content are retained. The rule is recorded in `AGENTS.md` and `locales/README.md`.
