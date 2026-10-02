import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('news_desk', ROOT/'scripts/build_news_desk.py')
news_desk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(news_desk)

class NewsDeskTests(unittest.TestCase):
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
