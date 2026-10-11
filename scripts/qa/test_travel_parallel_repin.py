"""Synthetic exact scope and shared hreflang/pin refusal coverage."""
import importlib.util
from pathlib import Path
import unittest
import tempfile
import json
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('parallel_repin',ROOT/'scripts/i18n/repin_travel_parallel_hreflang.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ParallelTravelRepinTests(unittest.TestCase):
 def test_scope_twelve_zh_one_th_no_annaya_guide(self):
  self.assertEqual(len(m.FAMILIES),13);self.assertNotIn('visit-annaya-zh-travel-master',m.FAMILIES)
  self.assertEqual(sum('zh-travel-master' in f for f in m.FAMILIES),12)
 def test_only_isolated_correct_ru_link(self):
  old=b'<head>\n<title>Same</title>\n</head><main>Body</main>';new=old.replace(b'</head>',b'  <link rel="alternate" hreflang="ru" href="https://marsharbel.com/ru/travel" />\n</head>')
  m.tools.hreflang_delta(old,new,'https://marsharbel.com/ru/travel')
  for bad in [new.replace(b'Body',b'Other'),new.replace(b'Same',b'Other'),new.replace(b'/ru/travel',b'/ru/other'),new.replace(b'</head>',b'<meta name="extra"/>\n</head>')]:
   with self.assertRaises(ValueError):m.tools.hreflang_delta(old,bad,'https://marsharbel.com/ru/travel')
 def test_path_pin_preserves_provenance(self):
  raw='{"masterSha256":"'+'a'*64+'","frozen":"'+'a'*64+'"}'
  changed=m.tools.pin_text(raw,'masterSha256','a'*64,'b'*64)
  self.assertEqual(changed,raw.replace('a'*64,'b'*64,1))
 def test_prepare_all_thirteen_and_refusals(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);snap={};base='a'*40
   def put(path,raw):
    snap[path]=raw;p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
   for family,slug in m.FAMILIES.items():
    master=slug+'.html';before=b'<head>\n<title>Same</title>\n</head><main>Body</main>'
    put(master,before)
    (root/master).write_bytes(before.replace(b'</head>',('<link rel="alternate" hreflang="ru" href="https://marsharbel.com/ru/'+slug+'" />\n</head>').encode()))
    put('locales/en/'+family+'-bindings.json',json.dumps({'master':master,'masterSha256':m.tools.sha(before),'sourceRevision':'frozen','bindings':[]}).encode())
    code='th' if family=='travel-th-travel-master' else 'zh-Hans'
    put('locales/'+code+'/'+family+'-copy.json',b'{}')
    put('locales/en/'+family+'-copy.json',b'{}')
   for f in ['travel','history','prayer']:put('locales/'+f+'-equivalence.json',b'{}')
   with patch.object(m.tools,'blob',side_effect=lambda r,b,p:snap[p]), patch('subprocess.check_output',side_effect=lambda args,**kw: (args[-1]+'\n').encode() if args[-1] in snap else b''):
    updates,rows=m.prepare(root,base);self.assertEqual(len(updates),13);self.assertEqual(len(rows),13)
    bp=root/'locales/en/travel-zh-travel-master-bindings.json';original=bp.read_text()
    for bad in [original.replace('frozen','changed'),original+'\n']:
     bp.write_text(bad)
     with self.assertRaises(ValueError):m.prepare(root,base)
    bp.write_text(original)
    catalog=root/'locales/zh-Hans/travel-zh-travel-master-copy.json';catalog.write_text('{"changed":true}')
    with self.assertRaises(ValueError):m.prepare(root,base)
    catalog.write_bytes(b'{}')
    (root/'travel.html').write_bytes((root/'travel.html').read_bytes().replace(b'Body',b'changed'))
    with self.assertRaises(ValueError):m.prepare(root,base)
    with self.assertRaises(ValueError):m.prepare(root,'abcd')
if __name__=='__main__':unittest.main()
