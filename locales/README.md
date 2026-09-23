# Editing website languages

The international reading guides support English (`en`), Arabic (`ar`), French (`fr`), Spanish (`es`), Portuguese (`pt`), Italian (`it`), German (`de`) and Polish (`pl`). Each language has the same five topics: biography, prayer, nine-day reflections, Rosary and Annaya. These are complete static reading guides; the older interactive experiences are a separate migration backlog.

## Where to edit

- `registry.json`: languages, native names, writing direction, stable routes, topic/section order and source links.
- `<code>/common.json`: shared labels and homepage/search descriptions.
- `<code>/pages.json`: guide titles, descriptions, introductions and sections, addressed by meaningful IDs.
- `../templates/international/page.html`: shared layout. Text comes from the catalogs.
- `../international.css`: shared presentation, including Arabic right-to-left layout.

For example, change the French navigation label by editing `fr/common.json`:

```json
"navigation.home": "Accueil"
```

Change the French daily prayer in `fr/pages.json` at `prayers.sections.daily.body`. The corresponding ID exists in every language. Keep those IDs unchanged when rewording text. JSON keys and quotes must remain valid; values are plain text, without HTML.

Then run:

```sh
npm run i18n:build
npm run i18n:check
npm run i18n:test
```

The build updates the HTML, language links, canonical URLs, hreflang, sitemap and route map together. Never edit generated HTML or `locale-routes.js` directly. The build does not call a translation service: supply meaningful text in each language when adding or changing a message's meaning. It rejects missing/empty messages instead of silently showing English.

## Adding a language

1. Add one entry to `registry.json` with the language code, native name, `ltr`/`rtl`, homepage route and all five topic slugs. Use language-wide codes unless a real regional content difference calls for a separate locale.
2. Create `<code>/common.json` and `<code>/pages.json` with exactly the English catalog's message IDs and complete translations. Match named placeholders such as `{name}` if introduced.
3. Build and run all checks in `../AGENTS.md`. Update the explicit expected language set in the coverage test when intentionally changing supported languages.
4. Inspect mobile navigation, long text, direction, source labels and topic-preserving language switching. Test route redirects under Apache/LiteSpeed.
5. Have Joey test locally before requesting publication approval. Do not change published URL slugs casually; a route change needs permanent redirects.

The renderer needs no per-language conditionals. The English homepage remains the existing `/`; English reading guides live under `/en/`. The seven other homepages are `/ar`, `/fr`, `/es`, `/pt`, `/it`, `/de` and `/pl`.

## Hard rule and existing pages

`../AGENTS.md` requires every new or changed user-facing message to use catalogs. `legacy-text-baseline.json` records pre-existing hardcoded wording in older HTML/JavaScript; it is a frozen migration boundary, not an editable translation source. Do not expand the baseline to make a check pass. Migrate the affected messages when changing a legacy feature.

The legacy JavaScript detector is heuristic and does not prove that every dynamic or inline-script message is cataloged. Manual review remains required. The new international pages are generated entirely from catalogs and render without JavaScript or a remote translation widget. Some older interactive pages still use the previous translation integration; this rollout does not claim those experiences have been fully translated or migrated.

## Existing language control

The app already provides `#sc-language-select` at the top. Reuse it; do not add footer or in-content language menus. Existing pages' managed `i18n-navigation` blocks intentionally remain empty, and the generator keeps them empty. Standalone guides have one header language control because they do not load the app selector. The duplicate-control regression test protects the affected app pages. See `AGENTS.md` for the mandatory rule.
