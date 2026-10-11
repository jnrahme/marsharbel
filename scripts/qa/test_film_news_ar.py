"""Independent executor runs these against the EN feature candidate."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('film_news_ar',ROOT/'scripts/build_film_news_ar.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class FilmNewsArabicTests(unittest.TestCase):
    def test_only_one_feature_and_same_shared_links(self):
        template,keys=module.feature_template(ROOT)
        path,text=module.render_source(ROOT)
        ar=BeautifulSoup(text,'html.parser'); en=BeautifulSoup(template,'html.parser')
        self.assertEqual(ar.html['dir'],'rtl');self.assertEqual(ar.html['lang'],'ar')
        self.assertEqual(len(ar.select('main article')),1);self.assertEqual(len(ar.select('h1')),1)
        self.assertEqual([a['href'] for a in en.select('a[href]')],[a['href'] for a in ar.select('main article a[href]')])
        self.assertEqual(en.select_one('iframe')['src'],ar.select_one('iframe')['src'])
        self.assertNotIn('gallery-ai-transformation',text)
        self.assertIn(module.CHARITY_SOURCE,text)
        self.assertIsNotNone(ar.select_one('#sc-share-labels'))
        self.assertEqual(ar.select_one('link[rel=canonical]')['href'],'https://marsharbel.com'+module.ROUTE)
        self.assertEqual({a['hreflang'] for a in ar.select('link[hreflang]')},{'ar'})
    def test_final_built_feature_preserves_raw_subtree(self):
        path,raw=module.render_source(ROOT)
        final=BeautifulSoup(path.read_text(),'html.parser')
        self.assertEqual(str(final.select_one('main article')),str(BeautifulSoup(raw,'html.parser').article))
        self.assertEqual(final.html['dir'],'rtl')
        self.assertEqual(final.select_one('link[rel=canonical]')['href'],'https://marsharbel.com'+module.ROUTE)
    def test_exact_single_inline_link_rule(self):
        _,text=module.render_source(ROOT)
        page=BeautifulSoup(text,'html.parser')
        styles=page.select('head style')
        self.assertEqual(len(styles),1)
        self.assertEqual(styles[0].get_text(),'.film-news-article p a{text-decoration:underline;text-underline-offset:.15em}')
        served=BeautifulSoup((ROOT/'ar/charbel-film-premiere.html').read_text(),'html.parser')
        self.assertEqual([s.get_text() for s in served.select('head style')],[styles[0].get_text()])
    def test_ar_home_lead_reaches_feature_only(self):
        home=BeautifulSoup((ROOT/'ar/index.html').read_text(),'html.parser')
        self.assertEqual(home.select_one('.home-news-lead--film')['href'],module.ROUTE)
    def fixture(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
        for p in ['templates/news-desk/cards.html','templates/international/page.html','locales/registry.json','locales/en/news-desk.json','locales/ar/film-premiere-copy.json','locales/ar/share.json','locales/ar/common.json','scripts/lib/jsonld.mjs']:
            dst=root/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,dst)
        return root
    def test_missing_arabic_value_refused(self):
        root=self.fixture();p=root/'locales/ar/film-premiere-copy.json';j=json.loads(p.read_text());del j['premiere.body'];p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):module.render_source(root)
    def test_duplicate_feature_refused(self):
        root=self.fixture();p=root/'templates/news-desk/cards.html';p.write_text(p.read_text()*2)
        with self.assertRaises(ValueError):module.render_source(root)
    def test_foreign_key_refused(self):
        root=self.fixture();p=root/'templates/news-desk/cards.html';p.write_text(p.read_text().replace('${premiere.body}','${opening.body}',1))
        with self.assertRaises(ValueError):module.render_source(root)
    def test_markup_value_refused(self):
        root=self.fixture();p=root/'locales/ar/film-premiere-copy.json';j=json.loads(p.read_text());j['premiere.body']='<b>bad</b>';p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):module.render_source(root)
if __name__=='__main__':unittest.main()
