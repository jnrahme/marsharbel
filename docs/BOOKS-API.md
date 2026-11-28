# Books content API (schema v1)

One canonical source, one static JSON feed. The website, and later the iOS and Android apps, read the same files.

- Canonical source: `content/books/<slug>/book.json` (language-independent: ids, order, shelf, access tier, asset refs, scene, evidence) plus `content/books/<slug>/<locale>.json` (text only). Shelves in `content/shelves.json`, UI strings in `content/ui/<locale>.json`.
- Generated feed (committed, served as static files): `api/v1/`. Never edit by hand. `npm run books:api` writes it, `npm run books:check` fails if stale or invalid and re-proves the feed matches the legacy sources.
- Legacy converter: `scripts/books/extract-legacy.mjs` (one-time, kept for provenance). After the canonical tree is accepted, add or edit books in `content/` only.

## Files
- `/api/v1/manifest.json`: schema, `contentVersion`, locales, media config, and every book with per-locale file path, sha256 and bytes. Apps poll this one file and download only books whose hash changed.
- `/api/v1/books.<locale>.json`: book summaries for shelves and search.
- `/api/v1/books/<slug>/<locale>.json`: full book (pages, text, evidence with sources, voices, assets map).
- `/api/v1/shelves.json`, `/api/v1/ui/<locale>.json`.

## Rules
- Stable ids (`bk-peter`, `bk-peter-p01`, `bk-peter-img-01`). Slugs are web URLs and may change; ids never do.
- No URL baked into text or data. Assets carry a relative `path`; clients build `media.base + path`.
- `access` (`public` | `subscriber`) sits on every book, page and asset. Everything is `public` today. Gating later means setting `media.access.subscriber` in the manifest to a signed-URL or authenticated resolver and flipping tiers in `content/`; ids, paths and schema do not change.
- Schema is additive within v1; a breaking change means `/api/v2`.
- A locale appears only when it is a page-aligned mirror of English. Unreviewed or misaligned locales are absent.
- Deploy: ship `api/`; `content/` is source and can follow the existing exclusion rules.
