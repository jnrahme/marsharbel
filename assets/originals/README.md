# Clean originals of AI-generated images

The new AI gallery images and social derivative in this release carry a baked-in "marsharbel.com" watermark so it keeps the name when pinned or shared. The served file lives where the page expects it (for example `gallery/`). The clean, un-watermarked original lives here under the same filename so the mark can be regenerated.

Regenerate one:

    python3 scripts/watermark_ai_image.py assets/originals/gallery/NAME.webp gallery/NAME.webp

Rules:
- Never watermark historic photographs.
- Never serve a file from this folder on a page.
- New AI images: save the clean file here first, then watermark into place. Keep the same dimensions and format.

Portrait images that appear in the gallery grid (object-fit:cover, 360px tall) must be watermarked with `--bottom-frac 0.72 --size-frac 0.034`, so the mark sits inside the part of the image the grid crop keeps (checked at 390, 600 and 1280px wide). Wide strips and the og image keep the default bottom-corner placement.
