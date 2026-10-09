"""Raw discovery blocks survive the actual shared composer."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.travel_metadata import compose_travel_clusters
class SpliceTests(unittest.TestCase):
 def run_composer(self,text):
  p=ROOT/'travel.html';cluster={'/travel':{'en':'/travel','ru':'/ru/travel','x-default':'/travel'}}
  with patch('i18n.travel_metadata.travel_clusters',return_value=cluster):
   return compose_travel_clusters(ROOT,{'site':'https://marsharbel.com'},{p:text})[p]
 def base(self,separator=''):
  return '<html><head><link href="https://marsharbel.com/travel" rel="canonical"/>'+separator+'<link href="https://marsharbel.com/travel" hreflang="en" rel="alternate"/>'+separator+'<link href="https://marsharbel.com/travel" hreflang="x-default" rel="alternate"/>'+separator+'</head><main>Exact</main></html>'
 def tag(self):return '<link href="https://marsharbel.com/ru/travel" hreflang="ru" rel="alternate"/>'
 def test_compact_minimal_insert_and_idempotence(self):
  before=self.base();after=self.run_composer(before)
  expected=before.replace('<link href="https://marsharbel.com/travel" hreflang="x-default"',self.tag()+'<link href="https://marsharbel.com/travel" hreflang="x-default"')
  self.assertEqual(after,expected);self.assertEqual(self.run_composer(after),after)
 def test_expanded_correct_block_untouched(self):
  expanded=self.base('\n').replace('<link href="https://marsharbel.com/travel" hreflang="x-default"',self.tag()+'\n<link href="https://marsharbel.com/travel" hreflang="x-default"')
  self.assertEqual(self.run_composer(expanded),expanded)
 def test_malformed_ru_and_non_ru_gap_refuse(self):
  correct=self.run_composer(self.base())
  for bad in [correct.replace('/ru/travel','/ru/wrong'),correct.replace(self.tag(),self.tag()*2),correct.replace('hreflang="ru" rel="alternate"','hreflang="ru" rel="canonical"'),self.base().replace('hreflang="en"','hreflang="fr"')]:
   with self.subTest(bad=bad),self.assertRaises(ValueError):self.run_composer(bad)
if __name__=='__main__':unittest.main()
