# ADR-001: Unified content API for web and mobile

Status: proposed, phase 1 (news, rosary, saint of the day) built. Date: 2026-10-14.
Decision owner: Joey (directive 2026-10-14). Implementation: content API lane. Reviewer: scrum master.

## Context
Marsharbel.com is a static site (generated HTML, Hostinger, deploy per merge to `stage`). News, the daily rosary and the saint of the day change daily, so each change costs a merge and a deploy. Books already ship as a static versioned feed (`marsharbel.com/api/v1`, docs/BOOKS-API.md). Mobile apps (iOS, Android, React Native) and accounts are planned. A Hostinger VPS (7 small sites, ~2% CPU, ~17% RAM, Caddy) and a Supabase project (accounts, testimonies) already exist.

## Decision
1. One backend, a modular monolith. Modules: content (news, rosary, saints, prayers, books), search, media, later accounts/subscriptions/notifications. No per-feature services.
2. One content model, one versioned API at `https://api.marsharbel.com/api/v1/...`. The path shape matches the books feed on the main site; the host differs, so there is no collision. Breaking change means `/api/v2`.
3. Stack: Node 22, zero runtime dependencies for phase 1 (node:http). Reasons: already installed and used by the repo's build scripts, nothing to patch, tiny footprint. Move to Fastify only when routing, validation or auth complexity justifies a dependency.
4. Storage: phase 1 is file-backed. Git (`content/**`) is the source of truth and the service reloads files on change. Phase 4 adds Postgres (container on the VPS; schema below) as the query/search store, loaded from the same files. Supabase stays for user accounts and private submissions; content does not live there, so a Supabase outage or quota never takes news down.
5. SEO guardrail: every page stays pre-rendered. API-fed blocks ship real HTML; the browser may refresh them from the API after load, and any failure leaves the static HTML. Crawlers see static HTML.
6. Publishing: git merge stays the audited path. A token-gated `PUT /api/v1/admin/news` is the fast path for the news lane (shape-checked, atomic); it is off unless a secret is mounted, and every fast-path publish must be committed to git so the two never diverge.
7. Environments: staging first (a second container and `staging.api` host on the same VPS), production after verified requests. Rollback is `docker compose` image/data revert; the static site is unaffected by an API outage by design.
8. Cost: no new paid service. VPS container limits 128 MB / 0.25 CPU.

## Unified content model (contract, all types)
Every record has a stable id that never changes and a locale relationship, not a copy.
- `content_item(id, type, slug, status[draft|review|published|archived], published_at, access[public|subscriber], source_refs[], rights)` where type is news | saint | prayer | book | audio | rosary_episode.
- `content_locale(item_id, locale, title, body_json, status, reviewed_by, master_sha256)`: one row per item per locale. `master_sha256` records the English master so stale translations are detectable (same rule the site uses). A locale appears only when reviewed; otherwise the API returns English with `fallback:true`.
- `media_asset(id, kind, path, mime, bytes, sha256, access, rights)`; clients build `media.base + path`, no URLs baked into text.
- `content_link(from_id, to_id, rel)`: saint to book, rosary episode to mystery set, news to source.
- `search_index(item_id, locale, tsv)` (Postgres full-text, per-language configs; Arabic uses `simple` + normalized text until a better config is proven).
- Later: `account`, `subscription`, `device`, `notification` (kept out of content tables).
Ids: `news-<slug>-<date>`, `saint-<slug>`, `prayer-<slug>`, `book-<slug>` (existing `bk-*` ids kept), `rosary-<date>-<locale>`.
SQL contract: `services/content-api/schema/001_content.sql` (not applied in phase 1).

## API surface
Built: `GET /api/v1/health`, `/manifest.json`, `/news?locale=&limit=`, `/news/{id}?locale=`, `/rosary/today?locale=&date=`, `/saints/today?locale=&date=`.

Phase-1 data ships in `content/` (news per locale, rosary daily config, saint-of-day) as generated seeds: `scripts/content-api/extract-news-from-homes.mjs` bridges the generated homes, `scripts/content-api/extract-saint-of-day.mjs` converts the reviewed saint manifest (`locales/saint-of-day.json`) and refuses a manifest with no entry for today. The service tests and both extractor `--check` gates run in `scripts/qa/prepush.sh` and `run_full_qa.sh`, so CI exercises the backend and fails on a stale seed. Contract only (returns 501): `/prayers?locale=`, `/search?q=&locale=`. Later: `/books`, `/books/{id}`, auth and notifications under `/api/v1/me/...`.
Conventions: `schema` field on every body, ETag, `Cache-Control: public, max-age=60, stale-while-revalidate=300`, CORS limited to marsharbel.com, 4xx/5xx always `{error}`.

## Caching and CDN
Browser/edge cache 60 s with revalidation; Caddy `encode`. A CDN is optional later; the ETag contract works with any.

## Security
Read endpoints are public and read-only. Admin PUT needs a bearer secret (constant-time compare, size cap, shape and path validation; image paths must be under `/media/`). No secrets in the repo. Container: loopback bind, no-new-privileges, resource limits, non-root user. Accounts (phase 5+) use Supabase auth tokens verified by the service.

## Jobs, monitoring, backup
Phase 1 needs none (read-only). Later: a systemd/cron job for scheduled publish; `/api/v1/health` polled by the board desk; JSON access log to the VPS journal; data dir is git-backed plus a nightly tar to the VPS backup path; Postgres dump nightly when introduced.

## CI/CD
PR to `stage` with the service tests (`node --test services/content-api`), content shape checks, then a deploy script that rsyncs `services/content-api` and `content/` to the VPS and restarts the container. Not automated yet.

## Tradeoffs
- File-backed first means no relational queries until phase 4; accepted because the dataset is small (11 locales, tens of items) and git gives review and history for free.
- A separate host (api.marsharbel.com) adds a DNS record and CORS but isolates failures and lets mobile apps use it unchanged.
- Dual publish paths (git and admin PUT) risk divergence; mitigated by the rule that fast-path publishes are committed.
- Zero-dependency service means hand-rolled routing; fine at 6 routes, revisit at ~20.

## Phases
2 news live and consumed by the 11 homes (static fallback). 3 daily rosary episodes (video lane writes `episodes[]`). 4 saints, prayers, search on Postgres. 5 mobile readiness: OpenAPI file, pagination cursors, stable ids audit, auth.
Each phase is claimed only after real requests against staging and production.
