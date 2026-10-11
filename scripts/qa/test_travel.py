"""Travel hub parity and destination pattern regression checks."""
import sys, unittest, json, re
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.catalog import read_json,published_home_locales
from i18n.travel_mirror import render_travel
from i18n.tour_nav import tour_nav
from i18n.travel_components import travel_frame
from i18n.runtime_labels import ensure_runtime_labels
from i18n.same_page_injection import inject_control
from i18n.travel_metadata import compose_travel_clusters
def fc(t):return inject_control(t,ROOT,read_json(ROOT/'locales/same-page-manifest.pending.json'),read_json(ROOT/'locales/same-page-copy.json'))
class TravelTests(unittest.TestCase):
 def test_catalog_and_render_parity(self):
  registry=read_json(ROOT/'locales/registry.json')
  pages=render_travel(ROOT,registry)
  self.assertEqual(len(pages),len(registry['authoredMirrors']['travel']['routes']))
  for path,text in pages.items():
   self.assertEqual(path.read_text(),fc(ensure_runtime_labels(compose_travel_clusters(ROOT,registry,{path:travel_frame(tour_nav(text,ROOT,'en' if path.parent==ROOT else path.parent.name),ROOT,'en' if path.parent==ROOT else path.parent.name,'/'+str(path.relative_to(ROOT)).removesuffix('.html'),registry)})[path],ROOT,'en' if path.parent==ROOT else path.parent.name,registry)))
   soup=BeautifulSoup(text,'html.parser')
   self.assertEqual(len(soup.select('main')),1)
   self.assertEqual(len(soup.select('a.skip-link')),1)
   self.assertEqual(len(soup.select('.travel-place')),12)
   self.assertEqual(soup.select_one('.travel-hero .btn.primary')['href'],'/annaya-tour')
   self.assertEqual(len(soup.select('link[hreflang]')),len(registry['authoredMirrors']['travel']['routes'])+1)
   self.assertIn('/travel.css',soup.select('link[rel=stylesheet]')[-1]['href'])
   self.assertNotIn('{{',text)
 def test_homes_never_receive_travel_framing(self):
  registry=read_json(ROOT/'locales/registry.json')
  for code in published_home_locales(registry):
   config=registry['locales'][code]
   path=ROOT/(code+'/index.html' if code!='en' else 'index.html')
   text=path.read_text();soup=BeautifulSoup(text,'html.parser')
   self.assertNotIn('travel-page',soup.body.get('class',[]))
   self.assertNotIn('travel-destination',soup.body.get('class',[]))
   self.assertFalse(soup.select('.travel-breadcrumb'))
   self.assertNotIn('i18n-travel-schema',text)
   self.assertNotIn('/travel.css',text)
   self.assertEqual(len(re.findall(r'\bclass=',re.search(r'<body[^>]*>',text)[0])),1 if soup.body.get('class') else 0)
   self.assertEqual(text,travel_frame(text,ROOT,code,config['home'],registry))
 def test_one_semantic_breadcrumb_on_every_travel_route(self):
  registry=read_json(ROOT/'locales/registry.json');cfg=read_json(ROOT/'locales/travel-routes.json')
  routes=set([cfg['hub'],*cfg['destinations']])
  for name in ('travel','qadisha','qannoubine','qozhaya'):routes.update(registry['authoredMirrors'][name]['routes'].values())
  def trails(node):
   if isinstance(node,dict):return ([node] if node.get('@type')=='BreadcrumbList' else [])+sum((trails(v) for v in node.values()),[])
   if isinstance(node,list):return sum((trails(v) for v in node),[])
   return []
  for route in routes:
   text=(ROOT/(route.lstrip('/')+'.html')).read_text();soup=BeautifulSoup(text,'html.parser')
   found=sum((trails(json.loads(s.get_text())) for s in soup.select('script[type="application/ld+json"]')),[])
   self.assertEqual(len(found),1,route)
   items=found[0]['itemListElement'];self.assertEqual(items[1]['item'].split('/')[-1],'travel',route)
   self.assertEqual(items[-1]['item'],'https://marsharbel.com'+route,route)
   self.assertLessEqual(len(re.findall(r'\bclass=',re.search(r'<body[^>]*>',text)[0])),1,route)
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
