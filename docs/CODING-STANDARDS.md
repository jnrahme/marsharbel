# Coding standards

The bar for changing this repo, as actually practiced. Every rule names what enforces it:

- **CI** = a check in `qa.yml` / `quality.yml` / `dead-code-check.yml` that fails the merge. Required checks on `stage` and `main`: `qa`, `browser-quality`, `dead-code`.
- **Review** = no automatic check; the reviewer owns it.
- **Target** = not true of the repo today. A direction, not a rule. Do not cite a target as a reason to reject a PR.

Operating rules (git flow, deploy, rendered review, secrets) live in `AGENTS.md`. This file covers code structure only. The refactor history is in `docs/engineering/refactor-dry-solid-plan.md`.

## 1. One definition per repeated shape

| Rule | Enforcement |
|---|---|
| Page HTML is generated from `src/pages/**` plus `partials/fragments/*.html`. Edit the source, then run `node scripts/build-pages.mjs`. Never edit a served root `*.html` that has a `src/pages` source. | CI: `node scripts/build-pages.mjs --check` (`qa` job, run on a clean checkout). |
| A repeated block (analytics, skip link, header, footer credit, head meta and preloads, JSON-LD) is a fragment include `{{> name "arg"}}`, not pasted markup. Before writing markup, look in `partials/fragments/`. | CI for the blocks already extracted: `scripts/qa/test_head_fragments.py` and `test_jsonld_serializer.py` pin the per-fragment usage counts. Review for new shapes. |
| JSON-LD is produced by the serializers in `scripts/lib/jsonld.mjs` (WebPage, Article, Person, FAQ, and so on), not hand-written script blocks. | CI: `test_jsonld_serializer.py`. |
| Navigation is edited only in `partials/primary-navigation.html` and `templates/mirrors/*.html`, then synced. | CI: `node scripts/sync-navigation.mjs --check`. |
| Generated output is never edited by hand: `src/pages` output, `locales/**` international pages (`npm run i18n:build`), `home.css` (`npm run build:home-css`), feeds, news desk, sitemap lastmod, same-page manifest. Change the input and regenerate. | CI: each has a `--check` (`build-pages`, `build-international --check`, `build-home-css --check`, `build_feeds --check`, `build_news_desk --check`). |
| A patch prepared against an older base must be rebased onto the fragments, not paste them back inline. (PR 582 did this to the JPII page; PR 585 restored it.) | Review. Target: a lint that fails on an inline block identical to a fragment's output. |
| Every new file a change depends on is committed. | CI: clean-checkout build in the `qa` job (`build-pages --check`). Stage with `git status --short` before committing. |

## 2. Byte-identical refactor discipline

A refactor changes source, not served bytes.

1. Hash every affected served file before and after (`sha256sum`) and show they match, or list each page whose bytes changed and why.
2. Run `node scripts/build-pages.mjs --check`, then the characterization tests, then the full `qa` gate.
3. After merge, compare live bytes to the repo at the merge commit: `curl -sL "https://marsharbel.com/<page>?x=$RANDOM" | sha256sum`.
4. A refactor that cannot be byte-identical needs a reviewed pixel and behavior pass and an explicit owner decision.

Enforcement: CI for 2. Review and the PR description for 1, 3 and 4. Worked examples: increments 1-3 (PR 501: build step, header and footer fragments), inc6 to inc9 (PRs 570, 571, 573, 577: JSON-LD serializer and head fragments, 18 to 97 pages each, byte-identical). The inc8 miss (PR 573 left four untracked fragment files out of the commit, fixed in 574) is why the clean-checkout build exists (PR 575).

## 3. Internationalization

| Rule | Enforcement |
|---|---|
| User-facing wording lives in `locales/<lang>/*.json` under stable keys (`navigation.home`), never as English text in templates. | CI: `scripts/qa/check_i18n_policy.py` (hardcoded-wording policy, baseline in `locales/legacy-text-baseline.json`). |
| Locale pages are built from catalogs and templates (`npm run i18n:build`), and locales and slugs are registered in `locales/registry.json`. | CI: `build-international.py --check`, `test_i18n.py`. |
| Hreflang is emitted by the builder: reciprocal, absolute URLs, `x-default`, self-canonical. | CI: `check_seo.py`. |
| An exact (authored) translation records `masterSha256` of the English master. When the English master changes, the digest changes and the locale file is stale. Refresh it only after the translation is updated, never to silence the check. | CI: `test_exact_master.py`, `test_exact_wiring.py`, `test_de_exact_catalogs.py`. |
| Lanes supply translations. Engineering does not write locale copy. | Review. |
| A missing string key must fail the build, with no silent English fallback. | Target. Not verified as enforced today; do not rely on it. |

## 4. What CI enforces automatically

Required checks: `qa` (`npm run qa:ci`, which runs the sections of `scripts/qa/run_full_qa.sh`), `browser-quality` (8-shard Playwright), `dead-code` (`scripts/qa/dead_code_check.sh`: unreferenced JS and images, orphan HTML pages with no inbound link, stale versioned JS).

Inside `qa`: page build sync; the contract tests under `scripts/qa/test_*.py`; security headers including the enforced CSP (`test_security_headers.py`); testimony security and XSS checks (`npm run test:testimony-security`: SQL denial tests, validation and form-abuse cases, an HTML-sink scan plus a hostile-row browser probe in `testimony_xss.mjs`); SEO metadata and sitemap (`check_seo.py`); feeds; and the browser suites.

New pages need an entry in `locales/en/nav-legacy-copy.json` and at least one inbound link, or `dead-code` fails.

## 5. What review owns

No automatic check exists for these today.

- **Components.** Reuse an existing control and preserve user flows (`AGENTS.md`). A new pattern gets built from existing fragments first.
- **JS structure.** Client JS is classic script files, most as an IIFE, loaded per page. There are no ES modules in the browser. Keep one responsibility per file, no new globals beyond a single `window.<Name>`, and no HTML-injection sinks in testimony code (that one is CI).
- **CSS.** `styles.css` is the shared sheet with a `:root` token block; `home.css` is generated, so do not edit it. Reuse the existing tokens (`--bg`, `--gold`, `--text`, `--muted`, `--panel`) before adding a value. Scope page-specific rules narrowly. Prefer logical properties (`margin-inline`, `inset-inline-start`) in new rules so Arabic works without overrides.
- **Naming.** New files use kebab-case. The repo has legacy snake_case Python scripts, so match the neighboring files in a directory.
- **Tests.** Name tests by behavior, use role or label locators in Playwright, and add a failure case, not only the happy path.

## 6. Targets

Not true today. Treat as direction only.

- A lint that fails when markup matches an existing fragment (stops pasted blocks).
- Missing-string-key build failure.
- A CSS `@layer` order and zero new `!important` (about 50 exist today). Today the sheets have no layers.
- BEM naming. Today class names are plain kebab-case.
- ES-module JS.
- Strict import-direction checks between build scripts (Stage E of the refactor plan).
