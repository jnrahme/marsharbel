#!/usr/bin/env python3
"""Generate sitemap-images.xml and sitemap-video.xml from the built pages.

Both files are derived from sitemap.xml (page set) and the committed HTML behind
each canonical URL, so they never list a page the main sitemap does not. Images
must be served from this site and exist on disk. Videos are local mp4 files and
YouTube embeds that carry a descriptive iframe title.

Usage:
  python3 scripts/build-media-sitemaps.py          # rewrite both files
  python3 scripts/build-media-sitemaps.py --check  # fail if either is stale
"""
import argparse
import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sitemap_lastmod import ENTRY, SITE, source_for  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif')
SKIP_PARTS = ('/media/flags/', '/pwa/', '/icons/', '/fonts/')
YOUTUBE = re.compile(r'youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{11})')
GENERIC_TITLES = {'', 'youtube video player', 'video', 'player'}
IMG_NS = 'http://www.google.com/schemas/sitemap-image/1.1'
VID_NS = 'http://www.google.com/schemas/sitemap-video/1.1'


def page_urls(root):
    text = (root / 'sitemap.xml').read_text()
    return [m.group(1) for m in ENTRY.finditer(text)]


def local_file(root, absolute):
    parts = urlsplit(absolute)
    if parts.netloc != urlsplit(SITE).netloc:
        return None
    path = root / parts.path.lstrip('/')
    return path if path.is_file() else None


def clean(url):
    parts = urlsplit(url)
    return f'{parts.scheme}://{parts.netloc}{parts.path}'


def shorten(text, limit=100):
    if len(text) <= limit:
        return text
    return text[:limit - 3].rsplit(' ', 1)[0].rstrip(' ,.;:') + '...'


def scan(root, url):
    soup = BeautifulSoup(source_for(root, url).read_text(errors='replace'), 'html.parser')
    area = soup.find('main') or soup.body or soup
    images, seen = [], set()
    for img in area.find_all('img'):
        src = (img.get('src') or '').strip()
        if not src or src.startswith('data:'):
            continue
        absolute = clean(urljoin(url, src))
        if not absolute.lower().endswith(IMAGE_EXT) or any(p in absolute for p in SKIP_PARTS):
            continue
        if absolute in seen or local_file(root, absolute) is None:
            continue
        seen.add(absolute)
        images.append(absolute)
    meta = soup.find('meta', attrs={'name': 'description'})
    description = (meta.get('content') if meta else '') or ''
    videos, seen_v = [], set()
    declared = {}
    for block in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(block.string or '')
        except ValueError:
            continue
        for node in (data.get('@graph', [data]) if isinstance(data, dict) else []):
            if node.get('@type') == 'VideoObject' and node.get('contentUrl'):
                declared[clean(node['contentUrl'])] = node
    for video in soup.find_all('video'):
        sources = [video.get('src')] + [s.get('src') for s in video.find_all('source')]
        for src in filter(None, sources):
            content = clean(urljoin(url, src))
            node = declared.get(content, {})
            thumb = node.get('thumbnailUrl') or video.get('poster')
            title = (node.get('name') or video.get('aria-label') or video.get('title') or '').strip()
            if not content.endswith('.mp4') or local_file(root, content) is None or content in seen_v:
                continue
            if not thumb or not title or not (node.get('description') or description):
                continue
            thumb = clean(urljoin(url, thumb))
            if local_file(root, thumb) is None:
                continue
            seen_v.add(content)
            videos.append({'title': shorten(title), 'description': node.get('description') or description, 'thumb': thumb, 'content': content})
    for frame in soup.find_all('iframe'):
        found = YOUTUBE.search(frame.get('src') or frame.get('data-src') or '')
        title = ' '.join((frame.get('title') or '').split())
        if not found or title.lower() in GENERIC_TITLES or not description or found.group(1) in seen_v:
            continue
        vid = found.group(1)
        seen_v.add(vid)
        videos.append({'title': shorten(title), 'description': description,
                       'thumb': f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg',
                       'player': f'https://www.youtube-nocookie.com/embed/{vid}'})
    return images, videos


def render(root):
    image_rows, video_rows = [], []
    for url in page_urls(root):
        images, videos = scan(root, url)
        if images:
            image_rows.append(f'  <url><loc>{escape(url)}</loc>' + ''.join(
                f'<image:image><image:loc>{escape(i)}</image:loc></image:image>' for i in images) + '</url>')
        for v in videos:
            loc = f'<video:content_loc>{escape(v["content"])}</video:content_loc>' if 'content' in v \
                else f'<video:player_loc>{escape(v["player"])}</video:player_loc>'
            video_rows.append(f'  <url><loc>{escape(url)}</loc><video:video>'
                              f'<video:thumbnail_loc>{escape(v["thumb"])}</video:thumbnail_loc>'
                              f'<video:title>{escape(v["title"])}</video:title>'
                              f'<video:description>{escape(v["description"])}</video:description>{loc}'
                              '<video:family_friendly>yes</video:family_friendly></video:video></url>')
    head = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:%s="%s">\n'
    return {
        'sitemap-images.xml': (head % ('image', IMG_NS)) + '\n'.join(image_rows) + '\n</urlset>\n',
        'sitemap-video.xml': (head % ('video', VID_NS)) + '\n'.join(video_rows) + '\n</urlset>\n',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = render(ROOT)
    stale = [name for name, text in outputs.items()
             if not (ROOT / name).is_file() or (ROOT / name).read_text() != text]
    if args.check:
        if stale:
            print('stale: ' + ', '.join(stale) + ' - run python3 scripts/build-media-sitemaps.py')
            return 1
        print('Media sitemaps are current.')
        return 0
    for name, text in outputs.items():
        (ROOT / name).write_text(text)
        print(f'{name}: {text.count("<url>")} url entries')
    return 0


if __name__ == '__main__':
    sys.exit(main())
