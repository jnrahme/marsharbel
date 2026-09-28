# 2026-09-28 - AEO tranche 1, page 7: FAQ layer on /history

Branch: feat/aeo-faq-history (off origin/stage c59f30c)

## What
- history.html: added a "Frequently Asked Questions" section (5 Q&A, reveal classes matched to page convention) between "Continue Exploring" and "Sources". Pure additive layer, no rewrites.
- FAQPage JSON-LD filled by apply_seo_tags.py. Page now carries WebPage + FAQPage + existing Person block.
- sitemap lastmod bumped; baseline merge-updated for the history entry only.
- scripts/qa/test_seo.py: narrowed the featured-image negative control for history.html from assertNotIn("mainEntity", whole file) to asserting the WebPage block has no mainEntity. Original intent (history carries no Article schema) preserved exactly; the whole-file substring check broke the moment any FAQPage block existed. Test intent and trail-page positive checks untouched.

## FAQ mapping
1. Who was Saint Charbel - Maronite monk and priest; silence, asceticism, Eucharistic devotion.
2. When/where born - Youssef Antoun Makhlouf, May 8, 1828, Bkaakafra; entered the Order 1851; ordained 1859.
3. Where a hermit - hermitage of Saints Peter and Paul near Annaya, from 1875.
4. When died - December 24, 1898, stroke during the Divine Liturgy.
5. When canonized - October 9, 1977 by Paul VI; beatified December 5, 1965 (Vatican II).
All dates from the page's own Vatican-aligned timeline.

## QA (all green)
- Full chunked QA incl. all 8 rosary/story suites; rendered review desktop (1280) + phone (390).
