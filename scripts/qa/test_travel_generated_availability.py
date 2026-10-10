"""Actual generated artifact: discovery is not ZH/TH exact availability."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.travel_variant_evidence import SLUGS

class GeneratedTravelAvailabilityTests(unittest.TestCase):
 def test_twelve_generated_groups_and_actual_resolver_refuse_parallel_locales(self):
  # No fixture, no mocked validators: this is the real checked-in/generated JS.
  raw=(ROOT/'same-page-manifest.js').read_text()
  prefix='window.SC_SAME_PAGE_MANIFEST = '
  self.assertTrue(raw.startswith(prefix))
  manifest=json.loads(raw[len(prefix):].strip().removesuffix(';'))
  scoped={key:page for key,page in manifest['pages'].items() if any(v.get('proof',{}).get('type')=='scoped-travel-variant' for v in page['variants'].values())}
  expected={slug+'-travel-master-equivalence' for slug in SLUGS}
  self.assertEqual(set(scoped),expected)
  queries=[]
  for slug in sorted(SLUGS):
   page=scoped[slug+'-travel-master-equivalence']
   self.assertEqual(set(page['variants']),{'en','de','ru','hi'} if slug=='travel' else {'en','de','ru'})
   self.assertNotIn('zh-Hans',page['variants']);self.assertNotIn('th',page['variants'])
   # Also call the real resolver: discoveryRoutes cannot silently widen proof.
   for code in ('zh-Hans','th'):
    queries.append({'href':'https://marsharbel.com/'+slug,'requested':code,'actual':'en'})
  driver="const fs=require('fs');const api=require(process.argv[1]);const d=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(d.queries.map(q=>api.resolve(d.manifest,q.href,q.requested,q.actual))));"
  results=json.loads(subprocess.check_output(['node','-e',driver,str(ROOT/'same-page-resolver.js')],input=json.dumps({'manifest':manifest,'queries':queries}),text=True))
  self.assertEqual(len(results),24)
  for query,result in zip(queries,results):
   with self.subTest(query=query):
    self.assertFalse(result['available'],result)
    self.assertEqual(result['reason'],'translation-unavailable')
 def test_actual_resolver_approved_de_ru_and_hi_hub_available(self):
  raw=(ROOT/'same-page-manifest.js').read_text()
  manifest=json.loads(raw.split(' = ',1)[1].strip().removesuffix(';'))
  queries=[]
  for slug in sorted(SLUGS):
   for code in (('de','ru','hi') if slug=='travel' else ('de','ru')):
    queries.append({'href':'https://marsharbel.com/'+slug,'requested':code,'actual':'en','target':'https://marsharbel.com/'+code+'/'+slug})
  driver="const fs=require('fs');const api=require(process.argv[1]);const d=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(d.queries.map(q=>api.resolve(d.manifest,q.href,q.requested,q.actual))));"
  results=json.loads(subprocess.check_output(['node','-e',driver,str(ROOT/'same-page-resolver.js')],input=json.dumps({'manifest':manifest,'queries':queries}),text=True))
  self.assertEqual(len(results),25)
  for query,result in zip(queries,results):
   with self.subTest(query=query):
    self.assertTrue(result['available'],result)
    self.assertEqual(result['reason'],'verified-twin')
    self.assertEqual(result['contentLanguage'],query['requested'])
    self.assertEqual(result['href'],query['target'])
if __name__=='__main__':unittest.main()
