"""English-master home rendering rejects stale or incomplete translations."""
import copy
import json
from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.home_mirror import render_home

class HomeMirrorTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT/'locales/registry.json').read_text())
        self.copy = json.loads((ROOT/'locales/en/home-copy.json').read_text())

    def test_main_structure_and_asset_paths_preserved(self):
        # English copy is an explicit test fixture, never a published locale.
        rendered = BeautifulSoup(render_home(ROOT, self.registry, 'de', self.copy), 'html.parser')
        source = BeautifulSoup((ROOT/'index.html').read_text(), 'html.parser')
        def structure(node):
            return [(n.name, n.get('class'), n.get('id')) for n in node.find_all()]
        self.assertEqual(structure(source.main), structure(rendered.main))
        self.assertEqual(rendered.html['lang'], 'de')
        self.assertEqual(rendered.select_one('link[rel=canonical]')['href'], 'https://marsharbel.com/de/')
        self.assertEqual(rendered.select_one('video')['data-src-mp4'], '/media/hero/home-hero-full.mp4?v=1')
        self.assertIn('/home.css', rendered.select_one('link[rel=stylesheet]')['href'])

    def test_missing_key_fails(self):
        self.copy.pop(next(iter(self.copy)))
        with self.assertRaisesRegex(ValueError, 'missing/extra'): render_home(ROOT, self.registry, 'de', self.copy)

    def test_html_and_placeholder_drift_fail(self):
        key='home.runtime.monthly.next'
        self.copy[key]='Bad markup <b>text</b>'
        with self.assertRaisesRegex(ValueError, 'unsafe'):render_home(ROOT,self.registry,'de',self.copy)
        self.copy[key]='No month parameter'
        with self.assertRaisesRegex(ValueError, 'placeholders'):render_home(ROOT,self.registry,'de',self.copy)

if __name__ == '__main__': unittest.main()
