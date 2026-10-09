"""Synthetic exact scope and shared hreflang/pin refusal coverage."""
import importlib.util
from pathlib import Path
import unittest
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
if __name__=='__main__':unittest.main()
