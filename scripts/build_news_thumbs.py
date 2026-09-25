#!/usr/bin/env python3
"""Serve homepage news-rotator images as small square thumbnails.

The rotator shows each image at 64x64 CSS px. Source images in media/news/
are 320px or larger, so each item would download 5-25x the pixels it shows.
This script makes a 128px (2x) center-cropped WebP for every rotator image
under media/news/thumb/ and points the rotator <img> at it.

Run after adding a rotator item:   python3 scripts/build_news_thumbs.py
QA runs it with --check, which fails if a thumbnail is missing or unused.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
SIZE = 128
ITEM = re.compile(r'(<a class="news-rotator-item[^"]*"[^>]*>\s*<img src=")([^"]+)(")')


def thumb_for(src: str) -> str:
    """./media/news/x.webp -> ./media/news/thumb/x-128.webp (idempotent)."""
    if "/thumb/" in src:
        return src
    path = Path(src.removeprefix("./"))
    return f"./{path.parent.as_posix()}/thumb/{path.stem}-{SIZE}.webp"


def source_for(thumb: str) -> Path | None:
    name = Path(thumb).name.removesuffix(f"-{SIZE}.webp")
    folder = ROOT / Path(thumb.removeprefix("./")).parent.parent
    matches = sorted(folder.glob(f"{name}.*"))
    return matches[0] if matches else None


def make_thumb(source: Path, target: Path) -> None:
    from PIL import Image
    image = Image.open(source).convert("RGB")
    side = min(image.size)
    left, top = (image.width - side) // 2, (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, "WEBP", quality=82, method=6)


def main(check: bool) -> int:
    html = INDEX.read_text(encoding="utf-8")
    errors = []

    def rewrite(match: re.Match) -> str:
        src = match[2]
        thumb = thumb_for(src)
        target = ROOT / thumb.removeprefix("./")
        if thumb != src:
            if check:
                errors.append(f"index.html: rotator image {src} should use {thumb}")
            elif not target.exists():
                make_thumb(ROOT / src.removeprefix("./"), target)
        elif not target.exists():
            source = source_for(thumb)
            if check or source is None:
                errors.append(f"index.html: missing rotator thumbnail {thumb}")
            else:
                make_thumb(source, target)
        return match[1] + thumb + match[3]

    updated = ITEM.sub(rewrite, html)
    if errors:
        print("\n".join(errors))
        return 1
    if not check and updated != html:
        INDEX.write_text(updated, encoding="utf-8")
    print("News rotator thumbnails checked." if check else "News rotator thumbnails built.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
