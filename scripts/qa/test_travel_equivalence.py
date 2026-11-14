"""Published travel routing stays pinned; unrelated pending groups stay pending."""
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.reviewed_travel import travel_manifest
class TravelEquivalence(unittest.TestCase):
 def test_pending_families_unchanged_and_review_required(self):
  original=json.loads((ROOT/'locales/same-page-manifest.pending.json').read_text())
  out=travel_manifest(ROOT,{},original)
  travel_paths={v['path']for g in json.loads((ROOT/'locales/travel-equivalence.json').read_text())['groups'].values()for v in g['variants'].values()}
  for key,page in original['pages'].items():
   if not any(v['path']in travel_paths for v in page['variants'].values()):self.assertEqual(out['pages'][key],page)
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'locales').mkdir();review=json.loads((ROOT/'locales/travel-equivalence.json').read_text());next(iter(review['groups'].values()))['renderedReviewStatus']='pending';(root/'locales/travel-equivalence.json').write_text(json.dumps(review))
   with self.assertRaisesRegex(ValueError,'review incomplete'):travel_manifest(root,{},original)
 def test_changed_body_refuses(self):
  original=json.loads((ROOT/'locales/same-page-manifest.pending.json').read_text());groups=json.loads((ROOT/'locales/travel-equivalence.json').read_text())['groups'];file=ROOT/next(iter(groups.values()))['variants']['en']['file']
  with self.assertRaisesRegex(ValueError,'body changed'):travel_manifest(ROOT,{file:file.read_text().replace('<main','<main data-test-drift="1"',1)},original)
if __name__=='__main__':unittest.main()
