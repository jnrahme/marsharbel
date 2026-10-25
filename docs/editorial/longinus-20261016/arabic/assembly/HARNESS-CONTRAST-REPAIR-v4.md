# Harness contrast repair v4 - evidence claim/type readability (2026-10-25 ~08:05 ET)

Scope (Main 07:59): scoped PRIVATE harness contrast repair; content/assets/data pinned; no shared production reader change; no unrelated chrome/localization sweep. Root cause (code-verified): storybook-joy.css (lines 133-136) colors the evidence panel dark (#49382a li, #69421e badge) for its light theme, while storybook-stage.css (line 115) gives the same panel a dark translucent background over the dark page - dark-on-dark, pre-existing in BOTH EN and AR.

Repair (harness-only): rtlharness-* copies carry a scoped <style id="rtlharness-contrast-fix"> that re-points the evidence colors to existing theme tokens (--theme-ink-soft li/summary, --theme-ink h3/badge, --theme-line badge border). Links untouched (already 12.76:1 PASS). Files: rtlharness-storybook.js (v3 R1+R7 hunks), rtlharness-longinus-ar.html (+R6 approved note +ar data +fix), rtlharness-longinus-en.html (EN equivalent, pinned longinus-story.html untouched).

Measured composited contrast (local Chromium via system google-chrome, served repo root, computed styles composited over ancestor backgrounds):
- claim text: 9.54:1 (was 1.74:1 FAIL) - phone AR p1, phone AR p6, desktop AR p6, phone EN p1 (all four identical)
- type badge: 11.76:1 (was 1.57:1 FAIL)
- source links: 11.62:1 (unchanged, pass)
R7 pairing re-measured in the same run: AR phone p6 labels at cx 118 (مرقس/Mark, LEFT) and 272 (يوحنا/John, RIGHT) - matches the EN pairing and the baked bitmap halves; desktop p6 cx 862/1122 same order. Visual self-inspection: AR p6 full frame + AR/EN evidence crops reviewed - pairing correct, panels readable.

Prior failing evidence preserved (v3 re-gate report/bundle + addendum, commits 59882915/436e94dd). Producer measurements are NOT the independent re-gate - design re-gate owed on these exact harness files.
