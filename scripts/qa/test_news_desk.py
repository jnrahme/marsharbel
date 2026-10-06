import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('news_desk', ROOT/'scripts/build_news_desk.py')
news_desk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(news_desk)

class NewsDeskTests(unittest.TestCase):
    def test_movie_opening_status(self):
        import json
        catalog=json.loads((ROOT/'locales/en/movie-status-copy.json').read_text())
        source=(ROOT/'src/pages/saint-charbel-movie.html').read_text()
        from html import escape
        served=(ROOT/'saint-charbel-movie.html').read_text()
        for key,value in catalog['copy'].items():
            self.assertIn('{{copy movie-status '+key+'}}',source)
            self.assertIn(escape(value,quote=True),served)
        self.assertNotIn('was released in Lebanon in 2026',served)
        self.assertIn('id="mar-charbel-october-opening-2026-10"',(ROOT/'news.html').read_text())

    def test_ministers_visit_card(self):
        text = (ROOT/'news.html').read_text()
        self.assertEqual(text.count('id="religious-trails-minister-visit-2026-10"'), 1)
        self.assertIn('not a new agreement or a trail opening', text)

    def test_douaihy_hoayek_altar_card(self):
        text = (ROOT/'news.html').read_text()
        self.assertEqual(text.count('id="douaihy-hoayek-altar-consecration-2026-09"'), 1)
        self.assertIn('Both remain Blessed, not canonized saints', text)

    def test_gallery_series_news(self):
        text = (ROOT/'news.html').read_text()
        self.assertEqual(text.count('id="gallery-ai-transformation-series-2026-10"'), 1)
        self.assertIn('dark beard with a grey center streak', text)
        self.assertIn('not independent verification', text)
        self.assertIn('href="./gallery"', text)

    def test_generated_output_fresh(self):
        for path, text in news_desk.outputs().items():
            self.assertEqual(path.read_text(), text, str(path))
    def test_news_has_sourced_cards(self):
        text = (ROOT/'news.html').read_text()
        for ident in ['el-paso-lebanese-festival-2026-10','emmitsburg-shrine-anniversary-2026-09','kfifan-patron-relics-2026-10']:
            self.assertEqual(text.count('id="'+ident+'"'), 1)
            if ident.startswith(('emmitsburg', 'kfifan')):
                self.assertIn('./news#'+ident, (ROOT/'index.html').read_text())
        self.assertIn('https://stsharbelelpaso.org/',text)
        self.assertIn('https://www.familyofsaintsharbel.org/our-news',text)
    def test_static_editorial_news(self):
        text = (ROOT/'index.html').read_text()
        self.assertEqual(text.count('class="home-news-lead"'), 1)
        self.assertEqual(text.count('class="home-news-row"'), 5)
        self.assertNotIn('news-rotator.js', text)
        self.assertIn('class="home-news-lead" href="./news#byblos-annaya-prayer-walk-2026-09"', text)
        self.assertNotIn('el-paso-lebanese-festival-2026-10', text)

    def test_unsupported_movie_headline_removed(self):
        self.assertNotIn('rolls out worldwide', (ROOT/'index.html').read_text())
