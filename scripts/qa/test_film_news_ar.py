"""Independent executor runs these against the EN feature candidate."""
import importlib.util
import json
import shutil
import tempfile
import unittest
import sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
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
    def test_standalone_and_international_final_bytes_match(self):
        spec=importlib.util.spec_from_file_location('film_i18n_compare',ROOT/'scripts/build-international.py')
        pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)
        path,text=module.output(ROOT)
        self.assertEqual(text,pipeline.outputs(ROOT)[path])
        raw_path,raw_text=module.render_source(ROOT)
        self.assertEqual(path,raw_path)
        self.assertNotEqual(text,raw_text)
        parsed=BeautifulSoup(text,'html.parser')
        self.assertEqual(len(parsed.select('#sc-runtime-labels')),1)
        self.assertEqual(len(parsed.select('script[src="/same-page-switcher.js"]')),1)
        self.assertEqual(len(parsed.select('script[src*="translate.js"]')),1)
        self.assertIn('scripts/build_film_news_ar.py',text)
    def fixture(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
        for p in ['templates/news-desk/cards.html','templates/international/page.html','locales/registry.json','locales/en/news-desk.json','locales/ar/film-premiere-copy.json','locales/ar/share.json','locales/ar/common.json']:
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
