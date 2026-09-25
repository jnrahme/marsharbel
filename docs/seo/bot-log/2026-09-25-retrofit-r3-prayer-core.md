# 2026-09-25 - Retrofit R3: prayer core pages

Third retrofit batch under Joey's 4:31 PM program.

## Outcome
- saint-charbel-prayers.html: UPGRADED. Added "How This Collection Is
  Labeled" section (traditional Rosary core texts vs this site's original
  devotional compositions, no guaranteed outcomes) and a Sources section
  (Annaya monastery novena text, Vatican Saint of the Day, link to the
  Prayer Library sourcing policy). Before this retrofit the page's original
  compositions were unlabeled - a gap under the sacred-content rules.
- saint-charbel-prayer-for-a-miracle.html: AUDIT PASS. Reader promise,
  monastery-published prayer text quoted with provenance, urgent prayer
  explicitly labeled original composition, "When the Miracle Does Not Come"
  honesty section, sourced miracle cases, dated Sources with what each
  supports.
- saint-charbel-prayer-for-healing.html: AUDIT PASS. Same standard: honest
  hero promise, labeled original compositions, documented healings with
  sources, pastoral honesty (oil is devotion, never medicine), FAQ, Sources.
- saint-charbel-novena.html: AUDIT PASS. Monastery-published day-by-day
  text labeled as such, "What Is a Novena" explainer, Sources traced.
- prayer-library.html: AUDIT PASS. Its "How This Library Is Sourced and
  Labeled" section is the site-wide reference the other pages now link to.

## QA
check_seo green (130), test_seo OK, i18n policy green (baseline refreshed
for the changed page, 93 to 105 entries), sitemap_lastmod run, diff --check
clean. Playwright: new sections render desktop, zero console errors.
