"""Daily saint module source, provenance and paired book contract."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('saintbuild',ROOT/'scripts/build_saint_of_day.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class SaintDay(unittest.TestCase):
 def test_source_fresh(self):
  p,text=mod.output();self.assertEqual(p.read_text(),text)
 def test_locales_have_same_keys(self):
  en=json.loads((ROOT/'locales/en/saint-of-day.json').read_text())
  for lang in json.loads((ROOT/'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
   local=json.loads((ROOT/f'locales/{lang}/saint-of-day.json').read_text());self.assertEqual(set(en),set(local));self.assertTrue(all(v.strip() for v in local.values()))
 def test_sources_and_book_exist(self):
  m=json.loads((ROOT/'locales/saint-of-day.json').read_text());e=m['entries'][m['activeDate']]
  self.assertEqual(m['timezone'],'America/New_York');self.assertTrue(e['sources']);self.assertTrue(e['infoUrl'].startswith('https://'))
  self.assertTrue((ROOT/(e['bookUrl'].strip('/')+'.html')).is_file());self.assertTrue((ROOT/e['bookImage'].lstrip('/')).is_file())
 def test_section_and_ids(self):
  from bs4 import BeautifulSoup
  s=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser');n=s.select_one('#saint-of-the-day')
  self.assertEqual(len(n.select('.home-saint-pair > a')),2);self.assertIsNone(n.select_one('a a'))
 def test_missing_date_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'locales').mkdir();(p/'locales/saint-of-day.json').write_text('{"activeDate":"bad","entries":{}}')
   with self.assertRaises(ValueError):mod.output(p)
