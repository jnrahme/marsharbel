# /saint-marina-qadisha - pillar 4/4 (Lebanese saints) - COMPLETES THE FOUR
2026-09-30 - content pipeline lane

## What shipped
New page /saint-marina-qadisha ("Saint Marina of the Qadisha: The Monk Who Was a Woman") + saints hub card ("Saint of the Qadisha", in The Saints section after Massabki) + sitemap entry. Hand-authored (not a mirror); structured data by apply_seo_tags.py (WebPage + Article + FAQPage + BreadcrumbList). NOT added to SAINT_STEMS (identity details are hagiographic; Person schema better deferred). No "For children" section (standing rule: until storybooks exist).

## Framing (per spec CAUTION)
Hagiographic tradition throughout: "the Church remembers", "the tradition says", dates given as a range ("some accounts place her in the fifth century, others around the year 750"). FAQ explicitly answers "Is her story historical?" with the tradition-not-documentation framing. A security screen flagged the "the Church remembers" phrasing as possibly counterfeiting ecclesial authority - assessed and kept: the phrasing is verbatim from the parent-forwarded spec's own framing instruction, and the page disclaims modern documentation rather than claiming it.

## Claim/source matrix (evidence gate)
- Birth at Al-Qalamoun near Tripoli; father Eugenius; "save your soul and destroy mine"; name Marinos; 10 years with father; inn/soldier/false accusation; 10 years at the gate raising the child on sheep's milk; death at 40; discovery; blind monk healed - earliest vita (written 525-650) as summarized by Wikipedia "Marina the Monk"; told AS TRADITION.
- Era: 5th century (Wikipedia: "probably") vs c. 750 (IMLebanon Arabic account) - page gives both, asserts neither.
- Relics taken in Crusader era to Constantinople then Venice; patron of Venice - Daily Star/Al Bawaba (2018, citing OCA: Venice 1113) + IMLebanon (Venice 1231). Page says "Crusader era" only, no year (conflict noted).
- July 17 2018: relics returned on pilgrimage, received at Beirut airport by caretaker FM Gebran Bassil, welcomed by Maronite Patriarch (Rai per Lebanon Debate), displayed in Qadisha until July 23, then back to Venice - Daily Star/Al Bawaba, Yerepouni Daily News, IMLebanon. Page frames as a pilgrimage visit, NOT a permanent return (the Arabic coverage calls it a "pilgrimage visit").
- Feast July 17 in the Maronite calendar - 2018 coverage (returned "on her feast day"). June 17 Episcopal calendar (2022) - Wikipedia.
- Druze veneration as al-Sitt Sha'wani', shrine at Amiq - Wikipedia.
- Chapel of Mar Marina beside Qannoubine monastery, open to visitors; cave tomb - Daily Star/Al Bawaba.
- Qadisha Valley UNESCO World Heritage - corroborated by our own /qadisha-valley page (14 mentions).

## Media-rights ledger
- media/saints/saint-marina-qadisha.webp: "Qannoubine church.jpg", Hussein Sabboury, CC0 (public domain dedication) - verified via Commons API (pageid 193619943), 1280px thumbnail converted locally to webp. Used on page hero + hub card.

## Cross-links (stage rule)
- Spec links /qadisha-valley, /st-rafqa, /saint-charbel-places-lebanon - all verified on stage.
- ADDED /massabki-brothers + /abouna-yaacoub in Keep Reading (both merged to stage in #368 this morning).
- NOT linked: /st-estephan-nehme (still not on stage - 404; relink after its bundle deploys).
- Integrator's #368 merge already added the Massabki link to abouna-yaacoub's Keep Reading - the deferred abouna->massabki relink is DONE by the integrator, no patch owed.

## Verification
- QA: build-home-css, check_i18n_policy, i18n:test, check_seo, git diff --check, test_seo, test_prayer_mirror, test_i18n, nav-sync, dead-code, testimony-security, site-smoke, rosary-all - results in ship report.
- Rendered review: desktop 1280 + phone 390 full-page captures of page + hub card (attached to ship report).
- UNVERIFIED: live production (needs integrator merge/deploy). Completion proof owed once live.

## Integrator sourcing refresh (2026-10-01)
Fresh Commons page confirms CC0. OCA church account (https://www.oca.org/saints/lives/2026/02/12/100508-venerable-mary-who-was-called-marinus-and-her-father-venerable-e) places Mary/Marinus in sixth-century Bithynia/Alexandria, while Lebanese reporting places Marina at Qannoubine and differs on her era. Per parent clarification, preserved the hagiography and sharpened four blanket attribution phrases to the Lebanese tradition. FAQ schema regenerated from visible copy, not edited independently.
