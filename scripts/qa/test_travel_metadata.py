"""Discovery composition is reciprocal, deterministic and body-preserving."""
import sys,json,unittest,re
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
 def test_zh_faq_questions_and_answers_never_retain_english_only_text(self):
  registry=json.loads((ROOT/'locales/registry.json').read_text())
  def walk(value,file):
   if isinstance(value,dict):
    if value.get('@type') in ('Question','Answer'):
     for field in ('name','text'):
      if field in value:self.assertRegex(value[field],r'[\u3400-\u9fff]',f'{file}: {field} English-only FAQ residual')
    for child in value.values():walk(child,file)
   elif isinstance(value,list):
    for child in value:walk(child,file)
  for cluster in travel_clusters(ROOT,registry).values():
   file=ROOT/(cluster['zh-Hans'].lstrip('/')+'.html')
   for script in BeautifulSoup(file.read_text(),'html.parser').select('script[type="application/ld+json"]'):walk(json.loads(script.string),file)
 def test_duplicate_language_target_rejected(self):
  r=json.loads((ROOT/'locales/registry.json').read_text());r['pageMirrors']['test-duplicate']={'english':'/visit-annaya','routes':{'de':'/de/duplicate'}}
  with self.assertRaisesRegex(ValueError,'Ambiguous'):travel_clusters(ROOT,r)
if __name__=='__main__':unittest.main()
