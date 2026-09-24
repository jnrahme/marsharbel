# SEO bot work log - 2026-09-24 - content batch 9 (prayer intentions)

date: 2026-09-24
task_id: content-batch-9-prayer-intentions
change_type: new content pages (3) + healing page enhancement + link bug fix
risk_level: low-medium (prayer content; traditional text quoted from the
Annaya monastery's published novena; original prayers labeled; no outcome
promises; no medical claims)
depends_on: stage tip fe086a6

## Prepared in this batch (PR proposed; merge via integrator lane)

| Page | Target | Notes |
|---|---|---|
| /saint-charbel-prayer-for-a-miracle | prayer for a miracle | traditional Day-1 novena prayer quoted from saintcharbel.com; Nohad + Gutierrez summaries sourced; "when the miracle does not come" section |
| /saint-charbel-prayer-for-pregnancy | prayer for pregnancy/fertility | all-original prayers, labeled; no medical claims; "still waiting" pastoral section |
| /saint-charbel-prayer-for-the-sick | prayer for the sick | loved one / surgery / chronic illness prayers; holy oil + Mass framing |
| /saint-charbel-prayer-for-healing (enhanced) | prayer for healing | +cancer prayer, +When to Pray, +Documented Healings, +FAQ/FAQPage, +Read Aloud |

Also: new shared read-aloud.js (speechSynthesis toggle) on all four pages;
fixed a second stale pr-13 preview URL on saint-charbel-prayers.html
(Prayer Coach link); sitemap +3 (100 indexable pages).

Deviations from spec: schema kept WebPage+breadcrumb+FAQPage (site
convention; spec said Article - flagged for the technical lane to decide);
hreflang kept x-default+en pending international-lane locale builds (new-
language religious content stays behind Joey's gate); no sepia/tomb photos
available in-repo - default og image, flagged for imagery lane.

## Verification (local, 2026-09-24)

check_seo passes (100 pages); i18n policy passes; lastmod in sync; JSON-LD
parses on all edited pages; diff --check clean; render checks (H1s, FAQ
visible, Read Aloud button present, no console errors, no mobile overflow).

## Measurement and next review

- Expected metric: coverage for miracle/pregnancy/sick prayer queries where
  charbel.app currently outranks.
- next_review_date: 2026-10-24
- rollback_reference: revert this batch's commit.
