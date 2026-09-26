# 2026-09-26 - Self-hosted Noto Arabic webfonts for ar pages

## Task
Parent 10:23 AM (queued behind George merge + pilot decision, both now cleared): self-host Noto Naskh / Noto Sans Arabic woff2 for ar pages. The cloud verification browser has no Arabic fonts and a broken shaper, so Arabic rendering was unverifiable; self-hosting gives a deterministic target everywhere. #260 had dropped a system-font Noto stack that broke letter joining - this restores the design intent with the fonts actually shipped.

## Changes
- media/fonts/noto-naskh-arabic-arabic-v1.woff2 (92K, variable 400-700, arabic subset) + noto-sans-arabic-arabic-v1.woff2 (164K, variable 100-900, arabic subset), from the Google Fonts CSS API (notonaskharabic v44, notosansarabic v33), both valid wOF2.
- OFL license files for both families (github.com/google/fonts ofl tree); media/fonts/README.md provenance table extended.
- styles.css: two @font-face blocks (Arabic unicode-range, font-display swap) + html[lang="ar"] rules - body Noto Sans Arabic (line-height 1.8), headings Noto Naskh Arabic (line-height 1.35), matching the #260 design intent.
- home.css regenerated (npm run build:home-css).
- No per-page preload changes (mirrors are generated; fonts load on demand with swap). Baseline untouched (styles.css is not in the snapshot's scope).

## Verification
- Font URLs serve 200; woff2 magic bytes verified.
- Full QA chunked ALL GREEN (build-home-css/i18n/seo/feeds/testimony; testimony-security/site-smoke; six rosary sub-suites).
- Pixel: ar/qadisha-valley rendered in the fontless verification browser - H1, nav, body, and buttons all show properly JOINED Arabic letterforms with correct RTL layout; headings in Naskh serif, body in Sans. ar/prayers hero verified likewise. This is the deterministic target the task was for.

## Notes
- Arabic string content is unchanged; this is presentation only. No mirror regeneration needed (CSS covers all ar pages site-wide).
- Future optimization if wanted: preload the two woff2 on ar pages via the mirror templates + i18n:build.
