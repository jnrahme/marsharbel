# 2026-09-24 - Guard against redirecting internal links (technical SEO lane)

Live crawl after SEO batch 8 (#103): visit-annaya linked to st-nimatullah.html,
st-rafqa.html and maronite-history.html, and the three new pages' brand
link pointed at `index`. All four are 301s, and they came back four hours
after #93 cleaned the site.

Fix: cleaned the links, and check_seo.py now fails on any internal <a> to
`*.html` or `index` (with a unit test). The convention note says so too.
Everything else on the live crawl was clean: 102/102 sitemap URLs return 200,
no other redirecting internal links, and hreflang/canonical checks passed.
