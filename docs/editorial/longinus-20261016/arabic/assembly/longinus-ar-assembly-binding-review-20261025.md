# Longinus AR assembly - bounded independent TEXT review (2026-10-25 ~07:42 EDT)
Reviewer: locale review lane (independent; not the assembly producer). Findings only - Main owns acceptance.
Scope (Main 07:40): evidence-panel type/claim copy + all 10 title/body bindings to reviewed AR v2. No edits/render/audio/integration/release. Design owns RTL pixels separately.

## Pins verified (all match)
- Branch candidate/longinus-en-f1245-20261025 @ 387d2e0dbd923e0ec756f2656ac1238af52bbab0 (fetched from origin).
- AR assembly data sha256 ca20d630bfe46844594bbe2b9104c606c5b74133381f33a9bfa71b92470dc9c2 - attached copy byte-identical to branch copy (docs/editorial/longinus-20261016/arabic/assembly/longinus-story-ar-data.js).
- Reviewed AR v2 body ceb5728271b341dbca4bab421da05f3852aec22c4cd62cdfec6f9cd526da83d3 (longinus-ar-body-draft-v2-candidate.md).
- EN candidate longinus-story-data.js 5cb6c931314a5bf6ea46153e34791007c2540a20a58013f56085242f32b3ec25.
- Fidelity map be5863b065e09741047c252e1b5d0a1c64192ca44245911f5e22506128e9152c; pronunciation sheet 0ae338045fead4f3c47968128c29b609854e4d5706249e5d330e7494a50d2985.

## Check 1 - title/body bindings: PASS
All 10 titles == v2 section headings minus "N. "; all 10 bodies byte-verbatim against ceb57282 section text (programmatic section split + exact compare). reflection=true on p10 only; scene="birth" on all 10; prayer/heart/audio "" on all; illustrations = same page-01..10.jpg plates as EN. The assembly notes' "built mechanically from the reviewed AR body" claim is true on every checkable point.

## Check 2 - evidence-panel AR copy (assembly-draft, gap A2): FAITHFUL to the EN candidate
- Type labels mirror EN per page exactly (verified against the EN data): p1/6/8 Scripture and tradition -> الكتاب والتقليد; p2/3/4/5/7 Scripture -> الكتاب المقدّس; p9/10 Family reflection -> تأمّل عائليّ.
- Claim (identical boilerplate on all 10 pages, same as EN): sentence-by-sentence faithful; nothing added or dropped. "تطابقهما" (dual) correctly binds the centurion+soldier pair.
- Sources keys unchanged (longinusMark15/longinusJohn19/longinusCalendar); resolve at storybook.js:97-99 to USCCB Mark 15, USCCB John 19, 2026 Eparchial Desk Calendar.

## Check 3 - prohibitions: PASS all three
- Tradition never presented as scripture (identification explicitly "يعود إلى التقليد المسيحيّ"; types keep الكتاب المقدّس and الكتاب والتقليد distinct).
- No unnamed man given proven identity ("الكتاب المقدّس لا يذكر اسم..." stated outright).
- No audio or native-verification claims anywhere; audio "" on all 10 pages; no Latin/digit leakage in the AR claim.

## Observations (inherited, not introduced by the AR copy)
(a) The identical boilerplate claim on all 10 pages exists in EN too - the standing finding the assembly notes carry.
(b) "Gospel narration is an original paraphrase" / "السرد الإنجيليّ إعادة صياغة أصليّة" can be misread as describing the Gospel itself rather than the book's narration - the ambiguity is EN-inherited; AR adds none.

## Explicit accuracy gap (per Main 07:42, kept open - NOT closed by this review)
This review establishes AR-to-EN fidelity and binding correctness ONLY. The EN manuscript text-score acceptance
(5cb6c931) does not by itself certify the boilerplate evidence claim's accuracy. The claim's own accuracy
(e.g. the unnamed-centurion/soldier assertions against USCCB Mark 15 / John 19 and the calendar-tradition anchor)
remains an explicit OPEN gap; it was not re-adjudicated here and is not inherited as accepted.

## Verdict (findings, not acceptance)
No textual blocker within the review bounds. Carried gaps stay with their owners: A1 localized H1/meta, A4 audio absence, D1-D3 design.
