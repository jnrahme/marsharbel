# Saint Longinus storybook - bounded TEXT review (2026-10-25)

**Scope:** independent reading/editorial review of the existing Longinus EN manuscript and static HTML reader shell. This is a bounded TEXT review only. It is NOT a whole-reader/render PASS, NOT an audio verdict, and NOT release clearance. No edits, no regeneration, no production restart were made or are authorized by this review; the provisional score is a finding, not rewrite authority.

**Bundle reviewed:** `longinus-reader-review-bundle-20261025-dd3a36cb.zip`, source branch `content/longinus-master-20261016` @ `1d0e10f2d2810c1ce25f58dd2ee4c92c766449b8`.
**Series todo:** todo-01M3DRVP14S9VT17JDZXC84QXF.

## 1. Bundle integrity (verified by sha256)

| Object | SHA256 | Status |
| --- | --- | --- |
| zip bundle | b1ff66644bb22f21bf387a3b8a7ff7a8f23dd87f6181e50435a3bcb2aa4ee5a6 | matches reported |
| longinus-story.html | a07cb7f18cf28323f594807875d2f48aae3e8bbad4ecac39e71a3c2858b90879 | matches reported |
| longinus-story-data.js | d98f269ff4ba685ae33af6b4ed4958971232147f05ceb6c9f8a91f423c1ced24 | matches reported |
| longinus-audio-ledger-20261016.json | 47ec31a840e84a41531ff7fe76fd58e2867745cc058b7a42e52830247b338c27 | computed |

Bundle contents: exactly those 3 payload files + BUNDLE-MANIFEST.md. No images, no MP3s, no CSS/JS/fonts included.

## 2. The two script hashes - what the objects actually are

- Ledger `scriptSha256` = `ad4f53c3384a3c55032f811d473bbbb581a13931549daa4cdceddfb22cb8be65` = a hash of the script TEXT snapshot used for audio generation (per the ledger's own binding note).
- `d98f269f...` = sha256 of the current data.js FILE on the branch.

They hash different objects, so inequality alone proves nothing in either direction. Test: 8 obvious canonicalizations of the current manuscript (concatenated bodies; newline-joined; double-newline-joined; bodies with trailing newline; titles+bodies; raw data.js bytes; JSON compact; JSON indent-2) - none reproduce ad4f53c3. This failure does NOT prove the audio used older text; it only shows the hashed script-text object is not derivable from the current manuscript in any tested form.

**Correct next step (recovery first, no production restart):** recover the actual script-text artifact that was hashed as ad4f53c3 from the generation records and compare it to the current manuscript. Only if recovery fails is any other path a question for the owner - regeneration is not an accepted fallback from this review.

Consequence until then: text/audio correspondence is UNVERIFIED - neither "match" nor "mismatch" can be claimed. The ten EN MP3s remain listening-unverified; no ASR, text or signal proxy may produce an audio PASS.

Informational only (explicitly NOT a pass signal): ledger durations total 355.21s (~5:55), inside the 5-8 minute envelope; implied pace 126-167 wpm per page against the 865-word manuscript - plausible, no impossible ratios. Page 1 (40.75s vs 30s guide) and page 10 (61.23s vs 50s guide) exceed the template's page guides, which are editing guides, not pass/fail.

## 3. Editorial review of the manuscript (saint-storybook-writing)

Metrics: 10 pages; 865 narrated words (within the 750-1,000 envelope); zero sentences over 22 words (longest 20w); sentence lengths vary 1-20 words; 4-7 sentences per story page (16 on the reflection page, allowed). Static HTML page-1 body is byte-identical to data.js page-1 body. `reflection` flag set only on page 10. Page 10 contains all four required elements: one open question, one verified Bible passage (Mark 15:33-39, with John 19:31-37), one safe small action, one short prayer to God with saint intercession kept distinct (quote: "God, help us look at Jesus with honest hearts. ... Saint Longinus, pray for us. Amen."). Death is stated plainly (p5: "Jesus gave a loud cry and died."). No invented dialogue, thoughts, witnesses or weather; tradition is labeled on every relevant page; the opening uses the sanctioned era-only pattern ("In the first century, outside Jerusalem, a Roman officer stood near the cross of Jesus."). Empty `prayer`/`heart` fields throughout - consistent with the no-duplicate-Heart-Moment rule; no body/heart duplication on screen.

### Five-dimension provisional score (TEXT ONLY; the Smooth audio leg is unscored - no ear review exists)

- **Smooth: 3/4.** Page turns are genuinely connected: p4 closes "The officer was still there, facing Jesus." and p5 opens "Jesus gave a loud cry and died."; p8 opens with the explicit time bridge "Long after that day, Christians continued to remember Longinus." Deducted for the repeated attribution machinery: "Mark tells us that..." opens sentences on pages 3, 4 AND 5 ("Mark tells us that women who had followed and cared for him were watching from a distance." / "Mark tells us that it lasted until three in the afternoon." / "Mark tells us that the great curtain in the Temple was torn from top to bottom.").
- **Human voice: 3/4.** Mostly warm spoken register. Machinery moments: the "Mark tells us" triple; p6 "We should keep those threads clear." (narrator addressing the reader like a pupil); p8 "We do not know every step of Longinus's life." echoing p1's "Much of his life is unknown to us."
- **No obvious explanation: 3/4.** Page 4 carries a mid-story instructional aside - "When we read this part of his story, we can bring our own difficult questions to God. We can also bring them to someone who cares for us." - which duplicates guidance already given on page 10; p9 "That is the moment we carry from this hillside." restates the sentence before it.
- **Respectful intelligence: 4/4.** No patronizing; the reflection invites rather than demands ("You do not have to find a quick answer. Talk with a parent or another trusted grown-up about what feels surprising or difficult in this story."); honest about the unknowns; crucifixion handled with dignity and no spectacle ("We do not need to picture its terrible details to understand that Jesus was suffering.").
- **Magical/inspiring: 3/4.** Real wonder beats exist - a Roman officer recognizing Jesus only after his death (p5), the women who stayed (p3: "Jesus had friends, and they were there."), p7's landing "The day did not end with a soldier's words alone. It also held the work of people who cared for Jesus when he could no longer speak.", and the closing "At the foot of the cross, a soldier's voice still invites us to look again." (p9). But page 6 ("The name Christians remember") is a flat meta-teaching page - pure Scripture-vs-tradition explanation - that drops the story's lift mid-book.

**TOTAL: 16/20 provisional** - every dimension at minimum 3, but 1 point below the 17/20 house gate, and that is before the unscored audio leg. Weakest dimensions first: magical/inspiring (page 6 flatness) and smooth (repeated "Mark tells us").

### Ranked text findings (findings only - NOT authorized edits)

1. Vary the "Mark tells us" sentence starts (p3, p4, p5); the template bans repeated starts / stock attribution.
2. Trim page 4's two-sentence reader-instruction aside to at most one line or move it to p10 - it duplicates p10 and breaks scene flow.
3. Give page 6 more story texture and shorten narrator-address lines ("We should keep those threads clear.") while keeping the Scripture/tradition clarity, which is this book's core promise.
4. Copyedit: British spelling "travelled" (p1, "His words have travelled far beyond that hillside.") - site is US English; suggest "traveled".
5. Consider merging the duplicated "unknown life" sentiment (p1 "Much of his life is unknown to us." and p8 "We do not know every step of Longinus's life."); keep one.

## 4. Scripture and tradition claims - verified against live sources

Full chapter texts were fetched live on 2026-10-25 from drbo.org (Douay-Rheims, public domain). The two USCCB pages resolved (HTTP titles returned: "Mark, CHAPTER 15 | USCCB", "John, CHAPTER 19 | USCCB") but their body text could not be extracted by the fetcher, so the verse-level text was verified at drbo.org instead.

- https://drbo.org/cgi-bin/d?b=drb&bk=48&ch=15 (Mark 15, full chapter, fetched live)
- https://drbo.org/cgi-bin/d?b=drb&bk=50&ch=19 (John 19, full chapter, fetched live)
- https://bible.usccb.org/bible/mark/15 (resolves; body extraction blocked)
- https://bible.usccb.org/bible/john/19 (resolves; body extraction blocked)
- https://saintmaron.org/wp-content/uploads/2022/11/Bulletin-10-16-2022.pdf (Maronite Eparchy parish bulletin, found via web search; contains "St Longinus / COMMANDER OF THE LEGION, MARTYR / Feast Day October 16")
- https://byzantinela.com/oct-16-2023/ (HTTP 200; "Oct. 16 The Holy Martyr Longinus the Centurion")
- https://www.stmaron.org/s/2026-Eparchial-Desk-Calendar.pdf (HTTP 302 -> https://static1.squarespace.com/static/5d47453b7563de000171d864/t/68dd26a792de98235cd9ff3a/1759323815122/2026+Eparchial+Desk+Calendar.pdf, HTTP 200, application/pdf)

Verified claims (Mark 15 / John 19, Douay-Rheims wording):

- p1, p5: centurion at the cross unnamed in Mark (15:39 "the centurion who stood over against him, seeing that crying out in this manner he had given up the ghost, said: Indeed this man was the son of God").
- p2: Golgotha (15:22); two others crucified with him (15:27); passersby mocked him and challenged him to come down from the cross (15:29-32).
- p3: women watching from a distance - Mary Magdalen, Mary the mother of James the less and of Joseph, and Salome - who followed him, ministered to him, and came up with him to Jerusalem (15:40-41).
- p4: darkness from the sixth hour until the ninth hour = noon to three in the afternoon (15:33); the cry "My God, my God, why hast thou forsaken me?" is Psalm 22 (15:34).
- p5: loud cry and died (15:37); Temple veil rent from top to bottom (15:38); the centurion saw how he died and declared afterward (15:39).
- p6: John 19:34 - "one of the soldiers with a spear opened his side" after Jesus was already dead (19:33-34); John gives no name.
- p7: evening (15:42); Joseph of Arimathea begged the body from Pilate (15:43); Pilate sent for the centurion and asked whether Jesus was already dead (15:44-45); linen and rock-hewn sepulchre (15:46); the women beheld where he was laid (15:47).
- p8: "The Maronite calendar commemorates him on October 16" - corroborated by the Maronite parish bulletin above and the Byzantine commemoration page; the cited 2026 Eparchial Desk Calendar PDF resolves.
- p10: citations Mark 15:33-39 and John 19:31-37 are accurate for the claims made.

## 5. Reader (HTML) verification - dependencies actually missing

The reader cannot be rendered or exercised from this bundle, and no render proof is fabricated here. Absent dependencies:

- 10 illustrations: `./media/storybook-longinus/images/page-01.jpg` ... `page-10.jpg` (data.js per page; page-01.jpg also the static img and og:image).
- 10 MP3s: `page-01.mp3` ... `page-10.mp3` (data.js `audio` fields).
- 4 stylesheets: `styles.css?v=20260922-1`, `storybook.css`, `storybook-joy.css`, `storybook-stage.css`.
- 8 scripts: `app.js`, `storybook.js`, `storybook-stage.js`, `translate.js?v=20260922-1`, `./nav.js?v=20260922-1`, `global-audio-player.js`, `/locale-routes.js`, `/analytics-init.js`.
- 2 fonts: `cormorant-garamond-latin-v1.woff2`, `manrope-latin-v1.woff2`.

Consequences: (a) the `audio: "page-01.mp3"` path resolution is unverifiable without storybook.js; (b) only page-1 text+image are static in the HTML - pages 2-10 hydrate via storybook.js, so per-page rendering is unverifiable from this bundle; (c) playback controls (voice pack select, auto-continue, rate buttons, resume banner) could not be exercised. Main routes the real dependency/render checks separately against the actual branch checkout.

Other reader findings:

- **Data anomaly:** every page object carries `"scene": "birth"` - an apparent un-updated value from the series template (page 1's static HTML uses class `scene-birth`). Functional impact is unverifiable without storybook.js; flagged for the integrator.
- **Evidence blocks:** identical boilerplate on all 10 pages (same generic claim text, same three source keys `longinusMark15`, `longinusJohn19`, `longinusCalendar`). The house rule asks for a page-specific claim-to-source map; the source keys cannot be resolved from this bundle (no sources registry included).
- **Preview markers (production-only note):** the HTML carries `noindex,nofollow` and the hero states "This English master is a private production preview. Narration, art and all-locale release gates remain open." This is consistent with WIP and is NOT a defect for private acceptance; removal is a production-release step only.

## 6. Bottom line

The manuscript is careful, truthful and close: all Scripture/tradition claims verified against live sources, structure and safety gates pass on text, and the provisional editorial score is 16/20 against a 17/20 gate with the audio dimension unscored. Remaining before any clearance:

1. The five small text findings in section 3 (findings, not authorized edits).
2. A real full-ear listening review of the ten EN MP3s - currently absent and unproxiable.
3. Recovery of the actual script-text artifact hashed as ad4f53c3 (recovery first; no production restart; regeneration is not an accepted fallback from this review).
4. A page-specific evidence map replacing the boilerplate evidence blocks.
5. Integrator check of the `"scene": "birth"` anomaly.
6. Dependency/render verification in the real branch checkout (routed separately by Main) - this bundle cannot render.

AR text retains only its existing bounded independent acceptance; nothing in this review extends it to assembled or voice acceptance.
