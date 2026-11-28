"""Finite Arabic creator credits retain full Unicode names and handles."""
import sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.catalog import load_catalog
from i18n.page_mirror import render_page

class CreatorBidi(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.registry,_=load_catalog(ROOT)
 def test_complete_credits_are_single_ltr_isolates(self):
  for slug,credit in [('terco-da-batalha','Adrines Kölln, Católica (@adrineskolln)'),('mary-who-goes-ahead-prayer','Catholic Prayer (@catholicprayerofc)'),('lebanese-mountain-prayers','Anthony El Hachem')]:
   rendered=render_page(ROOT,self.registry,'ar',slug+'-master','/ar/'+slug)
   self.assertGreaterEqual(rendered.count('\u2066'+credit+'\u2069'),2,slug)
   self.assertNotIn('K\u2069ö',rendered)
   self.assertNotIn('(@\u2068',rendered)
   french=render_page(ROOT,self.registry,'fr',slug+'-master','/fr/'+slug)
   self.assertNotIn('\u2066',french)

if __name__=='__main__':unittest.main()
