"""Source copy placeholders support the same stable keys as locale catalogs."""
import json,re,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class SourceCopyKeys(unittest.TestCase):
 def test_history_hyphenated_keys_resolve_from_catalog(self):
  builder=(ROOT/'scripts/build-pages.mjs').read_text()
  pattern=re.search(r'const copyPattern = (/.+?/g);',builder).group(1)
  source=(ROOT/'src/pages/history.html').read_text()
  catalog=json.loads((ROOT/'locales/en/history-accessibility-copy.json').read_text())['copy']
  js='const fs=require("fs");const source=fs.readFileSync(0,"utf8");const pattern='+pattern+';console.log(JSON.stringify([...source.matchAll(pattern)].map(m=>[m[1],m[2]])));'
  matches=json.loads(subprocess.check_output(['node','-e',js],input=source,text=True))
  actual={key for name,key in matches if name=='history-accessibility'}
  self.assertEqual(actual,set(catalog))
  rendered=(ROOT/'history.html').read_text()
  for value in catalog.values():self.assertIn('aria-label="'+value+'"',rendered)
  self.assertNotIn('{{copy',rendered)
if __name__=='__main__':unittest.main()
