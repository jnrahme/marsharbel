# Rosary bead teaching specimen

## Scope and visitor job
A first-time visitor can recognize the next bead, practice one decade and choose a short session on the existing Rosary Prayer Coach. The existing header, hero, Teaching Mode, prayer wording and plan builder remain intact. This is one page, not a redesign.

## Chosen implementation
An original SVG illustration uses shaded cream spheres, one larger bronze sphere and a straight connecting cord. It evokes depth but is **not a 3D mesh or a draggable 3D viewer**. A linear decade is explicitly labeled as a teaching diagram, not a complete Rosary or a relic. All geometry and shading are original code in the page source; no stock image, generated image, external license, paid provider or likeness is used.

The static render route is deliberate. The incumbent has a classic-script/static-page stack and a report-only script policy with specific hashes. A model-viewer/WebGL dependency would add requests, startup work and policy integration for no prayer-order benefit. No viewer, remote model, autoplay or render loop is loaded. A real 3D mesh remains a separate, unimplemented option and must not be claimed as shipped.

## Interaction specification
- Poster visible before activation, with reserved SVG aspect ratio.
- Native disclosure: "Practice bead by bead". It works without JavaScript.
- Keyboard Enter/Space toggles the disclosure. Native buttons provide previous, next and reset.
- State 0: Our Father. States 1-10: ten Hail Marys. State 11: Glory Be and optional Fatima prayer. The mystery is announced before the decade. A single decade is not described as the full Rosary.
- Live status identifies prayer and number; the ring is supplementary. Boundaries disable previous/next. Reset preserves control focus.
- No persistence, countdown, prayer-completion metric, inferred devotion or telemetry.
- "Choose a short session" moves to the existing time field; the existing plan remains authoritative.

## Accessibility and fallback
Static image title/description plus the complete visible sequence in the always-visible introduction. No-JS retains illustration/disclosure/text. No-WebGL is identical to normal operation. Reduced motion has no moving interaction; controls remain usable. Buttons are at least 44px high; new controls do not disable zoom or rely on hover. No network is required after the incumbent page loads. Phone emulation is verified; physical iOS/Android hardware is not available here and remains an explicit release-review caveat.

The sequence follows the incumbent Teaching Mode/FAQ. No new theological promise or pastoral claim is added. Independent faith and design review are required before merge, particularly the linear-decade explanation and small-phone SVG labels.

## Code structure
Edit src/pages/rosary-prayer-coach.html and regenerate with scripts/build-pages.mjs. New visible prose and interactive status templates use stable keys in locales/en/rosary-bead-copy.json. The builder expands and HTML-escapes catalog keys, failing on a missing key. The existing frozen legacy baseline is not widened. Policy counts allow only the cataloged additions. No translations are claimed or generated.

## Performance method and release gate
Compare incumbent and final under the same compressed local dev server, cold browser context and viewport. Record request count, transfer bytes, LCP and CLS. Local numbers are not real-user Core Web Vitals or proof of a production improvement. No extra request, model or renderer is allowed. Proposed specimen guardrails are added compressed markup under 4KB, LCP under 2.5 seconds and CLS under 0.1. These are proposed, not verified incumbent budget definitions. The sample shows a small LCP increase, so zero-regression is not established. A production check remains required after deployment.

## Verification
Behavior specs cover keyboard activation, each bead through completion, previous/reset, unchanged 5-minute session generation, narrow viewport overflow, scoped axe, reduced motion, no-WebGL and no-JS. Existing full QA and independent rendered desktop/phone review are separate gates, not substituted by these specs.


## Initial local performance observations
Three cold contexts per viewport, compressed dev server: 15 requests before and after, transfer 141,465 to 144,013 bytes (+2,548). Median LCP desktop 176 to 228ms; phone 140 to 184ms. Maximum CLS unchanged (desktop .01759, phone .06881). There is a measured small LCP increase, not a no-regression proof. The sample is unthrottled and may vary; production CWV is not established. Do not merge on a claim that the brief's performance requirement is proven until independent review resolves this caveat.
