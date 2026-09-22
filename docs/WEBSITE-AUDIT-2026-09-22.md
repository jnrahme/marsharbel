# Website audit — September 22, 2026

Audited the local working tree, including the earlier text-spacing fixes. Changes have not been deployed.

## Fixed

- Navigation: Escape now dismisses hovered dropdowns, returns keyboard focus to the parent, and keeps expanded-state announcements synchronized. Moving focus between menu groups no longer closes the newly focused group. Touch menus can reopen after dismissal.
- Gallery: added dialog semantics, initial focus, keyboard focus containment, and focus restoration on close. Arrow keys change photos without scrolling the underlying page. Removed duplicate close handling.
- Gallery on landscape phones: image and Previous/Next controls now stay within the viewport; previously Next appeared below the bottom edge at 667 × 375.
- All 20 mystery pages and the shared meditation page: labeled the mystery selector and gave the prayer-progress group valid accessible semantics.
- Story player: increased contrast of the small sticky progress label using the shared text color.
- Internal links: corrected the floating audio player's initial guide URL for nested mystery pages and normalized the moderation page's public testimonies link.
- Regression tests: updated two outdated assertions to open the grouped navigation and accept valid same-page filename-plus-fragment links.

## Verification

- Crawled all 50 HTML application pages: no JavaScript exceptions, duplicate IDs, broken loaded images, or serious/critical WCAG A/AA violations after fixes.
- Checked 124 unique internal URLs and fragments: no broken destinations. The Install App action is handled by JavaScript and was excluded from static fragment validation.
- Existing Playwright quality suite: 125 tests passed across five device profiles.
- Existing site smoke, Rosary smoke/menu/end-stage/prayer/intro/UI, story floating-player, and checklist suites passed, with the corrected checklist suite rerun separately after the original full run exposed its stale assertion.
- New `npm run test:ui-behavior`: passed at 375 × 667, 667 × 375, and 1366 × 900. Covers menu dismissal/reopening, keyboard focus, gallery image changes, and screen containment for every gallery image.
- All 260 Rosary audio files referenced by the manifest exist locally.
- Earlier layout audit: 50 pages at five widths, 250 checks passed.
- `git diff --check` passed.

## Limits and configuration

- These are local browser checks, not a production deployment or a guarantee against every possible bug.
- Account creation, testimony intake/uploads, and moderation are deliberately paused with placeholder service configuration. Live authenticated submissions and moderation were not exercised.
- The souvenir store is intentionally unconfigured; live checkout was not exercised.
- Browser speech voices were unavailable in the automated environment, so the existing speech-sanitization tests were skipped. Physical-device audio output, native installation prompts, and every translated language still need device/service validation.
- Third-party destination availability was not exhaustively checked.

The repeatable UI regression script is `scripts/tests/navigation_gallery.mjs`; run it against the local dev server with `npm run test:ui-behavior`.
