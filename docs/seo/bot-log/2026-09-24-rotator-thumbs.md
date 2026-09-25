# 2026-09-24 - Homepage news rotator thumbnails (technical SEO lane)

Rotator images show at 64x64 but loaded 320px squares, and one used a
906x667 portrait (squashed to a square because the img uses object-fit:
fill). The 5 images were ~113 KB; the new 128px center-cropped WebP thumbs
total 21 KB. The portrait now shows undistorted.

Source fix: scripts/build_news_thumbs.py (idempotent) builds the thumbs and
rewrites the rotator srcs. QA runs it with --check, so a new rotator item
with a full-size image fails the build. Convention added to
docs/content-conventions.md for the news desk.

Looked at and left alone: the storybook/rosary promo images (768w). They
display at 326-734 CSS px, so 768 is right for 2x screens; Lighthouse's
savings estimate there assumes 1x.
