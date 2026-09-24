# SEO bot work log - 2026-09-24 - content batch 7 (October 22nd refresh)

date: 2026-09-24
task_id: content-batch-7-october-22-refresh
change_type: seasonal refresh (22nd-of-the-month, novena) + keyword map notes
risk_level: low (devotional custom clearly labeled; no outcome promises)
depends_on: content-batches 1-6 (stacked)

## Changes

Ahead of the October 22, 2026 monthly pilgrimage spike:
- /22nd-of-the-month: new "Common Questions About the 22nd" section (4 Q&As:
  official feast? - no, devotional custom; keep it away from Annaya? - yes;
  what happens there; asking for healing with the no-guaranteed-outcome note)
  with FAQPage JSON-LD. Added links to feast-day, around-the-world,
  prayer-for-healing. Also fixed a duplicate </main> closing tag (latent
  HTML bug).
- /saint-charbel-novena: "When to Pray It" now suggests timing a novena to
  end on the 22nd and links the 22nd page.
- keyword map: seasonal section added (monthly 22nd spike; July feast novena
  window with a June refresh reminder).

## Verification (local, 2026-09-24)

Same method as batches 1-6: check_seo.py zero new errors vs stage baseline;
i18n policy only the two pre-existing stage failures; baseline refreshed;
JSON-LD blocks parse; git diff --check clean; render check on both edited
pages (no console errors, FAQ renders).

## Measurement and next review

- Expected metric: impressions/CTR for "22nd of the month saint charbel"
  query class around October 22; FAQ rich-result eligibility.
- next_review_date: 2026-10-23 (post-spike review)
- rollback_reference: revert this batch's commit.
