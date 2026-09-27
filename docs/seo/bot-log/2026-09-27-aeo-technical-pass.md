# 2026-09-27 AEO technical pass

## What changed
- Added /llms.txt (v2: H1, summary, H2 sections for History, Miracles,
  Prayers, Novena, Feast Day, Annaya, Saints, Places, Letters, News).
- robots.txt: documented AI-crawler section explicitly Allowing GPTBot,
  OAI-SearchBot, PerplexityBot, Perplexity-User, ClaudeBot, Googlebot.
- FAQPage schema on /miracles (generator now recognizes "Common Questions"
  sections; the four on-page Q&As are the schema text). /22nd-of-the-month
  already carried FAQPage. /saint-charbel-feast-day and /visit-annaya have no
  visible FAQ section, so no schema was added there (would not match visible
  text).
- Entity graph: WebSite alternateName ["Mar Charbel", "Saint Charbel
  Makhlouf"] on all 87 generator-managed pages; Person schema (name from the
  visible H1) on the ten st-* saint profiles + /history.
- /miracles redirect-stub check: canonical https://marsharbel.com/miracles/
  resolves 200, /miracles.html 301s to it, sitemap lists the trailing-slash
  URL, no internal links target the .html form. No fix needed.
- ARIA audit (rosary coach, nav dropdowns, forms): no failures. Nav dropdown
  parents carry aria-haspopup + aria-expanded with JS state toggling; coach
  controls are label-wrapped; testimony/account forms are labeled.

## Pending decision
- AI referral tracking: the site has no analytics property (no GA/gtag), so
  the monthly AEO referrer metric is defined in the operating plan but cannot
  be measured until Joey decides whether to add analytics.
