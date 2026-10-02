# Clean originals of AI-generated images

Every AI-generated image on the site carries a baked-in "marsharbel.com" watermark so it keeps the name when pinned or shared. The served file lives where the page expects it (for example `gallery/`). The clean, un-watermarked original lives here under the same filename so the mark can be regenerated.

Regenerate one:

    python3 scripts/watermark_ai_image.py assets/originals/gallery/NAME.webp gallery/NAME.webp

Rules:
- Never watermark historic photographs.
- Never serve a file from this folder on a page.
- New AI images: save the clean file here first, then watermark into place. Keep the same dimensions and format.
