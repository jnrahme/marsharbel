# marsharbel.com

A static Catholic devotional website dedicated to Saint Charbel Makhlouf: his
history, miracles, prayers and novenas, Rosary guidance, testimonies, and
visitor information for Annaya.

**Live site:** https://marsharbel.com

The site is plain HTML, CSS and JavaScript with no build step and no framework.
Every file in the repository root is served as-is.

## Features

- **Multilingual** - eight locales (English, Arabic, German, Spanish, French,
  Italian, Polish, Portuguese) with localized routes, hreflang and a shared
  language selector. Arabic is the first priority of the international
  program; more world languages follow in ranked order.
- **Prayer library** - Saint Charbel prayers, the novena, and the monthly
  22nd-of-the-month prayer tradition.
- **Interactive Rosary** - a visual step-by-step guide, all four mystery sets,
  and a prayer coach.
- **Storybook** - an illustrated, page-by-page telling of Saint Charbel's life.
- **Testimonies** - community and voice testimonies with a moderated
  submission and review flow.
- **PWA** - installable, with a service worker and offline shell.

## Tech stack

- Vanilla HTML / CSS / JavaScript; no bundler, no framework
- Hostinger (Apache) for production; extensionless URLs via `.htaccess`
- Netlify for pull-request previews
- Supabase for testimony storage and moderation
- Node 20 + Playwright for browser QA; Python for the international build
  tooling

## Architecture

- **`stage` is production.** Every push to `stage` auto-deploys to
  marsharbel.com via Hostinger (about four minutes), guarded by the QA
  workflow. `main` is updated only by auto-promotion from `stage`.
- **All changes land through pull requests into `stage`.** Feature branches
  are cut from `stage`; direct pushes are blocked by branch protection.
- **QA gates** (required status checks on every PR):
  - `qa` - full suite: site smoke tests, i18n policy, SEO checks, navigation
    sync, testimony security and UI checks
  - `browser-quality` - Playwright end-to-end behavior tests
  - `dead-code` - unused file and reference detection
- Branch protection on `stage` and `main`: pull requests required, checks must
  pass, force pushes and deletions disabled, secret scanning and push
  protection enabled.

Run the full suite locally:

```bash
npm ci
npm run qa
```

## 24/7 agent operations

An agent fleet works on this repository continuously under the operating
contract in [`docs/SEO-BOT-24-7-OPERATING-PLAN.md`](docs/SEO-BOT-24-7-OPERATING-PLAN.md).
Work is evidence-backed, lands through the PR flow above, and is logged in
[`docs/seo/bot-log/`](docs/seo/bot-log/).

| Lane | Focus | Output |
| --- | --- | --- |
| Integrator | QA gates, merges, post-deploy live verification, regression watch | Merge and verification reports |
| Technical SEO | Crawl health, indexing, redirects, structured data, sitemaps | Merged PRs, bot-log entries |
| Content pipeline | Evidence-backed content improvements | PRs for review |
| International | Arabic-first localization, expanding to ranked world languages | Localized pages, hreflang and sitemap updates |
| Authority / backlinks | Partnership and backlink preparation | Drafts only - nothing is sent to third parties without explicit approval |

This section is kept current with the fleet: when a lane changes or work
ships, the README is updated in the same PR or a small follow-up docs PR.

## Repository layout

- Root - the served site (pages, shared JS/CSS, media)
- `ar/ de/ en/ es/ fr/ it/ pl/ pt/` - localized page trees
- `locales/` - translation catalogs and the legacy text baseline
- `scripts/` - QA, i18n build, navigation sync and test runners
- `docs/` - operating plan, runbooks and audits; `docs/seo/` for SEO logs
- `supabase/` - testimony database schema

## Working in this repository

1. Branch from `stage`.
2. Open a pull request into `stage`.
3. All required checks must pass; merges deploy straight to production.

Engineering rules for contributors and coding agents live in
[`AGENTS.md`](AGENTS.md). Deployment details are in
[`docs/DEPLOYMENT-RUNBOOK.md`](docs/DEPLOYMENT-RUNBOOK.md).
