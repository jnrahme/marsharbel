# Longinus Storybook - Changed-EN Candidate Visual Verification (design-gate leg)

- Date: 2026-10-25, ~07:33-07:36 EDT
- Branch: longinus-en-f1245-20261025
- Render commit: f27c31567dda6d4c4ce8b6cb0d75f5607693b3c1 (content tip later moved to cb45344b, documentation-only; EN data/HTML pins unchanged, so this render remains the valid leg per main 07:32:57)
- EN data pin: 5cb6c931314a5bf6ea46153e34791007c2540a20a58013f56085242f32b3ec25 (verified exact)
- EN HTML pin: 238238282e31389c4a2a5aa37115f53fac527a6140b95be74f4f493811147ad4 (verified exact)
- Baseline for diff: commit 1d0e10f2 (accepted baseline leg)
- Renderer: local headless Chromium via Playwright, local python3 http.server, reducedMotion:reduce
- Viewports: phone 390x844, desktop 1440x900
- Scope: changed pages 1/3/4/5/6/8 only. Pages 2/7/9/10 unchanged - carried by the accepted baseline leg, not reswept. scene:'birth' on all pages ruled inert, not reswept.

## What changed (git diff, verified line by line)

Content delta confined to longinus-story-data.js (6 page bodies) + longinus-story.html (1 line, static p1 body). The rest of the diff is documentation (reviews, registry, AR drafts, report files).

- p1: "travelled" -> "traveled" (F4)
- p3: drops "Mark tells us that" opening -> "Women who had followed and cared for Jesus... Mark names..." (F1)
- p4: "Mark tells us that it lasted" -> "The Gospel says it lasted"; removes the reader-instruction aside ("When we read this part of his story...") -> body now ends "We can bring our own difficult questions to God. The officer was still there, facing Jesus." (F1+F2)
- p5: drops "Mark tells us that" before the curtain (F1)
- p6: drops "We should keep those threads clear." (F3); "Some Christian traditions also identify" -> "Some traditions also identify"; ending -> "Scripture tells us what happened. Tradition gives us the saint's name."
- p8: drops "We do not know every step of Longinus's life." (F5)
- Static HTML p1 body updated to match data.js ("traveled").

## Rendered-text verification (live DOM, both viewports)

- p1 body end: "...His words have traveled far beyond that hillside."
- p3 body start: "Jesus was not forgotten. Women who had followed and cared fo..."
- p4 body start: "At noon, darkness came over the land. The Gospel says it las..." / end: "...questions to God. The officer was still there, facing Jesus."
- p5 body start: "Jesus gave a loud cry and died. Then the great curtain in th..."
- p6 body end: "...tells us what happened. Tradition gives us the saint's name."
- p8: unknown-life sentence absent (removed at source; render reads data.js directly)
- Static p1 binding: raw server HTML #story-body before JS render ends "...traveled far beyond that hillside." - matches data.js p1 body and the rendered page. Binding holds.

## Reader chrome (measured)

- Counter "Page N of 10" correct on all 6 changed pages, both viewports.
- Active dot matches current page (1/3/4/5/6/8).
- Next not disabled through p8.

## End clearance (actual measurements vs sticky controls bar)

Phone just-clear gap (px): p1 10.9, p3 11.7, p4 10.9, p5 11.1, p6 11.4, p8 11.1. Max-scroll covered text elements: 0 on all six.
Desktop just-clear gap (px): p1 38.6, p3 44.8, p4 52.9, p5 44.8, p6 29.8, p8 44.8. Max-scroll covered: 0 on all six.

Baseline's explicit desktop just-clear graze caveat: this candidate measures 29.8-52.9px desktop gaps on changed pages; no graze observed.

## Capture bundle manifest (/tmp/longinus-shots/f1245/)

- en-phone-p01..p08 (6 files, changed pages): READING-POSITION frames (top of page after navigation). These are top/read positions, NOT end proof.
- en-desktop-p01..p08 (6 files): reading-position frames; full new bodies visible in the desktop spreads.
- decisive-phone-p04.png, decisive-phone-p06.png: reading-position decisive frames of the largest text changes.
- end-phone-p01..p08 (6 files), end-desktop-p01..p08 (6 files): END captures at the just-clear position - last text block resting just above the controls bar. These are the end-clearance proof frames; they correspond to the just-clear measurements above.
- results.json: full measured values (rendered body start/end, counters, dots, nav state, just-clear gaps, max-scroll covered counts).

## Findings

1. All six changed bodies render with the new text on phone and desktop; no leftover old strings in rendered DOM.
2. Reader chrome (counter, dots, nav) intact on all changed pages.
3. End clearance holds on all changed pages both viewports (gaps above; zero covered at max scroll).
4. No layout regressions vs baseline: plates, p6 comparison captions, drop caps, desktop two-spread, private-preview banner all unchanged.
5. Private story-shelf 404 remains an explicit known private-existing gap (unchanged; not a candidate regression).

## Ruling (design gate only)

Changed-EN text revision at f27c3156 renders correctly with reader chrome and clearances intact on all six changed pages, both viewports. Nothing new to flag visually. This is not a merge/publish GO. Unchanged-page and release gates stand on main's accepted baseline leg. Accepted by main 07:34:59 ("bounded changed-EN visual leg accepted with exact f27c3156 pins and reported clearances").
