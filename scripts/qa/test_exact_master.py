import json
from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT,read_json
from i18n.exact_master import render_exact
def prepared_catalog(name):
 c=read_json(ROOT/f'locales/de/{name}-exact.json')
 # Retired novena renderer is characterized against its frozen master only.
 # Published six-route output belongs to test_prayer_keyed_masters.
 if name=='novena':c['master']='templates/masters/saint-charbel-novena.html'
 return c
class ExactMasterTests(unittest.TestCase):
 def test_german_preview_complete(self):
  r=read_json(ROOT/'locales/registry.json')
  for name,route in [('novena','/de/novene'),('feast','/de/gedenktag'),('miracles','/de/miracles/')]:
   c=prepared_catalog(name);source=BeautifulSoup((ROOT/c['master']).read_text(),'html.parser');s=BeautifulSoup(render_exact(ROOT,r,'de',name,route,catalog=prepared_catalog(name)),'html.parser')
   self.assertEqual(s.select_one('body > a.skip-link').get_text(),read_json(ROOT/'locales/de/common.json')['navigation.skip'])
   self.assertEqual(s.select_one('body > a.skip-link')['href'],'#main-content')
   self.assertEqual(s.main.get('tabindex'),'-1')
   self.assertEqual(s.main.get('id'),'main-content')
   self.assertEqual(s.html['lang'],'de');self.assertEqual(s.select_one('link[rel=canonical]')['href'],r['site']+route)
   self.assertEqual([n.name for n in source.select('main *')],[n.name for n in s.select('main *') if 'translation-note' not in n.get('class',[])])
   self.assertEqual(len(source.select('script[type="application/ld+json"]')),len(s.select('script[type="application/ld+json"]')))
   self.assertEqual(len(s.select('script[src$="translate.js?v=20260922-1"]')),1)
   self.assertEqual(s.select_one('.translation-note').get_text(),c['translationNote'])
   self.assertEqual([(a.get('hreflang'),a.get('href','').removeprefix('https://marsharbel.com') or None) for a in source.select('main a[hreflang]')],[(a.get('hreflang'),a.get('href')) for a in s.select('main a[hreflang]')])
   for image in s.select('main img'):self.assertTrue(image['src'].startswith('/'))
   for n in s.select('script[type="application/ld+json"]'):
    d=json.loads(n.string)
    if d['@type']=='FAQPage':
     faq=next(sec for sec in s.select('main section') if sec.h2 and sec.h2.get_text()==c['faqHeading'])
     self.assertEqual([(q['name'],q['acceptedAnswer']['text']) for q in d['mainEntity']],[(h.get_text(' ',strip=True),p.get_text(' ',strip=True)) for h,p in zip(faq.select('h3'),faq.select('p'))])
    else:self.assertEqual(d['inLanguage'],'de');self.assertEqual(d['url'],r['site']+route)
 def test_drift_fails(self):
  r=read_json(ROOT/'locales/registry.json');c=prepared_catalog('novena');c['masterSha256']='bad'
  with self.assertRaisesRegex(ValueError,'digest changed'):render_exact(ROOT,r,'de','novena','/de/novene',c)
if __name__=='__main__':unittest.main()

class ExactRuntimeGuards(unittest.TestCase):
 def test_missing_accessible_attribute_fails(self):
  r=read_json(ROOT/'locales/registry.json');c=prepared_catalog('novena')
  c['attributes'].pop('main #nine-days nav')
  with self.assertRaisesRegex(ValueError,'accessible attribute'):render_exact(ROOT,r,'de','novena','/de/novene',c)
 def test_skip_target_changed_fails(self):
  import tempfile,shutil,hashlib
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);r=read_json(ROOT/'locales/registry.json');c=prepared_catalog('novena')
   source=(ROOT/c['master']).read_text().replace('tabindex="-1"','tabindex="0"')
   (root/c['master']).parent.mkdir(parents=True,exist_ok=True)
   (root/c['master']).write_text(source);c['masterSha256']=hashlib.sha256(source.encode()).hexdigest()
   with self.assertRaisesRegex(ValueError,'focus attributes'):render_exact(root,r,'de','novena','/de/novene',c)

class ExactLocalizedDestinations(unittest.TestCase):
 def test_prayer_and_eucharistic_twins(self):
  r=read_json(ROOT/'locales/registry.json')
  for name,route,label,href in [('novena','/de/novene','Gebete zum heiligen Charbel','/de/gebete'),('miracles','/de/miracles/','Zur Sammlung','/de/miracles/eucharistic/')]:
   s=BeautifulSoup(render_exact(ROOT,r,'de',name,route,catalog=prepared_catalog(name)),'html.parser')
   links=[a for a in s.select('main a[href]') if a.get_text(strip=True)==label]
   self.assertTrue(links)
   self.assertTrue(all(a.get('href')==href for a in links))
