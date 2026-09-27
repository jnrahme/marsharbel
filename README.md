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
- **Saint storybooks** - illustrated read-aloud storybooks in a shared
  page-turn player with gentle voice narration on every page and a closing
  Points-of-reflection page: Saint Charbel (27 pages), Padre Pio, John Paul
  II, and Mother Teresa. Browsable at /stories.
- **Testimonies** - community and voice testimonies with a moderated
  submission and review flow.
- **PWA** - installable, with a service worker and offline shell.
- **AI-answer-engine ready (AEO)** - `/llms.txt` site briefing, explicit
  AI-crawler Allows in `robots.txt`, FAQPage schema on pages with visible
  FAQs, and Organization/WebSite/Person entity schema emitted by the SEO
  generator.

## Tech stack

- Vanilla HTML / CSS / JavaScript; no bundler, no framework
- Hostinger (Apache) for production; extensionless URLs via `.htaccess`
- Netlify for pull-request previews
- Supabase for testimony storage and moderation
- Node 20 + Playwright for browser QA; Python for the international build
  tooling

## Architecture

- **`stage` is production.** Production deploys run through the Hostinger
  file API (TUS uploads) driven by the integrator agent: after each merge the
  changed web files are uploaded, the CDN cache is purged, and every deployed
  file is byte-verified against the repository - immediately, after 90
  seconds, and again on a 15-minute cadence. The legacy Hostinger
  git-integration still runs on pushes but is not the deploy path. `main` is
  updated only by auto-promotion from `stage`.
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

- **Golden rule: rendered review before done.** Nothing is reported done
  on CI green alone - every shipped change is opened in a real browser and
  visually inspected on desktop AND phone viewports before it counts.

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
| Technical SEO | Crawl health, indexing, redirects, structured data (FAQPage and TouristAttraction emitted by the SEO generator), sitemaps | Merged PRs, bot-log entries |
| Content pipeline | Evidence-backed content improvements | PRs for review |
| International | Arabic-first localization, expanding to ranked world languages | Localized pages, hreflang and sitemap updates; shared prayers mirror live in 8 locales (ar, en, fr, es, pt, it, de, pl); Arabic and French monastery mirrors (Arabic with self-hosted Noto Naskh/Sans webfonts); saved-locale routing to published twins |
| Storybook | Saint storybooks: narrative art, Kokoro narration, shared player, page-by-page and audio QA before merge | New books in the shared player, library cards |
| Authority / backlinks | Partnership and backlink preparation | Drafts only - nothing is sent to third parties without explicit approval |

This section is kept current with the fleet: when a lane changes or work
ships, the README is updated in the same PR or a small follow-up docs PR.

## Current state (2026-09-27)

**Live now:** 154 indexable pages in the sitemap across eight locales;
four saint storybooks in the shared player under the warm cream
child-friendly design standard (storybook-joy.css); Arabic and French monastery
mirrors; shared prayers mirrored in all 8 locales; FAQPage/Person/Organization
structured data sitewide on managed pages; `/llms.txt` and AI-crawler-friendly
`robots.txt`.

**Recent ships:**

- 2026-09-27 - Child-friendly stories design standard: warm cream storybook
  treatment (storybook-joy.css) is the permanent design language for the
  stories section - landing cards with pill CTAs, cream reader surfaces,
  unified header/controls across all four storybooks (#303)
- 2026-09-27 - Mother Teresa storybook: 10 narrated pages (7:20 audio),
  Points-of-reflection outro, stories library card, sitemap entry (#300)
- 2026-09-27 - AEO technical pass: llms.txt, AI-crawler robots rules,
  FAQPage + entity schema expansion (#298)
- 2026-09-27 - AGENTS.md rulebook at repo root (#296)
- 2026-09-27 - French monastery mirrors, Arabic webfonts (Noto Naskh/Sans),
  storybook reading-UX pass
- 2026-09-26 - Shared prayers mirror live in 8 locales; saved-locale routing

**In flight:** testimony-youtube lane is paused pending backend access;
retroactive rendered review sweep of pre-2026-09-27 pages is running under
the golden rule.

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
