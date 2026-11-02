#!/usr/bin/env python3
"""Pin the image and video sitemaps: derived from sitemap.xml, served assets only."""
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://marsharbel.com'
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9',
      'i': 'http://www.google.com/schemas/sitemap-image/1.1',
      'v': 'http://www.google.com/schemas/sitemap-video/1.1'}


def locs(name):
    return [(u.find('s:loc', NS).text, u) for u in ET.parse(ROOT / name).getroot().findall('s:url', NS)]


class MediaSitemaps(unittest.TestCase):
    def test_generated_files_are_current(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/build-media-sitemaps.py'), '--check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pages_come_from_the_main_sitemap(self):
        main = set(re.findall(r'<loc>([^<]+)</loc>', (ROOT / 'sitemap.xml').read_text()))
        for name in ('sitemap-images.xml', 'sitemap-video.xml'):
            for page, _ in locs(name):
                self.assertIn(page, main, f'{name}: {page}')

    def test_images_exist_and_stay_on_site(self):
        for page, node in locs('sitemap-images.xml'):
            images = node.findall('i:image/i:loc', NS)
            self.assertTrue(images, page)
            self.assertLessEqual(len(images), 1000)
            for image in images:
                parts = urlsplit(image.text)
                self.assertEqual(f'{parts.scheme}://{parts.netloc}', SITE, image.text)
                self.assertTrue((ROOT / parts.path.lstrip('/')).is_file(), image.text)

    def test_video_entries_have_required_fields(self):
        for page, node in locs('sitemap-video.xml'):
            video = node.find('v:video', NS)
            for tag in ('thumbnail_loc', 'title', 'description'):
                self.assertTrue((video.findtext(f'v:{tag}', namespaces=NS) or '').strip(), f'{page} {tag}')
            self.assertTrue(video.find('v:content_loc', NS) is not None or video.find('v:player_loc', NS) is not None, page)
            self.assertLessEqual(len(video.findtext('v:title', namespaces=NS)), 100, page)

    def test_robots_declares_both(self):
        robots = (ROOT / 'robots.txt').read_text()
        for name in ('sitemap-images.xml', 'sitemap-video.xml'):
            self.assertIn(f'Sitemap: {SITE}/{name}', robots)


if __name__ == '__main__':
    unittest.main()
