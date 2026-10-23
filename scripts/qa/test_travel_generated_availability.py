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
  # Travel-4 re-pin (scrum 2026-10-12): exactly these 4 families carry the additive ar
  # variant; the other 8 scoped slugs must stay en/de/ru - a mistaken ar there still fails.
  TRAVEL4={'travel','qadisha-valley','qannoubine-monastery','qozhaya-monastery'}
  # Travel authored-mirror re-pin (A2, 2026-10-22): the travel family additionally
  # carries exactly the 5 certified es/fr/it/pl/pt mirror variants; every other
  # family's variant set is unchanged, and zh-Hans/th stay refused below.
  queries=[]
  for slug in sorted(SLUGS):
   page=scoped[slug+'-travel-master-equivalence']
   self.assertEqual(set(page['variants']),{'en','de','ru','hi','ar','es','fr','it','pl','pt'} if slug=='travel' else ({'en','de','ru','ar'} if slug in TRAVEL4 else {'en','de','ru'}))
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
  # Travel-4: the actual resolver offers Arabic from EN for exactly the 4 paired families
  # and still refuses it for the other 8 - re-pinned as a check, not a loosening.
  ar_queries=[{'href':'https://marsharbel.com/'+slug,'requested':'ar','actual':'en'} for slug in sorted(SLUGS)]
  ar_results=json.loads(subprocess.check_output(['node','-e',driver,str(ROOT/'same-page-resolver.js')],input=json.dumps({'manifest':manifest,'queries':ar_queries}),text=True))
  self.assertEqual(len(ar_results),12)
  for query,result in zip(ar_queries,ar_results):
   with self.subTest(query=query):
    slug=query['href'].rsplit('/',1)[-1]
    if slug in TRAVEL4:
     self.assertTrue(result['available'],result)
     self.assertEqual(result['reason'],'verified-twin',result)
     self.assertEqual(result['contentLanguage'],'ar',result)
     self.assertEqual(result['href'],'https://marsharbel.com/ar/'+slug,result)
    else:
     self.assertFalse(result['available'],result)
     self.assertEqual(result['reason'],'translation-unavailable',result)
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
