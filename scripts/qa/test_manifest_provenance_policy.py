"""Precise path-bound provenance exclusion cannot exempt arbitrary wording."""
import copy,json,sys,unittest,tempfile,subprocess
from collections import Counter
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import manifest_policy as m
class ManifestPolicyTests(unittest.TestCase):
 def pages(self):
  return {slug+'-travel-master-equivalence':{'sourcePath':slug+'.html','variants':{code:{'proof':{'type':'scoped-travel-variant','scope':('hero-alt-credit-scrim' if slug=='annaya-tour' else 'stage bytes carried; no new review' if code=='en' else 'reviewed scope')}} for code in (('en','de','ru','hi') if slug=='travel' else ('en','de','ru'))}} for slug in m.SLUGS}
 def text(self,pages,extra=None):return m.PREFIX+json.dumps({'pages':pages,**(extra or {})})+';\n'
 def test_exact_thirty_four_scope_entries_only(self):
  pages=self.pages()
  with patch.object(m,'travel_manifest',return_value={'pages':pages}):
   excluded=m.scoped_provenance(ROOT,self.text(pages))
  self.assertEqual(sum(excluded.values()),34)
  self.assertEqual(excluded['stage bytes carried; no new review'],11)
 def test_same_phrase_outside_scope_and_new_display_still_flag(self):
  pages=self.pages();phrase='stage bytes carried; no new review'
  with patch.object(m,'travel_manifest',return_value={'pages':pages}):
   excluded=m.scoped_provenance(ROOT,self.text(pages,{'outside':phrase,'display':'New display wording'}))
  extracted=excluded+Counter({phrase:1,'New display wording':1})
  self.assertEqual(extracted-excluded,Counter({phrase:1,'New display wording':1}))
 def test_modified_scope_extra_family_or_membership_refuse(self):
  pages=self.pages();key='travel-travel-master-equivalence'
  variants=[]
  bad=copy.deepcopy(pages);bad[key]['variants']['en']['proof']['scope']='edited scope';variants.append(bad)
  bad=copy.deepcopy(pages);bad['unknown-equivalence']=copy.deepcopy(pages[key]);variants.append(bad)
  bad=copy.deepcopy(pages);bad[key]['variants']['zh-Hans']=copy.deepcopy(pages[key]['variants']['en']);variants.append(bad)
  for bad in variants:
   with self.subTest(bad=bad),patch.object(m,'travel_manifest',return_value={'pages':pages}),self.assertRaises(ValueError):m.scoped_provenance(ROOT,self.text(bad))
 def test_real_js_extractor_and_production_filter_keep_unbound_display(self):
  pages=self.pages();phrase='stage bytes carried; no new review'
  text=self.text(pages,{'outside':phrase,'display':'New display wording'})
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'same-page-manifest.js';file.write_text(text)
   values=json.loads(subprocess.check_output(['node',str(ROOT/'scripts/i18n/extract-js-text.mjs'),str(file)],text=True))
   # Isolate only evidence lookup; extraction and the production snapshot's
   # exact filter path are real. The lane also runs full real-tree policy.
   with patch.object(m,'travel_manifest',return_value={'pages':pages}):
    remaining=m.manifest_text_counter(ROOT,text,values)
   self.assertEqual(remaining,Counter({phrase:1,'New display wording':1}))
   self.assertEqual(Counter(values)[phrase],12)
if __name__=='__main__':unittest.main()
