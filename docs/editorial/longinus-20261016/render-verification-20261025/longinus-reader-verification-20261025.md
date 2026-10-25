# Longinus reader - independent render/reader verification (2026-10-25, design director lane)

Scope: bounded private visual/render review. No edits, no merges, no integration, no audio/listening verdict, no release GO. Text review (16/20) is a separate lane and was not repeated. AR not assembled on the branch - EN only, nothing created.

## Pins / commit (verified, actual bytes)
- Repo cloned (public; correct name jnrahme/marsharbel), checked out exact pinned commit 1d0e10f2d2810c1ce25f58dd2ee4c92c766449b8 (branch tip has since moved to 440fc4cd; pinned files identical at tip).
- longinus-story-data.js sha256 = d98f269ff4ba685ae33af6b4ed4958971232147f05ceb6c9f8a91f423c1ced24 - exact pin
- longinus-story.html sha256 = a07cb7f18cf28323f594807875d2f48aae3e8bbad4ecac39e71a3c2858b90879 - exact pin

## Render matrix (local Playwright, served repo root, no cloud browser)
- 10/10 EN pages rendered at 390x844 and 1440x900. Counter "Page N of 10" correct on all 20 states; prev disabled only p1; next disabled only p10; active dot == open page on all 20.
- All 10 plates load and paint (media/storybook-longinus/images/page-01..10.jpg); no broken media; Cormorant/Manrope render.
- p6 diptych + account labels ("Mark: an unnamed centurion / John: an unnamed soldier / Tradition links these accounts with Longinus...") intentional and legible.
- p10 reflection cites Mark 15:33-39 / John 19:31-37 - correct readings for this book.

## scene:'birth' on all pages - INERT (finding, not a bug)
Class scene-art scene-birth present on every page's art container, but the scene-birth CSS rules (storybook.css ~477-490) target children (.scene-ground/.scene-halo/.scene-child) that sceneMarkup never emits for these pages. All 20 renders show clean plates, zero decorative birth-scene artifacts. No visible consequence; no fix proposed (reassignment would be an unauthorized edit).

## Text reachability (measured, not inferred)
- Header at settled load: topbar bottom 96px, h1 top 118px - no overlap.
- Max scroll, all 10 phone pages: 0 covered text blocks; last content clears controls by +51.2px on every page. Desktop p10: 0 covered, +45.1px.
- Just-clear phone positions: p1 +10.9px, p6 +11.2px, p10 prayer +11.0px - final lines readable above the bar.
- Honest edge: desktop p10 at the exact just-clear scroll position grazes at +0.3px; one more scroll tick opens +45px.

## Audio (state only)
"Listen to the story" button present and enabled on all pages; en/page-01..10.mp3 exist on branch. No playback or ASR verification; no listening PASS.

## Explicit private gaps (not production passes)
- stories-shelf fetch 404 (shelf suggestion fails in standalone context) - existing private navigation gap, not cosmetic, not escalated.
- Desktop p10 just-clear graze (+0.3px) - registered.
- Footer chrome low-contrast links (production-wide, radar class).

## Evidence attachments (sent to Main 2026-10-25)
sheet-en-phone.png, sheet-en-desktop.png (all 10 pages each); en-phone-p06.png; decisive-phone-p06.png, decisive-phone-p10.png, decisive-desktop-p10.png; clearance-en-phone-p01..p10.png; clearance-en-desktop-p10.png.
