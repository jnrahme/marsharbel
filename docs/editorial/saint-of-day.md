# Daily Saint of the Day

Source: authenticated October 13 2026 website directive, homepage saint info link paired with its illustrated children's book. First target date: October 14, Saint Jude (Maronite calendar).

1. Verify feast in Maronite eparchy calendar, otherwise Roman Church calendar. Label which calendar applies. Verify biography separately. No unsupported historical detail or miracle.
2. Update locales/saint-of-day.json activeDate + dated entry and locales/<lang>/saint-of-day.json for each current homepage language. Translation status remains agent-translated, native-review pending until reviewed. External info destination may be used when no local biography exists. Link existing illustrated book; absent book needs an explicit availability state implemented before selecting that entry.
3. Run python3 scripts/build_saint_of_day.py; node scripts/build-pages.mjs --pages=index.html; python3 scripts/i18n/refresh_saint_home_bindings.py; npm run i18n:build twice to fixpoint; node scripts/build-home-css.mjs; npm run i18n:check; relevant QA/full gate; sitemap_lastmod.py after commit.
4. Non-author reviews copy and binding diff. Do not change baseline/gates to admit the content. Existing unrelated home copy values must validate unchanged.
5. Render real EN/AR desktop and phone pixels, + German 200% stress, source and book destinations. Recheck live exact date/card after normal merge/deploy.

Daily preparation wake: 06:00 ET, maximum 15-minute delivery window, 08:00 deadline. Main coordinates studio/social and merge review. Queue ahead where practical. The manifest date is explicit, never inferred from browser timezone. A stale card must retain its real date, not be relabeled today's saint. Date rollover/publication is verified daily, not inferred from a scheduler receipt.

No new illustration produced: Jude cover reuses the existing book's page 1, labeled imaginative illustration, not historical portrait. This module extends existing news-card visual system, not a redesign.
