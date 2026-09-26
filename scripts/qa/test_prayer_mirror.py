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
from i18n.mirror import render_pair, render_mirrors


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

    def test_spanish_mirror_uses_same_shape_and_complete_rosary(self):
        pages = render_mirrors(ROOT)
        master = pages[ROOT / 'saint-charbel-prayers.html']
        spanish = pages[ROOT / 'es/oraciones.html']
        self.assertEqual(Shape(spanish).nodes, Shape(master).nodes)
        self.assertEqual(Shape(spanish).images, Shape(master).images)
        self.assertIn('lang="es" dir="ltr"', spanish)
        self.assertIn('href="https://marsharbel.com/es/oraciones"', spanish)
        for prayer in ('creed', 'ourFather', 'hailMary', 'glory', 'fatima', 'queen', 'closing'):
            text = read_json(ROOT / 'locales/es/mirrors/prayers.json')[f'rosary.{prayer}Prayer']
            self.assertIn(text, spanish)

    def test_portuguese_mirror_uses_same_shape_and_complete_rosary(self):
        pages = render_mirrors(ROOT)
        master = pages[ROOT / 'saint-charbel-prayers.html']
        portuguese = pages[ROOT / 'pt/oracoes.html']
        self.assertEqual(Shape(portuguese).nodes, Shape(master).nodes)
        self.assertEqual(Shape(portuguese).images, Shape(master).images)
        self.assertIn('lang="pt" dir="ltr"', portuguese)
        self.assertIn('href="https://marsharbel.com/pt/oracoes"', portuguese)
        for prayer in ('creed', 'ourFather', 'hailMary', 'glory', 'fatima', 'queen', 'closing'):
            text = read_json(ROOT / 'locales/pt/mirrors/prayers.json')[f'rosary.{prayer}Prayer']
            self.assertIn(text, portuguese)

    def test_italian_mirror_uses_same_shape_and_complete_rosary(self):
        pages = render_mirrors(ROOT)
        master = pages[ROOT / 'saint-charbel-prayers.html']
        italian = pages[ROOT / 'it/preghiere.html']
        self.assertEqual(Shape(italian).nodes, Shape(master).nodes)
        self.assertEqual(Shape(italian).images, Shape(master).images)
        self.assertIn('lang="it" dir="ltr"', italian)
        self.assertIn('href="https://marsharbel.com/it/preghiere"', italian)
        for prayer in ('creed', 'ourFather', 'hailMary', 'glory', 'fatima', 'queen', 'closing'):
            text = read_json(ROOT / 'locales/it/mirrors/prayers.json')[f'rosary.{prayer}Prayer']
            self.assertIn(text, italian)

    def test_german_mirror_uses_same_shape_and_complete_rosary(self):
        pages = render_mirrors(ROOT)
        master = pages[ROOT / 'saint-charbel-prayers.html']
        german = pages[ROOT / 'de/gebete.html']
        self.assertEqual(Shape(german).nodes, Shape(master).nodes)
        self.assertEqual(Shape(german).images, Shape(master).images)
        self.assertIn('lang="de" dir="ltr"', german)
        self.assertIn('href="https://marsharbel.com/de/gebete"', german)
        for prayer in ('creed', 'ourFather', 'hailMary', 'glory', 'fatima', 'queen', 'closing'):
            text = read_json(ROOT / 'locales/de/mirrors/prayers.json')[f'rosary.{prayer}Prayer']
            self.assertIn(text, german)

    def test_polish_mirror_uses_same_shape_and_complete_rosary(self):
        pages = render_mirrors(ROOT)
        master = pages[ROOT / 'saint-charbel-prayers.html']
        polish = pages[ROOT / 'pl/modlitwy.html']
        self.assertEqual(Shape(polish).nodes, Shape(master).nodes)
        self.assertEqual(Shape(polish).images, Shape(master).images)
        self.assertIn('lang="pl" dir="ltr"', polish)
        self.assertIn('href="https://marsharbel.com/pl/modlitwy"', polish)
        for prayer in ('creed', 'ourFather', 'hailMary', 'glory', 'fatima', 'queen', 'closing'):
            text = read_json(ROOT / 'locales/pl/mirrors/prayers.json')[f'rosary.{prayer}Prayer']
            self.assertIn(text, polish)

    def test_french_mirror_uses_same_sections_cards_photo_and_canonical(self):
        pages=render_mirrors(ROOT)
        master=pages[ROOT/'saint-charbel-prayers.html']
        french=pages[ROOT/'fr/prieres.html']
        self.assertEqual(Shape(french).nodes, Shape(master).nodes)
        self.assertEqual(Shape(french).images, Shape(master).images)
        self.assertIn('lang="fr" dir="ltr"', french)
        self.assertIn('href="https://marsharbel.com/fr/prieres"', french)
        for prayer in ('creed','ourFather','hailMary','glory','fatima','queen','closing'):
            self.assertIn(read_json(ROOT/'locales/fr/mirrors/prayers.json')[f'rosary.{prayer}Prayer'], french)

    def test_english_static_guide_uses_master_structure_and_own_canonical(self):
        pages = render_mirrors(ROOT)
        guide = pages[ROOT/'en/prayers.html']
        master = pages[ROOT/'saint-charbel-prayers.html']
        self.assertEqual(Shape(guide).nodes, Shape(master).nodes)
        self.assertEqual(Shape(guide).images, Shape(master).images)
        self.assertIn('href="https://marsharbel.com/en/prayers"', guide)
        self.assertIn('"url": "https://marsharbel.com/en/prayers"', guide)
        self.assertNotEqual(read_json(ROOT/'locales/en/mirrors/prayers-guide.json')['title'],
                            read_json(ROOT/'locales/en/mirrors/prayers.json')['meta.title'])

    def test_generated_outputs_and_authored_arabic_are_current(self):
        from importlib.util import spec_from_file_location, module_from_spec
        spec=spec_from_file_location('intl_builder',ROOT/'scripts/build-international.py')
        builder=module_from_spec(spec);spec.loader.exec_module(builder)
        expected=builder.outputs(ROOT)
        for page in (ROOT/'ar/prayers.html', ROOT/'en/prayers.html', ROOT/'fr/prieres.html', ROOT/'es/oraciones.html', ROOT/'pt/oracoes.html', ROOT/'it/preghiere.html', ROOT/'de/gebete.html', ROOT/'pl/modlitwy.html', ROOT/'saint-charbel-prayers.html'):
            self.assertEqual(page.read_text(),expected[page])
        self.assertEqual(expected[ROOT/'ar/prayers.html'].count('hreflang="ar"'),1)

    def test_keys_and_urls_are_separated_from_page_structure(self):
        template = (ROOT / 'templates/mirrors/prayers.html').read_text()
        english = read_json(ROOT / 'locales/en/mirrors/prayers.json')
        arabic = read_json(ROOT / 'locales/ar/mirrors/prayers.json')
        self.assertEqual(english.keys(), arabic.keys())
        self.assertEqual(len(english), 133)
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
