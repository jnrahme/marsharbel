"""Exact policy context rejects self-declared master and routing claims."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.stories_policy_context import trusted_context
from i18n.mirror_structure import check_pair

class StoriesPolicyContextTests(unittest.TestCase):
 def setUp(self):
  self.registry=json.loads((ROOT/'locales/registry.json').read_text())
  self.policy=json.loads((ROOT/'config/locale-mirror-policy.json').read_text())
 def test_all11_strict_real_outputs(self):
  for code in ('ar','fr','es','pt','it','de','pl','ru','hi','th','zh-Hans'):
   entry=self.policy['pages'][code+'/stories.html'];self.assertEqual(entry['status'],'strict')
   context=trusted_context(ROOT,self.registry,entry)
   self.assertEqual(check_pair((ROOT/entry['master']).read_text(),(ROOT/(code+'/stories.html')).read_text(),entry['masterRoute'],entry['route'],entry['normalizers'],context),[])
 def test_wrong_master_hash_route_family_and_membership_refused(self):
  for kind in ('master','hash','route','locale','family','membership'):
   r=copy.deepcopy(self.registry);e=copy.deepcopy(self.policy['pages']['de/stories.html']);real=Path.read_bytes
   if kind=='master':e['master']='history.html'
   elif kind=='route':e['route']='/de/other'
   elif kind=='locale':e['locale']='en'
   elif kind=='family':e['family']='other'
   elif kind=='membership':r['pageMirrors']['stories-master']['renderLocales'].remove('de')
   with self.subTest(kind=kind),patch.object(Path,'read_bytes',lambda p:b'hostile frozen master' if kind=='hash' and p==ROOT/'templates/masters/stories.html' else real(p)),self.assertRaises(ValueError):trusted_context(ROOT,r,e)
 def test_both_side_keyed_data_drift_refused(self):
  e=self.policy['pages']['de/stories.html'];context=trusted_context(ROOT,self.registry,e)
  en=(ROOT/e['master']).read_text();de=(ROOT/'de/stories.html').read_text()
  for side in ('en','locale'):
   import re
   before=en if side=='en' else de
   changed=re.sub(r'data-keywords="[^"]*"','data-keywords="hostile"',before,count=1)
   with self.subTest(side=side),self.assertRaises(ValueError):
    check_pair(changed if side=='en' else en,changed if side=='locale' else de,e['masterRoute'],e['route'],e['normalizers'],context)

 def test_missing_context_and_script_or_attribute_drift_refused(self):
  e=self.policy['pages']['de/stories.html'];context=trusted_context(ROOT,self.registry,e)
  en=(ROOT/e['master']).read_text();de=(ROOT/'de/stories.html').read_text()
  with self.assertRaises(ValueError):check_pair(en,de,e['masterRoute'],e['route'],e['normalizers'])
  for changed in [de.replace('</body>','<script>window.hostile=true;</script></body>'),de.replace('<main','<main data-hostile="1"',1)]:
   try:result=check_pair(en,changed,e['masterRoute'],e['route'],e['normalizers'],context)
   except ValueError:continue
   self.assertTrue(result)

if __name__=='__main__':unittest.main()
