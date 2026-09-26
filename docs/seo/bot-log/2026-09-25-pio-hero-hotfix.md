# Bot log - 2026-09-25 - HOTFIX: st-padre-pio hero layout

## Bug (user-reported via Joey, screenshot)
The hero-figure sat INSIDE the hero cta-row div, so the flex row stretched the four
cta buttons into full-height empty gray strips beside the giant portrait. Root cause:
figure misplaced by one line when the page was authored; merged in #197 without a
rendered check catching it on the integrator side.

## Fix
Moved the hero-figure above the cta-row (sibling, matching the visit-annaya /
pilgrimage pattern). One-line structural move, no wording change, no CSS change.

## Verification (full top-to-bottom UI pass, not a spot check)
Desktop 1280px: 12 viewport segments; mobile 390px: 16 segments; every section
inspected (hero, life, stigmata, investigated, confessional, hospital, prayer,
his way, watch embeds, pilgrimage, FAQ, sources). All render correctly, zero
console errors. Contact-sheet screenshots attached to the report.

## Same defect in pending saints PR 1
The st-john-paul-ii and st-teresa-of-calcutta pages in the pending PR 1 bundle
(seo/saints-pr1) carry the identical misplaced figure. PR 1 v2 bundle with the
same one-line fix on both pages accompanies this report.
