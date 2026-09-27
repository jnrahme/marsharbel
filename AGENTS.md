# Marsharbel engineering rules

Read this file before touching the repo. It is the standing rulebook for every agent and contributor. **Update it whenever a new hard rule or lesson lands** - an unrecorded lesson will be re-learned the expensive way.

## The golden rule: rendered review before done (Joey, 2026-09-27)

Nothing merges, deploys, or is reported done without a real rendered review: open the affected pages in a browser and visually inspect them on desktop AND phone. CI green is a precondition, never the gate. HTTP 200 and test-only verification proved insufficient - a hub once shipped unstyled while returning 200.

- Verify the actual viewport (`innerWidth`) before trusting a screenshot; browser tooling can pin a stale viewport.
- No browser available = the work waits. It does not ship.

## Git flow

- Never push directly to `stage` or `main`. Branch off the latest `stage`, open a PR, run the full QA gate, merge only when everything is green.
- `stage` IS production. Merging to `stage` publishes marsharbel.com.
- Verify live after every merge (byte-verify + rendered check). If anything broke, roll back and report - never hot-patch live files outside the merge flow.
- Keep the working tree clean: never `git add -A` unscoped in a worktree that carries a `node_modules` symlink (`git add -A -- ':!node_modules'`).

## Deployment (Hostinger)

- Production is served by Hostinger. Deploy web-only files via the established TUS upload flow; never wholesale overwrite or delete.
- Exclude `docs/`, `scripts/`, `tests/`, `templates/`, `.github/`, package files, README and `*.md`. INCLUDE changed `locales/*.json` - they are fetched at runtime.
- Throttle manual uploads. After deploy: CDN purge, byte-verify immediately, again after ~90s, and twice more at ~15-minute intervals - edge caches lie in both directions.
- After every merge, wait for the git-integration sync to conclude before TUS-deploying, or the deploy races it.
- Never upload Arabic woff2 fonts to git-tracked paths; the git-integration sync shadows them in some regions. Arabic webfonts live at TUS-only `-v3` filenames. `international.css` pages use system Arabic fonts by design - `document.fonts` empty there is expected, not a bug.

## Required verification (merge gate)

Run the full gate before merging, in this order, and inspect the results:

1. `python3 scripts/build-international.py --check` - generated international files fresh (build first with `npm run i18n:build` when catalogs/templates changed).
2. `python3 scripts/qa/check_seo.py` - indexability, metadata, links, reciprocal hreflang.
3. `python3 scripts/qa/check_i18n_policy.py` - hardcoded-wording policy (rebuild `locales/legacy-text-baseline.json` via its snapshot function when legacy wording legitimately changed).
4. `node scripts/sync-navigation.mjs --check` - navigation parity (edit nav ONLY in `partials/primary-navigation.html` + `templates/mirrors/*.html`, then sync in write mode).
5. From `scripts/qa`: `python3 -m unittest test_seo test_prayer_mirror test_i18n`.
6. `bash scripts/qa/dead_code_check.sh` - new pages need real inbound links.
7. `bash scripts/qa/run_full_qa.sh` and `npx playwright test` for behavioral/browser scope when the change warrants it.
8. Run `python3 scripts/sitemap_lastmod.py` after `i18n:build` when pages changed.
9. New pages must also be registered in `scripts/apply_seo_tags.py`.

Re-run the FULL gate after any edit, in gate order. Do not claim perfect SEO, guaranteed rankings, or worldwide field performance from structural tests alone.

## Secrets

No passwords, tokens, keys, or credentials in the repo - ever. The repo is public. Do not commit personal analytics exports or local artifacts either.

## Content rules (Joey, standing)

- Real photos from referenced sources, with rights recorded. Never generated or animated images on content pages. (Storybook art is the one exception: painterly illustration.)
- Pictures on every page, no exceptions.
- Whole news/story cards clickable to their article.
- "Letters", never "testimonials".
- Journalist-quality pages: images, videos, links, references.
- Original content only - nothing copied from competitors, no thin or AI-looking pages.
- Translations mirror the English page exactly; only the text changes.

## Fact-checking

Re-derive factual claims from primary sources before shipping (Holy See, whc.unesco.org, etc.). Do not ship claims from memory or from competitor sites.

## Storybook standards

- Scripts sourced from primary sources. No miracle promises; reported experiences framed as reported; composite scenes flagged as composite.
- Consistent painterly illustration with correct age and clothing progression for the period.
- Narration: Kokoro `am_michael` at 0.94 speed with sentence-end rests.
- Checkpoint production work to an origin branch at every milestone. Work must never exist only in scratch - a full book's WIP was lost to a workspace wipe on 2026-09-27.

## Localization and mirrors

All user-facing wording lives under `locales/<language>/` with stable message IDs (see the mandatory localization rule below). For mirrored pages (locale versions of English pages):

- Mirror via locale catalogs and templates; translations mirror the English page exactly.
- Reciprocal hreflang across all language versions, locale routing (`locale-routes.js`), registry (`locales/registry.json`) and sitemap registration.
- Mirror templates need the `Generated by npm run i18n:build` marker or nav sync fights the builder parity test.

## Mandatory rule: reuse existing controls and preserve user flows

Before adding or changing a UI control, inspect the current page in the browser and search the shared HTML, JavaScript and styles for an existing implementation. Identify which component owns the behavior, then extend that component. Do not introduce a second control for the same purpose unless Joey explicitly requests it.

- Marsharbel already has a top language selector: `#sc-language-select`, created by `translate.js` and placed in the navigation. It is the single language control on existing app pages. Do not add footer language lists, in-content language menus or another translation widget to those pages.
- Connect localization and catalog improvements through the existing control. SEO work does not authorize new visible menus or a redesign. Keep canonical URLs, hreflang, sitemap and translated content separate from decisions about visible controls.
- Standalone translated guides may have one header language control because they do not load the app selector. Never render both controls on the same page. If the app header is reused there later, remove the standalone control.
- Preserve the user's current task, navigation and available functionality. Do not substitute a different experience merely because it uses the same language or topic; explain material flow changes and obtain the user's direction before expanding the scope.
- Add a regression check when correcting a duplicate control. Verify one selector, language switching and mobile layout on affected pages; inspect the actual UI, not just generated HTML.
- Update or remove superseded tests, generated output and styles so a rebuild cannot restore the rejected UI. Do not claim a Markdown rule alone guarantees that a mistake cannot recur.

This rule records Joey's correction on 22 September 2026: the app already had translation at the top, and the additional menus were unwanted.

## Mandatory localization rule

All new or changed user-facing wording MUST live under `locales/<language>/`, addressed by a stable, descriptive message ID. This includes headings, paragraphs, buttons, errors, loading/empty states, navigation, accessible labels, image descriptions, and search/social metadata. Do not embed translations in HTML templates, JavaScript conditionals, CSS generated content, or positional arrays. Do not assemble sentences from translated fragments.

- `locales/registry.json` is the source of truth for supported languages, native names, directions, topic order, source URLs and routes.
- `locales/<code>/common.json` holds shared messages such as `navigation.chooseLanguage`.
- `locales/<code>/pages.json` holds topic messages and sections keyed by semantic IDs such as `prayers.sections.daily.body`.
- Maintain all keys and named placeholders across English, Arabic, French, Spanish, Portuguese, Italian, German and Polish. Published pages must never silently fall back to English or machine translation to conceal missing catalog text.
- Add a language by editing the registry and adding complete catalogs. Do not add language-specific branches to renderers. Keep URL slugs stable once published.
- Catalog values are plain text. Escape them at the rendering boundary. Layout and links belong in templates/renderers. Never inject catalog text with `innerHTML`.
- Edit generated pages only through their catalogs and templates, then run `npm run i18n:build`. Managed navigation blocks, routes, canonical URLs, hreflang and sitemap entries are generated together.
- Use the page's declared language/direction. Keep native language labels and accessible links that preserve the current topic. Never force a country or language redirect based on IP.
- Existing legacy interactive pages are an explicit migration backlog. `locales/legacy-text-baseline.json` freezes their pre-existing wording; it is not permission to add more hardcoded strings. When changing a legacy feature's wording, migrate its affected messages to catalogs and render them through a keyed integration. Do not expand or regenerate the baseline merely to silence a failure. The JS detector is heuristic; review all UI strings, including single-word and dynamic messages, manually as well.
- Do not replace actual translated content with English copied into every locale. Validate language meaning as well as structural parity. Keep the independent status of this site clear and distinguish original devotions from traditional or official texts.

## Coding practices

Keep content, rendering, route configuration and tests separate. Prefer small functions with explicit inputs and no import-time writes. Use standard libraries and pinned dependencies where possible. Validate at boundaries, fail with actionable errors, preserve existing behavior and URLs, and test failure cases rather than only the happy path. Do not add frameworks, dependencies or abstractions without a concrete need.

## SEO ops on ship

- Submit changed URLs to IndexNow (`scripts/submit-indexnow.py`).
- Refresh sitemap lastmod (`scripts/sitemap_lastmod.py`).
- Log the change in `docs/seo/bot-log/`.

## Editorial review

Joey asked the assistant to research authoritative sources and use best judgment; external/native-speaker reviewers are not a required gate. Do not claim an external review took place.

## SmartAssist

When available, call `rag_search` before project-specific code, test, Git or architecture decisions. Use `apply_feedback_protocol` to persist user corrections and reusable rules. If SmartAssist is unconfigured, preserve the rule here and continue; do not install or configure it without a task reason.
