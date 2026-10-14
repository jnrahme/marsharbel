# Content API: news and daily rosary (phase 1)

Owner decision (Joey, 2026-10-14): a backend layer feeds the website so news and the daily rosary update without a site deploy, and the same source feeds the future mobile app.

## Principles
- SEO first. Every page stays pre-rendered. API-fed blocks ship real HTML in the page; the API only refreshes it after load. If the API is down or slow (4 s), the static HTML stays. Crawlers see the static HTML.
- Free infra. One small container on the existing Hostinger VPS, behind the Caddy already serving media.marsharbel.com. No new paid service.
- Same contract for web and apps. Versioned `/v1`, additive changes only, breaking change means `/v2`.
- Git stays the source of truth. `content/news/<locale>.json` and `content/rosary/daily.json` are canonical; the service reads copies of them. Fast path: the news lane can `PUT /v1/admin/news` (bearer token, shape-checked, atomic write) and then commit the same file so git and the service agree.
- Books keep their static feed at `/api/v1/` (docs/BOOKS-API.md). The service is for data that changes daily.

## Endpoints (api.marsharbel.com)
| Path | Returns |
|---|---|
| `GET /v1/health` | liveness, locale files loaded |
| `GET /v1/manifest.json` | endpoints, locales |
| `GET /v1/news?locale=&limit=` | home latest-news items for a locale (`fallback:true` when that locale has no file and English is returned) |
| `GET /v1/rosary/daily?date=&locale=` | weekday mystery set and page, saint of the day, episode metadata for that locale (null until the video lane publishes; `episodeFallbackLocales` lists locales that have one) |
| `PUT /v1/admin/news` | authenticated publish of one locale file |

Responses carry ETag and `Cache-Control: public, max-age=60, stale-while-revalidate=300`. CORS allows only marsharbel.com origins. Read-only except the admin PUT, which is off unless a token secret is mounted.

## Data
- `content/news/<locale>.json`: seeded from the live homes by `scripts/content-api/extract-news-from-homes.mjs` (11 locales). Items: id, kind (lead|row), href, image {src,alt,width,height}, date, title, dek, credit.
- `content/rosary/daily.json`: weekday to mystery set (Mon/Sat joyful, Tue/Fri sorrowful, Wed/Sun glorious, Thu luminous, same as the site's own rule), set pages, `episodes[]` {date, locale, url, ...}.
- Saint of the day is read from `locales/saint-of-day.json`.

## Cutover
1. Service live on VPS, verified by curl (this PR plus VPS install).
2. PR 2: load `content-api-client.js` on the 11 homes. It rebuilds only the `.home-news-rows` list, only from validated items (href starts with `/`, image under `/media/`), via textContent (no innerHTML).
3. Then the news lane publishes to the API first; the homes change without a deploy. Static HTML still gets refreshed by normal merges, so the fallback never goes stale for long.
4. Daily rosary surface follows the same pattern once the video lane writes `episodes[]`.

## Deploy and isolation (VPS)
Container `marsharbel-content-api`, loopback 127.0.0.1:8787, 128 MB, 0.25 CPU, no-new-privileges. One Caddy site block, one DNS A record for `api` to the VPS. Snapshot first; check the other VPS sites before and after. Nothing else on the box is touched.

## Not in phase 1
Accounts, subscriber gating, searchable archive, the /news archive page, non-home news surfaces.
