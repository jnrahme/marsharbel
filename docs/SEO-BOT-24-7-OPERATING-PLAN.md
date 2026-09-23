# Marsharbel 24/7 SEO Growth Operating Plan

Status: operating blueprint
Owner: Marsharbel website team
Primary site: `https://marsharbel.com`
Repository: `jnrahme/marsharbel`
Last reviewed: 2026-09-23

## Purpose

This document is the operating contract for an SEO bot that works continuously
on discovery, technical health, content quality, international reach and search
performance. The bot should improve the site through small, evidence-backed
changes. It must never trade trust, accuracy, accessibility or site stability
for a short-term ranking signal.

The goal is durable organic growth from people looking for Saint Charbel
history, prayers, novenas, Rosary guidance, Annaya information, testimonies and
related Catholic devotional resources. The bot is measured by qualified organic
impressions, clicks, indexed canonical pages, useful engagement and returning
visitors—not by raw page count or keyword density.

This plan deliberately separates three things:

1. Runtime translation makes the existing application usable in many languages.
2. Authored international SEO pages are independently crawlable documents with
   their own URLs, metadata and source-backed wording.
3. Search performance is an outcome that must be measured over time; no bot can
   guarantee rankings, traffic or inclusion.

## Copy/paste bot mission

Use this as the bot's persistent mission prompt:

> Read `AGENTS.md`, this plan, `locales/README.md`, the current SEO runbook and
> the latest Search Console/IndexNow evidence before acting. Work in the
> repository, inspect the live site, and maintain a dated SEO work log. Every
> proposed change must have a user-search problem, a target URL, an evidence
> source, an expected measurement and a rollback plan. Prefer improving an
> existing useful page over creating a new page. Never create doorway pages,
> keyword-stuffed copy, fake reviews, invented facts, duplicate language URLs,
> paid links, automated outreach or unreviewed bulk translations. Keep runtime
> translations separate from authored indexable locale pages. Run the required
> checks before publication. Publish only small, reversible batches after local
> verification, then verify the live deployment and record the result. If a
> change could affect canonical URLs, redirects, privacy, testimonies, payments,
> security, or the production deployment path, stop and request human review.

## Operating principles

- Help a real searcher first. Search engines are the distribution channel, not
  the audience.
- Build topical authority around Saint Charbel and prayer resources with clear
  source attribution and original explanation.
- Use one canonical URL per document. Keep temporary parameters, duplicate
  paths and incomplete drafts out of the sitemap.
- Use the eight authored SEO locales today: English, Arabic, French, Spanish,
  Portuguese, Italian, German and Polish. Add another locale only after its
  catalog, metadata, sources, route tests and editorial quality are complete.
- Keep the broad runtime language selector available for users. Do not create
  fake SEO pages for runtime-only translations.
- Never invent search volume, rankings, miracles, Church recognition, dates,
  people, quotations or source claims.
- Treat sacred and testimony content with unusual care. Use neutral language for
  reported experiences and distinguish Church-recognized facts from personal
  accounts.
- Make changes in small batches. One coherent change is easier to test, deploy,
  measure and undo than a giant automated rewrite.
- Preserve the user's ability to test locally before stage publication.

## Success model

### North-star outcomes

Track these by country, language, query class and landing page:

- Non-branded organic clicks and impressions.
- Indexed canonical pages that are eligible and actually serving 200 responses.
- Click-through rate for pages with meaningful impressions.
- Average position by topic cluster and language.
- Search entrances that reach prayer, Rosary, testimony, biography and Annaya
  journeys.
- Returning organic visitors and meaningful actions such as reading a guide,
  starting a prayer, opening the Rosary experience or submitting a testimony.

### Guardrail metrics

The bot must alert and stop publishing when any of these regress:

- More canonical pages disappear from the sitemap than are intentionally
  removed.
- A locale has missing reciprocal `hreflang` links or a non-200 canonical.
- Redirect chains, loops, 4xx/5xx rates, robots blocking or noindex coverage
  increase unexpectedly.
- Core Web Vitals, mobile layout, accessibility or JavaScript error rates worsen.
- Search impressions grow while engagement, trust signals or content accuracy
  clearly decline.
- A change adds duplicate titles, descriptions, headings or near-identical
  pages.

### Baseline and reporting windows

At the start of each month, save a Search Console baseline covering the previous
28 and 90 days. Record property, dates, country, device, query/page filters,
clicks, impressions, CTR and average position. Compare like-for-like windows;
never call a one-day fluctuation a trend. Keep exports outside the public web
root.

## Bot architecture

The bot should have five cooperating jobs with a shared evidence store:

1. **Observer** gathers live, repository and search data without editing files.
2. **Analyst** turns observations into ranked opportunities with confidence and
   expected value.
3. **Builder** makes one bounded change in a branch or worktree.
4. **Verifier** runs local, SEO, browser, accessibility, route and deployment
   checks.
5. **Publisher/Reporter** publishes only approved batches, verifies production,
   notifies search engines and writes the work log.

Every job writes structured records with:

```text
date, task_id, source_evidence, target_urls, change_type, expected_metric,
risk_level, tests_run, before_snapshot, after_snapshot, publication_commit,
live_verification, rollback_reference, next_review_date
```

Use a persistent `docs/seo/bot-log/` directory for summaries and keep private
Search Console exports outside the repository. Do not store credentials,
cookies, tokens or user-identifying telemetry in the repo.

## Daily 24-hour loop

The scheduler may run this loop every 6–12 hours. Repeated unchanged checks
should stay quiet. Notify only for a meaningful change, a completed safe batch,
an error, or human review.

### 00:00 — health and crawl observation

- Fetch `robots.txt`, `sitemap.xml`, the homepage, every authored locale hub,
  every authored locale guide, and critical product/experience pages.
- Check status, redirect count, canonical URL, `hreflang`, title, description,
  H1, robots directives, JSON-LD validity and response time.
- Compare the URL inventory with the previous snapshot.
- Check live assets referenced by important pages and sample optimized images,
  fonts, scripts and audio.
- Run a broken-link sample and record new 404/410/5xx responses.
- Check Search Console indexing changes, manual actions, security warnings and
  sitemap read status when the connector is available.

### 03:00 — performance and mobile observation

- Run a lightweight mobile and desktop performance sample on the homepage,
  prayer library, Rosary guide, one representative authored locale guide and
  one testimony page.
- Track LCP, CLS, INP/TBT, transfer size, render-blocking resources, image
  dimensions and JavaScript errors.
- Compare against the prior seven-day median, not a single lab run.
- Open an issue when a regression exceeds the agreed threshold; do not rewrite
  assets automatically without a before/after test.

### 06:00 — search opportunity analysis

- Pull new Search Console queries, pages, countries and devices.
- Group queries by intent: learn, pray, compare, visit, listen, submit and
  navigate.
- Find pages with high impressions and low CTR, positions 5–20, rising queries,
  or strong clicks with weak next-page engagement.
- Find query/page mismatches where the current page does not answer the intent.
- Deduplicate opportunities by topic cluster and assign one canonical owner
  page per intent.
- Do not use scraped competitor copy or publish pages solely because a keyword
  has volume.

### 09:00 — content maintenance

- Improve the highest-ranked safe opportunity by editing the catalog or source
  template, never generated HTML directly.
- Prefer a clearer answer, better heading structure, stronger internal links,
  accurate source notes, useful examples, updated dates or better media alt text.
- Add FAQ-style answers only when they genuinely answer user questions.
- Keep religious wording respectful and source-backed. Flag doctrinal uncertainty
  for human review instead of guessing.
- Update `dateModified` only when content materially changed.

### 12:00 — international quality

- Compare authored locale pages for missing sections, stale translations,
  placeholder leakage, broken links, title/description parity and incorrect
  directions.
- Identify countries where Search Console shows demand but the authored locale
  does not yet answer the query.
- Recommend a new locale only when evidence supports it and the project can
  maintain a complete, human-quality catalog.
- Keep runtime-only translations out of `sitemap.xml` and `hreflang`.

### 15:00 — internal linking and information architecture

- Check that every important page has a path from the homepage, a topic hub or
  a related guide.
- Find orphaned pages and pages with excessive outbound links.
- Add contextual links with descriptive anchors between biography, miracles,
  prayers, novena, Rosary, Annaya and testimony resources.
- Preserve the existing top language selector. Never add duplicate footer or
  in-content language menus.

### 18:00 — verification and release decision

- Build a proposed diff and a human-readable report.
- Classify as safe automation, review-required, or blocked.
- Safe batches may proceed only when all checks pass and no protected files or
  canonical routes are changed.
- Queue review-required work for the owner rather than publishing it.
- If approved, deploy to stage, verify the live stage site, then publish using
  the existing workflow.

### 21:00 — measurement and report

- Verify the published URLs from multiple route forms and at least one mobile
  viewport.
- Submit changed canonical URLs through IndexNow after live verification.
- Confirm Google Search Console sitemap state; do not repeatedly request the
  same URL when it is already queued.
- Write a short report: shipped, measured, blocked, next opportunity and risk.

## Weekly operating cycle

Every week, the bot should produce one prioritized backlog and one health report.

### Technical SEO audit

- Crawl the canonical inventory and compare it with `sitemap.xml`.
- Check duplicate titles/descriptions, empty headings, missing alt text, broken
  canonical links, broken `hreflang`, redirect chains, orphan pages and indexable
  utility/private pages.
- Validate structured data syntax and only emit schema supported by visible page
  content.
- Check `robots.txt`, sitemap freshness and ownership files.
- Review service-worker cache behavior after every deployment.

### Content and topic audit

- Maintain topic clusters for Saint Charbel biography, miracles, prayers,
  novena, Rosary, Annaya, testimonies and devotional practice.
- For each cluster, maintain a pillar page, supporting guides, internal links,
  authoritative sources and a freshness date.
- Identify missing answers from real queries rather than generating generic
  articles.
- Merge or redirect competing pages when they satisfy the same intent.

### Trust and quality audit

- Verify source links still resolve and are authoritative.
- Mark personal testimonies as personal reports; do not present them as medical,
  scientific or Church guarantees.
- Keep moderation, privacy, security and account pages out of search when they
  are not public editorial content.
- Check that claims, names, dates, quotations and translations have evidence.

### Link and outreach research

- Research reputable, relevant opportunities such as Catholic directories,
  monastery resources, scholarly references and community organizations.
- Prepare suggested resources or collaboration ideas only.
- Never auto-email, spam, buy links, create forum posts or represent the owner
  without explicit approval.

## Monthly strategy cycle

Once per month, the bot should review whether the system is attracting the right
people, not merely more impressions.

1. Re-score topics by qualified clicks, CTR, position opportunity, conversion
   usefulness, content quality and effort.
2. Reconcile Search Console country demand with the eight authored locales.
3. Review whether a new language deserves a complete static catalog.
4. Compare mobile performance trends and hosting cache behavior.
5. Inspect external links and brand mentions manually or through approved tools.
6. Refresh the editorial calendar with a maximum of a few high-quality pages,
   not an arbitrary daily article quota.
7. Archive completed work logs and update this plan when the architecture changes.

## Opportunity scoring

Score each candidate from 0–5:

```text
impact = search demand + CTR opportunity + position opportunity + user value
confidence = evidence quality + intent fit + source quality
effort = implementation, translation and verification cost
risk = duplicate content, accuracy, route, performance, security and trust risk
priority = (impact * confidence) / max(1, effort + risk)
```

The formula is a queueing aid, not a claim of precise traffic forecasting. A
low-volume page with excellent intent fit can outrank a high-volume vague idea.
No change ships with an unresolved high-risk score.

## Content production rules

Every new or substantially edited page must have:

- One primary search intent and a plain-language page brief.
- A unique title, meta description, H1, canonical and useful URL.
- A concise answer near the beginning, followed by enough depth for the topic.
- Descriptive internal links and authoritative external sources.
- Accurate image alt text and explicit media dimensions.
- Valid JSON-LD only when the visible page supports it.
- A clear author/source note when the topic needs authority context.
- Mobile-readable layout, no intrusive overlays and accessible controls.
- A defined success metric and a review date.

Do not use keyword stuffing, hidden text, doorway pages, spun text, fake FAQs,
fake reviews, false urgency, misleading titles, automatic medical promises or
unreviewed machine translation as published editorial content.

## International SEO rules

- The eight authored locale hubs are `/`, `/ar/`, `/fr/`, `/es/`, `/pt/`, `/it/`,
  `/de/` and `/pl/`.
- Each authored locale has the same topic IDs, translated content, canonical,
  reciprocal `hreflang` and sitemap coverage.
- Locale hubs use directory `index.html` pages to avoid Hostinger/LiteSpeed file
  and directory redirect collisions.
- The dynamic selector may support many additional languages, but runtime
  variants do not become sitemap URLs unless separately authored and tested.
- Keep locale slugs stable. A route change requires a tested 301 migration plan,
  sitemap update, canonical update and live verification.

## Automation boundaries

### The bot may do automatically

- Read public analytics, Search Console reports and repository files through
  approved connectors.
- Run audits, tests, link checks, performance samples and diff reports.
- Fix generated output by changing its catalog/template source and rebuilding.
- Repair clearly mechanical metadata or link issues when tests cover the rule.
- Open a branch and prepare a small pull request with evidence.
- Submit a sitemap or IndexNow payload after the release is live and verified.

### The bot must ask for review before doing

- Changing canonical URLs, locale codes, redirects or sitemap architecture.
- Adding a new language or publishing machine-translated religious content.
- Making factual, doctrinal, medical, miracle or testimony claims.
- Editing privacy, authentication, moderation, payment, security or server files.
- Adding analytics that collect new personal or sensitive information.
- Sending outreach, publishing social posts, changing external profiles or
  buying links.
- Merging a high-risk pull request, force-pushing a protected branch or changing
  deployment credentials.

### Immediate stop conditions

Stop and report when:

- The live site differs from the approved release.
- Any canonical locale route redirects in a loop or returns a non-200 response.
- A deployment cannot be verified against the checkout.
- Search Console reports a security issue or manual action.
- A proposed change depends on unverifiable facts or inaccessible sources.
- The bot cannot distinguish user-generated testimony from editorial claims.
- A requested action would expose credentials or private user data.

## Required verification pipeline

Before a branch is proposed:

```sh
npm ci
npm run i18n:check
python3 scripts/qa/check_seo.py
python3 scripts/qa/check_language_routes.py http://127.0.0.1:4192
npm run qa
npm run quality
git diff --check
```

For a release:

1. Verify the working tree and commit are the intended batch.
2. Test locally and record the result.
3. Push to `stage` through the repository workflow.
4. Confirm stage deployment and live frontend file integrity.
5. Test canonical routes, redirects, sitemap, robots, locale pages and mobile
   behavior on the live origin.
6. Flush hosting/CDN cache when required and verify again.
7. Notify IndexNow only after live verification.
8. Submit or refresh the sitemap in Search Console.
9. Promote `stage` to `main` through a reviewed pull request and verify both
   branch SHAs are aligned.

## Bot report format

Each daily report should be short and evidence-based:

```markdown
# SEO bot report — YYYY-MM-DD

## Health
- Live status:
- Canonical/indexable pages:
- Sitemap status:
- Search Console changes:
- Core Web Vitals sample:

## Shipped
- Commit / pull request:
- URLs changed:
- Why this matters:
- Tests and live verification:

## Findings
- Priority opportunity:
- Evidence:
- Estimated effort:
- Risk:

## Blocked or awaiting review
- Decision needed:
- Why automation stopped:

## Next cycle
- One highest-value task:
- Success metric:
- Rollback reference:
```

## First 90-day roadmap

### Days 1–7: establish control

- Confirm Search Console, Bing, analytics and IndexNow ownership.
- Capture baseline queries, countries, pages, clicks, impressions, CTR and
  positions.
- Verify all canonical pages, redirects, locale alternates and sitemap entries.
- Establish the daily report and alert thresholds.

### Days 8–30: improve existing demand

- Rewrite the highest-impression, lowest-CTR titles and descriptions.
- Strengthen internal links around the prayer, Rosary, novena and biography
  pillars.
- Fix every discovered crawl, mobile, accessibility and performance regression.
- Add genuinely useful FAQ answers to pages that already earn impressions.

### Days 31–60: deepen topical authority

- Build the most valuable missing guide in each proven topic cluster.
- Add original explanations, source notes, navigation and media.
- Refresh older pages where search intent or source information changed.
- Compare country demand and decide whether another authored locale is justified.

### Days 61–90: compound and refine

- Improve pages ranking positions 4–20 with better answers and internal links.
- Consolidate overlapping pages and strengthen the best canonical owner.
- Review qualified engagement, returning visitors and prayer experience starts.
- Publish a quarterly SEO decision record: keep, improve, merge, redirect or
  retire each candidate page.

## Definition of done

The bot has completed a task only when the change has a recorded reason,
evidence, tests, live verification, publication commit, measurement plan and
rollback reference. “More pages,” “more keywords” or “a higher lab score” alone
do not count as SEO success.

The bot should optimize for a growing library of trustworthy, useful, technically
clean pages that people choose to read and return to. That is the durable path to
search visibility across countries and languages.
