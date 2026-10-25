# Longinus - page-specific evidence registry + render dependency locator (2026-10-25 ~07:01 EDT)

Basis: real branch content/longinus-master-20261016 @ 1d0e10f2d2810c1ce25f58dd2ee4c92c766449b8 (origin-verified). Manuscript longinus-story-data.js sha256 d98f269ff4ba685ae33af6b4ed4958971232147f05ceb6c9f8a91f423c1ced24. Companion to the preserved independent TEXT review (docs/editorial/longinus-20261016/longinus-text-review-20261025.md, commit ed2ab9cc). Findings only - NO edit, regeneration, or production authority.

## A. Review finding evidence (each verified present on the real branch)

F1 repeated "Mark tells us" sentence starts: present p3, p4, p5 (substring-verified in each page body).
F2 p4 mid-story reader-instruction aside duplicating p10: "When we read this part of his story" present p4; the duplicated guidance "Talk with a parent" present p10.
F3 p6 meta-teaching narrator address: "We should keep those threads clear." present p6.
F4 British spelling: "travelled" present p1 ("His words have travelled far beyond that hillside.").
F5 unknown-life echo: "Much of his life is unknown to us." present p1; "We do not know every step" present p8.

## B. scene:'birth' on all pages - mechanics, for runtime inspection (not a blind fix)

- All 10 pages carry scene:'birth' in longinus-story-data.js (page 10 also reflection:true).
- Consumption: storybook.js line ~1081 sceneMarkup(scene, illustration) emits class scene-<scene>; line ~1410 illustration falls back to SCENE_IMAGES[page.scene] only when page.illustration is absent; line ~1428 sets data-scene.
- Every Longinus page carries an explicit illustration (./media/storybook-longinus/images/page-XX.jpg), so the SCENE_IMAGES fallback is never used for imagery. The scene value's only effect is the scene-birth CSS class + data-scene attribute, i.e. the decorative CSS scene layer (storybook.css .scene-* elements: stars/ground/mountain/moon/cloud/house/cross/path/heart/halo/rays/candle/book/saint/child).
- Whether the all-birth decorative layer is visually wrong on pages 2-10 requires actual rendered inspection; the fix (if any) is per-page scene reassignment in data.js, which is an edit and is NOT authorized.

## C. Render dependency locator for design (real checkout)

Checkout: branch content/longinus-master-20261016 @ 1d0e10f2d2810c1ce25f58dd2ee4c92c766449b8. Serve repo root over HTTP (reader uses absolute and relative paths; file:// will misbehave). Page: /longinus-story.html.

Runtime dependencies referenced by longinus-story.html (all present on the branch):
- CSS: styles.css?v=20260922-1, storybook.css, storybook-stage.css, storybook-joy.css
- JS: app.js, storybook.js, storybook-stage.js, global-audio-player.js, longinus-story-data.js, nav.js?v=20260922-1, translate.js?v=20260922-1, /locale-routes.js, /analytics-init.js
- Fonts: media/fonts/cormorant-garamond-latin-v1.woff2, media/fonts/manrope-latin-v1.woff2
- Images: media/storybook-longinus/images/page-01.jpg .. page-10.jpg
- Audio: media/storybook-longinus/en/page-01.mp3 .. page-10.mp3 (render may load; audio content remains listening-unverified - no playback verdict may be produced)

Known non-dependency: no external CSS/JS beyond fonts already local; outbound links (usccb.org etc.) are hyperlinks only.

## D. Audio script snapshot ad4f53c3 - recovery status

The hashed object is the Oct 16 file /tmp/longinus-book/script-v1-review.md (hashed 2026-10-16 10:08:46 EDT by this lane). The /tmp dir is wiped. NOT in branch history (checked: no commit on the branch ever carried script-v1-review.md or narration-v1.*). The exact original bytes survive ONLY as attachments delivered to Main: agentmsg-01M52GJDKWGM30GTTMVXKDEHRK (Oct 16 10:06:34, script-v1-review.md + evidence plan) and agentmsg-01M52GSN7PZH4D4TMV4ZGY2J8C (Oct 16 10:10:31, script-v1-review.md + narration-v1.txt + narration-v1.json, narration json sha f4631ad02a3f96b91c08289077dbe70e95fa87ba2c6a4613cd425ae1751d9c96). If the reviewer needs the byte-exact snapshot, Main can re-supply the attachment from either message; this lane cannot fetch another agent's attachment bytes.
