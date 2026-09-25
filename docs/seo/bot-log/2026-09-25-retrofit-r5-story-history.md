# 2026-09-25 - Retrofit R5: story/history cluster

Fifth retrofit batch under Joey's 4:31 PM program.

## Outcome
- history.html: UPGRADED. The timeline page made dated factual claims with
  no Sources section; added one (Paul VI beatification address 1965,
  canonization homily 1977, Vatican Saint of the Day, archived Annaya
  biography) with dates and what each supports.
- become-like-charbel.html: LIGHT FIX. The Prayer of Commitment is an
  original site composition and was unlabeled; added the standard label
  line. Page otherwise at standard (health-aware fasting guidance, honest
  practice framing).
- story.html: AUDIT PASS. Per-page evidence panel, "True Dates" list with
  the devotional-tradition vs formal-recognition note, dated Vatican
  Research Basis.
- maronite-history.html: AUDIT PASS. Multi-publisher Sources (CNEWA,
  Lebanese Maronite Order, Britannica, Maronite Meditations).
- saint-charbel-quotes.html: AUDIT PASS. Provenance-first framing, sourced
  selection, "Words Reported Through Others" distinction, misattribution
  guide, dated Sources.
- how-did-saint-charbel-die.html: AUDIT PASS. Narrative with traced
  sources (Vatican Saint of the Day for the death dates).

## QA
check_seo green (130), test_seo OK, i18n policy green (baseline refreshed
for 2 changed pages), sitemap_lastmod run, diff --check clean. Playwright:
both changed pages render (reveal animations triggered), zero console
errors.
