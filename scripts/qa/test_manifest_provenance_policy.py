"""Precise path-bound provenance exclusion cannot exempt arbitrary wording."""
import copy,json,sys,unittest,tempfile,subprocess
from collections import Counter
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import manifest_policy as m
from i18n import citation_amendment as ca
class ManifestPolicyTests(unittest.TestCase):
 # Synthetic Travel-only fixtures: citation lookup is isolated (ca.load -> None) so the
 # unit covers Travel provenance only. The REAL citation validator against the REAL
 # sidecar and production manifest is covered by ProductionCitationProvenance below -
 # citation_provenance itself, its identity set, and its named branches stay live code.
 def pages(self):
  return {slug+'-travel-master-equivalence':{'sourcePath':slug+'.html','variants':{code:{'proof':{'type':'scoped-travel-variant','scope':('hero-alt-credit-scrim' if slug=='annaya-tour' else 'stage bytes carried; no new review' if code=='en' else 'reviewed scope')}} for code in (('en','de','ru','hi') if slug=='travel' else ('en','de','ru'))}} for slug in m.SLUGS}
 def text(self,pages,extra=None):return m.PREFIX+json.dumps({'pages':pages,**(extra or {})})+';\n'
 def test_exact_thirty_four_scope_entries_only(self):
  pages=self.pages()
  with patch.object(m,'travel_manifest',return_value={'pages':pages}),patch.object(ca,'load',return_value=None):
   excluded=m.scoped_provenance(ROOT,self.text(pages))
  self.assertEqual(sum(excluded.values()),34)
  self.assertEqual(excluded['stage bytes carried; no new review'],11)
 def test_same_phrase_outside_scope_and_new_display_still_flag(self):
  pages=self.pages();phrase='stage bytes carried; no new review'
  with patch.object(m,'travel_manifest',return_value={'pages':pages}),patch.object(ca,'load',return_value=None):
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
   with self.subTest(bad=bad),patch.object(m,'travel_manifest',return_value={'pages':pages}),patch.object(ca,'load',return_value=None),self.assertRaises(ValueError):m.scoped_provenance(ROOT,self.text(bad))
 def test_real_js_extractor_and_production_filter_keep_unbound_display(self):
  pages=self.pages();phrase='stage bytes carried; no new review'
  text=self.text(pages,{'outside':phrase,'display':'New display wording'})
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'same-page-manifest.js';file.write_text(text)
   values=json.loads(subprocess.check_output(['node',str(ROOT/'scripts/i18n/extract-js-text.mjs'),str(file)],text=True))
   # Isolate only evidence lookup; extraction and the production snapshot's
   # exact filter path are real. The lane also runs full real-tree policy.
   with patch.object(m,'travel_manifest',return_value={'pages':pages}),patch.object(ca,'load',return_value=None):
    remaining=m.manifest_text_counter(ROOT,text,values)
   self.assertEqual(remaining,Counter({phrase:1,'New display wording':1}))
   self.assertEqual(Counter(values)[phrase],12)

class ProductionCitationProvenance(unittest.TestCase):
 """Real production manifest x real sidecar x real validator: the production manifest
 must satisfy citation identity, and full-sidecar tampering must reject on each NAMED
 branch. Nothing is patched in this class."""
 def manifest(self):
  text=(ROOT/'same-page-manifest.js').read_text()
  assert text.startswith(m.PREFIX) and text.endswith(';\n')
  return json.loads(text[len(m.PREFIX):-2])
 def _first_addendum(self,pages):
  for key,page in pages['pages'].items():
   for code,v in page['variants'].items():
    if v.get('proof',{}).get('citationAmendment'):return key,code
  raise AssertionError('no citationAmendment in production manifest')
 def test_production_manifest_satisfies_citation_identity(self):
  scopes=m.citation_provenance(ROOT,self.manifest())
  self.assertIsInstance(scopes,Counter)
 def test_missing_addendum_named_branch(self):
  pages=self.manifest();key,code=self._first_addendum(pages)
  del pages['pages'][key]['variants'][code]
  with self.assertRaisesRegex(ValueError,'Manifest citationAmendment set differs from sidecar'):
   m.citation_provenance(ROOT,pages)
 def test_tampered_digest_named_branch(self):
  pages=self.manifest();key,code=self._first_addendum(pages)
  pages['pages'][key]['variants'][code]['proof']['citationAmendment']['newBodySha256']='0'*64
  with self.assertRaisesRegex(ValueError,'digest mismatch'):
   m.citation_provenance(ROOT,pages)
 def test_addendum_on_unexpected_page_key_named_branch(self):
  pages=self.manifest();key,code=self._first_addendum(pages)
  pages['pages']['zz-foreign']={'sourcePath':'zz.html','variants':{'en':copy.deepcopy(pages['pages'][key]['variants'][code])}}
  with self.assertRaisesRegex(ValueError,'Manifest citationAmendment on unexpected page key'):
   m.citation_provenance(ROOT,pages)
 def test_addendum_outside_sidecar_coverage_named_branch(self):
  pages=self.manifest();key,code=self._first_addendum(pages)
  pages['pages'][key]['variants']['zz']=copy.deepcopy(pages['pages'][key]['variants'][code])
  with self.assertRaisesRegex(ValueError,'Manifest citationAmendment outside sidecar coverage'):
   m.citation_provenance(ROOT,pages)
if __name__=='__main__':unittest.main()
