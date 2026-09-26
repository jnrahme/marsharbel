# 2026-09-26 - li-human sweep batch 1: story, history, miracles index (+ verdicts: visit-annaya, prayer-library)

## Task
Joey approved the li-human pilot by voice note (relayed by parent 11:32 AM): run the sweep site-wide in batches. Motivation (his): copy must not read AI-generated, for Google ranking; quality is the standard, not detector scores. Method per pilot: humanize.py report-only as analysis, hand edits, accuracy diff-review, never blanket auto-apply.

## Page verdicts (detect.py baseline -> editorial review)
- story.html (65.9 REVIEW): mostly UI chrome + fact lists; prose already warm. One real catch: the phrase "people from many places and backgrounds" appeared twice on one page (book lede + Mercy for All card).
- history.html (64.9 REVIEW): copy already good ("a school of listening rather than speaking"). Flagged triad is "poverty, chastity, and obedience" - the factual vow formula, rejected on accuracy grounds. Flagged "landscape -> market" rejected (literal Mount Lebanon landscape).
- miracles/index.html (69.4 REVIEW): careful sourced devotional journalism; "the truth is remarkable enough that it needs no exaggeration" kept verbatim ("remarkable -> notable" swap rejected - the word does the work). "journey -> process" rejected (Vatican term "apostolic journey"). Middle dots are register-card separators, markup. One smooth-out applied.
- visit-annaya.html (64.0 REVIEW, VOICE 30.9): NO CHANGE. Score is dragged by practical/list content (directions, times, tips) which should be plain; the prose itself is the standard ("people pray as they wait, many carrying a written intention, a photograph of someone sick").
- prayer-library.html (56.6 REVIEW, VOICE 16.5): NO CHANGE, excluded from rewording. The low score is the sacred liturgical texts (Our Father, Hail Mary, Trisagion, Saint Ephrem) - formal register is correct and untouchable; the editorial prose around them is already human ("On waking, before the phone and before work."). Documented so future batches don't re-flag it.

## Edits applied (4, all accuracy-reviewed)
1. story.html Mercy card: "...to people from many places and backgrounds." -> "...to people of every place and background." (dedup; meaning identical)
2. history.html H1: curly -> straight apostrophe (typography).
3. history.html lede: "whose life was marked by silence... His witness continues to influence Christians and non-Christians worldwide." -> "who gave his life to silence... His witness still draws Christians and non-Christians from around the world." (de-passivized, warmer; facts untouched)
4. miracles/index.html exhumations: "- notably in 1927, and in 1950, 1952 and 1955 as evidence was gathered" -> ": in 1927, then in 1950, 1952 and 1955, as evidence was gathered" (dates verbatim)

Scores: story 65.9->65.9, history 64.9->66.1, miracles 69.4->69.5. Flat by design - these pages were already good; the sweep certifies and polishes, it does not churn. Quality is the verdict, scores are a signal.

## Verification
- Baseline: 3 pages re-registered via snapshot extractor; i18n policy green.
- Full QA chunked: chunk1 (build-home-css, i18n:check/test, check_seo, test_seo, feeds, testimony) GREEN; chunk2 (testimony-security, site-smoke) GREEN; chunk3 (6 rosary sub-suites) GREEN.
- Pixel review: history hero, story Mercy card, miracles exhumations card - all well-set, no layout shift; facts visually verified intact (timeline dates, exhumation years).

## Sweep plan (remaining ~85 hand-authored English pages)
Full mechanical scan (detect + humanize report) across all pages; batch by REAL flagged items - slop terms in prose (not markup), em dashes, curly quotes in visible text, triads in non-factual sentences - plus editorial passes where prose is genuinely stiff. Pages already good get certified, not churned. Mirror pages (prayers, qadisha) go through keyed en catalogs with intl regeneration via parent. Prayer texts, vows, quotes, scripture, dates, names, geography always verbatim.
