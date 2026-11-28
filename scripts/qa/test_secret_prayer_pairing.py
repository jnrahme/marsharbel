"""Exact-three-locale technical pairing, no language or release certification."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.secret_prayer_pairing import secret_prayer_manifest,FAMILIES,LANGUAGES

class SecretPairing(unittest.TestCase):
 def setUp(self):
  self.record=json.loads((ROOT/'locales/secret-prayer-technical-pairing.json').read_text())
 def test_exact_manifest_and_resolver(self):
  manifest=secret_prayer_manifest(ROOT,{}, {'version':1,'pages':{},'languages':['en','ar','fr','de'],'homes':{},'aliases':{}})
  self.assertEqual(len(manifest['pages']),4)
  for slug in FAMILIES:
   page=manifest['pages']['secret-prayer-'+slug]
   self.assertEqual(set(page['variants']),set(LANGUAGES))
   for c,v in page['variants'].items():
    self.assertEqual(v['status'],'technically-paired')
    self.assertNotIn('editorialReview',v['proof'])
  code="const a=require(process.argv[1]);let m=JSON.parse(require('fs').readFileSync(0,'utf8'));let out=[];for(let s of ['powerful-secret-prayers','mary-who-goes-ahead-prayer','lebanese-mountain-prayers','terco-da-batalha'])for(let c of ['ar','fr']){let r=a.resolve(m,'https://marsharbel.com/'+s,c);if(r.href!=='https://marsharbel.com/'+c+'/'+s)throw Error(JSON.stringify(r));let h=a.resolve(m,'https://marsharbel.com/'+s,'de');if(h.href==='/de/'+s)throw Error('held route enabled');}"
  subprocess.run(['node','-e',code,str(ROOT/'same-page-resolver.js')],input=json.dumps(manifest),text=True,check=True,capture_output=True)
 def test_each_binding_occurrence_has_its_own_catalog_key(self):
  for slug in FAMILIES:
   contract=json.loads((ROOT/f'locales/en/{slug}-master-bindings.json').read_text())
   keys=[binding['key'] for binding in contract['bindings']]
   self.assertEqual(len(keys),len(set(keys)),slug)
   for code in LANGUAGES:
    catalog=json.loads((ROOT/f'locales/{code}/{slug}-master-copy.json').read_text())
    self.assertEqual(set(keys),set(catalog),(slug,code))
 def test_existing_reviewed_family_not_replaced(self):
  manifest={'pages':{'existing':{'variants':{'en':{'path':'/powerful-secret-prayers','status':'verified'}}}}}
  with self.assertRaises(ValueError):secret_prayer_manifest(ROOT,{},manifest)
 def test_mb16_control_inverse_is_finite(self):
  from i18n.secret_prayers_registry_continuation import control_preimage,CONTROL_ORIGINAL_SHA256
  import hashlib
  raw=(ROOT/'scripts/i18n/same_page_injection.py').read_bytes()
  self.assertEqual(hashlib.sha256(control_preimage(ROOT,raw)).hexdigest(),CONTROL_ORIGINAL_SHA256)
  for bad in (raw+b' ',raw.replace(b'    out={}',b'    out=dict()')):
   with self.assertRaises(ValueError):control_preimage(ROOT,bad)
 def test_body_drift_rejected(self):
  file=ROOT/'powerful-secret-prayers.html'
  with self.assertRaises(ValueError):secret_prayer_manifest(ROOT,{file:file.read_text().replace('</main>','X</main>')},{'pages':{}})

if __name__=='__main__':unittest.main()
