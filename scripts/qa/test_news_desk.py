import importlib.util
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('news_desk', ROOT/'scripts/build_news_desk.py')
news_desk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(news_desk)

class NewsDeskTests(unittest.TestCase):
    def test_massabki_priority_is_maronite_and_mayor_is_paraphrased(self):
        from bs4 import BeautifulSoup
        source = 'https://maronite.org.au/news/three-brothers-become-first-maronite-laymen-to-be-canonised/'
        en = json.loads((ROOT/'locales/en/news-desk.json').read_text())
        self.assertIn('first Maronite laymen to be canonized', en['massabkiCentenary.summary'])
        self.assertNotIn('modern canonical norms', en['massabkiCentenary.summary'])
        self.assertNotIn('"a religious and national celebration', en['massabkiCentenary.summary'])
        for path in ['news.html', 'ar/news.html']:
            soup = BeautifulSoup((ROOT/path).read_text(), 'html.parser')
            self.assertIsNotNone(soup.select_one('a[href="'+source+'"]'))
        packet = json.loads((ROOT/'locales/massabki-oct25-home-translations.json').read_text())
        self.assertIn('علمانيين موارنة', packet['ar']['popeRosary.homeCredit'])
        self.assertIn('beatyfikacji braci Massabkich', packet['pl']['popeRosary.homeTitle'])
        self.assertNotIn('błogosławieństwa', packet['pl']['popeRosary.homeTitle'])

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
        self.assertIn('International release dates, streaming distribution and any English-dubbed version remain unconfirmed; VOX lists the film with Arabic audio and English subtitles',article_text)
        self.assertNotIn('English-language availability remain unconfirmed',article_text)
        self.assertIn('VOX Cinemas Lebanon lists Mar Charbel as Now Showing',news)
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

    def test_news_generator_owns_source_and_served_blocks(self):
        import re
        outputs = news_desk.outputs()
        for file, marker in [('index.html', 'news-home'), ('news.html', 'news-desk')]:
            source = ROOT/'src/pages'/file
            self.assertIn(source, outputs)
            pattern = rf'<!-- i18n-{marker}:start -->.*?<!-- i18n-{marker}:end -->'
            self.assertEqual(re.search(pattern, outputs[source], re.S).group(),
                             re.search(pattern, outputs[ROOT/file], re.S).group())

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
        for ident in ['pope-leo-assisi-cancel-2026-10-23','mary-mediterranean-harissa-2026-10-28']:
            self.assertIn('./news#'+ident, index)
        self.assertIn('https://stsharbelelpaso.org/',text)
        self.assertIn('https://www.familyofsaintsharbel.org/our-news',text)
    def test_static_editorial_news(self):
        text = (ROOT/'index.html').read_text()
        self.assertEqual(text.count('class="home-news-lead home-news-lead--film"'), 1)
        self.assertEqual(text.count('class="home-news-row"'), 5)
        # REVISION 2026-10-30: text-only almoner supporting row (no photo, rights-safe)
        self.assertEqual(text.count('class="home-news-row home-news-row--text"'), 1)
        self.assertIn('class="home-news-row home-news-row--text" href="./news#almoner-zaporizhzhia-poltava-2026-10-30"', text)
        self.assertNotIn('news-rotator.js', text)
        self.assertIn('class="home-news-lead home-news-lead--film" href="./charbel-film-premiere"', text)
        self.assertNotIn('el-paso-lebanese-festival-2026-10', text)


    def test_almoner_home_refresh_check_reproducible(self):
        # REVISION 2026-10-30 (PR #901 repair): refresh --check must be green
        # on the committed artifact. The contract carries content-derived
        # evidence only (masterSha256 + fully regenerated bindings/catalogs);
        # provenance lives in commit history, never in a stored git revision,
        # so a squash merge cannot break reproducibility.
        import subprocess, sys
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/i18n/refresh_almoner_oct30_home.py'), '--check'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-500:])

    def test_papal_rows_en_ar_parity(self):
        from bs4 import BeautifulSoup
        expected = {
            'pope-leo-assisi-cancel-2026-10-23': ('chip-update', 'Update'),
            'pope-leo-gemelli-prayer-2026-10-13': ('chip-update', 'Update'),
            'pope-leo-gemelli-discharge-2026-10-17': ('chip-update', 'Update'),
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
            # Row hrefs stay on the row's cited primary source, and AR carries the same hrefs as EN.
            domains = {
                'pope-leo-assisi-cancel-2026-10-23': 'https://www.vaticannews.va/',
                'pope-leo-gemelli-prayer-2026-10-13': 'https://www.vaticannews.va/',
                'pope-leo-gemelli-discharge-2026-10-17': 'https://www.vaticannews.va/',
                'pope-leo-rosary-announcement-2026-10-13': 'https://www.usccb.org/',
            }
            self.assertTrue(en_links)
            for href in en_links + ar_links:
                self.assertIn(domains[rid], href)
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

    def test_ddf_venite_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'ddf-venite-ad-me-2026-10-22'
        primary = 'https://www.doctrinafidei.va/'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        # Row href stays on the Dicastery announcement, and AR carries the same hrefs as EN.
        self.assertTrue(en_links)
        for href in en_links + ar_links:
            self.assertIn(primary, href)
        self.assertEqual(en_links, ar_links)
        # Same chip class on both; EN chip text matches the ruling vocabulary.
        self.assertIn('chip-announcement', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-announcement', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('.chip').get_text(strip=True), 'Announcement')
        # Considerations, not a doctrinal note, on both twins.
        self.assertIn('not a doctrinal note', en_row.get_text(' '))
        self.assertIn('ملاحظة عقائدية', ar_row.get_text(' '))
        # The row href is cited in the credits list on both pages.
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            for href in en_links:
                self.assertIn(href, credit_hrefs)


    def test_marian_meeting_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'mary-mediterranean-harissa-2026-10-28'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        url = 'https://www.vaticannews.va/en/pope/news/2026-10/pope-rediscover-in-mary-the-path-to-peace.html'
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        self.assertEqual(en_links, [url])
        self.assertEqual(en_links, ar_links)
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-28')
        # Message only, signed by Cardinal Parolin: no papal-attendance claim on either twin.
        self.assertIn('Parolin', en_row.get_text(' '))
        self.assertIn('بارولين', ar_row.get_text(' '))
        self.assertIn('Harissa', en_row.get_text(' '))
        self.assertIn('حريصا', ar_row.get_text(' '))
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            self.assertIn(url, credit_hrefs)

    def test_ukraine_ceasefire_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'ukraine-oleshky-ceasefire-2026-10-28'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        url = 'https://www.vaticannews.va/en/world/news/2026-10/pope-leo-s-appeals-help-bring-ceasefire-to-southern-ukraine.html'
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        self.assertEqual(en_links, [url])
        self.assertEqual(en_links, ar_links)
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-28')
        # Local humanitarian respite only: no nationwide-ceasefire or sole-causation claim.
        self.assertIn('Oleshky', en_row.get_text(' '))
        self.assertIn('أوليشكي', ar_row.get_text(' '))
        self.assertNotIn('nationwide', en_row.get_text(' ').lower())
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            self.assertIn(url, credit_hrefs)

    def test_acn_report_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'acn-persecuted-forgotten-2026-10-27'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        url = 'https://acninternational.org/christian-persecution-worsens-in-much-of-the-world-according-to-new-acn-report/'
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        self.assertEqual(en_links, [url])
        self.assertEqual(en_links, ar_links)
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-27')
        # Bounded finding: 55 percent of the 18 countries examined, not all countries.
        self.assertIn('18 countries examined', en_row.get_text(' '))
        self.assertIn('الثمانية عشر', ar_row.get_text(' '))
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            self.assertIn(url, credit_hrefs)

    def test_almoner_kyiv_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'almoner-kyiv-visit-2026-10-29'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        url = 'https://www.vaticannews.va/en/vatican-city/news/2026-10/pope-s-almoner-visits-ukraine-to-offer-support-to-people.html'
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        self.assertEqual(en_links, [url])
        self.assertEqual(en_links, ar_links)
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-29')
        # Bounded finding: conclusion of the multi-city mission is scheduled, not accomplished.
        self.assertIn('scheduled', en_row.get_text(' '))
        self.assertIn('من المقرر', ar_row.get_text(' '))
        # Kept distinct from the Oleshky ceasefire; no claim the visit reached Oleshky.
        self.assertIn('separate from the humanitarian ceasefire around Oleshky', en_row.get_text(' '))
        self.assertNotIn('Oleshky', en_row.select_one('h3').get_text(' '))
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            self.assertIn(url, credit_hrefs)

    def test_spain_train_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'spain-urda-train-telegram-2026-10-29'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        url = 'https://www.vaticannews.va/en/pope/news/2026-10/pope-leo-mourns-lives-lost-in-spain-train-crash.html'
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        self.assertEqual(en_links, [url])
        self.assertEqual(en_links, ar_links)
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-29')
        # Bounded finding: provisional toll, search ongoing (source silent on cause; no status asserted).
        self.assertIn('remained provisional', en_row.get_text(' '))
        self.assertNotIn('cause', en_row.get_text(' '))
        self.assertIn('مؤقتة', ar_row.get_text(' '))
        self.assertNotIn('سبب', ar_row.get_text(' '))
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            self.assertIn(url, credit_hrefs)

    def test_almoner_zaporizhzhia_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'almoner-zaporizhzhia-poltava-2026-10-30'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        url = 'https://www.vaticannews.va/en/vatican-city/news/2026-10/papal-almoner-pope-charity-ukraine-30-october-2026.html'
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        self.assertEqual(en_links, [url])
        self.assertEqual(en_links, ar_links)
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-30')
        # Bounded finding: only Zaporizhzhia and Poltava confirmed; completion not claimed.
        self.assertIn('does not confirm', en_row.get_text(' '))
        self.assertIn('Zaporizhzhia and Poltava', en_row.get_text(' '))
        self.assertNotIn('completed', en_row.get_text(' '))
        self.assertNotIn('concluded', en_row.get_text(' '))
        # Separate figures kept distinct: ~2,000 at the reported distribution, ~10,000 weekly.
        self.assertIn('2,000', en_row.get_text(' '))
        self.assertIn('10,000', en_row.get_text(' '))
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            self.assertIn(url, credit_hrefs)

    def test_pope_leo_ai_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'pope-leo-ai-address-2026-10-30'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        url = 'https://www.vaticannews.va/en/pope/news/2026-10/pope-ai-decisions-affecting-human-life-must-never-be-delegated.html'
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        self.assertEqual(en_links, [url])
        self.assertEqual(en_links, ar_links)
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-30')
        # Bounded finding: an address, not a new encyclical or binding regulation.
        self.assertIn('not a new encyclical or a binding regulation', en_row.get_text(' '))
        self.assertIn('Magnifica Humanitas', en_row.get_text(' '))
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            self.assertIn(url, credit_hrefs)

    def test_massabki_row_en_ar_parity(self):
        from bs4 import BeautifulSoup
        rid = 'massabki-centenary-aqoura-2026-10-25'
        en_text = (ROOT/'news.html').read_text()
        ar_text = (ROOT/'ar/news.html').read_text()
        self.assertEqual(en_text.count(f'id="{rid}"'), 1)
        self.assertEqual(ar_text.count(f'id="{rid}"'), 1)
        en = BeautifulSoup(en_text, 'html.parser')
        ar = BeautifulSoup(ar_text, 'html.parser')
        en_row = en.select_one(f'article#{rid}')
        ar_row = ar.select_one(f'article#{rid}')
        self.assertIsNotNone(en_row)
        self.assertIsNotNone(ar_row)
        en_links = [a.get('href') for a in en_row.select('a')]
        ar_links = [a.get('href') for a in ar_row.select('a')]
        # The row href is the cited post-event primary source, identical on both twins.
        self.assertEqual(en_links, ['https://www.elnashra.com/news/show/1806076'])
        self.assertEqual(en_links, ar_links)
        # Same chip class and ruling vocabulary on both twins.
        self.assertIn('chip-update', en_row.select_one('.chip').get('class'))
        self.assertIn('chip-update', ar_row.select_one('.chip').get('class'))
        self.assertEqual(en_row.select_one('.chip').get_text(strip=True), 'Update')
        self.assertEqual(en_row.select_one('time').get('datetime'), '2026-10-25')
        # Outcome wording stays distinct from the pre-event mayoral announcement.
        self.assertIn('had announced', en_row.get_text(' '))
        # All three cited sources appear in the credits list on both pages.
        for soup in (en, ar):
            credit_hrefs = [a.get('href') for a in soup.select('.news-credits-list a')]
            for href in ['https://www.elnashra.com/news/show/1806076',
                         'https://noursat.tv/6371/',
                         'https://jbeiltoday.com/news/170288']:
                self.assertIn(href, credit_hrefs)

    def test_unsupported_movie_headline_removed(self):
        self.assertNotIn('rolls out worldwide', (ROOT/'index.html').read_text())



class AlmonerRefreshSandboxTests(unittest.TestCase):
    """PR #901 regression: the almoner home refresh --check must be
    reproducible with no git metadata present (squash merge, shallow clone,
    exported tarball) and must still fail on real content drift."""
    SCRIPT = 'scripts/i18n/refresh_almoner_oct30_home.py'

    @classmethod
    def setUpClass(cls):
        import shutil, tempfile
        cls.tmp = tempfile.TemporaryDirectory(prefix='almoner-check-')
        cls.sandbox = Path(cls.tmp.name)
        shutil.copytree(ROOT / 'scripts' / 'i18n', cls.sandbox / 'scripts' / 'i18n')
        shutil.copytree(ROOT / 'locales', cls.sandbox / 'locales')
        shutil.copy2(ROOT / 'index.html', cls.sandbox / 'index.html')
        # Deliberately no .git: a stored sourceRevision pin would fail here.

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_check(self):
        import subprocess, sys
        return subprocess.run([sys.executable, self.SCRIPT, '--check'],
                              cwd=self.sandbox, capture_output=True, text=True)

    def reset(self, rel):
        import shutil
        shutil.copy2(ROOT / rel, self.sandbox / rel)

    def assert_drift_detected(self, rel, mutate, signatures=('Needs refresh',)):
        # Drift must fail the check. Contract-file drift surfaces as a soft
        # 'Needs refresh' diff; drift that breaks a binding guard surfaces as
        # a hard validation error. Both are detection; accept the listed
        # signatures but require a non-zero exit.
        self.reset(rel)
        try:
            mutate(self.sandbox / rel)
            r = self.run_check()
            out = r.stdout + r.stderr
            self.assertNotEqual(r.returncode, 0, out[-500:])
            self.assertTrue(any(s in out for s in signatures), out[-500:])
        finally:
            self.reset(rel)

    def test_contract_carries_no_git_revision_pin(self):
        contract = json.loads((ROOT / 'locales/en/home-bindings.json').read_text())
        self.assertNotIn('sourceRevision', contract)

    def test_check_reproducible_without_git_metadata(self):
        first = self.run_check()
        self.assertEqual(first.returncode, 0, (first.stdout + first.stderr)[-500:])
        second = self.run_check()
        self.assertEqual(second.returncode, 0, (second.stdout + second.stderr)[-500:])

    def test_check_fails_on_catalog_value_drift(self):
        def mutate(path):
            data = json.loads(path.read_text())
            key = sorted(data)[0]
            data[key] = data[key] + ' DRIFT'
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        self.assert_drift_detected('locales/en/home-copy.json', mutate)

    def test_check_fails_on_binding_source_drift(self):
        def mutate(path):
            data = json.loads(path.read_text())
            data['bindings'][0]['source'] = data['bindings'][0]['source'] + 'x'
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        self.assert_drift_detected('locales/en/home-bindings.json', mutate,
                                   ('Unrelated source drift', 'Needs refresh'))

    def test_check_fails_on_binding_selector_drift(self):
        def mutate(path):
            data = json.loads(path.read_text())
            # Valid CSS that matches no node: exercises the selector gate.
            data['bindings'][0]['selector'] = data['bindings'][0]['selector'] + ' > spanx'
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        self.assert_drift_detected('locales/en/home-bindings.json', mutate,
                                   ('Unrelated binding selector changed', 'Needs refresh'))

    def test_check_fails_on_master_byte_drift(self):
        def mutate(path):
            raw = path.read_bytes()
            assert raw.count(b'St Charbel') >= 1
            path.write_bytes(raw.replace(b'St Charbel', b'St Charbel!', 1))
        self.assert_drift_detected('index.html', mutate,
                                   ('drift', 'Needs refresh'))


class NewsMetadataTests(unittest.TestCase):
    # The desk's latest reviewed content revision is the October 30 almoner-Zaporizhzhia/Poltava follow-up and AI-address row additions (intake October 30; integrated October 30).
    REVISION = '2026-10-30'

    def assert_news_metadata(self, html, lastmod):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        page = next(json.loads(n.string) for n in soup.select('script[type="application/ld+json"]')
                    if json.loads(n.string).get('@type') == 'WebPage')
        self.assertEqual(page['dateModified'], self.REVISION)
        self.assertEqual(lastmod, self.REVISION)
        self.assertEqual(page['mainEntity']['headline'], soup.h1.get_text(' ', strip=True))
        self.assertEqual(page['mainEntity']['datePublished'], '2026-09-20')

    def test_en_ar_metadata_matches_reviewed_revision_and_visible_headline(self):
        import xml.etree.ElementTree as ET
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        dates = {n.find('s:loc', ns).text: n.find('s:lastmod', ns).text
                 for n in ET.parse(ROOT/'sitemap.xml').getroot()}
        for file, url in [('news.html', 'https://marsharbel.com/news'),
                          ('ar/news.html', 'https://marsharbel.com/ar/news')]:
            with self.subTest(file=file):
                self.assert_news_metadata((ROOT/file).read_text(), dates[url])

    def test_old_webpage_date_is_rejected(self):
        html = (ROOT/'news.html').read_text().replace('"dateModified": "2026-10-30"',
                                                    '"dateModified": "2026-10-10"')
        with self.assertRaises(AssertionError):
            self.assert_news_metadata(html, self.REVISION)

    def test_old_sitemap_date_is_rejected(self):
        with self.assertRaises(AssertionError):
            self.assert_news_metadata((ROOT/'news.html').read_text(), '2026-10-15')

    def test_english_headline_on_arabic_page_is_rejected(self):
        html = (ROOT/'ar/news.html').read_text().replace('"headline": "مار شربل في الأخبار"',
                                                       '"headline": "Saint Charbel in the News"')
        with self.assertRaises(AssertionError):
            self.assert_news_metadata(html, self.REVISION)


class NewsImageRecordTests(unittest.TestCase):
    def setUp(self):
        self.records = json.loads((ROOT/'locales/en/news-image-records.json').read_text())['slots']
        self.template = (ROOT/'templates/news-desk/home.html').read_text()

    def test_records_cover_every_home_slot_and_template_renders_from_records(self):
        self.assertEqual(set(self.records), set(news_desk.SLOT_ANCHORS))
        for slot in news_desk.SLOT_ANCHORS:
            self.assertIn('${img.%s.src}' % slot, self.template)
            self.assertIn('${img.%s.width}' % slot, self.template)
            self.assertIn('${img.%s.height}' % slot, self.template)
        self.assertNotIn('src="./media/', self.template)

    def test_records_validate_against_template_anchors(self):
        news_desk.load_image_records(ROOT, self.template)

    def test_story_drift_fails_closed(self):
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT/'locales/en', tmp/'locales/en')
        self._touch_assets(tmp)
        rec = json.loads((tmp/'locales/en/news-image-records.json').read_text())
        rec['slots']['trail']['storyId'] = 'some-other-story'
        (tmp/'locales/en/news-image-records.json').write_text(json.dumps(rec))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('trail', str(ctx.exception))
        self.assertIn('story drift', str(ctx.exception))

    def _touch_assets(self, tmp):
        for slot, rec in self.records.items():
            asset = tmp / rec['image']['src']
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.touch()

    def _record_with(self, mutate):
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT/'locales/en', tmp/'locales/en')
        self._touch_assets(tmp)
        rec = json.loads((tmp/'locales/en/news-image-records.json').read_text())
        mutate(rec['slots']['premiere'])
        (tmp/'locales/en/news-image-records.json').write_text(json.dumps(rec))
        return tmp

    def _records_root(self, mutate_top=lambda rec: None):
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT/'locales/en', tmp/'locales/en')
        self._touch_assets(tmp)
        rec = json.loads((tmp/'locales/en/news-image-records.json').read_text())
        mutate_top(rec)
        (tmp/'locales/en/news-image-records.json').write_text(json.dumps(rec))
        return tmp

    def test_valid_fixture_passes(self):
        news_desk.load_image_records(self._records_root(), self.template)

    def test_schema_version_pinned(self):
        tmp = self._records_root(lambda rec: rec.update(schemaVersion=99))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('schemaVersion', str(ctx.exception))

    def test_exactly_the_six_slots(self):
        tmp = self._records_root(lambda rec: rec['slots'].pop('trail'))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('slot set', str(ctx.exception))
        tmp = self._records_root(lambda rec: rec['slots'].update(extra=rec['slots']['trail']))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('slot set', str(ctx.exception))

    def test_subject_and_context_types_required(self):
        tmp = self._records_root(lambda rec: rec['slots']['premiere'].update(subject=''))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('subject', str(ctx.exception))
        tmp = self._records_root(lambda rec: rec['slots']['premiere'].update(contextNotEvent='yes'))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('contextNotEvent', str(ctx.exception))

    def test_checked_at_must_be_a_real_date(self):
        tmp = self._records_root(lambda rec: rec['slots']['premiere']['revalidation'].update(checkedAt='soon'))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('checkedAt', str(ctx.exception))

    def test_licensed_slots_require_evidence_urls(self):
        tmp = self._records_root(lambda rec: rec['slots']['popeGemelli']['license'].update(licenseUrl=''))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('licenseUrl', str(ctx.exception))
        tmp = self._records_root(lambda rec: rec['slots']['emmitsburg']['license'].update(sourceUrl=''))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('sourceUrl', str(ctx.exception))

    def test_unlicensed_status_requires_reason(self):
        tmp = self._records_root(lambda rec: rec['slots']['borik']['license'].pop('reason'))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('reason', str(ctx.exception))
        tmp = self._records_root(lambda rec: rec['slots']['borik']['license'].update(reason='  '))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('reason', str(ctx.exception))

    def test_uncertain_slots_are_not_marked_licensed(self):
        """The documented-uncertainty slot must never silently claim a verified licence."""
        self.assertNotEqual(self.records['borik']['license']['status'], 'licensed')
        self.assertIn('Charbel.jpg', self.records['borik']['license']['sourceUrl'])
        self.assertIn('photograph', self.records['borik']['subject'])

    def test_src_traversal_rejected(self):
        tmp = self._record_with(lambda slot: slot['image'].update(src='./media/../index.html'))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('escapes media', str(ctx.exception))

    def test_src_injection_charset_rejected(self):
        tmp = self._record_with(lambda slot: slot['image'].update(src='./media/test" onerror="bad.jpg'))
        with self.assertRaises(ValueError) as ctx:
            news_desk.load_image_records(tmp, self.template)
        self.assertIn('invalid characters', str(ctx.exception))

    def test_bool_and_nonpositive_dims_rejected(self):
        for bad in (True, -5, 0, '960'):
            tmp = self._record_with(lambda slot, bad=bad: slot['image'].update(width=bad))
            with self.assertRaises(ValueError, msg=repr(bad)) as ctx:
                news_desk.load_image_records(tmp, self.template)
            self.assertIn('positive integer', str(ctx.exception), repr(bad))

    def test_license_evidence_fields_and_revalidation_notes_present(self):
        for slot, rec in self.records.items():
            for field in ('author', 'spdx', 'permittedUse', 'adaptations'):
                self.assertTrue(rec['license'].get(field), '%s license.%s' % (slot, field))
            self.assertTrue(rec['revalidation']['note'], slot)

    def test_trail_swap_from_permission_gap_is_documented(self):
        """The trail slot's 2026-10-15 swap from the LLEW CC BY-SA derivative to
        the owner-granted monastery photo (owner-reported permission with a
        record gap) must stay documented, not silent."""
        trail = self.records['trail']
        self.assertEqual(trail['license']['status'], 'courtesy-permission-record-gap')
        self.assertEqual(trail['license']['spdx'], 'LicenseRef-owner-reported-permission')
        self.assertIn('saintcharbel.com', trail['license']['sourceUrl'])
        self.assertTrue(trail['image']['src'].endswith('/annaya-church-dusk-entrance.webp'))
        self.assertIn('LLEW', trail['revalidation']['note'])
        self.assertIn('2026-10-15', trail['revalidation']['note'])

    def test_home_img_alts_match_refresh_catalog(self):
        """Alt attributes must equal the refresh_pope_home_news.py EN catalog so
        the refresh script and the records renderer never diverge."""
        import re
        refresh = (ROOT/'scripts/i18n/refresh_pope_home_news.py').read_text()
        index = (ROOT/'index.html').read_text()
        block = index.split('i18n-news-home')[1].split('i18n-news-home')[0]
        for alt in re.findall(r'alt="([^"]+)"', block):
            if 'Gemelli' in alt or 'Rosary' in alt:
                self.assertIn(alt.replace('&amp;', '&'), refresh.replace('&amp;', '&'))


if __name__ == '__main__':
    unittest.main()
