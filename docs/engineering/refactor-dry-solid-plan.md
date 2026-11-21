# DRY + SOLID refactor: audit and staged plan

Status date: 2026-10-03. Base: stage 93de999. Rule for all stages: served output stays byte-identical (or, where a stage cannot, a reviewed pixel and behavior parity pass with Joey's approval). Full QA gates every increment.

## Done (HTML scaffolds, byte-identical)

Inc 1 page build + analytics/skip-link fragments. Inc 2 header family + shared nav generator. Inc 3 footer credit fragments. 93 hand-authored pages build from `src/pages`.

## Audit findings still open

HTML: head meta/preload lines (80-93 pages), 96 inline JSON-LD blocks, 8 inline `<style>`, 8 header brand variants, hero and card patterns, 8 footers outside the credit pattern, generated mirrors (templates/mirrors) that own their own nav copy.

JavaScript (534 KB, 11.4k lines):
- `global-audio-player.js` and `global-audio-player.v20260304.js` are byte-identical (32,561 bytes). 35 pages load one URL, 1 page the versioned one.
- `storybook.js` (88 KB, 1 closure, 83 inner declarations): URL parsing, data loading, rendering, audio, language, localStorage and DOM wiring in one IIFE. Mixed responsibilities, 29 direct DOM lookups, no module seams.
- `mystery-meditation.v20260304.js` (52 KB, top-level script, 45 declarations): reads globals (`ROSARY_MYSTERIES`, `MYSTERY_KEY`, `MYSTERY_BASE`), session storage, audio sequencing and rendering together. `mystery-data.js` is 57 KB of data assigned to a global, plus `mystery-library.js`.
- 13 `*-story-data.js` files share one shape (`window.<NAME>_STORY_EN = [ {illustration,title,body,prayer,...} ]`) and are loaded one per page, so the duplication is structural, not textual.
- `translate.js` (32 KB, 25 functions) and `share.js` (19 KB) are plausible modules.
CSS (204 KB): `styles.css` is 2,882 lines and holds tokens, base, layout, nav, components and page-specific rules together. `:root` tokens are defined in styles/home/storybook/international separately. Repeated breakpoints (820px written 3 ways: `@media(max-width:820px)`, `@media (max-width: 820px)`, 760/680 variants).

## Staged plan, lowest risk first

Stage A (byte-identical, finish HTML): head meta/preload fragments; JSON-LD as data + one serializer that reproduces the exact bytes (verify per page); inline `<style>` extraction only where the bytes can stay (otherwise defer); hero/card fragments; footer long tail. Verification: compare-served.sh.

Stage B (byte-identical, JS dedupe): remove the audio player duplicate by making the versioned filename a build-time copy (both URLs keep serving the same bytes), or by repointing the 1 page, which changes that page's bytes and is flagged for approval. Story-data: no change to served files; add a schema check (`scripts/qa`) that all 13 files match one documented shape. Verification: manifest + schema test.

Stage C (output changes bytes, behavior must not): split JS into ES modules under `src/js/` with a bundler step that emits the same public filenames. Order: `share.js` and `translate.js` (small, tested), then `storybook.js` (state/data loader, renderer, audio controller, language, storage as separate modules, one dependency direction, DOM access injected), then `mystery-meditation` (same split; replace window globals with one explicit config object). Single responsibility and dependency inversion are the SOLID targets that apply to a browser app; interface segregation and Liskov have no real surface here and I will not invent class hierarchies for them. Verification: all existing Playwright suites (rosary, story player, navigation, a11y), plus new characterization tests written BEFORE each split (record current DOM output and audio-sequence behavior for fixed inputs), plus desktop+phone rendered pass. Bytes change, so this stage needs Joey's explicit go and a full-site rendered review, and ships one module family per PR.

Stage D (CSS): extract tokens to one `tokens.css` source, split `styles.css` into base / layout / nav / components / pages sources, concatenated by a build step into the same public `styles.css`, in the same rule order so the cascade is unchanged. Normalize breakpoints only inside the source if the emitted CSS stays identical, otherwise a separate approved change. Verification: emitted CSS diff first (target: byte-identical), computed-style snapshot of every page at 390 and 1440 widths if not.

Stage E (architecture guardrails): lint/CI rules that stop re-duplication (no pasted nav/footer/GA, fragment usage check, import-direction check for JS), AGENTS.md update with the twin workflow, deploy exclude for `src/` and `partials/fragments/`, contributor doc.

## Risks and calls needed from Joey

- Stage C and any CSS change that alters bytes: needs his go; they carry real regression risk on rosary audio and the storybook player. I recommend doing them after A and B merge, with characterization tests first.
- Other lanes editing a page with a `src/pages` twin must edit the twin and run `npm run build:pages`. Needs a rule in AGENTS.md and a CI check (Stage E, cheap, can ship early).
- Generated mirror pages and the international build (about 64 locale pages) keep their own generators; folding them into the same build is a later, separate stage.
