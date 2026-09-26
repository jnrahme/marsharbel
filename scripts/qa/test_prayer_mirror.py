"""Guard the Arabic prayers pilot against a shortened or stale translation."""
import json
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.catalog import read_json
from i18n.mirror import render_pair


class Shape(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.path = []
        self.nodes = []
        self.images = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.path.append(tag)
        if 'main' in self.path and tag not in ('script', 'style'):
            self.nodes.append((tag, tuple(attrs.get('class', '').split()), attrs.get('width'), attrs.get('height')))
            if tag == 'img':
                self.images.append(attrs['src'])
            if tag == 'a':
                self.links.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag in self.path:
            self.path = self.path[:len(self.path)-self.path[::-1].index(tag)-1]


class PrayerMirrorTests(unittest.TestCase):
    def test_rendered_mirrors_match_structure_and_sources(self):
        pages = render_pair(ROOT)
        en = pages[ROOT / 'saint-charbel-prayers.html']
        ar = pages[ROOT / 'ar/prayers.html']
        self.assertEqual(Shape(en).nodes, Shape(ar).nodes)
        self.assertEqual(Shape(en).images, Shape(ar).images)
        # The English master should not drift outside its keyed source.
        original = (ROOT / 'saint-charbel-prayers.html').read_text()
        self.assertEqual(Shape(original).nodes, Shape(ar).nodes)
        self.assertEqual(len(Shape(ar).images), 1)
        self.assertEqual(ar.count('card prayer-card'), 14)
        self.assertEqual(ar.count('<section class="section">'), 6)
        self.assertIn('dir="rtl"', ar)
        self.assertIn('lang="ar"', ar)
        for prayer in ('creed', 'ourFather', 'hailMary', 'glory', 'fatima', 'queen', 'closing'):
            self.assertIn(read_json(ROOT / 'locales/ar/mirrors/prayers.json')[f'rosary.{prayer}Prayer'], ar)
        self.assertNotIn('https://marsharbel.com/ar/prayers"', en.split('<link rel="canonical"')[1].split('\n')[0])
        for page in (en, ar):
            self.assertNotIn('{{', page)
            self.assertEqual(page.count('id="sc-language-select"'), 0)  # existing control is mounted by translate.js
            self.assertEqual(page.count('class="lang-switcher-slot"'), 1)
            self.assertEqual(page.count('src="/translate.js'), 1)

    def test_generated_outputs_and_authored_arabic_are_current(self):
        from importlib.util import spec_from_file_location, module_from_spec
        spec=spec_from_file_location('intl_builder',ROOT/'scripts/build-international.py')
        builder=module_from_spec(spec);spec.loader.exec_module(builder)
        expected=builder.outputs(ROOT)
        for page in (ROOT/'ar/prayers.html', ROOT/'saint-charbel-prayers.html'):
            self.assertEqual(page.read_text(),expected[page])
        self.assertEqual(expected[ROOT/'ar/prayers.html'].count('hreflang="ar"'),1)

    def test_keys_and_urls_are_separated_from_page_structure(self):
        template = (ROOT / 'templates/mirrors/prayers.html').read_text()
        english = read_json(ROOT / 'locales/en/mirrors/prayers.json')
        arabic = read_json(ROOT / 'locales/ar/mirrors/prayers.json')
        self.assertEqual(english.keys(), arabic.keys())
        self.assertEqual(len(english), 130)
        self.assertIn('href="/ar/prayers" aria-current="page"', render_pair(ROOT)[ROOT/'ar/prayers.html'])
        self.assertEqual(Shape(render_pair(ROOT)[ROOT/'ar/prayers.html']).links.count('/ar/novena'), 1)
        self.assertIn('data-authored-mirror="prayers"', template)

    def test_missing_or_unescaped_catalog_slots_fail(self):
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            shutil.copytree(ROOT/'templates/mirrors',root/'templates/mirrors')
            shutil.copytree(ROOT/'locales',root/'locales')
            catalog=root/'locales/ar/mirrors/prayers.json'
            data=read_json(catalog);data.pop('rosary.creedPrayer')
            catalog.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'slot mismatch'):
                render_pair(root)
            data['rosary.creedPrayer']='<script>alert(1)</script>'
            catalog.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'HTML belongs'):
                render_pair(root)

if __name__ == '__main__':unittest.main()
