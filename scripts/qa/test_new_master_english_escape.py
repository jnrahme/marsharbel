"""English source access does not certify translation equivalence."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.same_page_injection import with_english_sources,_english_source_cache,inject_control
from bs4 import BeautifulSoup
from i18n.catalog import published_home_locales
class NewMasterEscape(unittest.TestCase):
 def test_generated_routes_have_english_source_even_with_pending_review(self):
  _english_source_cache.clear()
  m=with_english_sources(ROOT,json.loads((ROOT/'locales/same-page-manifest.pending.json').read_text()))
  for lang in ('hi','th'):self.assertEqual(m['englishSources'][f'/{lang}/history'],'/history')
 def test_footer_expands_frozen_nine_links_and_is_idempotent(self):
  text=(ROOT/'ar/novena.html').read_text();s=BeautifulSoup(text,'html.parser')
  for a in s.select('nav.footer-locales a[hreflang=hi],nav.footer-locales a[hreflang=th]'):a.decompose()
  m=json.loads((ROOT/'locales/same-page-manifest.pending.json').read_text());c=json.loads((ROOT/'locales/same-page-copy.json').read_text())
  once=inject_control(str(s),ROOT,m,c);nav=BeautifulSoup(once,'html.parser').select_one('nav.footer-locales')
  self.assertEqual([a['hreflang']for a in nav.select('a')],published_home_locales(json.loads((ROOT/'locales/registry.json').read_text())))
  self.assertEqual(once,inject_control(once,ROOT,m,c))
if __name__=='__main__':unittest.main()
