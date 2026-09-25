# 2026-09-24 - Mystery pages: remove layout shift (technical SEO lane)

Problem: CLS 0.079 on every mystery page (Lighthouse mobile). After load,
mystery-meditation.js removed the "Back to Mystery List" link, inserted the
progress/scripture card, and inserted the "Start Prayer" button above the
controls. Each change pushed the controls down.

Fix at source (20 mystery pages + the mystery-meditation.html template):
- The progress/scripture card ships empty in the HTML with a reserved line
  per row (min-height: 1lh). JS fills it and only builds it on pages that
  lack it.
- The Start Prayer slot ships in the HTML with an invisible same-size
  placeholder. JS swaps the real button in.
- The Back link JS always removed is gone from the HTML. What users see is
  unchanged; the page nav still links to the Rosary guide.
No new wording (i18n policy passes). Assets are served no-cache, so no
stale-JS mismatch.

Result: joyful-1 CLS 0.079 -> 0.003 (412px) and 0 (1366px); sorrowful-2
0.002 / 0.
