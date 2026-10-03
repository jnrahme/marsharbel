"""English/Arabic Chaplet parity and authored copy guards."""
import json
from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.chaplet_mirror import render_chaplet
from i18n.tour_nav import tour_nav
from i18n.travel_components import travel_frame
from i18n.catalog import read_json
from i18n.same_page_injection import inject_control
from i18n.catalog import read_json as _read_json_fc
def fc(t):return inject_control(t,ROOT,_read_json_fc(ROOT/'locales/same-page-manifest.pending.json'),_read_json_fc(ROOT/'locales/same-page-copy.json'))
from i18n.catalog import read_json


class ChapletMirrorTests(unittest.TestCase):
    def test_final_render_matches_master_shape(self):
        en=BeautifulSoup((ROOT/'saint-charbel-chaplet.html').read_text(),'html.parser')
        ar=BeautifulSoup(render_chaplet(ROOT)[ROOT/'ar/saint-charbel-chaplet.html'],'html.parser')
        self.assertEqual(fc(travel_frame(tour_nav(str(ar),ROOT,'ar'),ROOT,'ar','/ar/saint-charbel-chaplet',read_json(ROOT/'locales/registry.json'))),(ROOT/'ar/saint-charbel-chaplet.html').read_text())
        self.assertEqual(len(en.select('main > section')),8)
        self.assertEqual([tag.name for tag in en.select('main *')],[tag.name for tag in ar.select('main *')])
        self.assertEqual(len(ar.select('main .grid-2 article')),6)
        self.assertEqual([img['src'].removeprefix('.') for img in en.select('main img')],[img['src'] for img in ar.select('main img')])
        self.assertEqual([a['href'] for a in en.select('main .section:nth-of-type(8) a')],
                         [a['href'] for a in ar.select('main .section:nth-of-type(8) a')])
        self.assertEqual(ar.html['dir'],'rtl');self.assertEqual(ar.html['lang'],'ar')
        self.assertEqual({link['hreflang']:link['href'] for link in ar.select('link[rel=alternate][hreflang]')},
                         {'x-default':'https://marsharbel.com/saint-charbel-chaplet',
                          'en':'https://marsharbel.com/saint-charbel-chaplet',
                          'ar':'https://marsharbel.com/ar/saint-charbel-chaplet'})
        schemas=[json.loads(x.string) for x in ar.select('script[type="application/ld+json"]')]
        self.assertEqual(len(schemas[1]['mainEntity']),5)
        copy=read_json(ROOT/'locales/ar/chaplet.json')
        for i,item in enumerate(schemas[1]['mainEntity'],1):
            self.assertEqual(item['name'],copy[f'faq.q{i}']);self.assertEqual(item['acceptedAnswer']['text'],copy[f'faq.a{i}'])
        self.assertIn(copy['prayers.father'],ar.get_text(' ',strip=True))
        self.assertIn(copy['prayers.graces'],ar.get_text(' ',strip=True))
        self.assertNotIn('no formula guarantees',str(ar.main))

    def test_missing_slot_rejected(self):
        import tempfile,shutil
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'locales/ar').mkdir(parents=True)
            shutil.copy(ROOT/'saint-charbel-chaplet.html',root/'saint-charbel-chaplet.html')
            shutil.copytree(ROOT/'locales/en/mirrors',root/'locales/en/mirrors')
            shutil.copytree(ROOT/'locales/ar/mirrors',root/'locales/ar/mirrors')
            copy=read_json(ROOT/'locales/ar/chaplet.json');copy.pop('faq.a5')
            (root/'locales/ar/chaplet.json').write_text(json.dumps(copy,ensure_ascii=False))
            with self.assertRaisesRegex(ValueError,'missing/extra'):render_chaplet(root)

if __name__=='__main__':unittest.main()
