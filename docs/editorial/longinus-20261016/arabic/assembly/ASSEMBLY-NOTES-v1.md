# Longinus AR private paired assembly v1 (2026-10-25 ~07:40 ET) - REVERSIBLE, PRIVATE, NOT APPROVED

Scope (Main 07:37): private paired assembly grounding under the existing series. No audio, no integration, no release, no user approval implied. Artifact for the independent RTL binding/render gate.

## Artifact
- assembly/longinus-story-ar-data.js - window.LONGINUS_STORY_AR, 10 pages, sha256 recorded below.
  Built mechanically from the reviewed AR body v2-candidate (ceb57282...): page titles = section headings minus "N. ", bodies = section text verbatim, reflection=true on p10 only, illustration = same plates as EN (book rule: same images EN+AR), scene="birth" parity (inert per render leg), prayer/heart "" parity.
  - audio: "" on every page - NO AR audio exists (gap A4 carried; UI renders the button with no pack; no audio production authorized).
  - evidence: type labels + claim translated to AR as ASSEMBLY-DRAFT (NOT independently reviewed - the reviewed v2 body does not cover evidence-panel copy; gap A2 carried). Sources keys unchanged (longinusMark15/longinusJohn19/longinusCalendar); per-page type variants mirrored from EN (1/6/8 "الكتاب والتقليد", 2/3/4/5/7 "الكتاب المقدّس", 9/10 "تأمّل عائليّ"). Standing finding: in-reader evidence blocks remain identical boilerplate claim text on all pages - unchanged here.
- assembly/binding-rtl-gate.patch - exact binding for the gate harness: storybook.js story map gains ar entry; harness COPY of the book page adds the ar data script tag and is opened at ?story=longinus&lang=ar. The pinned longinus-story.html (2382382e...) and production storybook.js are NOT modified on this branch.

## Gate prerequisites already established (G3 RTL-RENDER-TEST-20261023, Isaiah branch)
Reader RTL frame works (dir=rtl, shaping, reversed pagination, dots, plate swap). Carried defects: D1 resume-chip English template; D2 desktop spread geometry in RTL (design adjudication); D3 Latin numerals in AR page indicator. A3: /stories link 404 on bare static server - stage-only check. A5: tashkeel spot-check applies (this AR body has full tashkeel).

## Open for the gate / later lanes
A1 localized H1/subtitle/meta (template is EN) - NOT produced here; needs its own reviewed copy.
A2 evidence-panel AR claim - assembly-draft above, needs independent translation review.
OPEN-4: this assembly + independent RTL render = the resolution path; gate verdict pending.
