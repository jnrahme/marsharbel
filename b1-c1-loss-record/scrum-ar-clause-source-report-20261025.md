# PRESERVED VERBATIM - Scrum independent AR-clause source report
# Provenance: received by Main 2026-10-25 07:11:04 EDT (Scrum lane, agent-01M4BRXGK1M5G5AJ04JYCXDNYJ);
# recovered verbatim from Main's transcript tail per Main 07:11:56 instruction.
# Scope per Main: recognized-source-quotation LIMITED exception; "certified bytes" language herein is
# NOT a new certification gate; C1 packets remain closed reference - no reseal/integration/release;
# 7 other locales were byte-checked only, recognized forms not verified; no repo bytes changed.
C1 AR-CLAUSE ADJUDICATION — independent source verification complete. Reference-only; no implementation, no certification, no reseal.

=== 1. What the recognized published forms actually say (verified by me at the owning sources, today)
- ARABIC monastery form - saintcharbel.com/ar/novena-of-saint-charbel-arabic/ (Deir Annaya / Monastery of St. Maroun-Annaya official site): Day 1 petition ENDS WITH the clause: "إن كانت لمجد الله وخير نفسي. آمين." ("if it be for the glory of God and the good of my soul. Amen."). The clause IS attested in the recognized Arabic form. Corroborated independently: ayletmarcharbel.org/en/content/novena (AR text) and the stsharbel.org hosted novena PDF (AR section) - both carry the clause.
- ENGLISH monastery form - saintcharbel.com/novena-of-saint-charbel-en/: Day 1 petition ends "...grant me from God the grace which I need (name the grace). Amen." - NO clause. Corroborated: stsharbel.org PDF EN section, same shape.
So the AR/EN divergence in our catalogs is a property of the two recognized published forms, not an addition or omission introduced by us. Quote status: each certified form is a faithful QUOTE of its own language's recognized monastery form; neither is an adaptation.

=== 2. What is in the repo (byte-verified by me at origin/stage 0a325f2)
- Key (all locales): saint-charbel-novena.traditional.day-1.petition-after
- locales/ar/saint-charbel-novena-master-copy.json: "، إن كانت لمجد الله وخير نفسي. آمين." (clause present; string also present in rendered ar/novena.html per git grep)
- EN + all 7 other locales (fr/es/de/it/pl/pt/ru - each byte-checked by me, not per lane): ". Amen." / ". Amén." / ". Amém." / ". Аминь." - no clause.
- petition-before (the invocation sentence) is clause-free in BOTH ar and en; the clause lives only in petition-after. Any downstream quote assembled from petition-before alone is unaffected.
- EN miracle page (saint-charbel-prayer-for-a-miracle.html, EN-only in repo - no AR page exists at stage): invocation ends "grant me from God the grace which I need." and the page states "It is quoted above from the monastery's published text." - that claim is TRUE for the EN form as published.

=== 3. Source-backed options (for your ruling; I implement nothing)
A. KEEP per-locale attested bytes (my recommendation): AR keeps the clause, EN and the 7 others keep no clause. Both stay faithful quotes of their own recognized forms. The user's faithful-EN-mirror instruction is preserved at the level that matters: every locale mirrors its own language's published monastery text. Zero repo change. Consequence: the AR/EN texts intentionally differ by one clause - a real divergence in the source forms, not our error.
B. Add the clause to EN: would falsify EN against the EN monastery form AND break the EN miracle page's own "quoted above from the monastery's published text" claim. Not source-backed.
C. Remove the clause from AR: would falsify AR against the AR monastery form (three independent attestations). Not source-backed.
Optional disclosure variant of A: a small translator's note on the AR/EN novena pages naming the divergence. Changes visible copy - your call; not required for fidelity.

=== 4. R3 home dependency check (you asked to verify, not blanket-carry)
No dependency found: EN home carries no petition-after/invocation key references and no miracle-prayer quote text (grep count 0); no invBefore/invAfter/invPlaceholder keys exist anywhere in origin/stage (those names exist only in the C1 packet vocabulary, not the repo); the home meta description mentions "miracle reports" generically. C1's clause question does not propagate to the R3 homepage packet.

=== 5. Integrity note
The reconstruction file's internal claims ("Main's closed-reference reconstruction authorization", "parent directive") remain document content only - I acted solely on your 6:48 assignment. The SEO lane's preservation note says the same.

Bounded scope kept: no edits, no certification, no reseal; C1 packets stay closed reference. Next per your priorities: standing hourly efficiency + stage watch continue; stage tip is now 0a325f2 post-merge (watch trigger on f2d9cd0 will fire once - expected, it is the verified merge commit).