# Bot log - Nav re-sync: Story library routing + storybook cross-links (2026-09-26 ~5:30 AM EDT)

## Trigger
prayer-hub merged as #226 (Prayer IA: 17-item Prayer dropdown, Places dropdown, prayer-finder) with mirror fixes #228/#230. The post-prayer-hub nav is now on every page (integrator synced all 69 nav-bearing pages). This bundle applies the deferred nav re-sync scope on top.

## What changed
- Story menu re-route site-wide (69 pages): Story parent ./story -> ./stories; dropdown sub-item "Story for Children" (./story) -> "Saint Storybooks" (./stories); "Full History" kept. Nav-block-scoped replacements only - body links to /story (the Charbel book) untouched.
- Active states: stories.html marks the Story parent + "Saint Storybooks" sub-item active (aria-current). story.html keeps the parent active (section context) but drops the sub-item active/aria-current - the library is now the destination, /story is a child of it.
- Pio cross-link (deferred from the pio-storybook review): st-padre-pio.html cta-row gains "The Children's Storybook" -> /pio-story; pio-story.html Research Basis gains a prose link to /st-padre-pio (life, prayers, pilgrimage).
- JPII mirror of the same pattern: st-john-paul-ii.html cta-row gains "The Children's Storybook" -> /jpii-story; jpii-story.html Research Basis gains a prose link to /st-john-paul-ii.
- sitemap.xml: lastmod sync via scripts/sitemap_lastmod.py (69 edited pages + the pre-existing stale /en/prayers entry from #228/#230 fixed by the same run).
- locales/legacy-text-baseline.json: merged for all 69 edited pages, insertion-order preserved (integrator's baseline format uses unsorted inner keys - write reproduces it byte-identically).
- apply_seo_tags: only addition was datePublished 2026-09-26 on saint-charbel-pilgrimage.html (a page this bundle edited) - kept; no other files touched.

## Already done before this bundle (verified, no action needed)
- All 69 pages carry the post-prayer-hub nav (integrator synced, including my storybook/library/saint pages).
- Places dropdown exists (prayer-hub) - the deferred "pilgrimage Places entry" item is satisfied.
- Saint pages' navs identical to canonical modulo per-page active markers.

## Verification
- check_i18n_policy PASS; check_seo PASS (143 indexable pages); git diff --check clean.
- DOM assertions on 10 representative pages (index, stories, story, pio-story, st-padre-pio, jpii-story, st-john-paul-ii, saints, visit-annaya, saint-charbel-novena): Story parent -> /stories, first sub-item "Saint Storybooks", zero page errors.
- Live-DOM active-state check on stories.html: active parent + sub-item with aria-current present (nav links are rewritten to absolute /stories at runtime by the locale router - expected).
- Pixel review (mobile): st-padre-pio + st-john-paul-ii cta-rows wrap cleanly with the new 5th/4th button; pio-story.html Research Basis cross-link renders.
- Storybook regressions: /story, /pio-story, /jpii-story load with zero page errors.

## Flags
- story.html no longer has a direct nav entry (by design - Joey's library model: Story -> library -> pick a book). It remains linked from the library's first card, the homepage promo, and /stories cards.
- IndexNow after merge: /stories plus all nav-touched pages are same-URL edits (no new URLs); at minimum /stories and the two saint pages with new cta buttons (/st-padre-pio, /st-john-paul-ii) and the two storybook pages (/pio-story, /jpii-story).
