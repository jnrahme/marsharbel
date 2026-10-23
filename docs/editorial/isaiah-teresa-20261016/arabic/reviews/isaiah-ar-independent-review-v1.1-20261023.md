# Isaiah AR - independent text-fidelity + pronunciation-sheet review v1.1 (G1/G2, text only)
Date: 2026-10-23 ~07:16 EDT, v1.1. SUPERSEDES v1 (same filename, sha256 3442f4635fa7f1f6d5c3a62de9370dac42709206b02eb2e5cb8245eb4f071df4, sent 07:12 EDT) - v1 remains the prior version of record. Superseded claim: v1's F2 attributed the draft's name forms to the Catholic Jesuit translation. That was model recall and was WRONG; the sourced evidence below shows the forms match Smith-Van Dyke 1865. v1's other findings (F1, F3-F6) are unaffected.
Scope per Main 07:09: text review only. No audio exists or was reviewed; no listening review claimed. No reseals, integration, publication, Bible-translation policy, or faith-release approval performed or implied.

Package: commit f87c74547fd83c8454498e929edb19e37861c57f, docs/editorial/isaiah-teresa-20261016/.
EN script isaiah-script-v1.md sha256 VERIFIED = 42886651ec99ea6f256ab8d82b0c60d4367e064976fc52c35770113c89b64e89 (matches Main-supplied pin).
AR body isaiah-ar-body-draft-v1.md sha256 at pin = f3dfb326c4288cb7399bf3175dde52a4a035140ac2e7d0bee94023ddcc6b7865 (post-finalfix abe9a529).

## Source / Scripture verification (live USCCB, unchanged from v1)
- Isaiah 6:1-8, 1:16-17, 7:1-9, 7:14+footnote, 11:1-9 VERIFIED at bible.usccb.org/bible/isaiah/{6,1,7,11}. USCCB footnote 7:14 wording is literally "Emmanuel: the name means 'with us is God.'" - the EN script matches it exactly; AR gloss «اللهُ معنا» correct.
- Ahaz -> Assyria grounded (footnote 7:1 -> 2 Kgs 16). 701 BCE deliverance consistent with Catholic introduction framing (Isa 36-37; "as Isaiah had promised" = Isa 37:33-35).
- Body narration contains NO direct Bible quotation (paraphrase only; e.g. "شفتيه غير الطاهرتين" vs Van Dyke Isa 6:5 "نَجِسُ ٱلشَّفَتَيْنِ"). VERIFIED.

## Arabic body fidelity (unchanged from v1)
Full sentence-level fidelity across all 10 pages; no additions, omissions, or invented dialogue. Grammar/tashkeel clean; ordinals and agreements correct; partial-tashkeel style consistent with the sheet's stated register. Map per-page claims independently re-verified.

## Pronunciation sheet v1.1 (unchanged from v1)
Every listed entry accurate; stress, gemination, and sun-letter assimilation marks correct; مَذْبَح MAḎ-baḥ fix (ba325a50) present. Validation-status label (producer-authored, unvalidated, G2 review required) present and accurate.

## F2 REPLACED - name-form provenance, sourced
Observed sources (exact URLs fetched and quoted 2026-10-23 ~07:13-07:14 EDT):

Smith-Van Dyke 1865, fully voweled (ebible.org arb-vd):
- https://ebible.org/arb-vd/ISA01.htm Isa 1:1: "رُؤْيَا إِشَعْيَاءَ بْنِ آمُوصَ... فِي أَيَّامِ عُزِّيَّا وَيُوثَامَ وَآحَازَ وَحِزْقِيَّا مُلُوكِ يَهُوذَا"
- https://ebible.org/arb-vd/ISA06.htm Isa 6:2: "ٱلسَّرَافِيمُ وَاقِفُونَ فَوْقَهُ"; 6:8: "هَأَنَذَا أَرْسِلْنِي"
- https://ebible.org/arb-vd/ISA07.htm Isa 7:3 "قَنَاةِ ٱلْبِرْكَةِ ٱلْعُلْيَا"; 7:14 "عِمَّانُوئِيلَ"; 7:17 "مَلِكَ أَشُّورَ"

Jesuit Catholic translation (arabchurch.com "ترجمة اليسوعية" host pages, unvoweled):
- https://arabchurch.com/ArabicBible/jab/Isaiah/1 Isa 1:1: "رؤيا أشعيا بن آموص... وآحاز وحزقيا، ملوك يهوذا" (prophet = أشعيا; Jerusalem = أورشليم)
- https://arabchurch.com/ArabicBible/jab/Isaiah/6 Isa 6:2: "من فوقه سرافون قائمون"; 6:6: "أحد السرافين" (Jesuit: سرافون/السرافين, not السرافيم)
- https://arabchurch.com/ArabicBible/jab/Isaiah/7 Isa 7:14: "ها إن الصبية تحمل فتلد آبنا وتدعو آسمه عمانوئيل"

Findings:
(a) All six voweled names on the pronunciation sheet (إِشَعْيَاء، آحَاز، حِزْقِيَّا، عِمَّانُوئِيل، السَّرَافِيم، أَشُّور) match Smith-Van Dyke 1865 vocalized forms exactly, consonants and voweling. Sheet verifies clean against VD.
(b) Versus Jesuit: آحاز/حزقيا/عمانوئيل share the same consonant skeletons (Jesuit text unvoweled; vocalization cannot be confirmed from it), but Jesuit uses أشعيا for the prophet and سرافون/السرافين for seraphim - the draft follows VD, not Jesuit, on both.
(c) القدس for Jerusalem matches NEITHER tradition (both use أورشليم); it is the live-site AR convention (attested in locales/ar/mirrors/prayers.json, qozhaya-monastery.json, qadisha.json) and the pronunciation sheet already flags أورشليم as a reviewer-ruling alternative. Keep as site convention.
(d) No claim is made or needed about which translation is "common in Catholic use"; the factual provenance is: VD-1865-consistent name forms + site القدس convention. Recommended map wording: "name forms per Smith-Van Dyke 1865; القدس per site convention".
(e) Accurate distinction, per Main: the body narration is original paraphrase with zero direct quotation; the unspoken P3 section heading «هَأَنَذَا» is a title that matches one Van Dyke word from Isa 6:8. Different categories - a single-word unspoken heading is not body narration and not presented as Scripture, but it should be recorded as an exact-match heading, not folded into the body's "no quotation" statement.

## Remaining findings (unchanged from v1)
F1 (DOC SYNC - content fixing): map v1.1 pins stale body sha b95a5b04...; current f3dfb326... after ba325a50 + abe9a529. OPEN-5 RESOLVED in body (option c "الاستجابةُ لدعوةِ الله"); map still lists it OPEN. Needs map v1.2 re-pin + dated closeout.
F3 (MINOR - content fixing): P2 unspoken heading present tense "يَقْدِرُ" vs EN past "could say" -> "كَانَ يَقْدِرُ".
F4 (carried opens): OPEN-1 القريب (P4 commandment register) vs جيران (P1/P10 everyday) - Main accepted the semantic register split subject to same original meaning, no source waiver. OPEN-2 «هَأَنَذَا» heading - see F2(e): exact VD word match recorded; acceptability ruling remains editorial. OPEN-3 verified as mapped. OPEN-4 RTL template - infra, outside text review.
F5 (optional - content fixing): sheet additions أذيال / قَنَاة / كَرَازَة.
F6 (precision note): P5 "trust God" = Isa 7:9b within cited range; VD 7:9b "إِنْ لَمْ تُؤْمِنُوا فَلَا تَأْمِنُوا" supports the paraphrase.

## Verdict
Conditional G1/G2 TEXT PASS (text only; explicitly NOT a listening pass - no audio exists). Required before assembly: content's F1 map re-pin/OPEN-5 closeout, F3 heading, F5 sheet additions; then this reviewer re-checks the final bytes/diff. F2 replaced as above - provenance is VD-1865 + site القدس, documented; no translation-policy or faith-release decision taken. The native-speaker-requirement waiver (user voice note 2026-10-22 4:23:02 PM EDT, verified on the user channel) removes the native-review requirement only; it does not waive quality, sourcing, or any gate.
