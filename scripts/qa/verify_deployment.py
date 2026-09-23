#!/usr/bin/env python3
"""Verify public frontend files against this checkout, not just HTTP success."""

import argparse
import json
import struct
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def palette_png_pixels(data):
    """Decode our 8-bit palette icons, allowing lossless CDN recompression."""
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        return None
    try:
        chunks = {}
        offset = 8
        while offset < len(data):
            length = struct.unpack('>I', data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            payload = data[offset + 8:offset + 8 + length]
            crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
            if zlib.crc32(kind + payload) != crc:
                return None
            chunks.setdefault(kind, bytearray()).extend(payload)
            offset += length + 12
        width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', chunks[b'IHDR'])
        if (depth, color, compression, filtering, interlace) != (8, 3, 0, 0, 0):
            return None
        raw = zlib.decompress(chunks[b'IDAT'])
        if len(raw) != height * (width + 1) or b'IEND' not in chunks:
            return None
        palette = chunks[b'PLTE']
        alpha = chunks.get(b'tRNS', b'')
        pixels = bytearray()
        previous = bytearray(width)
        for y in range(height):
            start = y * (width + 1)
            filter_type = raw[start]
            if filter_type > 4:
                return None
            row = bytearray(raw[start + 1:start + width + 1])
            for x in range(width):
                left = row[x - 1] if x else 0
                above = previous[x]
                corner = previous[x - 1] if x else 0
                predictor = left + above - corner
                paeth = min((left, above, corner), key=lambda value: abs(predictor - value))
                row[x] = (row[x] + (0, left, above, (left + above) // 2, paeth)[filter_type]) % 256
                index = row[x]
                rgb = palette[index * 3:index * 3 + 3]
                if len(rgb) != 3:
                    return None
                pixels.extend(rgb)
                pixels.append(alpha[index] if index < len(alpha) else 255)
            previous = row
        # Preserve color-management semantics as well as dimensions and pixels.
        color_metadata = tuple(bytes(chunks.get(key, b'')) for key in (b'gAMA', b'cHRM', b'sRGB', b'iCCP'))
        return width, height, bytes(pixels), color_metadata
    except (KeyError, ValueError, struct.error, zlib.error):
        return None


def contents_match(path, expected, actual):
    if expected == actual:
        return True
    if path.suffix.lower() == '.png':
        decoded = palette_png_pixels(expected)
        return decoded is not None and decoded == palette_png_pixels(actual)
    return False


def frontend_files(root):
    files = {path for pattern in ("*.html", "*.js", "*.css", "*.webmanifest")
             for path in root.glob(pattern)}
    files.update((root / "mysteries").glob("*.html"))
    for language in json.loads((root / "locales/registry.json").read_text())["locales"]:
        files.update((root / language).glob("*.html"))
    files.update(root / name for name in ("robots.txt", "sitemap.xml", "indexnow-key.txt"))
    files.update((root / "media/promo/optimized").glob("*.webp"))
    files.update((root / "media/fonts").glob("*.woff2"))
    files.update((root / "media/optimized").glob("*.webp"))
    files.update((root / "media/optimized").glob("*.avif"))
    files.update((root / "media/promo/optimized").glob("*.avif"))
    files.update((root / "pwa").glob("*-v2.png"))
    return sorted(path for path in files if path.is_file())


def verify_file(root, path, base_url, nonce):
    relative = path.relative_to(root).as_posix()
    url = f"{base_url.rstrip('/')}/{quote(relative)}?deployment-check={nonce}"
    request = Request(url, headers={"Cache-Control": "no-cache",
                                   "User-Agent": "Marsharbel-Deployment-Check/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            actual = response.read()
        if not contents_match(path, path.read_bytes(), actual):
            return f"{relative}: deployed contents differ from checkout"
    except (URLError, TimeoutError, OSError) as error:
        return f"{relative}: {error}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://marsharbel.com")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--interval", type=float, default=20)
    args = parser.parse_args()
    if args.attempts < 1 or args.interval < 0:
        parser.error("attempts must be positive and interval must be nonnegative")
    root = args.root.resolve()
    if not (root / "index.html").is_file():
        parser.error("root must contain the website, including index.html")
    try:
        files = frontend_files(root)
    except (OSError, ValueError, KeyError) as error:
        parser.error(f"root must contain a valid locales/registry.json: {error}")
    for attempt in range(1, args.attempts + 1):
        nonce = time.time_ns()
        with ThreadPoolExecutor(max_workers=6) as pool:
            errors = list(filter(None, pool.map(
                lambda path: verify_file(root, path, args.base_url, nonce), files)))
        if not errors:
            print(f"Verified {len(files)} live frontend files match the checkout.", flush=True)
            return 0
        print(f"Attempt {attempt}/{args.attempts}: {len(errors)} files not verified", flush=True)
        for error in errors:
            print(f"  {error}", flush=True)
        if attempt < args.attempts:
            time.sleep(args.interval)
    print("Deployment verification failed. Check Hostinger Git build output and cache.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
