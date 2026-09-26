# Bot log - 2026-09-25 - Sheen full-talks expansion

## Scope
Parent work item (9:08 PM): expand /blessed-fulton-sheen with more talks beyond the 5 embedded, sourced against the official fultonsheen.com full video/audio library; oEmbed-verify every YouTube ID before embedding.

## What shipped
- New section "Full Talks: Six Broadcast Lectures" on blessed-fulton-sheen.html: 6 full-length talks (Prayer, Suffering, Angels, How to Think, Miracles, The True Meaning of Christmas), hosted by The Catholic World channel, titles matched to the official fultonsheen.com catalog.
- Same embed discipline as the original 5: youtube-nocookie.com, loading=lazy, caption + one-line gloss + Watch-on-YouTube fallback link per card, hosted-by/not-produced-by disclaimer.
- FAQ answer updated (5 short talks + 6 full-length lectures).
- New wording registered in locales/legacy-text-baseline.json via check_i18n_policy.py's own extractor (117 strings).

## oEmbed verification (2026-09-25, all 200 OK)
- utFq5ltAcXQ Prayer | Knz7ofVfR7A Suffering | 9r4t2IOPvr0 Angels | J69VD-DpJ4g How to Think | p9wPa3WKu4A Miracles | sOvlFDqOusE The True Meaning of Christmas
- All author_name "The Catholic World". Miracles duration verified 1489s (full talk); other durations not stated on the page.
- No dead IDs. Nothing dropped.

## QA
- check_i18n_policy PASS; check_seo (132 pages) PASS; test_seo OK; test_feeds OK; test_i18n OK; git diff --check clean.
- Playwright render: 11 iframes load; one console notice "Permissions policy violation: compute-pressure" - benign Chrome feature-policy noise from YouTube's own player, not a site error; playback unaffected.
- Screenshot /tmp/ph-sheen-lectures.png pixel-inspected.

IndexNow after merge: /blessed-fulton-sheen
