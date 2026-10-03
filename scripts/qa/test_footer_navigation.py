import sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.same_page_injection import inject_control
from i18n.catalog import ROOT,read_json
class FooterNavigation(unittest.TestCase):
 def test_generated_footer_links_are_native_home_navigation(self):
  registry=read_json(ROOT/'locales/registry.json');count=0
  for row in read_json(ROOT/'locales/same-page-manifest.pending.json')['pages'].values():
   file=ROOT/row['sourcePath']
   soup=BeautifulSoup(file.read_text(),'html.parser')
   for nav in soup.select('nav.footer-locales'):
    count+=1
    self.assertFalse(nav.select('.sc-language-helper,.sc-unavailable-suffix'))
    for code,cfg in registry['locales'].items():
     a=nav.select_one('a[hreflang="'+code+'"]');self.assertIsNotNone(a,str(file))
     self.assertEqual(a['href'],cfg['home']);self.assertEqual(a.get_text(),cfg['nativeName'])
     self.assertEqual(a['lang'],code);self.assertEqual(a['dir'],cfg['direction'])
     for attr in ['aria-disabled','tabindex','data-language-switch']:self.assertNotIn(attr,a.attrs)
  self.assertGreaterEqual(count,10)
 def test_injection_is_idempotent(self):
  text=(ROOT/'history.html').read_text();manifest=read_json(ROOT/'locales/same-page-manifest.pending.json');copy=read_json(ROOT/'locales/same-page-copy.json')
  once=inject_control(text,ROOT,manifest,copy);self.assertEqual(once,inject_control(once,ROOT,manifest,copy))
if __name__=='__main__':unittest.main()
