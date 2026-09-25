# 2026-09-24 - Core Web Vitals: deferred scripts, storybook images (technical SEO lane)

Measured with Lighthouse 12 (mobile) against a local server on stage 929d95a,
because the live site returns 403 to headless Lighthouse and the PageSpeed
API quota was exhausted. Before: home 97, joyful-1 95, news 96 (FCP 2.0s,
~1.1s render-blocking scripts), story 93 (LCP 3.0s).

Changes:
- Local scripts on 51 pages now load with `defer`. They were already at the
  end of <body>, so execution order is unchanged (deferred scripts keep
  document order and run before DOMContentLoaded; translate.js already
  handles readyState). check_seo.py now fails on a new blocking local script.
  Exempt: 22nd-of-the-month and rosary-minibook (inline scripts depend on
  order), testimonies.html and the noindex auth pages (Supabase client,
  testimony lane).
- /story: the scene image is the LCP element but was `loading="lazy"` and
  only existed after storybook.js ran. The first scene is now in the HTML
  (eager, `fetchpriority="high"`), and render() keeps it when the page to show
  already has that art, so the LCP image is not repainted. Readers resuming
  on a later page still get their page from JS.
- /story: the 24 storybook illustrations were 3 MB PNG/JPG files (22.3 MB
  total). Added 1280px WebP copies (4.1 MB total) and pointed storybook.js at
  them. Originals kept in the repo.

Decision notes: no CSS inlining or font changes in this pass; styles.css is
the remaining render-blocking resource and a critical-CSS split is a larger
change that would need its own visual QA.

Result (Lighthouse, applied/devtools throttling, same machine, A/B):
/story LCP 5.8s -> 3.8s, score 75 -> 82; joyful-1 unchanged (88, LCP 3.0s).
Observed (unthrottled) /story LCP 250ms -> 160ms; the image now paints in
the first frame. Lantern's simulated estimate for /story moves the other way
(3.0s -> 3.7s) because it models JS-inserted content differently; the applied
and observed runs are the ones that match real users.
