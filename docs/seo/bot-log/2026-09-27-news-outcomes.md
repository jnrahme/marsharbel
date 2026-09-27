# 2026-09-27 - News outcomes: Monte Sole beatification + Byblos-Annaya walk

Branch: feat/news-2026-09-27-outcomes (off origin/stage 95f6e27)

## What
- news.html Monte Sole card (World section): flipped to past tense after the beatification took place September 27 in San Petronio, Bologna - headline now "Three Priests Martyred at Monte Sole Beatified in Bologna"; "will beatify" -> "beatified"; "from Sunday they will be called Blessed" -> "from Sunday they are called Blessed"; "Bologna Today reports" -> "reported". Names verified: Don Ubaldo Marchioni (diocesan), Don Elia Comini (Salesian), Father Martino Capelli (Dehonian). Added outcome source: Vatican News Italian, Sept 27 (vaticannews.va/it/vaticano/news/2026-09/beatificazione-cardinale-semeraro-martiri-monte-sole.html). Title discipline: they are Blessed only from the completed rite - outcome confirmed via Vatican News + la Repubblica Bologna + ANSA before flipping.
- news.html Byblos-Annaya card (Lebanon section): flipped to past tense with outcome detail from ACI MENA Arabic (Sept 27): believers from across Lebanon gathered in Byblos, walked ~16 km (some 10 miles) from Mar Girgis church to the Monastery of Saint Maron in Annaya, concluded with Mass at the Church of Saint Charbel; Anthony Jarjour of Rmeich reached the shrine after five days on foot from Tyre (~150 km, matching the announced ~93 miles rerouted for closures). Tag date moved from announcement date (Sept 20) to event date (Sept 26). Added outcome source link (acimena.com/news/9473).
- feed.xml regenerated (build_feeds.py), sitemap lastmod updated, locales/legacy-text-baseline.json news.html entry merge-updated via the checker's snapshot extractor (format preserved: insertion order, indent=2, no trailing newline).

## Quiet morning scan (1:47 AM wake, logged here per charter)
Saint watch: Vatican News + Agenzia Fides checked; no new canonizations/beatifications/decrees beyond the already-carded Sheen beatification (Sept 24, card live) and today's Monte Sole rite. Byblos walk outcome coverage had not yet published at 1:47 AM; held for this evening pass.

## QA (all green)
- check_seo.py, test_seo.py, test_feeds.py (feed regenerated), i18n:check, check_i18n_policy (baseline merge-updated), sync-navigation --check, git diff --check
- test:testimony-security, test:site-smoke
- rosary/story suites: smoke (one flaky first run, clean pass on re-run), menu, end-rules, prayer-behavior, intro-cta, ui-regression, story-floating-player, checklist
- Rendered review (standing gate): both edited cards screenshotted and pixel-inspected on desktop (1280) and phone (390) - past-tense copy, outcome source lines, images and license captions all render correctly.
