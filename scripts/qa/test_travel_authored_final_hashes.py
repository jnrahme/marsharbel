"""Final build bytes stay equal to nineteen frozen committed authored files."""
import hashlib,json,importlib.util,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.keyed_master import strip_generated_locale_nav
_FINAL=None
def final_outputs():
 """Build once per process; the builder is deterministic."""
 global _FINAL
 if _FINAL is None:
  spec=importlib.util.spec_from_file_location('authored_final_build',ROOT/'scripts/build-international.py')
  builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
  _FINAL=builder.outputs()
 return _FINAL
def frozen_files():
 raw=(ROOT/'scripts/qa/fixtures/travel-authored-heads-f6e0d947.json').read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='1cbbea7c251579d49714711ed100fac6ea2513c98682c9197ae6edb5a402f138','frozen fixture bytes changed - that is a re-seal, not a harness fix'
 return json.loads(raw)['files']
class AuthoredFinalHashTests(unittest.TestCase):
 def test_actual_pipeline_nineteen_frozen_full_file_hashes(self):
  files=frozen_files();self.assertEqual(len(files),19)
  # PR3: the marked generated locale-nav is a post-pin generator-owned control
  # overlay; strip ONLY that block before comparing with the frozen authored
  # hashes. Authored bytes are never stripped (covered by the drift negative).
  final=final_outputs()
  for file,row in files.items():
   stripped=strip_generated_locale_nav(final[ROOT/file].encode())
   with self.subTest(file=file):self.assertEqual(hashlib.sha256(stripped).hexdigest(),row['fileSha256'])
 def test_authored_drift_still_fails_and_restore_passes(self):
  """Negative: one authored byte outside the generator-owned block must still
  fail after stripping (the strip never masks authored drift); the restored
  exact bytes pass again."""
  files=frozen_files();file=sorted(files)[0];row=files[file]
  original=final_outputs()[ROOT/file].encode()
  self.assertIn(b'<title>',original)
  title_start=original.index(b'<title>')+7
  self.assertNotIn(b'i18n-locale-nav:start',original[:title_start],'mutation point must sit outside the generator-owned block')
  drift=original[:title_start]+bytes([original[title_start]^1])+original[title_start+1:]
  self.assertNotEqual(hashlib.sha256(strip_generated_locale_nav(drift)).hexdigest(),row['fileSha256'],'authored drift outside the generated block must fail')
  self.assertEqual(hashlib.sha256(strip_generated_locale_nav(original)).hexdigest(),row['fileSha256'],'restored exact bytes must pass')
if __name__=='__main__':unittest.main()
