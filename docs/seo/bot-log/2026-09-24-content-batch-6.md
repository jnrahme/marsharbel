# SEO bot work log - 2026-09-24 - content batch 6 (internal-link graph)

date: 2026-09-24
task_id: content-batch-6-internal-links
change_type: internal-link strengthening (5 files) + one link bug fix
risk_level: minimal
depends_on: content-batches 1-5 (stacked)

## Changes

Goal: every indexable page >=3 relevant inbound content links. Audit found 3
pages below threshold; fixes:
- rosary-visual-guide.html: fixed a stale absolute PR-preview URL
  (pr-13--marsharbel-preview.netlify.app/rosary-prayer-coach) to the relative
  rosary-prayer-coach.html - a real production bug: production pages linked
  out to a preview deploy.
- rosary-intro.html: added Prayer Coach to the cta-row.
- prayer-library.html: added "New to the Rosary?" -> rosary-intro.
- saint-charbel-prayers.html: added rosary-intro pointer at the Rosary
  section.
- saint-charbel-around-the-world.html: added 2026 film mention linking the
  movie page.

Result: all 27 indexable pages now have >=3 inbound content links
(nav/JS-driven links excluded from the count).

## Verification (local, 2026-09-24)

Same method as batches 1-5: check_seo.py zero new errors vs stage baseline;
i18n policy only the two pre-existing stage failures; baseline refreshed;
git diff --check clean; render checks on edited pages (no console errors).

## Measurement and next review

- Expected metric: crawl depth and internal PageRank distribution; watch
  movie/coach/intro page impressions when Search Console lands.
- next_review_date: 2026-10-24
- rollback_reference: revert this batch's commit.
