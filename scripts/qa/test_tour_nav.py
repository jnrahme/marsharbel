import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT
from i18n.tour_nav import tour_nav
from bs4 import BeautifulSoup
class TourNav(unittest.TestCase):
 def test_scoped_link(self):
  text='<html><header><nav class="links"><a href="/visit-annaya">Visit</a><a href="/bekaa-kafra">Bekaa</a></nav></header><main><p>unchanged</p></main></html>'
  for code,label in [('en','Annaya Online Tour'),('ar','جولة افتراضية في عنايا')]:
   s=BeautifulSoup(tour_nav(text,ROOT,code),'html.parser');self.assertEqual(s.header.select('a')[1].get_text(),label);self.assertEqual(str(s.main),'<main><p>unchanged</p></main>')
  self.assertEqual(tour_nav(text,ROOT,'de'),text)

if __name__=='__main__':unittest.main()
