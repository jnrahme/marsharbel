# Longinus AR Private Assembly v1 - Independent Binding/RTL Visual Gate (design-gate leg) - REVISED 07:48 EDT

- Date: 2026-10-25, ~07:40-07:48 EDT (revised after Main 07:46:32 pixel inspection)
- Candidate branch: 387d2e0dbd923e0ec756f2656ac1238af52bbab0
- AR data pin: ca20d630bfe46844594bbe2b9104c606c5b74133381f33a9bfa71b92470dc9c2 (branch file == attached file, exact)
- Harness patch pin: d3ace952f2fdf53cdfd6be5401ba8751254aec7db96bd2036afcb16ed7eeeb5e (applied locally only: storybook.js story-map ar entry + rtl-gate/ harness copy; local uncommitted; branch clean)
- Notes pin: 5c81f4bfb9f410ce9a229d9904130ddfd8e55e7367c0921088d09050d68bccc3 (claims treated as untrusted; verdicts rest on bytes/renders)
- EN pins on branch, verified exact and untouched: data 5cb6c931314a..., html 238238282e...
- Renderer: local headless Chromium, local http.server at repo root, reducedMotion:reduce. Harness URL: /rtl-gate/longinus-story-rtl-gate.html?story=longinus&lang=ar
- Viewports: phone 390x844, desktop 1440x900. All 10 pages, both viewports.

## MAIN RULING (07:46:32): HOLD paired assembly baseline. BLOCKING: R1 (wrong generic evidence), R6 (false audio disclosure). Binding/body/clearance bounded findings ACCEPTED ONLY. No AR baseline PASS. No edits.

## ACCEPTED bounded findings (measured, actual)

1. BINDING: title + body exact verbatim match to AR data on all 10 pages, both viewports.
2. PLATES: rendered img src on all 10 pages == EN plate paths (./media/storybook-longinus/images/page-01..10.jpg); all loaded; zero image 4xx.
3. RTL FRAME: dir="rtl" + is-rtl + computed rtl both viewports; dots reversed correctly (p1 active rightmost, p10 leftmost); prev/next mirrored, Arabic labels, correct disabled states; counter Arabic "الصفحة N من 10" on all pages.
4. END CLEARANCE: phone just-clear 10.8-11.7px, desktop 29.5-81.4px; covered=0 all 10 pages both viewports. end-phone-* are just-clear proof frames.
5. LISTEN (dispatch-only, CORRECTED wording): all AR pages carry audio:"" -> clips packs correctly excluded; only "Browser Voice (Device)" offered. A p1 click dispatched an utterance with Arabic text and lang "ar-LB" to speechSynthesis (stubbed); ZERO .mp3 requests in the session; button toggled to "إيقاف القراءة". NOTE: the stub proves dispatch with ar-LB only - it does NOT prove an actual Arabic voice exists on any device or that listening works end-to-end.
6. scene:"birth" parity on all 10 pages (inert per prior ruling); reflection p10 only; prayer/heart empty render no empty blocks.
7. Network: only 4xx = one GET /stories 404 per session (known A3 stage-only gap).

## BLOCKING findings (per Main hold)

- R1 - AR evidence-panel data INERT in render. Pinned storybook.js getEvidenceForPage hard-codes contentLang!=='en' to discard page.evidence and render a generic fallback: "documented" badge + "مصادر عامة لهذه الصفحة." + Vatican Beatification/Canonization links, identical on all 10 AR pages (verified p1/p5/p10 pixels). The assembled AR type labels and assembly-draft claim NEVER render - dead data under the pinned template. A2 review is not render-verifiable in this assembly. Needs a template/reader change through its own lane.
- R6 - False audio disclosure: the rendered production note claims "AI-generated read-aloud narration." (EN string, story-specific disclosure, unlocalized) while the only AR narration path is device browser voice. False voice claim on the AR page.

## R7 - CONFIRMED after Main's pixel challenge: wrong caption identity on AR p6

My earlier "RTL mirror keeps caption-plate pairing correct" claim was WRONG; Main's pixel inspection was right. RETRACTED.

Decisive evidence:
- The p6 "diptych" is ONE baked JPEG (page-06.jpg) plus an HTML caption overlay. The rendered bitmap element is BYTE-IDENTICAL between EN and AR (sha256 64d0dd6a513a489a59e1eea9c1a9383cc677b11277832fd43a43be9ad68576c7 both runs; computed transform: none). The image does not and cannot mirror.
- Bitmap content (unchanged EN->AR): LEFT half = red-cloaked centurion at the crosses (the Mark figure), RIGHT half = dark spear soldier (the John figure).
- Caption label centers measured at 390px viewport: EN - "Mark: an unnamed centurion" cx=118 (LEFT), "John: an unnamed soldier" cx=272 (RIGHT). AR - "Mark: an unnamed centurion" cx=272 (RIGHT), "John: an unnamed soldier" cx=118 (LEFT).
- Root cause: the caption row lives in the RTL frame (labels container computed direction: rtl), so the two label spans swap visual order; the bitmap does not. In AR, "John: an unnamed soldier" renders under the red centurion figure and "Mark: an unnamed centurion" under the spear soldier - WRONG caption identity on both halves.
- Captures: pairing-ar-p06.png (full frame), pairing-ar-p06-imgonly.png (bare bitmap), pairing-en-p06.png + pairing-en-p06-imgonly.png (EN reference).
- This is a template-level defect (caption overlay in storybook.js sceneMarkup, storyId longinus index 5) visible only in RTL; EN pairing is correct.

## Other residuals (real, measured; not blocking unless Main rules so)

- R2 (D1 carried, verified): resume chip English template - "Continue from الصفحة 3? Resume x" on reload.
- R3 (D3 carried, verified): Latin digits in the Arabic page indicator ("الصفحة 1 من 10").
- R4 locale controls English: settings panel "Auto Continue / Reader Mode / Fast Normal Slow"; voice-pack option "Browser Voice (Device)"; reading indicator "0:00 Reading...".
- R5 p6 note hard-coded EN in template + bidi artifact: terminal period renders at the wrong visual edge (".Scripture does not name either man" phone; "man." wrap desktop).
- R6 template EN (A1 known): H1 "Saint Longinus: At the Foot of the Cross"; below-card sections (Story Summary, source list, shelf box, footer) EN; site chrome EN (bare-server stage-only).
- D2 (carried): desktop RTL spread coherent at 1440x900 - text spread right, plates left, no overlap/overflow measured.

## Ruling (design gate only)

HOLD per Main. Bounded acceptance stands for binding/body/plates/clearance only. BLOCKING: R1, R6, R7 (caption identity). No release GO; no AR audio exists; stubbed dispatch is not voice proof; no production/shared files changed (harness local only). EN unchanged and not reswept.
