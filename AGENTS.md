# Marsharbel engineering rules

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

## Required verification

Before claiming changes are complete, run the checks appropriate to the affected scope and inspect their results:

1. `npm run i18n:check` — exact catalog parity, no empty messages, valid routes/placeholders, generated file freshness, and hardcoded wording checks.
2. `npm run i18n:test` — negative tests for missing keys, duplicates, unsafe routes, placeholder mismatches and escaping.
3. `python3 scripts/qa/check_seo.py` — indexability, metadata, local links and reciprocal hreflang.
4. `PORT=4191 BASE_URL=http://127.0.0.1:4191 npm run qa` — existing behavior and regressions.
5. `PORT=4191 BASE_URL=http://127.0.0.1:4191 npx playwright test --workers=3` — responsive, language switching, accessibility and other browser checks.
6. Test routing changes with Apache/LiteSpeed as well as the Node preview. Recheck representative mobile performance after rendering or asset changes.

Do not assert perfect SEO, guaranteed rankings, complete whole-site localization, or worldwide field performance from structural tests or local Lighthouse results alone.

## Coding practices

Keep content, rendering, route configuration and tests separate. Prefer small functions with explicit inputs and no import-time writes. Use standard libraries and pinned dependencies where possible. Validate at boundaries, fail with actionable errors, preserve existing behavior and URLs, and test failure cases rather than only the happy path. Do not add frameworks, dependencies or abstractions without a concrete need. Do not commit credentials, personal analytics exports or local artifacts.

## Deployment and account rules

Do not push to stage or publish a new batch until Joey has tested locally and explicitly approved that batch. Stage currently publishes the public website. Preserve the user's unrelated work and use the personal GitHub credentials without switching the global account. Verify the actual deployed files and routes after an authorized deployment.

## Editorial review

Joey asked the assistant to research authoritative sources and use best judgment; external/native-speaker reviewers are not a required gate. Do not claim an external review took place. The separate local-preview-before-push rule still applies.

## SmartAssist

When available, call `rag_search` before project-specific code, test, Git or architecture decisions. Use `apply_feedback_protocol` to persist user corrections and reusable rules. If SmartAssist is unconfigured, preserve the rule here and continue; do not install or configure it without a task reason.
