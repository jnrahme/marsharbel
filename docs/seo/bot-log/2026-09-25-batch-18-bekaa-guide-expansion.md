# 2026-09-25 - Batch 18: /bekaa-kafra travel-guide expansion + breadcrumb trailing-slash fix

Parent spec 2026-09-25 4:07 PM (competitor lane, places cluster #1): treat as
expansion of the existing page (batch 16, merged #149), not a new page. Fold
in travel/visiting depth, keep content and URLs, links to /history,
/visit-annaya, /saint-charbel-trail, /saint-charbel-hermitage,
/saint-charbel-places-lebanon. Real photos from source sites, no hand-added
JSON-LD. Also folded in the queued breadcrumb fix (parent 2:36 PM).

## Shipped
- /bekaa-kafra expanded: new "What to See in the Village" checklist (house,
  baptism church, Notre-Dame 1925, St Eusebius convent, grotto, feast-week
  exhibition) + "Pair It With the Qadisha Valley" (Qannoubine patriarchs,
  Cedars of God, links to saint-charbel-trail + saint-charbel-places-lebanon)
- FAQ +2: spelling variants (Bkaakafra/Beqaa Kafra), best time to visit
  (winter-road honesty). Meta description refreshed for travel intent.
- Photos: 2 real shots from LebanonUntravelled (cited source), served from
  media/news/ as webp with "Photo courtesy of LebanonUntravelled.com" in
  alt + caption: hero winter village scene (1200w, 106KB) + spring fountain
  inline (1000w, 166KB). Neither claimed to be the saint's house itself.
- Breadcrumb fix: the 5 miracle child pages' hand-authored Article JSON-LD
  parent item now points to canonical /miracles/ (trailing slash).
- i18n baseline refreshed for the 6 touched pages.

## Schema note
Page keeps generator-managed schema only (WebPage + BreadcrumbList via #154).
Article + FAQPage + Place from the spec need generator support - added to the
standing technical-lane feature request.

## QA
check_seo green (130), test_seo 15/15, i18n policy, nav 0/82, diff --check,
lastmod current. Playwright: 10 h2s in order, both images load, zero console
errors, desktop + mobile verified.
