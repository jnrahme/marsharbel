"""Raw discovery blocks survive the actual shared composer."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.travel_metadata import compose_travel_clusters, splice_travel_alternates, PARTIAL_AUTHORED_FILES
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
 def test_partial_allowlist_legacy_emission_offlist_and_wrong_href_refuse(self):
  cluster={'en':'/qadisha-valley','de':'/de/qadisha-valley','ru':'/ru/qadisha-valley','x-default':'/qadisha-valley'}
  raw='<head><title>Same</title><link rel="alternate" hreflang="en" href="https://marsharbel.com/qadisha-valley" />\n<link rel="alternate" hreflang="x-default" href="https://marsharbel.com/qadisha-valley" />\n</head><main>Exact</main>'
  expected='<head><title>Same</title>'+ '\n'.join('<link rel="alternate" hreflang="'+c+'" href="https://marsharbel.com'+v+'" />' for c,v in cluster.items())+'\n</head><main>Exact</main>'
  self.assertEqual(splice_travel_alternates(raw,cluster,'https://marsharbel.com','qadisha-valley.html'),expected)
  for file,text in [('de/qadisha-valley.html',raw),('qadisha-valley.html',raw.replace('/qadisha-valley','/wrong'))]:
   with self.assertRaises(ValueError):splice_travel_alternates(text,cluster,'https://marsharbel.com',file)
  self.assertNotIn('de/qozhaya-monastery.html',PARTIAL_AUTHORED_FILES)
  self.assertEqual(len(PARTIAL_AUTHORED_FILES),19)
  self.assertIn('travel.html',PARTIAL_AUTHORED_FILES)
 def test_no_empty_block_bootstrap(self):
  with self.assertRaisesRegex(ValueError,'bootstrap forbidden'):self.run_composer('<head><link rel="canonical" href="https://marsharbel.com/travel"/></head><main>Body</main>')
 def test_source_stub_flag_cannot_leak_into_served_inputs(self):
  from i18n.travel_metadata import SOURCE_STUB_FILES
  self.assertEqual(len(SOURCE_STUB_FILES),8)
  for file in SOURCE_STUB_FILES:
   slug=file.removesuffix('.html')
   cluster={'en':'/'+slug,'de':'/de/'+slug,'ru':'/ru/'+slug,'x-default':'/'+slug}
   raw='<head><title>Same</title>'+''.join('<link rel="alternate" hreflang="'+c+'" href="https://marsharbel.com/'+slug+'" />\n' for c in ('en','x-default'))+'</head><main>Exact</main>'
   expected='<head><title>Same</title>'+'\n'.join('<link rel="alternate" hreflang="'+c+'" href="https://marsharbel.com'+route+'" />' for c,route in cluster.items())+'\n</head><main>Exact</main>'
   with self.subTest(file=file):
    self.assertEqual(splice_travel_alternates(raw,cluster,'https://marsharbel.com',file,source_inputs=True),expected)
    with self.assertRaises(ValueError):splice_travel_alternates(raw,cluster,'https://marsharbel.com',file)
    with self.assertRaises(ValueError):splice_travel_alternates(raw.replace('/'+slug,'/wrong'),cluster,'https://marsharbel.com',file,source_inputs=True)
    extra=raw.replace('</head>','<link rel="alternate" hreflang="de" href="https://marsharbel.com/de/'+slug+'" />\n</head>')
    # Use an extra required locale so the third-code partial is not RU-only.
    larger={**cluster,'fr':'/fr/'+slug}
    with self.assertRaises(ValueError):splice_travel_alternates(extra,larger,'https://marsharbel.com',file,source_inputs=True)
if __name__=='__main__':unittest.main()
