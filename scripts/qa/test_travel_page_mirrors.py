import json,sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.page_mirror import render_page
from i18n.mirror_structure import check_pair
from i18n.catalog import home_url
FAMILIES=('annaya-master','twenty-second-master','pilgrimage-master')
class TravelPageMirrors(unittest.TestCase):
 def setUp(self):self.r=json.loads((ROOT/'locales/registry.json').read_text())
 def test_every_family_renders_all_eight_locales_with_parity(self):
  for family in FAMILIES:
   cfg=self.r['pageMirrors'][family];master=(ROOT/cfg['master']).read_text()
   self.assertEqual(sorted(cfg['renderLocales']),sorted(cfg['routes']))
   self.assertGreaterEqual(len(cfg['routes']),8)
   for lang,route in cfg['routes'].items():
    text=render_page(ROOT,self.r,lang,family,route);s=BeautifulSoup(text,'html.parser')
    self.assertEqual(check_pair(master,text,cfg['english'],route,normalizers=('partial-home-disclosure',) if home_url(self.r,lang) is None else ()),[],(family,lang))
    self.assertEqual(s.html['lang'],lang);self.assertEqual(s.select_one('link[rel=canonical]')['href'],self.r['site']+route)
    self.assertEqual({l['hreflang']:l['href'] for l in s.select('link[hreflang]')},{c:self.r['site']+p for c,p in cfg.get('discoveryRoutes',{'en':cfg['english'],'x-default':cfg['english'],**cfg['routes']}).items()})
    for a in s.select('main a[href^="/"]'):self.assertNotIn(a['href'].split('?')[0].split('#')[0],[c['english'] for name,c in self.r['pageMirrors'].items() if lang in c['routes'] and (not name.endswith('-travel-master') or (family=='annaya-master' and lang=='de' and c['english'] in ('/saint-charbel-hermitage','/saint-charbel-places-lebanon','/qadisha-valley','/qannoubine-monastery','/qozhaya-monastery','/saint-charbel-trail')))],(family,lang,a['href']))
    schemas=[json.loads(x.string) for x in s.select('script[type="application/ld+json"]')]
    for sc in schemas:
     self.assertEqual(sc.get('inLanguage'),lang)
     if sc.get('@type')=='FAQPage':
      for q in sc['mainEntity']:
       self.assertTrue(q['name'] and q['acceptedAnswer']['text'])
       self.assertNotIn('<',q['acceptedAnswer']['text'])
 def test_travel_pages_link_to_localized_siblings(self):
  routes={f:self.r['pageMirrors'][f]['routes'] for f in FAMILIES}
  s=BeautifulSoup(render_page(ROOT,self.r,'ru','annaya-master','/ru/annaya'),'html.parser')
  hrefs=[a['href'] for a in s.select('main a')]
  self.assertIn(routes['twenty-second-master']['ru'],hrefs)
 def test_published_novena_twins_use_localized_destination(self):
  novena=self.r['pageMirrors']['saint-charbel-novena-master']
  for lang in novena['renderLocales']:
   route=self.r['pageMirrors']['annaya-master']['routes'][lang]
   s=BeautifulSoup(render_page(ROOT,self.r,lang,'annaya-master',route),'html.parser')
   hrefs=[a['href']for a in s.select('main a')]
   self.assertIn(novena['routes'][lang],hrefs,lang)
   self.assertNotIn(novena['english'],hrefs,lang)
 def test_missing_locale_twin_keeps_english_destination(self):
  # Simulate an unpublished RU twin so fallback stays covered after activation.
  r=json.loads(json.dumps(self.r))
  cfg=r['pageMirrors']['saint-charbel-novena-master']
  cfg['routes'].pop('ru',None)
  cfg['renderLocales']=[lang for lang in cfg['renderLocales']if lang!='ru']
  s=BeautifulSoup(render_page(ROOT,r,'ru','annaya-master','/ru/annaya'),'html.parser')
  self.assertIn('/saint-charbel-novena',[a['href']for a in s.select('main a')])
 def test_missing_key_fails(self):
  c=json.loads((ROOT/'locales/fr/annaya-master-copy.json').read_text());c.pop(next(iter(c)))
  with self.assertRaisesRegex(ValueError,'missing/extra'):render_page(ROOT,self.r,'fr','annaya-master','/fr/annaya',c)
if __name__=='__main__':unittest.main()
