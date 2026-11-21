# Daily Saint of the Day

Source: per owner request, Oct 13, homepage saint info link paired with its illustrated children's book. First target date: October 14, Saint Jude (Maronite calendar).

1. Verify feast in Maronite eparchy calendar, otherwise Roman Church calendar. Label which calendar applies. Verify biography separately. No unsupported historical detail or miracle.
2. Update locales/saint-of-day.json activeDate + dated entry and locales/<lang>/saint-of-day.json for each current homepage language. Translation status remains agent-translated, native-review pending until reviewed. External info destination may be used when no local biography exists. Link existing illustrated book; absent book needs an explicit availability state implemented before selecting that entry.
3. Run python3 scripts/build_saint_of_day.py; node scripts/build-pages.mjs --pages=index.html; python3 scripts/i18n/refresh_saint_home_bindings.py; npm run i18n:build twice to fixpoint; node scripts/build-home-css.mjs; npm run i18n:check; relevant QA/full gate; sitemap_lastmod.py after commit.
4. Non-author reviews copy and binding diff. Do not change baseline/gates to admit the content. Existing unrelated home copy values must validate unchanged.
5. Render real EN/AR desktop and phone pixels, + German 200% stress, source and book destinations. Recheck live exact date/card after normal merge/deploy.

News desk plan daily preparation wake: 06:00 ET, maximum 15-minute delivery window, 08:00 deadline. Main coordinates studio/social and merge review. Queue ahead where practical. The manifest date is explicit, never inferred from browser timezone. A stale card must retain its real date, not be relabeled today's saint. Date rollover/publication is verified daily, not inferred from a scheduler receipt.

No new illustration produced: Jude cover reuses the existing book's page 1, labeled imaginative illustration, not historical portrait. This module extends existing news-card visual system, not a redesign.

## Availability and rollover ownership
The publication timezone is America/New_York. The manifest date generates the visible numeric day.month.year label; editorial catalog files do not carry a date literal. The inert template unit is revealed only on its exact publication date by saint-of-day.js, rechecked every minute and on visibility changes. No-JS visitors do not see this additive unit. Inactive markup exists only in template content, not the live document; active-day runtime clones it once and removes it after expiry. This deliberate fail-closed tradeoff avoids tomorrow's or yesterday's feast being shown as today's.

This news/daily-saint lane owns daily pick, primary-source check, dated manifest, all 11 homepage copy packs, original social card and caption, generator runs, proof and handoff. Main coordinates independent review and content/engineering merge before 8 AM; social opportunity desk executes the matching Buffer slot via main. This lane never queues a duplicate social post.

Daily source updates: locales/saint-of-day.json and locales/<lang>/saint-of-day.json. Generated rollover files: src/pages/index.html, index.html, all 10 locale index.html mirrors, locales/en/home-bindings.json, all home-copy.json packs, locales/en/saint-of-day-copy.json, same-page-manifest.js and sitemap.xml. CSS and runtime JS are mechanism-only unless changed. After source-generation commit, run sitemap_lastmod.py and include its generated delta in the same PR. Catalog admission is text:positive occurrence count for index.html, generated from the keyed pack; only the sanctioned tuple name is added to the existing wording gate. Never change baselines, evidence pins or other gate conditions.

PR review must state: no-JS unit hidden; locale text agent-translated/native review pending; existing English book may be linked where no translated book twin exists; no-book entry selection remains blocked until an honest absence state is implemented; current-date live verification remains required after deploy. Local clock-controlled previews are not production proof.

## PR-body section: Day 2+ rollover design
The first release changes the mechanism once: an inert template plus NY-date conditional clone. Later daily updates are data-only editorial releases, not new JavaScript/template/test rewrites. The lane updates activeDate/dated manifest entry and keyed saint copy in every active locale, then generators produce the source/root/mirror home bytes, bindings/copies/count catalog and normal manifest/sitemap deltas in the same PR. These generated HTML changes are data projections, not repeated mechanism changes. Minute/resume refresh mounts only the released active date and removes expired content; it does not fetch unreviewed future entries or fabricate tomorrow's saint. Prepare the next dated pack ahead of midnight and merge/deploy before its day begins. Missing review/deploy fails closed rather than displaying yesterday's feast. A future multi-day runtime-data feed would be a separate reviewed mechanism change, not claimed to exist in this PR.

The runtime test covers three clocks, no duplicate mount, expiration/remount. Playwright covers EN/AR active and inactive states with the active-day assertion and axe, plus no-JS absence. Existing release specs stay untouched and must pass independently.

Template is a body child after main, with data-saint-after selecting the existing news anchor. Runtime mounts after that anchor and fails closed when it is absent. Translation status: agent-translated, native-review pending.
