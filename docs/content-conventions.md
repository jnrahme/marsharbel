# Content conventions

Permanent rules for new and edited content, from Joey (site owner).

## Whole-card clickable (2026-09-24)

Every news card is fully clickable: title, body text, image - the entire card
area navigates to that story's dedicated page. Applies to:

- the news page (`news.html`) cards - implemented with the stretched-link
  pattern: wrap the card's `<h3>` in `<a class="card-cover" href="...">`;
  the CSS overlay makes the whole card clickable while inner source links
  stay clickable (z-index);
- the homepage Latest News section (`.home-news-lead` and `.home-news-row`
  elements are full anchors);
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
budget and splits link signals. The brand link and
breadcrumbs follow the same rule (`./`, not `index`). `check_seo.py` fails
the build on any internal link to `*.html` or `index`. The shared nav lives in
`partials/primary-navigation.html` and is applied with
`node scripts/sync-navigation.mjs`.

## Homepage news rotator thumbnails (legacy)

The homepage no longer has a rotator; the Latest News section uses full-size
images (320px squares for rows, the hero image for the lead). The rotator
rules below apply only if a rotator returns. Rotator images displayed at 64x64. After adding or changing a rotator item,
run `python3 scripts/build_news_thumbs.py`: it makes a 128px square WebP in
`media/news/thumb/` and points the item at it. QA fails if an item still
uses a full-size image.

## AI-generated images: watermark step (standard)

Every AI-generated image is watermarked "marsharbel.com" in the file itself, not by CSS, so the name travels with pins and shares (Joey directive, 2026-10-02 9:56 AM, relayed by the main agent). Never watermark historic photographs.

1. Save the clean original under `assets/originals/<folder>/NAME.ext` (see `assets/originals/README.md`).
2. Run `python3 scripts/watermark_ai_image.py assets/originals/<folder>/NAME.ext <folder>/NAME.ext`. It adds small semi-transparent serif text in the bottom corner, about 2.7% of image width, and keeps dimensions and format.
3. Look at the result before shipping; the mark must not cover a face. Use `--corner left` if the right corner is busy.
4. Keep the "AI transformation, not a photograph" label on the page as well.

