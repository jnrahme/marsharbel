# 2026-09-24 - Clean internal links (technical SEO lane)

What: every internal href on 57 HTML pages, the shared nav partial, and the
JS-built links (floating audio player, mystery meditation, legal footer links
in translate.js) now point at clean URLs instead of `.html`.

Why: canonicals, sitemap and hreflang all use clean URLs, but ~1,285 internal
links pointed at `.html` paths that 301. Googlebot had to follow a redirect
for nearly every internal link, and internal PageRank went to redirecting
URLs instead of the canonical ones.

Decision: fix at the source (partial + sync-navigation matching + JS
templates), not a regex pass on output. sync-navigation now compares pages by
clean name so active-state highlighting works with either form. Tests that
enforced `.html` links were inverted to enforce clean links.

Left alone: account.js magic-link redirect (auth file, and it is a redirect
target, not a crawlable link); external `.html` URLs; service-worker offline
cache path.

Verification: `npm run qa:ci` passes in full (SEO, i18n policy, site smoke,
rosary suites, testimony UI).
