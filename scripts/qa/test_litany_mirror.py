import json,sys,unittest,tempfile,shutil
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.litany_mirror import render_litany
class LitanyMirrorTests(unittest.TestCase):
    def test_structure_prayer_and_schema(self):
        en=BeautifulSoup((ROOT/'litany-of-saint-charbel.html').read_text(),'html.parser')
        ar=BeautifulSoup(render_litany(ROOT)[ROOT/'ar/litany-of-saint-charbel.html'],'html.parser')
        self.assertEqual(render_litany(ROOT)[ROOT/'ar/litany-of-saint-charbel.html'],(ROOT/'ar/litany-of-saint-charbel.html').read_text())
        self.assertEqual([n.name for n in en.select('main *')],[n.name for n in ar.select('main *')])
        self.assertEqual(len(ar.select('main > section')),8)
        invocations=ar.select('#the-litany .story p')[1]
        self.assertEqual(len(invocations.select('em')),29);self.assertEqual(len(invocations.select('br')),29)
        self.assertEqual(len(ar.select('#the-litany .story p')),6)
        self.assertEqual(ar.html['dir'],'rtl')
        self.assertEqual(ar.select_one('link[rel=canonical]')['href'],'https://marsharbel.com/ar/litany-of-saint-charbel')
        self.assertEqual({n['hreflang'] for n in ar.select('link[hreflang]')},{'ar','en','x-default'})
        self.assertEqual([n['href'] for n in en.select('main section:last-child a')],[n['href'] for n in ar.select('main section:last-child a')])
        faq=json.loads(ar.select('script[type="application/ld+json"]')[1].string)
        section=ar.select('main > section')[5]
        for item,h,p in zip(faq['mainEntity'],section.select('h3'),section.select('.story p')):
            self.assertEqual(item['name'],h.get_text());self.assertEqual(item['acceptedAnswer']['text'],p.get_text())
        self.assertIn('فلا صيغة تضمن نتيجة',ar.main.get_text())
    def test_master_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'locales/ar').mkdir(parents=True)
            shutil.copy(ROOT/'locales/ar/litany.json',root/'locales/ar/litany.json')
            (root/'litany-of-saint-charbel.html').write_text((ROOT/'litany-of-saint-charbel.html').read_text().replace('A Litany to the Hermit','Changed intro'))
            with self.assertRaisesRegex(ValueError,'master changed'):render_litany(root)
if __name__=='__main__':unittest.main()
