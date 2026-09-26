# Bot log - 2026-09-25 - Saints & Blesseds photos

## Scope
GO (parent 9:03 PM): real, rights-clean photos for all /saints hub cards (Charbel, St Maroun, St Nimatullah, St Rafqa, Blessed Fulton Sheen) and their pages. Exact Blessed-vs-Saint title discipline in captions/alt text.

## What shipped
- 4 new images in media/saints/ (WebP): st-maroun.webp (91KB), st-nimatullah.webp (24KB), st-rafqa.webp (19KB), blessed-fulton-sheen.webp (48KB). Saint Charbel card reuses existing media/news/saint-charbel-portrait.webp.
- saints.html: photo added to each of the 5 cards, photo is part of the card, whole card still clickable.
- st-maroun.html, st-nimatullah.html, st-rafqa.html, blessed-fulton-sheen.html: hero-figure with figcaption (credit + honest medium).
- docs/seo/photo-rights-registry.md: per-image provenance, license, verification date (all verified 2026-09-25 on Wikimedia Commons file pages).
- apply_seo_tags.py re-stamped the 5 changed pages (og:image -> new photos, Article schema). Generator-owned structured data; no hand-added JSON-LD.

## Rights summary (all public domain, verified 2026-09-25)
- St Maroun: 19th-c. Russian icon, PD (life+70, PD Mark 1.0). Captioned as icon, not photo.
- St Nimatullah: official portrait, source Holy See (vatican.va 2004 canonization), PD. Captioned as portrait.
- St Rafqa: real photograph, Archives of Saint Joseph's Monastery Jrabta, before 1914, PD. Captioned as photograph.
- Fulton Sheen: photograph, 1956, PD (US, no notice). Captioned as photograph.
- Saint Charbel: existing site portrait (already in use on news card).

## QA
- check_i18n_policy: PASS
- check_seo (132 pages): PASS
- test_seo (generator repeatability): PASS
- sync-navigation --check: 0 out of sync (testimony-review.html excluded by design)
- git diff --check: clean
- Playwright render, desktop all 5 pages + mobile /saints: zero console errors; screenshots pixel-inspected (/tmp/ph-*.png)

## Notes
- Blessed/Saint discipline kept everywhere: Sheen card tag reads "Beatified September 24, 2026"; Blesseds section header explains beatified vs canonized.
- IndexNow after merge: /saints, /st-maroun, /st-nimatullah, /st-rafqa, /blessed-fulton-sheen
