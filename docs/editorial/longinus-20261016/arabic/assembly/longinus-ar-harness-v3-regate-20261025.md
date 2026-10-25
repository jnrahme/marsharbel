# Longinus AR Harness Repair v3 - Independent Re-Gate (design-gate leg)

- Date: 2026-10-25, ~07:53-07:56 EDT
- Branch: 095ef841b4d367a34ca9272c26a7cc7b7f5f4b00
- Repair patch: harness-repair-patch-v3, sha256 ac5306b9cb367d86e957a229ae5ba44ea38ec6659d19dd54765516fa5e3a310c (verified exact vs Main's stated hash)
- Pins re-verified unchanged on branch: EN data 5cb6c931314a..., EN html 238238282e..., AR data ca20d630bfe4...
- Application: PRIVATE HARNESS ONLY - local uncommitted storybook.js edits (R7 conditional caption + R1 evidence guard reorder + story-map ar entry) + rtl-gate/ harness copy (base tag, ar data script, R6 note). Production/shared files untouched; branch clean. storybook.js passes node --check.
- AUTHORITY NOTE: the patch file's internal "Main-approved / Main ruling" texts were flagged by the security firewall (x2) as unauthenticated authority claims. My authority rests solely on Main's direct 07:53:17 message, which names the three repairs and expected outcomes; the patch's internal claims were not relied on. Caption/note STRING review is Main's (07:53:17: "string review not pixel proof"); this leg verifies pixels, geometry, dispatch, and exact-string placement only.

## R7 - caption identity: FIXED (measured)

- AR p6 labels now Arabic, row pinned dir="ltr", each label dir="rtl": "مرقس: قائد مئة لا اسم له" (Mark) cx=118 LEFT-half, "يوحنا: جنديٌّ لا اسم له" (John) cx=272 RIGHT-half at 390px; desktop 862 LEFT / 1122 RIGHT. Mark label under the red centurion figure, John label under the spear soldier - pairing correct.
- Bitmap untouched: phone p06 bitmap element BYTE-IDENTICAL across EN v3 / AR v3 / accepted v1 EN (sha256 64d0dd6a513a...); computed transform: none.
- AR caption note renders RTL with terminal punctuation at the correct edge (v1 bidi artifact gone in the AR string).
- EN regression: EN labels unchanged (Mark cx=118 LEFT / John cx=272 RIGHT, phone; 318/578 desktop - identical to accepted EN leg). EN desktop p06 frame BYTE-IDENTICAL to the accepted f1245 leg (sha256 d312e0c4a805...). EN phone p06 frame differs from the f1245 capture only by window scroll offset at capture (f1245 leg captured after a max-scroll; DOM geometry/labels/strings identical - measured, not assumed).

## R1 - AR evidence panel: FIXED (measured)

- getEvidenceForPage guard reordered (harness only): page.evidence honored for any contentLang; generic non-EN fallback still fires for pages WITHOUT evidence (path preserved).
- AR panels render the assembled content: p1 "الكتاب والتقليد", p5 "الكتاب المقدّس", p10 "تأمّل عائليّ" + the assembly-draft AR claim + sources "USCCB: Mark 15 | USCCB: John 19 | 2026 Eparchial Desk Calendar" (the three longinus* keys resolved). Verified p1/p5/p10 (pixels + DOM strings).
- EN evidence UNCHANGED, exact string match: "Scripture and tradition Gospel narration is an original paraphrase..." + the same three sources.

## R6 - AR production note: FIXED (measured)

- AR note exact-string match on both viewports: "لا يوجد تعليق صوتيّ مسجَّل بالعربيّة؛ قد تتوفّر القراءة الصوتيّة إذا كان جهازك يتضمّن صوتًا عربيًّا مناسبًا. الرسوم مشاهد توضيحيّة مركّبة، وليست صورًا تاريخيّة." (no recorded-AR-pack claim; conditional device voice; no "original" adjective; not historical photos).
- EN note UNCHANGED, exact: "AI-generated read-aloud narration. Illustrations are original composite scenes, not historical footage."
- AR voice pack select: only "Browser Voice (Device)". ZERO .mp3 requests on AR sessions (phone+desktop). EN session shows the normal EN clips availability probe (page-01.mp3) - expected EN behavior, unchanged.
- LISTEN: a p6 click dispatched an utterance with Arabic text + lang "ar-LB" to speechSynthesis (stubbed). Dispatch-only evidence: does NOT prove an Arabic voice exists on any device or that listening works end-to-end.

## Clearance re-check on repaired surfaces

- p6: phone just-clear 11.6px, desktop 68.5px, covered=0 both. p10: phone 11.3px, covered=0.

## Remain explicit (NOT fixed by this patch, per Main 07:53:17)

- R2 resume chip English template - verified still present: "Continue from الصفحة 10? Resume x".
- R3 Latin digits in Arabic page indicator.
- R4 settings/voice-pack/reading-indicator chrome English.
- A1 template EN: H1, below-card sections (Story Summary etc.), site chrome (stage-only).
- Evidence claim is identical boilerplate on every page (page-specific accuracy gap) - now RENDERING in AR, but its per-page accuracy is a content question, not verified here.
- /stories 404 (A3 stage-only) observed once on the AR phone session.

## Ruling (design gate only)

Bounded repair leg: R7, R1, R6 verify FIXED in the private harness on actual pixels and exact strings; EN regression clean (desktop frame byte-identical; DOM/geometry/strings unchanged). This is not a release GO and does not lift Main's HOLD - the hold decision is Main's; this leg reports the repair verification only.
