import json,sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.page_mirror import render_page
from i18n.travel_variant_evidence import review_pinned_locales
GATED=('ar','de')
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
    self.assertEqual(marked,not pinned,(family,lang))
 def test_unpinned_de_page_is_marked(self):
  cfg=self.r['pageMirrors']['history-master']
  text=render_page(ROOT,self.r,'de','history-master',cfg['routes']['de'])
  s=BeautifulSoup(text,'html.parser')
  self.assertTrue(s.select('header span.enc-language'))
 def test_pinned_de_travel_pages_are_unmarked(self):
  for family,lang in sorted(registry_scoped_pairs()):
   if lang not in GATED:continue
   cfg=self.r['pageMirrors'][family]
   text=render_page(ROOT,self.r,lang,family,cfg['routes'][lang])
   s=BeautifulSoup(text,'html.parser')
   self.assertFalse(s.select('header span.enc-language'),(family,lang))
   self.assertIsNotNone(s.select_one('header'),(family,lang))
if __name__=='__main__':unittest.main()
