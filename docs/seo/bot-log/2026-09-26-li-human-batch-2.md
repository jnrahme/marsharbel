# 2026-09-26 - li-human sweep batch 2: full-corpus review completed (gallery edit + 22 certifications)

## Task
Site-wide li-human sweep per Joey's approval (voice note, relayed by parent 11:32 AM): quality is the standard, scores are signals. Batch 2 completes the full-corpus review: every remaining hand-authored English page mechanically scanned (detect.py + humanize.py report over /tmp/sweep-*.txt extractions, 93 pages) and editorially reviewed.

## Edit applied (1)
gallery.html lede: "A curated visual collection connected to Saint Charbel devotion and miracle testimony traditions." -> "A visual collection drawn from Saint Charbel devotion and the testimony of miracles." (61.2 -> 63.0). Baseline re-registered via the snapshot extractor (one string swapped); i18n policy green.

## Certified NO CHANGE (with rationale)
- shop.html (58.7) + shop-mockup.html (63.0): coming-soon operations/product-concept pages; low score is functional list content, appropriate for purpose.
- testimonies.html (59.8): careful source-attributed reporting with honest Church-recognition labels; formal register is correct.
- st-nimatullah.html (62.7): strong biography ("We report that record; we do not add to it"); score dragged by FAQs and quotes.
- maronite-history.html (63.2): sourced historical journalism; FAQ/list structure.
- saint-charbel-quotes.html (63.4): the quotes themselves are untouchable; meta-copy about sourcing is honest and careful.
- saint-charbel-feast-day.html (63.7): honest calendrical explainer ("Rome's reasons... are not published, so we state the facts and attribute nothing more"); date lists.
- rosary-visual-guide.html (64.9): instructional step list, correct as-is.
- news.html (68.9): careful journalism; middle dots are metadata tag markup (site UI convention), not prose.
- how-did-saint-charbel-die.html (68.9): FAQ-structured; narrative prose good.
- jpii-story.html (69.0) + pio-story.html (70.9): storybook format with honest "story imagery, not claims" notes.
- pope-leo-xiv-annaya-visit.html (69.4): mostly papal quotes (untouchable) + good framing.
- blessed-fulton-sheen.html (68.2): strong feature copy ("calling him a saint today would simply be wrong"); quotes/film lists.
- account.html (71.9): app page, form copy.
- 70-78 REVIEW band (become-like-charbel, bekaa-kafra, 22nd-of-the-month, miracles-canonization, miracles-dafne-gutierrez, miracles-nohad-el-shami, miracles-raymond-nader, mysteries/*, mystery-meditation): all share one profile - BURSTINESS/SPECIFICITY/SLOP/FINGERPRINT at 98-100, VOICE 44-55 (contractions+pronouns per 100 words). That is a register property of liturgical, instructional, and testimony copy, not an AI tell. mysteries/* are scripture+prayer pages, excluded on the prayer-library principle. Prose spot-reads confirmed quality (e.g. bekaa-kafra "the slope does the navigating for you").

## Rejected auto-suggestions (judgment, site-wide)
- "journey -> process" (11 pages): literal pilgrimage travel or Vatican term "apostolic journey" - the human word, kept.
- novena "beacon": inside a traditional prayer text (translation) - untouchable.
- relics "foster": "Foster's Daily Democrat", a newspaper name.
- padre-pio "foster": "foster father of Jesus", St Joseph's title.
- augustine "pivotal": "Pivotal Players", Bishop Barron's series title.
- maroun "realm": inside a quoted Vatican biography passage.
- trail "landscape": literal Mount Lebanon landscape.
- shop triads (tax/shipping/order, weight/dimensions/stock): e-commerce metadata lists.
- Descriptor triads kept where informative (archbishop/preacher/pioneer; monk/scholar/spiritual father; poverty/chastity/obedience is the vow formula).
- Excluded pages: terms-of-service + privacy-policy (legal text, rewording changes legal meaning - needs Joey's call if ever wanted), google*.html (Search Console verification files, byte-exact), rosary-source-text.html (sacred source text).

## Corpus conclusion
All 98 hand-authored English pages have now been through the sweep (pilot + batch 1 + batch 2). Total edits: 13 lines across 5 pages (index 8, story 1, history 2, miracles-index 1, gallery 1). Every detector signal except VOICE sits at 98-100 site-wide; residual REVIEW verdicts are register properties. The copy is human by every measure that matters.

## Verification
- detect after: gallery 63.0 (up from 61.2).
- Baseline re-registered; i18n policy green.
- Full QA chunked ALL GREEN (chunk1 build-home-css/i18n/seo/feeds/testimony; chunk2 testimony-security/site-smoke; chunk3 six rosary sub-suites).
- Pixel review: gallery hero crop verified (new lede set cleanly, no layout shift).
