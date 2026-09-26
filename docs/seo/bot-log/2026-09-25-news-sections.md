# Bot log - 2026-09-25 - /news two-section restructure + card header photos

## Scope
Joey 2026-09-25 10:41 PM (via main): (1) header pictures on the latest news cards - real rights-clean photos, license captions per standard; (2) restructure news.html into two sections: TOP = news of Saint Charbel and the Lebanon saints; BELOW = world saints + Maronite/Catholic community news; re-file existing cards (Sheen beatification -> world section); make the split the standing news-desk pattern. Full SEO standard, i18n baseline registration, IndexNow /news after merge. Queued behind the merge train.

## What shipped
- news.html restructured: "Charbel The Movie" section unchanged at top; "Recent News, Newest First" renamed to "News of Saint Charbel and the Lebanon Saints" (7 Charbel cards, unchanged order); new section "World Saints and the Wider Catholic Family" below it holding the Sheen beatification card; hero intro updated to describe both sections; Editorial Standard unchanged.
- Header photo on every dated news card (9 figures total incl. movie poster): movie poster, annaya-entrance-pilgrims (Byblos walk card - the actual 320px walk photo was too small for a header; monastery-entrance pilgrims photo captioned honestly as the walk's destination), saint-charbel-portrait (Borik), trail-pilgrimage-hero (Trail), charbel-historic-photo (Revesby), charbel-tomb-vigil-lamp (Cebu relic), annaya-monastery (miracles register), pope-annaya-hero (papal visit), blessed-fulton-sheen (Sheen). All reuse rights-recorded site assets - registry entries appended.
- scripts/build_feeds.py: SECTION constant -> SECTIONS tuple covering both new section headings (feed keeps aggregating every dated card, sorted newest first; movie cards still excluded as before). feed.xml regenerated - byte-identical output (same 8 cards), test_feeds 4/4 OK.

## Photo choices
Every header is an asset already rights-recorded on the site (Commons CC BY-SA 4.0 with attribution links in figcaption, public domain, or site-credited courtesy/Vatican Media/official poster). No new downloads. The 320x320 media/news thumbs (byblos-annaya-walk, trail-pilgrimage, pope-annaya, movie-portrait) were rejected as too small for card headers; hero versions or substitutes used instead.

## QA
check_i18n_policy PASS (news.html wording max-merged into locales/legacy-text-baseline.json via the policy script's own extract_html - 119 entries); check_seo 132 pages PASS; test_seo 15/15 OK; test_feeds 4/4 OK; apply_seo_tags idempotent (0 files on second run; generator re-stamped news.html og:type article, og:image movie poster, mainEntity - generator-owned). git diff --check clean. Pixel-inspected desktop (both sections, card grid) + mobile 390px (Cebu card) - screenshots attached to report.

IndexNow after merge: /news

## Standing pattern (news desk)
Future cards file by subject: Saint Charbel + Lebanon saints -> top section; other saints + Maronite/Catholic community -> world section. NEWS DESK wake prompt updated with the rule.
