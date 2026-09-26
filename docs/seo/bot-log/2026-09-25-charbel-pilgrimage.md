# Bot log - 2026-09-25 - Saint Charbel pilgrimage guide

## Scope
Joey 2026-09-25 10:23 PM (todo-01M3DRC45678SFP40CPCHDFHKH): "find a suitable spot to add how to do a pilgramage for saint charbel with google location and suggestions for what people should visit when they go to lebanon." Parent queue confirmed 10:45 PM: pilgrimage guide first, interlink the places cluster.

## IA decision
New page /saint-charbel-pilgrimage - the planning hub ABOVE the existing place pages, not a replacement: Annaya heart (tomb + hermitage) linking down to /visit-annaya and /saint-charbel-hermitage; Bekaa Kafra linking to /bekaa-kafra; Qadisha (Qannoubine + Qozhaya); While You Are in Lebanon (Harissa, Bkerke, Cedars, Byblos, trail); 1/3/7-day itineraries; practical planning; Pray as You Go; FAQ x5; Sources. Cross-links added INTO the new page from visit-annaya (primary CTA), bekaa-kafra, places-lebanon, and the trail page.

## Google locations
Every stop carries a query-based Google Maps link (maps.google.com/search/?api=1&query=...) - deterministic, no API key: monastery + hermitage at Annaya, Bekaa Kafra, Qannoubine, Qozhaya, Harissa, Bkerke, Cedars of God, Byblos.

## Photos (all Commons API extmetadata verified 2026-09-25)
NEW: lebanon-qozhaya-monastery.webp (PD, Yellaban), lebanon-qozhaya.webp (CC BY 4.0, Argenberg - valley mist view, honestly captioned after pixel review caught the file title claiming monastery with none visible), lebanon-harissa.webp (CC BY-SA 4.0, Paul Saad), lebanon-cedars.webp (CC BY 4.0, Argenberg, 176KB - texture-dense, accepted at q56). REUSED (registered): annaya-monastery.webp hero, charbel-tomb.webp. LebanonUntravelled courtesy photos deliberately avoided (open rights question, batch-18 blocker).

## Facts discipline
Biography facts (1828 birth, 1851 Mayfouq, 1853 Annaya, 1875 hermitage, 1898 death) match the site's own verified pages. UNESCO claim phrased as the single joint listing (Qadisha Valley + Cedars forest). No entrance-fee/transport claims beyond what /visit-annaya already publishes. Safety handled honestly (check government travel advice) - no invented assurances.

## QA
check_i18n_policy PASS (5 files max-merged into baseline via the policy script's own extractor); check_seo 133 pages PASS; test_seo 15/15 OK; navigation sync clean (script ran once to normalize the new page, then 0 out of sync); apply_seo_tags idempotent; diff --check clean. Pixel review desktop + mobile: caught (1) missing stylesheet link in my hand-written head (unstyled render - fixed), (2) Qozhaya image caption mismatch (monastery not visible - replaced with PD monastery shot + honest valley caption). Screenshots attached to report.

IndexNow after merge: /saint-charbel-pilgrimage, /visit-annaya, /bekaa-kafra, /saint-charbel-places-lebanon, /saint-charbel-trail

## Flag for nav coordination
The whole places cluster (visit-annaya, bekaa-kafra, places-lebanon, trail, hermitage, this guide) is absent from the primary nav - same orphan disease Joey reported for prayers. Recommend fixing both in the prayer-IA nav rework (todo-01M3DSKNF95HHY3DD2Z1NJ653W) rather than shipping a second 85-page nav diff.
