"""All15 exact authored deltas and hostile full-file changes fail closed."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.stories_authored_header_delta import inverse,FILES

class AuthoredStoriesDeltaTests(unittest.TestCase):
 def test_all15_actual_outputs_and_hostile_controls(self):
  records=json.loads((ROOT/'scripts/qa/fixtures/travel-authored-heads-f6e0d947.json').read_text())['files']
  self.assertEqual(len(FILES),15)
  for file in sorted(FILES):
   code=file.split('/')[0];target='/'+code+'/stories';text=(ROOT/file).read_text();sha=records[file]['fileSha256']
   self.assertEqual(hashlib.sha256(inverse(ROOT,file,text,sha).encode()).hexdigest(),sha)
   changes=[text.replace('<main','<main data-hostile="1"',1),text.replace('href="'+target+'"','href="/stories?x=1"',1),text.replace('href="'+target+'"','href="/'+code+'/stories#x"',1),text.replace('href="'+target+'"','href="/other/stories"',1),text.replace('href="'+target+'"','data-extra="1" href="'+target+'"',1),text.replace('</header>','<a href="'+target+'">duplicate</a></header>',1),text.replace('</body>','changed</body>',1),text.replace('href="'+target+'"','hreflang="en" href="'+target+'"',1)]
   for changed in changes:
    with self.subTest(file=file),self.assertRaises(ValueError):inverse(ROOT,file,changed,sha)
   with self.assertRaises(ValueError):inverse(ROOT,file,text,'0'*64)
 def test_other4_files_are_not_normalized(self):
  records=json.loads((ROOT/'scripts/qa/fixtures/travel-authored-heads-f6e0d947.json').read_text())['files']
  others=set(records)-FILES;self.assertEqual(len(others),4)
  for file in others:
   text=(ROOT/file).read_text();self.assertEqual(inverse(ROOT,file,text,records[file]['fileSha256']),text)

if __name__=='__main__':unittest.main()
