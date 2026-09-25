# 2026-09-25 - Retrofit R2: miracle hub pages (editorial-quality audit + upgrade)

Second retrofit batch under Joey's 4:31 PM program.

## Outcome
- miracles/index.html: AUDIT PASS, no churn. Already at standard - status
  tags (formally recognized vs recorded vs under study), metric grids,
  varied modules, whole-card destinations to the child pages, woven prose
  links, 7-entry Sources. Distinctions are the page's organizing principle.
- pope-leo-xiv-annaya-visit.html: AUDIT PASS, no churn. Rights-credited
  hero (Vatican Media / Vatican News with date), all quotations traced to
  the official Vatican text in Sources (dated), quote-card grid, woven
  links to trail/visit-annaya/novena/become-like-charbel.
- saint-charbel-miracles-2026.html: UPGRADED. Added "At a Glance" fact box
  (latest registrations, 2025 context, what "registered" means) for
  news-roundup orientation; sources already publisher/title/date/supports.
  No embed added - the Tablet coverage lives on latest-register-entries;
  duplicating it adds nothing (skill: embed only what text cannot give).

## QA
check_seo green (130), test_seo 15/15, i18n policy (baseline refreshed for
the changed page), diff --check clean. Playwright: fact box renders desktop,
zero console errors across all 3 pages.
