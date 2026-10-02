"""Travel hub parity and destination pattern regression checks."""
import sys, unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.catalog import read_json
from i18n.travel_mirror import render_travel
from i18n.tour_nav import tour_nav
class TravelTests(unittest.TestCase):
 def test_catalog_and_render_parity(self):
  registry=read_json(ROOT/'locales/registry.json')
  pages=render_travel(ROOT,registry)
  self.assertEqual(len(pages),8)
  for path,text in pages.items():
   self.assertEqual(path.read_text(),tour_nav(text,ROOT,'en' if path.parent==ROOT else path.parent.name))
   soup=BeautifulSoup(text,'html.parser')
   self.assertEqual(len(soup.select('main')),1)
   self.assertEqual(len(soup.select('a.skip-link')),1)
   self.assertEqual(len(soup.select('.travel-destination-list .travel-place')),3)
   self.assertEqual(soup.select_one('.travel-hero .btn.primary')['href'],'/annaya-tour')
   self.assertEqual(len(soup.select('link[hreflang]')),9)
   self.assertIn('/travel.css',soup.select('link[rel=stylesheet]')[-1]['href'])
   self.assertNotIn('{{',text)
 def test_shared_destination_pattern(self):
  r=read_json(ROOT/'locales/registry.json')
  for route in r['authoredMirrors']['qadisha']['routes'].values():
   soup=BeautifulSoup((ROOT/(route.lstrip('/')+'.html')).read_text(),'html.parser')
   self.assertEqual(len(soup.select('.travel-hero')),1)
   self.assertEqual(len(soup.select('.travel-section')),8)
   self.assertEqual(soup.select_one('.travel-hero .btn.primary')['href'],'#visiting')
   for link in soup.select('.travel-chapters a'):
    self.assertIsNotNone(soup.select_one(link['href']))
if __name__=='__main__':unittest.main()
