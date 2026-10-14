import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('news_desk', ROOT/'scripts/build_news_desk.py')
news_desk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(news_desk)

class NewsDeskTests(unittest.TestCase):
    def test_el_paso_is_archived_not_upcoming(self):
        text=(ROOT/'news.html').read_text()
        self.assertNotIn('Upcoming parish festival',text)
        self.assertNotIn('El Paso will host',text)
        self.assertIn('Archived parish announcement',text)
        self.assertIn('not a post-event report',text)

    def test_movie_opening_status(self):
        import json
        catalog=json.loads((ROOT/'locales/en/movie-status-copy.json').read_text())
        source=(ROOT/'src/pages/saint-charbel-movie.html').read_text()
        from html import unescape
        served=(ROOT/'saint-charbel-movie.html').read_text()
        for key,value in catalog['copy'].items():
            self.assertIn('{{copy movie-status '+key+'}}',source)
            self.assertIn(value,unescape(served))
        self.assertNotIn('was released in Lebanon in 2026',served)
        self.assertIn('id="mar-charbel-october-opening-2026-10"',(ROOT/'news.html').read_text())

    def test_premiere_feature_is_sourced_and_not_a_worldwide_release(self):
        news=(ROOT/'news.html').read_text()
        movie=(ROOT/'saint-charbel-movie.html').read_text()
        self.assertEqual(news.count('id="charbel-premiere-release-2026-10"'),1)
        # /news carries a compact row; sources stay in its credits list and the
        # full claims live in the standalone article (PR 2 decoupling).
        self.assertIn('https://www.nidaalwatan.com/article/401403',news)
        self.assertIn('https://www.lorientlejour.com/article/1550058/la-projection-du-film-charbel-au-profit-de-anta-akhi.html',news)
        from bs4 import BeautifulSoup
        article=BeautifulSoup((ROOT/'charbel-film-premiere.html').read_text(),'html.parser').select_one('main > article.film-news-article')
        self.assertIsNotNone(article)
        article_text=article.get_text(' ')
        self.assertIn('no screening sessions scheduled',article_text)
        self.assertIn('International release dates, streaming distribution and English-language availability remain unconfirmed',article_text)
        self.assertIn('no screening sessions are scheduled yet',news)
        self.assertNotIn('movie-poster-hero.webp',movie)

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
        self.assertIn('artistic renditions, not photographs', text)
        self.assertIn('href="./gallery"', text)
        # The long caveats live on the gallery page the row links to.
        gallery=(ROOT/'gallery.html').read_text()
        self.assertIn('dark beard with a grey center streak', gallery)
        self.assertIn('not independent verification', gallery)

    def test_generated_output_fresh(self):
        for path, text in news_desk.outputs().items():
            self.assertEqual(path.read_text(), text, str(path))
    def test_news_has_sourced_cards(self):
        text = (ROOT/'news.html').read_text()
        for ident in ['el-paso-lebanese-festival-2026-10','emmitsburg-shrine-anniversary-2026-09','kfifan-patron-relics-2026-10']:
            self.assertEqual(text.count('id="'+ident+'"'), 1)
            if ident.startswith('emmitsburg'):
                self.assertIn('./news#'+ident, (ROOT/'index.html').read_text())
        index = (ROOT/'index.html').read_text()
        for ident in ['pope-leo-gemelli-prayer-2026-10-13','pope-leo-rosary-announcement-2026-10-13']:
            self.assertIn('./news#'+ident, index)
        self.assertIn('https://stsharbelelpaso.org/',text)
        self.assertIn('https://www.familyofsaintsharbel.org/our-news',text)
    def test_static_editorial_news(self):
        text = (ROOT/'index.html').read_text()
        self.assertEqual(text.count('class="home-news-lead home-news-lead--film"'), 1)
        self.assertEqual(text.count('class="home-news-row"'), 5)
        self.assertNotIn('news-rotator.js', text)
        self.assertIn('class="home-news-lead home-news-lead--film" href="./charbel-film-premiere"', text)
        self.assertNotIn('el-paso-lebanese-festival-2026-10', text)

    def test_papal_rows_en_ar_parity(self):
        from bs4 import BeautifulSoup
        expected = {
            'pope-leo-gemelli-prayer-2026-10-13': ('chip-update', 'Update'),
            'pope-leo-rosary-announcement-2026-10-13': ('chip-event', 'Prayer'),
        }
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        for rid, (chip_class, chip_text) in expected.items():
            self.assertEqual(en_text.count(f'id="{rid}"'), 1)
            self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
            en_row = en.select_one(f'article#{rid}')
            ar_row = ar.select_one(f'article#{rid}')
            self.assertIsNotNone(en_row)
            self.assertIsNotNone(ar_row)
            en_links = [a.get('href') for a in en_row.select('a')]
            ar_links = [a.get('href') for a in ar_row.select('a')]
            # Row hrefs stay on Vatican News only, and AR carries the same hrefs as EN.
            self.assertTrue(en_links)
            for href in en_links + ar_links:
                self.assertIn('https://www.vaticannews.va/', href)
            self.assertEqual(en_links, ar_links)
            # Same chip class on both; EN chip text matches the ruling vocabulary.
            self.assertIn(chip_class, en_row.select_one('.chip').get('class'))
            self.assertIn(chip_class, ar_row.select_one('.chip').get('class'))
            self.assertEqual(en_row.select_one('.chip').get_text(strip=True), chip_text)
            # Each row href is cited in the credits list on both pages.
            for soup in (en, ar):
                credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
                for href in en_links:
                    self.assertIn(href, credit_hrefs)

    def test_unsupported_movie_headline_removed(self):
        self.assertNotIn('rolls out worldwide', (ROOT/'index.html').read_text())
