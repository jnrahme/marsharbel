"""Independent HTML-parser checks for search excerpts and sitemap bootstrap coverage."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]

class Head(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.description = ''
        self.scripts = []
        self.css = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('name', '').lower() == 'description':
            self.description = a.get('content', '')
        if tag == 'script': self.scripts.append(a.get('src', '').split('?')[0])
        if tag == 'link': self.css.append(a.get('href', '').split('?')[0])

def source(url):
    p = urlparse(url).path
    for f in [ROOT / (p.lstrip('/') + '.html'), ROOT / p.lstrip('/') / 'index.html']:
        if f.is_file(): return f
    raise AssertionError(f'No source for {url}')

class SearchSourceContract(unittest.TestCase):
    def test_every_sitemap_page_has_index_row_excerpt_and_bootstrap(self):
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [urlparse(e.text).path for e in ET.parse(ROOT / 'sitemap.xml').findall('.//s:loc', ns)]
        rows = [r for f in (ROOT / 'search-index').glob('*.json') if f.name != 'labels.json' for r in json.loads(f.read_text())]
        self.assertEqual(len(rows), len(urls))
        self.assertEqual({r[0] for r in rows}, set(urls))
        self.assertGreaterEqual(len(rows), 410)
        for row in rows:
            with self.subTest(url=row[0]):
                head = Head(source(row[0]).read_text())
                self.assertEqual(row[2], re.sub(r'\s+', ' ', head.description).strip())
                translate = any(s.endswith('/translate.js') or s == 'translate.js' for s in head.scripts)
                direct = {'/search-core.js', '/search.js'}.issubset(head.scripts) and '/search.css' in head.css
                self.assertTrue(translate or direct, f'{row[0]} has no search bootstrap')
        # unittest subtests above retain each failing URL in the result.

if __name__ == '__main__': unittest.main()
