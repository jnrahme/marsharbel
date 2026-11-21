import json,sys,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from bs4 import BeautifulSoup
from i18n.feature_mirror import adapted,one
from i18n.keyed_master import apply_keyed_master

class FilmFreshnessNovember11(unittest.TestCase):
    def test_every_premiere_has_dated_status_not_upcoming_opening(self):
        pack=json.loads((ROOT/'locales/film-freshness-nov11-translations.json').read_text())
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        cfg=registry['pageMirrors']['film-premiere-master']
        for code,route in {'en':cfg['english'],**cfg['routes']}.items():
            with self.subTest(locale=code):
                soup=BeautifulSoup((ROOT/(route.strip('/')+'.html')).read_text(),'html.parser')
                _,keyed,copy=apply_keyed_master(ROOT,'film-premiere-master',code)
                self.assertEqual(str(one(soup,'main > article.film-news-article')),str(one(keyed,'main > article.film-news-article')))
                self.assertEqual(soup.select_one('article span.tag').get_text(),pack[code]['date'])
                self.assertIn(pack[code]['release'],soup.get_text())
                self.assertTrue(copy['premiere.release'].startswith(pack[code]['historicalRelease']+' '))
                if code=='de':
                    self.assertIn('am 9. Oktober unter der Schirmherrschaft',copy['premiere.release'])
                    self.assertIn('ab dem 22. Oktober. Verfügbarkeit',copy['premiere.release'])
                if code!='en':self.assertEqual(soup.select_one('meta[name=description]')['content'],pack[code]['release'])
    def test_home_premiere_text_and_locale_destination_match(self):
        pack=json.loads((ROOT/'locales/film-freshness-nov11-translations.json').read_text())
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        for code,locale in registry['locales'].items():
            home=locale.get('home')
            if not home:continue
            with self.subTest(locale=code):
                file='index.html' if code=='en' else code+'/index.html'
                soup=BeautifulSoup((ROOT/file).read_text(),'html.parser');lead=soup.select_one('a.home-news-lead--film')
                self.assertIn(pack[code]['homeDek'],lead.get_text())
                self.assertIn(pack[code]['openingValue'],lead.get_text())
                from urllib.parse import urljoin
                self.assertEqual(urljoin('https://marsharbel.com'+home,lead['href']),'https://marsharbel.com'+('' if code=='en' else '/'+code)+'/charbel-film-premiere')
    def test_article_original_publication_preserved_modification_explicit(self):
        soup=BeautifulSoup((ROOT/'charbel-film-premiere.html').read_text(),'html.parser')
        schemas=[json.loads(n.string) for n in soup.select('script[type="application/ld+json"]')]
        article=next(s['mainEntity'] for s in schemas if isinstance(s,dict) and isinstance(s.get('mainEntity'),dict) and s['mainEntity'].get('@type')=='Article')
        self.assertEqual(article['datePublished'],'2026-10-11')
        # Serializer's modification is intentionally on the enclosing WebPage.
        webpage=next(s for s in schemas if isinstance(s,dict) and s.get('mainEntity')==article)
        self.assertEqual(webpage['dateModified'],'2026-11-11')
        self.assertIn('Checked November 11',soup.select_one('meta[name=description]')['content'])

if __name__=='__main__':unittest.main()
