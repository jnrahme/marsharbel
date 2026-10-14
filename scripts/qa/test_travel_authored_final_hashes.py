"""Final build bytes stay equal to nineteen frozen committed authored files."""
import hashlib,json,importlib.util,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
class AuthoredFinalHashTests(unittest.TestCase):
 def test_actual_pipeline_nineteen_frozen_full_file_hashes(self):
  raw=(ROOT/'scripts/qa/fixtures/travel-authored-heads-f6e0d947.json').read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'b1e931cccc6e7ca9018ef34ee90f57f5d45d4b1b419d78cea77c569ab91f5b7d')
  files=json.loads(raw)['files'];self.assertEqual(len(files),19)
  spec=importlib.util.spec_from_file_location('authored_final_build',ROOT/'scripts/build-international.py')
  builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
  final=builder.outputs()
  for file,row in files.items():
   with self.subTest(file=file):self.assertEqual(hashlib.sha256(final[ROOT/file].encode()).hexdigest(),row['fileSha256'])
if __name__=='__main__':unittest.main()
