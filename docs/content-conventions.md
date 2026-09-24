# Content conventions

Permanent rules for new and edited content, from Joey (site owner).

## Whole-card clickable (2026-09-24)

Every news card is fully clickable: title, body text, image - the entire card
area navigates to that story's dedicated page. Applies to:

- the news page (`news.html`) cards - implemented with the stretched-link
  pattern: wrap the card's `<h3>` in `<a class="card-cover" href="...">`;
  the CSS overlay makes the whole card clickable while inner source links
  stay clickable (z-index);
- the homepage rotating news feed (`.news-rotator-item` elements are full
  anchors);
- all content built going forward.

Target is always our own article page where one exists; otherwise the
closest relevant site page, otherwise the cited external source.

## News imagery (2026-09-24)

News thumbnails and article featured images use real photos from the cited
source articles, downloaded and served from the repo (`media/news/`, webp,
compressed, lazy-loaded) with attribution in alt text/caption where the
source requires it. Never hotlink. Never take rights-restricted stock
(e.g. Shutterstock) - use a site asset and flag instead.

## Internal links

Internal links use clean URLs that match the canonical tags: `./story`,
`../rosary-visual-guide`, `./news#item-id`, and `./` (or `../`) for home.
Never link to `*.html`; the host 301s those, and each redirect costs crawl
budget and splits link signals. The shared nav lives in
`partials/primary-navigation.html` and is applied with
`node scripts/sync-navigation.mjs`.
