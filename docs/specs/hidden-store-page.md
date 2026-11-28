# Hidden /store product workshop

## Scope and release hold
This is a **product workshop page**, not a public shop launch. It exists so Joey can
review real Shopify product data (names, handles, prices) in a reverent, on-brand
layout before anything is announced. No payments, no Shopify password, no API keys,
no checkout flow, no fake photography, no fake reviews, and no invented prices are
part of this change. Nothing here enables purchases. `SHOP_LINK_ENABLED` (PR 912's
footer-link scaffold) stays off and is untouched by this PR.

Joey must explicitly approve before:
- the page is linked from any public nav, header, footer, or other page,
- the page is added to `sitemap.xml` (or any sitemap) or has its `robots` meta changed from `noindex, nofollow`,
- real product photography, checkout, or pricing changes beyond the three listed products are added.

## Success criteria
1. `src/pages/store.html` builds (via `node scripts/build-pages.mjs`) to a served
   page reachable at the clean URL `/store` (root `store.html`, resolved by the
   existing `.htaccess` clean-URL rewrite the same way every other page here works;
   `/store.html` itself 301s to `/store`, matching every other page on the site).
2. The page shows the three real, currently-live Shopify products, with no
   invented facts:
   - Saint Charbel Classic T-Shirt — $29.99 — `saint-charbel-classic-t-shirt`
   - Saint Charbel Winter Chapel Mug — $17.99 — `saint-charbel-winter-chapel-mug`
   - Saint Charbel Organic Tote Bag — $24.99 — `saint-charbel-organic-tote-bag`
   Each card uses a tasteful typographic/line-art placeholder in place of product
   photography (the real Shopify listings currently have no photos or long
   descriptions) and is structured so a fourth, fifth, etc. product drops in by
   adding one more card/entry, not by restructuring the page.
3. Hidden:
   - `<meta name="robots" content="noindex, nofollow">`, no conflicting robots directive.
   - Not present in `sitemap.xml`, `sitemap-images.xml`, `sitemap-video.xml`, or any other generated sitemap.
   - No `<a>`, `<area>`, or `<link>` anywhere else in the repo's served HTML points at `/store`, `/store.html`, or `/store/`. Not in `partials/primary-navigation.html`. Not in `feed.xml`.
   - Isolation is asserted by `locales/private-preview-pages.json` (the existing
     private-preview mechanism from the 2026-10-13 scrum ruling), which both
     `scripts/qa/dead_code_check.sh` and `scripts/qa/check_new_page_locales.py`
     already enforce on every run — the same mechanism protecting
     `rosary-book-joyful.html`.
   - `robots.txt` is left unchanged: a sitewide `Disallow` would stop crawlers from
     ever reading the `noindex` tag and can still leave a stale URL indexed from a
     prior crawl, so noindex + sitemap/link omission is the hiding policy, not
     `robots.txt`. (Matches the reasoning already in `docs/specs/hidden-shop-link.md`'s
     sibling scaffold.)
4. No forms, no payment inputs, no `ShopifyBuy`/Stripe/PayPal integration, no
   `/cart/add` or checkout endpoints, no credential-shaped strings anywhere in the
   page or any script it loads. The only outbound action is a plain link, "View in
   test store," to `https://marsharbel-test.myshopify.com` (no password embedded).
5. Every other served HTML file's bytes are unchanged, except the documented
   `robots.txt`/sitemap non-changes above (this PR does not touch `robots.txt` or
   any sitemap).

## English-only
This workshop ships English-only. Every published locale normally requires a
keyed `pageMirrors` family (`docs/CODING-STANDARDS.md` new-page catalog gate),
but that gate exists to protect *public* multilingual parity — a page nobody can
find yet has no multilingual audience to serve, and building seven more hidden
mirrors before Joey has approved the product content itself would be wasted
translation work. The page is registered in `locales/private-preview-pages.json`
or scoped under `public_page()`'s exclusion to skip the new-page locale gate, the
same way `rosary-book-joyful.html` does today for the same reason. If/when this
page is promoted to a public shop, it must either gain the full 7-locale keyed
mirror in that same promotion PR, or stay English-only by explicit decision —
this spec does not pre-decide that.

## Verification
- `node scripts/build-pages.mjs --check` — no served page drifts from source.
- `scripts/qa/dead_code_check.sh` — `/store` isolation (noindex + no inbound link) passes via the private-preview allowlist.
- `python3 scripts/qa/check_new_page_locales.py --base <merge-base-sha>` — locale gate passes via the same allowlist.
- `python3 scripts/qa/check_i18n_policy.py` — no new unkeyed hardcoded text beyond what the page's own catalog covers.
- `npm run test:hidden-store` (added in the sibling `feat/hidden-store-tests` branch, PR #916) — robots, sitemap, inbound-link, flag-off, product/price, and payment/credential regressions.
- Rendered review: desktop + phone screenshot of `/store` before merge.

## Rollback
Delete `src/pages/store.html` / `store.html` and the `locales/private-preview-pages.json`
entry. No other served page needs reverting; nothing else references this page.
