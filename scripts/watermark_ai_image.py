#!/usr/bin/env python3
"""Bake the "marsharbel.com" watermark into an AI-generated image file.

Usage: python3 scripts/watermark_ai_image.py SRC DEST [--corner right|left] [--bottom-frac F] [--size-frac F]

SRC is the clean original (keep it under assets/originals/). DEST is the
watermarked file the site serves. Dimensions and format are preserved.
Text is Cormorant Garamond (the site serif), about 2.5% of image width,
semi-transparent cream with a soft dark halo, bottom corner, never centred.
Requires Pillow, fontTools and brotli.
"""
import argparse, io, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_WOFF2 = os.path.join(ROOT, 'media/fonts/cormorant-garamond-latin-v1.woff2')
TEXT = 'marsharbel.com'

def load_font(size):
    font = TTFont(FONT_WOFF2)
    font.flavor = None
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    pil = ImageFont.truetype(buf, size)
    try:
        pil.set_variation_by_axes([700])
    except Exception:
        pass
    return pil

def watermark(src, dest, corner='right', bottom_frac=None, size_frac=0.027):
    im = Image.open(src)
    fmt = im.format
    base = im.convert('RGBA')
    w, h = base.size
    size = max(14, round(w * size_frac))
    font = load_font(size)
    margin = round(w * 0.025)
    probe = ImageDraw.Draw(base)
    l, t, r, b = probe.textbbox((0, 0), TEXT, font=font)
    tw, th = r - l, b - t
    x = w - margin - tw - l if corner == 'right' else margin - l
    y = (h - margin - th - t) if bottom_frac is None else (round(h * bottom_frac) - th - t)
    halo = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).text((x, y), TEXT, font=font, fill=(0, 0, 0, 200))
    halo = halo.filter(ImageFilter.GaussianBlur(max(1.5, size * 0.12)))
    text = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(text).text((x, y), TEXT, font=font, fill=(246, 238, 224, 205))
    out = Image.alpha_composite(Image.alpha_composite(base, halo), text).convert('RGB')
    if fmt == 'WEBP':
        out.save(dest, 'WEBP', quality=92, method=6)
    elif fmt == 'JPEG':
        out.save(dest, 'JPEG', quality=92, optimize=True)
    else:
        out.save(dest, fmt)
    return (x, y, tw, th)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dest')
    ap.add_argument('--corner', choices=['right', 'left'], default='right')
    ap.add_argument('--bottom-frac', type=float, default=None, help='bottom edge of the mark as a fraction of image height; use ~0.72 for portrait images shown in object-fit:cover grid cards so the mark is not cropped')
    ap.add_argument('--size-frac', type=float, default=0.027, help='mark text height as a fraction of image width')
    a = ap.parse_args()
    if os.path.abspath(a.src) == os.path.abspath(a.dest):
        sys.exit('SRC and DEST must differ; keep the clean original.')
    print(watermark(a.src, a.dest, a.corner, a.bottom_frac, a.size_frac))
