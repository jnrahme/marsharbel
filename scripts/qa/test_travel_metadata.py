"""Discovery composition is reciprocal, deterministic and body-preserving."""
import sys,json,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.travel_metadata import travel_clusters,compose_travel_clusters
class TravelMetadataTests(unittest.TestCase):
 def test_registered_complete_tabs_and_existing_url(self):
  registry=json.loads((ROOT/'locales/registry.json').read_text());clusters=travel_clusters(ROOT,registry)
  self.assertEqual(len(clusters),14)
  for c in clusters.values():self.assertIn('de',c);self.assertIn('zh-Hans',c)
  self.assertEqual(clusters['/visit-annaya']['de'],'/de/annaya')
 def test_idempotent_head_only_and_reciprocal(self):
  registry=json.loads((ROOT/'locales/registry.json').read_text())
  for english,c in travel_clusters(ROOT,registry).items():
   file=ROOT/(english.lstrip('/')+'.html');text=file.read_text();result=compose_travel_clusters(ROOT,registry,{file:text})[file]
   self.assertEqual(str(BeautifulSoup(text,'html.parser').body),str(BeautifulSoup(result,'html.parser').body))
   self.assertEqual(compose_travel_clusters(ROOT,registry,{file:result})[file],result)
   self.assertEqual({a['hreflang']:a['href'] for a in BeautifulSoup(result,'html.parser').select('head link[hreflang]')},{k:registry['site']+v for k,v in c.items()})
 def test_duplicate_language_target_rejected(self):
  r=json.loads((ROOT/'locales/registry.json').read_text());r['pageMirrors']['test-duplicate']={'english':'/visit-annaya','routes':{'de':'/de/duplicate'}}
  with self.assertRaisesRegex(ValueError,'Ambiguous'):travel_clusters(ROOT,r)
if __name__=='__main__':unittest.main()
