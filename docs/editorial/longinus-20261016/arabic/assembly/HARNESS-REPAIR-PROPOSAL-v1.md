# Longinus AR harness - scoped PRIVATE repair proposal v1 (2026-10-25 ~07:50 ET)

Scope: repair of gate-confirmed BLOCKING findings R1/R6/R7 for the PRIVATE RTL harness only. No shared reader/production edits authorized; every change below is proposed for the harness patch (binding-rtl-gate.patch successor), applied locally, re-gated by design before any broader question is even raised. New localized strings are candidates requiring independent fidelity review. No image flip (bitmap identity is physical and correct). No new audio, no rewrites, no merges.

## R7 (BLOCKING) - caption identity on AR p6
Root cause (measured): .longinus-account-labels row inherits RTL direction and mirrors; the baked JPEG (left=Mark centurion, right=John spear soldier, byte-identical EN/AR) cannot.
Repair (harness storybook.js, sceneMarkup longinus index 5):
1. Pin physical order: add dir="ltr" to the labels container so Mark stays LEFT and John stays RIGHT in every UI direction, matching the bitmap. Physical caption identity preserved by construction; no transform on the image.
2. Localize caption strings (CANDIDATE, needs fidelity review): "مرقس: قائد مئة لا اسم له" / "يوحنا: جنديٌّ لا اسم له"; note line: "يربط التقليد هذين الخبرين بلونجينوس؛ أمّا الكتاب المقدّس فلا يذكر اسمَ أيٍّ منهما." (preserves the Scripture/tradition boundary exactly: linking attributed to tradition, both unnamed in Scripture.) AR text in an RTL block also resolves the R5 bidi artifact (terminal period at the wrong edge).
Verification: re-render AR p6 at 390/1440; measure label centers (Mark cx left, John cx right) against bitmap halves; EN p6 regression frame byte-compared to the accepted EN leg.

## R1 (BLOCKING) - AR evidence panel inert, generic Vatican fallback
Root cause (storybook.js getEvidenceForPage ~1048): contentLang!=='en' discards page.evidence and returns a generic fallback whose sources (vaticanBeatification1965/vaticanCanonization1977) are wrong for this book.
Repair (harness storybook.js): reorder the guard - use page.evidence whenever present, for ANY contentLang; keep the generic fallback only when a non-EN page carries no evidence. The assembled AR type/claim (assembly-draft, fidelity-review pending per A2) then actually renders; its longinus* source keys resolve through the existing SOURCES registry (Mark 15 / John 19 / Eparchial Desk Calendar).
Out of scope but flagged: the generic non-EN fallback's Vatican links are a PRE-EXISTING reader defect affecting every non-EN story, not Longinus-specific - separate lane decision.
Verification: AR p1/p5/p10 evidence panels show the assembled type labels + claim + correct three sources; EN evidence rendering unchanged (byte-compare EN frames).

## R6 (BLOCKING) - false audio disclosure
Root cause: static note in the book page template ("AI-generated read-aloud narration...") is EN and inaccurate for AR, where Listen is device browser voice only (no recorded pack exists).
Repair (harness html copy): localized honest note (CANDIDATE, needs fidelity review): "لا يوجد تعليق صوتيّ مسجَّل بعد؛ القراءة الصوتية تعتمد صوت الجهاز. الرسوم مشاهد مركّبة أصليّة، وليست لقطات تاريخيّة." States: no recorded narration exists; device voice; illustrations composite. No listening/voice-availability claim anywhere (stub dispatch proved ar-LB tagging only, not an actual Arabic voice).
Verification: AR pages show the honest note; no .mp3 requests; Listen offers only "Browser Voice (Device)".

## Residuals NOT silently accepted (explicit, separate from this repair; need Main's ruling per item)
- R2 resume-chip English template ("Continue from الصفحة 3?") - storybook.js COPY move; affects ar+fr, series-wide.
- R3 Latin digits in AR page indicator - localization choice to rule on (Arabic-Indic vs Western digits), series-wide.
- R4 settings panel/voice-pack label/reading indicator English - series-wide chrome localization.
- R5 covered by the R7 caption localization above.
- D2 desktop RTL spread geometry - design adjudication carried from G3.
- A1 localized H1/subtitle/meta - separate reviewed copy task, not started.
- A2 evidence AR claim fidelity review - pending independent translation review (its render-verifiability is what R1 restores).

## Order + gates
1. Apply harness repairs locally (R7, R1, R6). 2. Design re-runs the same RTL gate + EN regression frames. 3. Fidelity review of the two new AR string sets (caption, note) + the evidence claim. 4. Only then any question of baseline acceptance returns to Main. No step implies the next.
