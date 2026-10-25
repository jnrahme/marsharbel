# Longinus AR/EN harness v4 - independent scoped contrast re-gate (design director, 2026-10-25 ~08:10 ET)

Assignment (Main 08:06:12): independent scoped re-gate of private contrast candidate commit 3c6be312fb207b218cbd6559e14c574561032d85 on branch candidate/longinus-en-f1245-20261025. Verify actual final bytes + composited surfaces; producer values are claims, not clearance. Private-only, no shared production change, no release clearance.

## VERDICT: PASS (scoped design re-gate) - all previously failing contrast roles now measure AA on actual composited pixels, independently reproduced on the exact committed harness bytes. R1 readability blockage resolved at harness level. No merge/publish GO - merge lane and Main own that.

## 1. Byte verification (producer hash claims -> actual bytes)
- rtlharness-storybook.js  sha256 86bcfa08efefc171...  == producer "Harness JS 86bcfa08"  CONFIRMED
- rtlharness-longinus-ar.html  sha256 7d789c216be88b31... == producer "AR HTML 7d789c21"  CONFIRMED
- rtlharness-longinus-en.html  sha256 cf576e9ffe3cc40b... == producer "EN HTML cf576e9f"  CONFIRMED
- Production pins UNCHANGED at candidate commit: EN data 5cb6c931..., EN html 23823828..., AR data ca20d630... (re-hashed myself). Diff vs 095ef841: harness files + docs only. No shared production byte modified. Scope constraint honored.

## 2. Harness delta audit (what the candidate actually changes)
- rtlharness-storybook.js vs production storybook.js: exactly the three v3 hunks (ar story-map entry, per-page evidence guard reorder, R7 caption conditional). Nothing else.
- rtlharness-longinus-en.html vs pinned longinus-story.html: +8-line <style id="rtlharness-contrast-fix"> (evidence colors re-pointed to theme tokens) + script src swap. Nothing else.
- Fix mechanism: .story-evidence/summary/li -> var(--theme-ink-soft); h3 + .story-evidence-type -> var(--theme-ink); badge border -> var(--theme-line). Links untouched. Overrides sit after joy.css in <head>, same-or-higher specificity -> deterministic win. No panel/background/geometry change.

## 3. Independent composited contrast measurements (my own headless Chromium, alpha-composited over actual ancestor surfaces incl. translucent panel tint; phone 390 + desktop 1440, AR + EN)
Identical on all four surfaces:
| role | v3 measured | v4 measured | producer claim | verdict |
| claim (li) | 1.74:1 FAIL | 9.54:1 | 9.54:1 | PASS, producer value independently confirmed |
| type badge | 1.57:1 FAIL | 11.76:1 | 11.76:1 | PASS, confirmed |
| panel summary | (not separately gated v3) | 12.22:1 | - | PASS |
| source links | 12.76:1 PASS | 11.62:1 | 11.62:1 | PASS (small shift from measurement path; still far above AA) |
| R6 production note | 6.75:1 PASS | 6.75:1 | - | unchanged, PASS |
Composited colors (AR phone): claim fg 199,189,176 on bg 30,23,18; badge fg 243,237,227 on 53,44,32; links fg 240,205,138 on 30,23,18.

## 4. Non-contrast states re-verified on candidate bytes
- R7 caption pairing INTACT: AR phone p6 Mark cx=118 LEFT / John cx=272 RIGHT; AR desktop 861/1122; EN desktop 319/579 - matches accepted v3 pairing and EN; visual frames confirm labels sit under the correct bitmap halves.
- R6 exact AR disclosure string present both viewports, 6.75:1, visually legible in frames.
- R1 content present AND NOW LEGIBLE: per-page evidence (assembled type/claim + USCCB links) renders readable on open panel (crops attached).
- AR network: zero failed requests, zero mp3 requests (correct - no AR narration).
- EN mp3 failure (page-01.mp3) reproduced on PRISTINE production longinus-story.html too - pre-existing production state (media not vendored in repo), NOT introduced by candidate.

## 5. EN regression proof
Harness EN closed-panel p1 full-page frame BYTE-IDENTICAL to pristine production EN render (sha256 b92beadc2e79... both). Open-panel differs only by the intended evidence text colors. Zero incidental EN change.

## 6. Observations (non-blocking, for the record)
- rtlharness-longinus-ar.html carries <html lang="en"> with no html-level dir; operative RTL comes from the production code path el.frame.setAttribute('dir','rtl') when contentLang=ar (verified in the ancestor chain: SECTION.storybook dir=rtl). Acceptable for a private harness; if this pattern ever ships as a page, html lang/dir must be ar/rtl.
- The SHARED production defect (joy.css dark evidence colors over dark stage panel) remains in production EN (and any future AR page) - this candidate is harness-only by design and does not clear production. Content owns any production fix; that is outside this re-gate.

## Evidence bundle
longinus-ar-v4-regate-bundle-20261025.tar.gz: v4.json (all measurements), AR/EN phone+desktop evidence crops, p1/p6 frames, prod-vs-harness EN identity proof frames.
