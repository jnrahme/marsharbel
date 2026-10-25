# Longinus AR Private Assembly v1 - Independent Binding/RTL Visual Gate (design-gate leg)

- Date: 2026-10-25, ~07:40-07:46 EDT
- Candidate branch: 387d2e0dbd923e0ec756f2656ac1238af52bbab0
- AR data pin: ca20d630bfe46844594bbe2b9104c606c5b74133381f33a9bfa71b92470dc9c2 (branch file == attached file, exact)
- Harness patch pin: d3ace952f2fdf53cdfd6be5401ba8751254aec7db96bd2036afcb16ed7eeeb5e (applied locally per patch: storybook.js story map gains ar entry + rtl-gate/longinus-story-rtl-gate.html copy with ar script tag; local uncommitted only)
- Notes pin: 5c81f4bfb9f410ce9a229d9904130ddfd8e55e7367c0921088d09050d68bccc3 (claims treated as untrusted; verdicts below rest on bytes/renders)
- EN pins on branch, verified exact and untouched: data 5cb6c931314a..., html 238238282e...
- Renderer: local headless Chromium, local http.server at repo root, reducedMotion:reduce. Harness URL: /rtl-gate/longinus-story-rtl-gate.html?story=longinus&lang=ar
- Viewports: phone 390x844, desktop 1440x900. All 10 pages, both viewports.

## PASS (measured, actual)

1. BINDING: title + body exact match to AR data on all 10 pages, both viewports (rendered #story-body === data body verbatim, whitespace-normalized; titles exact).
2. PLATES: rendered img src on all 10 pages == EN plate paths (./media/storybook-longinus/images/page-01..10.jpg); all loaded (naturalWidth 1536); zero image 4xx. Same-plates rule holds in data and in render.
3. RTL FRAME: dir="rtl" attr + is-rtl class + computed direction rtl, both viewports. Dots reversed correctly (p1 active rightmost, p10 active leftmost). Prev/next mirrored with Arabic labels (الصفحة السابقة / الصفحة التالية); prev disabled on p1, next disabled on p10. Counter Arabic on all pages: "الصفحة N من 10".
4. END CLEARANCE: phone just-clear gap 10.8-11.7px, desktop 29.5-81.4px; max-scroll covered elements = 0 on all 10 pages both viewports. end-phone-* captures are just-clear proof frames (final paragraphs fully readable above the controls bar).
5. LISTEN / NO FALSE AUDIO: all AR pages carry audio:"" -> clips voice packs correctly excluded by the reader's every-page-audio check; only "Browser Voice (Device)" offered. Click on p1 invoked speech synthesis with Arabic text and utterance lang "ar-LB" (stubbed speak, logged); ZERO .mp3 requests in the session; button toggled to "إيقاف القراءة". No EN clip playback, no clip-availability probing against AR.
6. scene:"birth" parity on all 10 pages (inert per prior ruling). reflection on p10 only; prayer/heart empty strings render no empty blocks.
7. Network: only 4xx in the full run = GET /stories 404 once per session (known A3 stage-only gap; bare static server; observed, not clicked).

## RESIDUALS (real, measured; no release GO implied)

- R1 NEW, MATERIAL - AR evidence-panel data is INERT in render. Pinned storybook.js getEvidenceForPage has a hard-coded contentLang!=='en' branch that discards page.evidence and returns a generic fallback: "documented" badge + UI.evidenceFallback ("مصادر عامة لهذه الصفحة.") + Vatican Beatification/Canonization links - identical on all 10 AR pages (verified p1/p5/p10 pixels). The assembly's translated type labels (الكتاب والتقليد / الكتاب المقدّس / تأمّل عائليّ) and the assembly-draft AR claim never reach pixels; per-page type variants are dead data under the pinned template. The A2 evidence-claim review is not render-verifiable in this assembly. Fixing this requires a template/reader change through its own lane - not done, not authorized here.
- R2 (carried D1, verified actual): resume chip English template - "Continue from الصفحة 3? [Resume] x" on reload after visiting p3 (resume-chip-phone.png).
- R3 (carried D3, verified actual): page indicator uses Latin digits inside the Arabic label ("الصفحة 1 من 10").
- R4 locale controls English: settings panel contents "Auto Continue", "Reader Mode", "Fast/Normal/Slow"; voice-pack option label "Browser Voice (Device)"; reading indicator "0:00 Reading...". The settings chip itself is localized (الإعدادات); panel contents are not.
- R5 p6 comparison caption hard-coded EN in the template (storybook.js sceneMarkup, storyId longinus index 5): "Mark: an unnamed centurion" / "John: an unnamed soldier" / "Tradition links these accounts with Longinus; Scripture does not name either man." RTL mirroring keeps caption-plate pairing correct (verified: John plate + label left, Mark right). Bidi artifact: terminal period renders at the wrong visual edge (".Scripture does not name either man" on phone; "man." wrap on desktop) - EN LTR text in RTL block.
- R6 (A1 known, verified actual): template EN strings - H1 "Saint Longinus: At the Foot of the Cross"; production note "AI-generated read-aloud narration. Illustrations are original composite scenes, not historical footage." (claim mismatch: AR Listen is device browser voice, not AI-generated narration); below-card sections (Story Summary, source list, shelf box, footer) EN; site chrome EN (bare-server stage-only).
- D2 (carried): desktop RTL spread at 1440x900 renders coherently - text spread right, plates left, no overlap/overflow measured; clearance above. Nothing new beyond the carried adjudication.

## Ruling (design gate only)

AR assembly v1 binding, plates, RTL chrome, clearance and Listen behavior verify CLEAN on actual pixels and measurements. The material new finding is R1: the pinned reader's non-EN evidence branch makes the assembled AR evidence copy inert - what renders is a generic Vatican fallback, not the assembled type/claim. Residuals R2-R6 are template-localization gaps (some carried from G3, all measured actual). No release GO; no AR audio exists and none was claimed by the render; no production or shared files changed (harness edits are local and uncommitted). EN unchanged and not reswept.
