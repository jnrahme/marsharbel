import sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT,read_json
class LocaleHomeNavigation(unittest.TestCase):
 def test_home_section_navigation(self):
  r=read_json(ROOT/'locales/registry.json')
  for code,cfg in r['locales'].items():
   if code=='en':continue
   s=BeautifulSoup((ROOT/code/'index.html').read_text(),'html.parser')
   if code in r.get('homepageMirrors',{}).get('renderLocales',[]):
    self.assertIsNotNone(s.select_one('header nav.links'))
    self.assertEqual(len(s.select('header .lang-switcher-slot')),1)
    nav=s.select_one('footer nav.footer-locales')
   else:nav=s.select_one('header nav[data-locale-section-navigation]')
   self.assertIsNotNone(nav)
   for lang,other in r['locales'].items():
    a=nav.select_one('a[hreflang="'+lang+'"]');self.assertEqual(a['href'],other['home']);self.assertEqual(a.get_text(),other['nativeName']);self.assertNotIn('aria-disabled',a.attrs)
 def test_article_identity_is_not_home_navigation(self):
  r=read_json(ROOT/'locales/registry.json')
  for code,route in r['pageMirrors']['history-master']['routes'].items():
   s=BeautifulSoup((ROOT/(route.lstrip('/')+'.html')).read_text(),'html.parser')
   self.assertIsNone(s.select_one('header nav[data-locale-section-navigation]'))
   self.assertEqual(len(s.select('header .lang-switcher-slot')),1)
   nav=s.select_one('footer nav.footer-locales');self.assertIsNotNone(nav)
   for lang,other in r['locales'].items():
    a=nav.select_one('a[hreflang="'+lang+'"]');self.assertEqual(a['href'],other['home']);self.assertNotIn('aria-disabled',a.attrs)
if __name__=='__main__':unittest.main()
