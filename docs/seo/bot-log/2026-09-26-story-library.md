# Bot log - Saint Storybooks library page (/stories)

Date: 2026-09-26
Branch: seo/story-library (based on the jpii-storybook tip 27d528e; the full nav re-sync bundle is merge-gated on prayer-hub)

## Trigger
Joey voice note (via parent, 2026-09-26 ~1:22 AM): each saint must have its own storybook (not all sharing the Charbel one), and the Story menu must open a picker page with a beautiful family/children-friendly card per saint story.

## What changed (this commit - library page only; site-wide nav re-sync follows after prayer-hub merges)
- New page stories.html: "Saint Storybooks" picker. Hero + one promo-card per storybook (Charbel /story, Padre Pio /pio-story, John Paul II /jpii-story), each with the book's own first-page illustration, a one-line pitch, and an "Open ... Storybook" link. Closing "About These Storybooks" card states the sourcing standard and the imaginative-illustration disclosure. Built entirely from existing component classes (promo-card, promo-grid, card story) - no CSS additions.
- Card art: media/storybook/images/event-01.webp (Charbel), media/storybook-pio/images/page-01.webp (Pio), media/storybook-jpii/images/page-01.webp (JPII) - each visually inspected; alt text describes only what is visible.
- Extensible: one promo-card block per new storybook; the page copy says new books join this shelf.
- sitemap.xml: /stories entry (weekly, 0.9, lastmod 2026-09-26).
- locales/legacy-text-baseline.json: stories.html wording registered (51 strings) via the policy script's own extract_html (max-merge, format-preserving write).
- stories.html's own nav already carries the new Story routing (Story -> ./stories, sub-item "Saint Storybooks") that the site-wide re-sync will apply after prayer-hub.

## Per-saint identity audit (Joey's complaint: books sharing Charbel identity)
- storybook.js: all Charbel text lives inside the charbel story data and charbel evidence sources, keyed by story id; the player UI has no hardcoded saint identity. PASS.
- jpii-story.html: no Charbel identity beyond the site-wide brand header/nav and WebSite JSON-LD name (site identity, expected). PASS.
- pio-story.html: only leak is the known og:title/twitter:title "Saint Charbel Story for Kids" template artifact on the pending pio-storybook bundle - handed to the integrator as a pre-merge touch-up. Everything else is site-wide chrome. PASS pending that touch-up.

## Verification
- check_i18n_policy: passed. check_seo: passed (only pre-existing stale-lastmod flags from this branch's older base).
- apply_seo_tags ran (added stories.html JSON-LD); its touches to pio-story.html / st-john-paul-ii.html / st-teresa-of-calcutta.html / jpii-story.html reverted (not this bundle's files); og:image on stories.html restored to the Charbel storybook illustration after the generator defaulted it.
- git diff --check: clean.
- Playwright (mobile 390x844, desktop 1440x900): stories.html renders hero + all 3 cards + about card, zero page errors, all 3 card images load (naturalWidth > 0), card links resolve to /story /pio-story /jpii-story. reveal animations verified firing on scroll (all cards reach opacity 1). Regressions: /story, /pio-story, /jpii-story all load with zero errors.
- Pixel review of d+m screenshots after scroll: layout, imagery, typography as intended; desktop third card wraps to its own row (grid-2), acceptable.

## Pending (next commit on this bundle, after prayer-hub merges into stage)
- Site-wide nav re-sync on the post-prayer-hub nav: Story -> ./stories everywhere ("Saint Storybooks" sub-item), /st-padre-pio cross-link, Pio/JPII/Teresa (+ PR2/PR3 saint pages) nav sync onto prayer-hub's new nav.
- IndexNow: submit /stories after merge.
