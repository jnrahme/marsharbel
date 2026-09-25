# Arabic miracle hub directory migration, September 25, 2026

Batch-13 English miracle child stories introduced a directory/file collision for the old Arabic `/ar/miracles.html` hub. The English hub was moved to `/miracles/index.html` on stage in #143; this branch is based on that merged fix and applies the same pattern to the Arabic hub.

- The catalog registry now defines the Arabic miracles hub as `/ar/miracles/`. The generator emits `ar/miracles/index.html` and a nested `.htaccess` with `DirectoryIndex index.html`; the old file is removed. The English hub's reciprocal hreflang, Arabic self-canonical, sitemap and locale routes all use the slash URL. The existing `/ar/miracles` request should redirect to `/ar/miracles/` when Apache DirectorySlash handles the real directory. This server redirect must be verified after deployment; localhost only proves that the directory index exists and renders.
- Source-level safe nested slugs allow `/ar/miracles/nohad-el-shami` and `/ar/miracles/dafne-gutierrez`, while tests reject path traversal. The two Arabic accounts distinguish personal testimony and eparchial medical review from the three Church-recognized miracles.
- Sources: https://cnewa.org/magazine/lebanons-beloved-saint/ , https://saintcharbel.com/ , https://www.ncregister.com/news/phoenix-mother-st-charbel-cured-my-blindness .
- Tests before handoff: international generator and policy check, 23 international tests, 51 full Python tests, SEO check for 126 indexable pages. A local HTTP server returned 200 for the Arabic directory index and both child files; inspected a 390px RTL screenshot of the hub with no horizontal overflow. This does not verify Hostinger's redirect behavior.

Next: Raymond Nader, recognized three, and latest register entries in Arabic; then the other six language versions, and the intention-prayer batch 2 now on stage. The Raymond source's movement-recognition year conflicts with the English master and has been flagged to the parent.

## Raymond Nader follow-up
- Added `/ar/miracles/raymond-nader` from the movement's published first-person narrative, with personal experience distinguished from a Church-declared miracle. Source: https://www.familyofsaintsharbel.org/experiences-blog/raymond-naders-experience-with-saint-sharbel . The movement's own account claims founding in 1995 and formal ecclesial recognition in 2010; we have not seen its decree. The English master's loose approval wording was corrected to attribution rather than an implied 1995 recognition. The legal/theological status of that decree is not independently verified.
- Generated related links now put the Arabic miracles hub first on child stories. Validated with a new unit test. The generated Arabic Raymond page returned 200 on a local HTTP server; visually inspected its 390px RTL screenshot, with readable text and no horizontal overflow.
- QA: i18n:check (48 guides), 24 i18n tests, 52 full Python tests, check_seo (127 indexable pages), all passed.
