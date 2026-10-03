import unittest,sys,json,shutil,tempfile
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.feast_mirror import render_feast
from i18n.tour_nav import tour_nav
from i18n.travel_components import travel_frame
from i18n.catalog import read_json
class FeastMirrorTests(unittest.TestCase):
 def test_shape_and_provenance(self):
  en=BeautifulSoup((ROOT/'saint-charbel-feast-day.html').read_text(),'html.parser');text=render_feast(ROOT)[ROOT/'ar/feast-day.html'];ar=BeautifulSoup(text,'html.parser')
  self.assertEqual(travel_frame(tour_nav(text,ROOT,'ar'),ROOT,'ar','/ar/feast-day',read_json(ROOT/'locales/registry.json')),(ROOT/'ar/feast-day.html').read_text())
  self.assertEqual([n.name for n in en.select('main *')],[n.name for n in ar.select('main *')])
  self.assertEqual(len(ar.select('main > section')),14)
  self.assertEqual(ar.html['dir'],'rtl');self.assertEqual(ar.html['lang'],'ar')
  self.assertEqual(ar.select_one('main img')['src'],en.select_one('main img')['src'].removeprefix('.'))
  self.assertEqual([n['href'] for n in en.select('main a[href^="https:"]')],[n['href'] for n in ar.select('main a[href^="https:"]')])
  self.assertEqual({n['hreflang']:n['href'] for n in en.select('link[hreflang]')},{n['hreflang']:n['href'] for n in ar.select('link[hreflang]')})
  route=(ROOT/'locale-routes.js').read_text();self.assertIn('"/saint-charbel-feast-day":{"ar":"/ar/feast-day","es":"/es/fiesta","pt":"/pt/festa","en":"/saint-charbel-feast-day"}',route)
  self.assertNotIn('footer-locales',text);self.assertEqual(len(ar.select('script[type="application/ld+json"]')),2)
  faq=json.loads(ar.select('script[type="application/ld+json"]')[1].string)
  section=next(sec for sec in ar.select('main section') if sec.h2 and sec.h2.get_text()=='أسئلة شائعة')
  self.assertEqual([(q['name'],q['acceptedAnswer']['text']) for q in faq['mainEntity']],[(h.get_text(),p.get_text()) for h,p in zip(section.select('h3'),section.select('p'))])
  self.assertIn('اختيار الموعد لرعيتك',ar.get_text());self.assertIn('العيد حول العالم',ar.get_text());self.assertIn('الطريق إلى العيد',ar.get_text())
 def test_drift_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'locales/ar').mkdir(parents=True);shutil.copy(ROOT/'locales/ar/feast-mirror.json',root/'locales/ar/feast-mirror.json');shutil.copy(ROOT/'locales/registry.json',root/'locales/registry.json');shutil.copy(ROOT/'locales/ar/common.json',root/'locales/ar/common.json')
   (root/'saint-charbel-feast-day.html').write_text((ROOT/'saint-charbel-feast-day.html').read_text().replace('Two Dates, One Feast','Changed heading'))
   with self.assertRaisesRegex(ValueError,'master changed'):render_feast(root)
if __name__=='__main__':unittest.main()
