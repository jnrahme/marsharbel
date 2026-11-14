import json,sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.page_mirror import render_page
from i18n.travel_variant_evidence import review_pinned_locales
from i18n.encyclopedia_nav import MARKING_LOCALES, PINNED_MARKING_LOCALES
GATED=MARKING_LOCALES
def registry_scoped_pairs():
    groups=json.loads((ROOT/'locales/travel-equivalence.json').read_text())['groups']
    out=set()
    for family,group in groups.items():
        if group.get('evidenceSchema') in ('scoped-variants-v1','annaya-hero-v1'):
            for code in group['variants']:
                if code!='en':out.add((family,code))
    return out
class NavMarkingExclusions(unittest.TestCase):
 def setUp(self):self.r=json.loads((ROOT/'locales/registry.json').read_text())
 def test_helper_matches_registry(self):
  self.assertEqual(review_pinned_locales(ROOT),registry_scoped_pairs())
 def test_excluded_set_equals_pinned_set(self):
  for family,cfg in self.r['pageMirrors'].items():
   if family in ('film-premiere-master','feedback','feedback-review','daily-prayer','daily-prayer-result','daily-prayer-admin'):continue  # separate keyed/catalog pipelines with their own suites
   for lang in GATED:
    if lang not in cfg.get('routes',{}):continue
    text=render_page(ROOT,self.r,lang,family,cfg['routes'][lang])
    s=BeautifulSoup(text,'html.parser')
    if s.select_one('header') is None:continue
    marked=bool(s.select('header span.enc-language'))
    pinned=(family,lang) in registry_scoped_pairs()
    expected=(not pinned) or lang in PINNED_MARKING_LOCALES
    self.assertEqual(marked,expected,(family,lang))
 def test_unpinned_de_page_is_marked(self):
  cfg=self.r['pageMirrors']['history-master']
  text=render_page(ROOT,self.r,'de','history-master',cfg['routes']['de'])
  s=BeautifulSoup(text,'html.parser')
  self.assertTrue(s.select('header span.enc-language'))
 def test_pinned_marked_locales_pages_are_marked(self):
  # Negative control: on a marked pinned page every English-destination header
  # link must carry hreflang="en"; a single unmarked English-destination nav
  # link fails this test.
  for family,lang in sorted(registry_scoped_pairs()):
   if lang not in PINNED_MARKING_LOCALES:continue
   cfg=self.r['pageMirrors'][family]
   text=render_page(ROOT,self.r,lang,family,cfg['routes'][lang])
   s=BeautifulSoup(text,'html.parser')
   self.assertIsNotNone(s.select_one('header'),(family,lang))
   self.assertTrue(s.select('header span.enc-language'),(family,lang))
   for a in s.select('header a[href]'):
    href=a.get('href','').split('#')[0].split('?')[0]
    if not href.startswith('/') or href=='/':continue
    if href.split('/')[1] in ('ar','de','es','fr','hi','it','pl','pt','ru','th','zh-Hans'):continue
    self.assertEqual(a.get('hreflang'),'en',(family,lang,href))
 def test_pinned_unmarked_locales_pages_remain_unmarked(self):
  for family,lang in sorted(registry_scoped_pairs()):
   if lang not in GATED or lang in PINNED_MARKING_LOCALES:continue
   cfg=self.r['pageMirrors'][family]
   text=render_page(ROOT,self.r,lang,family,cfg['routes'][lang])
   s=BeautifulSoup(text,'html.parser')
   self.assertFalse(s.select('header span.enc-language'),(family,lang))
   self.assertIsNotNone(s.select_one('header'),(family,lang))
 def test_no_marked_link_has_registered_twin(self):
  from i18n.encyclopedia_nav import nav_twin_hrefs
  skip=('film-premiere-master','feedback','feedback-review','daily-prayer','daily-prayer-result','daily-prayer-admin')
  for family,cfg in self.r['pageMirrors'].items():
   if family in skip:continue
   for lang in GATED:
    if lang not in cfg.get('routes',{}):continue
    if (family,lang) in registry_scoped_pairs() and lang not in PINNED_MARKING_LOCALES:continue
    text=render_page(ROOT,self.r,lang,family,cfg['routes'][lang])
    s=BeautifulSoup(text,'html.parser')
    if s.select_one('header') is None:continue
    twins=nav_twin_hrefs(self.r,lang)
    for a in s.select('header a[hreflang="en"]'):
     href=a.get('href','').split('#')[0].split('?')[0]
     key=href if href=='/' else href.rstrip('/')
     self.assertNotIn(key,twins,(family,lang,href))
 def test_de_twinned_routes_are_routed_not_marked(self):
  twinned=['/annaya-tour','/bekaa-kafra','/bkerke-maronite-patriarchate','/cedars-of-god-lebanon','/music','/our-lady-of-lebanon-harissa','/qadisha-valley','/qannoubine-monastery','/qozhaya-monastery','/saint-charbel-hermitage','/saint-charbel-places-lebanon','/saint-charbel-trail']
  cfg=self.r['pageMirrors']['history-master']
  text=render_page(ROOT,self.r,'de','history-master',cfg['routes']['de'])
  s=BeautifulSoup(text,'html.parser')
  for route in twinned:
   self.assertEqual(s.select('header a[hreflang="en"][href="%s"]'%route),[],route)
if __name__=='__main__':unittest.main()
