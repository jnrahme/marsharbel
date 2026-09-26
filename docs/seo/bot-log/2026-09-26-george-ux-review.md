# 2026-09-26 - George Elhage human-QA UX fixes (nav highlight, install button, sources links, Travel rename)

## Task
Joey forwarded George Elhage's WhatsApp site review (9:57 AM) via parent: "turn this into actionable tasks." Four items, shipped as one bundle: (1) current-section highlight in top nav, (2) Install App button out of the language pill, (3) Sources links should read as links, (4) nav rename "Places" -> "Travel" (cluster targets travel/visit keywords; searcher language). Item 5 (positive signals, kids' stories validation, eventual book sales) recorded, no action.

## 1. Active section highlight
- sync-navigation.mjs already marks current section at build time (class="active" + aria-current="page"); the CSS state was identical to :hover (faint wash) - invisible in practice.
- styles.css: `.links a.active` now gold text + wash + inset gold ring, distinct from hover. Shared rule covers top-level links, group parents, and dropdown children.
- templates/mirrors/qadisha.html had NO active markers (prayers template already had them): added class="active nav-parent" on the Travel parent + class="active" aria-current="page" on the Qadisha Valley child; i18n:build regenerates en + ar qadisha pages.
- qadisha-valley.html keeps its deliberate sync-skip marker (integrator, #258): it is generated from the qadisha mirror template; nav changes route through the template + i18n:build, NOT sync write mode.

## 2. Install App placement
- Root cause: translate.js createSwitcher appended the button INSIDE .lang-switcher (a bordered pill) - read as part of language selection.
- translate.js: button now appended to .topbar .nav as its own sibling control (floating-switcher fallback pages keep it inside the container - no .topbar there).
- styles.css: .nav gains an "install" grid area ("brand install lang" / "links links links"); button right-aligned beside the pill with grid gap. Mobile (<740px flex column) stacks it separately below the selector - verified by screenshot.

## 3. Sources links
- Root cause: global `a{color:inherit;text-decoration:none}`; nothing restyled content links.
- 47 pages share the `<h2>Sources</h2>` + `.card.story ul` pattern. Shared fix in styles.css: `.card.story p a:not(.btn):not(.promo-link), .card.story li a` gold + underline (matches footer link style), hover to --text. Also fixes inline prose links in story cards (qadisha cross-links verified in screenshot).

## 4. Places -> Travel
- Keyword check (docs/seo/keyword-map-2026-09-24.md): cluster is "pilgrimage and places" with learn+VISIT intent (trail, visit annaya, qadisha travel+heritage terms); nothing argues against "Travel"; it matches searcher language. URLs unchanged.
- partials/primary-navigation.html + sync-navigation.mjs WRITE mode: 95 pages.
- Mirror catalogs (flat keyed): en "Travel", ar prayers "السفر", ar qadisha "السفر مع مار شربل", de "Reisen", es "Viajes", fr "Voyages", it "Viaggi", pl "Podróże", pt "Viagens"; i18n:build regenerated mirror pages (en/ar qadisha, 7 prayer mirrors + en master).
- Baseline: 94 synced pages re-registered via check_i18n_policy.py snapshot extractor (fresh per-page replace). Also cleaned long-standing stale entries (Pilgrimage Guide / Story for Children / Testimonies / old meta descriptions) - same class the integrator flagged after nav-resync. 3 inert "Places" remain (mirror-master entries the policy check skips; build-verified pages).
- home.css regenerated (build-home-css tracks styles.css).

## Verification
- Full QA chunked, all green: chunk1 (build-home-css, i18n:check, i18n:test, check_seo, test_seo, feeds, testimony baseline+static), chunk2 (testimony-security, site-smoke), chunk3 (6 rosary sub-suites).
- Pixel review desktop 1440 + mobile 390, before/after: Travel gold+ringed on /visit-annaya and /qadisha-valley; dropdown open shows Qadisha Valley child highlighted (aria-current); Install App separate from language pill on both viewports; Sources links gold+underlined desktop + mobile; Arabic qadisha mirror RTL nav shows "السفر مع مار شربل" highlighted with Install App separated.
- #254 geography correction verified intact after mirror regeneration.
