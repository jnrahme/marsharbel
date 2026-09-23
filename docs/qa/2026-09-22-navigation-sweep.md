# Navigation consistency repair — 22 September 2026

The submission page retained an older flat navigation list. The main site had already moved to grouped Story, Miracles and Prayer menus. Other utility pages also retained independent menu copies, and previous tests did not compare their structure.

Primary navigation now comes from `partials/primary-navigation.html`. Run `npm run build:navigation` after editing that template. The generator preserves page-specific active states and handles relative paths for the mystery pages. All 49 pages with the main navigation are checked. The French and Arabic landing pages retain their intentional language navigation; the source-text redirect has no header. Search-engine verification files are not visitor pages.

The Browser quality CI workflow runs `npm run test:navigation-sync` (via the equivalent Node command) before browser tests, so stale menu markup or a missing navigation script fails the build. `tests/navigation-consistency.spec.js` checks every primary menu at five viewports: labels, dropdown opening, Escape closing, ARIA states, and horizontal containment.

Verification results are recorded after the final test run below. This is a navigation/layout audit, not certification of the unfinished testimony backend.

## Final results
- `node scripts/sync-navigation.mjs --check`: 49 pages, zero out of sync. Before applying the generator this check failed, including the reported submission page.
- `node scripts/tests/layout_audit.mjs --base-url=http://127.0.0.1:4321`: 52 pages × 5 widths (375, 768, 1024, 1366, 1920), 260 combinations, zero detected overflow/container-spacing failures.
- `PORT=4321 BASE_URL=http://127.0.0.1:4321 npx playwright test tests/navigation-consistency.spec.js --config playwright.config.cjs --workers=4 --output=/tmp/saint-charbel-nav-results`: 245 passed.
- Testimony quality suite: 60 passed, including responsive/accessibility checks and paused form behavior.
- Real Chrome inspection of the submission page confirmed the grouped Home / Story / Miracles / Prayer / Gallery / Souvenirs menu and active Miracles section.
- `git diff --check`: passed.

An initial test selector was corrected. A subsequent overlapping test run collided in Playwright's shared artifact directory; the final complete menu run used a separate output directory and passed. No application failure was hidden or retried away.

Changes are in the local testimony worktree; this report does not claim a public deployment. The user's open draft was not reloaded or cleared.
