"""Exact render sources must be present before generation, not post-build disk state."""
import hashlib,json,sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.guarded_dom import translate_slots
class ExactSourceInputs(unittest.TestCase):
 def test_complete_frozen_sources_and_slots(self):
  for name in ('miracles','biography'):
   c=json.loads((ROOT/f'locales/de/{name}-exact.json').read_text())
   self.assertTrue(c['master'].startswith('templates/masters/'))
   raw=(ROOT/c['master']).read_bytes()
   self.assertEqual(hashlib.sha256(raw).hexdigest(),c['masterSha256'])
   soup=BeautifulSoup(raw,'html.parser');before=[(n.name,n.attrs.copy())for n in soup.select('main *')]
   translate_slots(soup.main,c['slots'],name)
   self.assertEqual(before,[(n.name,n.attrs.copy())for n in soup.select('main *')])
if __name__=='__main__':unittest.main()
