# Implementation review - 2026-11-05 (Nov 3-7 batch)

Batch scope: window advanced from Oct 26-Nov 2 to Oct 31-Nov 7 (8 entries, span 7 days). Oct 26-30 pruned; Nov 3-7 inserted as kind=saint, calendar Maronite, book:null text-only units, translationStatus "agent-translated-native-review-pending".

Build executed on checkout of released stage 7961151d (PR902 head):
1. scripts/build_saint_of_day.py - "Saint of the Day source built" (src/pages/index.html, 76+/76-).
2. node scripts/build-pages.mjs --pages=index.html - "1 pages built".
3. scripts/i18n/refresh_saint_home_bindings.py - "Saint home bindings refreshed".
4. python3 scripts/build-international.py x2 to fixpoint - both "Localization built: 12 languages, 45 guides, 11 language homepages."
5. node scripts/build-home-css.mjs - "Generated home.css: 59927 bytes".
6. i18n:check - "Localization checked: 12 languages..." and "Localization policy passed: no new legacy wording or template literals."
7. QA: scripts.qa.test_saint_of_day 20/20 OK; scripts.qa.test_home_mirror 8/8 OK; scripts/qa/test_i18n (run from scripts/qa) OK.
8. scripts/sitemap_lastmod.py - "sitemap.xml updated" (delta included in patch).

Environment note: this working clone was shallow (recovery after sandbox wipe); the annaya-hero evidence gate failed closed with 'Missing/nonancestor evidence provenance' until the clone was deepened (git fetch --deepen=500 origin 7961151d...) so pinned evidence sha f94949db became a true ancestor of HEAD. No repo content change; environment-only.

Residuals: Playwright browser specs (tests/saint-of-day.spec.js: EN/AR active/inactive rendering, axe, three clocks) not runnable in this sandbox - left as Scrum's browser-verification residual. Native human review of translations remains pending per standing status. Nov 5 stays calendar-only until Main/Scrum resolves the Asya biography identity.

## Correction pass 2 (2026-10-31 07:00 ET)

Post-Scrum-finding correction head: locale twins neutralized for Nov 5 (no sex asserted; calendar label quoted and attributed) and Thai readings classification fixed (both pairs "readings", not "Gospel"). Re-ran on the corrected tree: build_saint_of_day, build-pages (0 written - EN unchanged), bindings refresh, build-international x2 fixpoint ("Localization built: 12 languages, 45 guides, 11 language homepages"), build-home-css (59927 bytes), i18n:check + policy PASS, test_saint_of_day OK, test_home_mirror OK, sitemap_lastmod "already current". Prior runtime/layout rendered PASS (80 native date+axe, 16 zoom axe, 264 runtime, 11 switcher, midnight transition, 20 unit/policy) is preserved ONLY as limited negative control - it does not approve this new head; editorial QA reopens on the corrected head.

## Reconstruction record (2026-11-01 ET)

Everything above this section records the withdrawn 2026-10-31 candidate line (heads 82ead7f3 / aaff9857, local-only, never pushed, destroyed by a sandbox wipe). Its build log, environment notes (including the shallow-clone/deepen note) and any correction rerun descriptions are HISTORICAL evidence of that destroyed candidate, not a description of the current head.

The current candidate was reconstructed 2026-11-01 on stage 7961151d as NEW commits 38eb33ea (pack) and 5cd1bf22 (Nov 5 correction, docs, sitemap). Source inputs: recovered authored source draft (sha256 9faa24ada65c8698f520d31e7287fb533c000e90938c6af06111f7898110f09a) and the Scrum Nov 5 neutralization corrections (sha256 ce69628ee578accb1ee11dd73b0c0a325ebd927cc7ab452c7cc4d0a58d831ff4), both hash-verified before application. No byte or ancestry identity with the withdrawn heads is claimed.

Gates actually run on the reconstructed head 2026-11-01: build_saint_of_day; build-pages --pages=index.html (0 written after the Nov 5 correction - EN unchanged); refresh_saint_home_bindings; build-international x2 to fixpoint plus --check PASS ("Localization checked: 12 languages, 45 guides, 11 language homepages."); build-home-css 59927 bytes; check_i18n_policy PASS; test_saint_of_day OK; test_home_mirror OK; sitemap_lastmod delta committed. Nov 1/2 templates verified byte-identical to stage on all 11 homepages; Nov 5 neutralization verified present in all 10 locale mirrors.
