# 2026-09-28 - AEO tranche 1, page 5: FAQ layer on /saint-charbel-quotes

Branch: feat/aeo-faq-quotes (off origin/stage c59f30c - re-verified fresh; note stage advanced past aefe92c with the es monastery mirrors #318 while novena/movie were in flight).

## What
- saint-charbel-quotes.html: added a "Frequently Asked Questions" section (4 Q&A) between "How to Spot a Misattributed Quote" and "Sources", site-standard markup. Pure additive layer, no rewrites.
- FAQPage JSON-LD filled by apply_seo_tags.py. Page now carries WebPage + FAQPage.
- sitemap lastmod bumped; baseline merge-updated for the quotes entry only.

## FAQ mapping
1. Most famous quotes - sourced selection (prayer, sanctity-is-a-choice, holy family, the Cross).
2. Did he write books - No; two collections carry the record (Words booklet; Skandar/Angelico Press).
3. "I have come to operate on you" - Nohad El Shami testimony, Jan 1993, not his writing.
4. How to verify a quote - traceable-collection + testimony-labeled tests; unsourced lists treated as unverified.
ACCURACY: every quotation in the FAQ restates only what the page already presents, with the page's own testimony-vs-writing distinction preserved verbatim in spirit.

## QA (all green)
- Full chunked QA incl. all 8 rosary/story suites; rendered review desktop (1280) + phone (390).
