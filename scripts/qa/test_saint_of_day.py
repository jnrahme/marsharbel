"""Daily saint module source, provenance and paired book contract."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('saintbuild',ROOT/'scripts/build_saint_of_day.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def manifest():return json.loads((ROOT/'locales/saint-of-day.json').read_text())
class SaintDay(unittest.TestCase):
 def test_source_fresh(self):
  p,text=mod.output();self.assertEqual(p.read_text(),text)
 def test_locales_have_same_keys(self):
  en=json.loads((ROOT/'locales/en/saint-of-day.json').read_text())
  self.assertEqual(set(en),set(manifest()['entries']),'English copy dates must match the manifest window')
  for lang in json.loads((ROOT/'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
   local=json.loads((ROOT/f'locales/{lang}/saint-of-day.json').read_text())
   self.assertEqual(set(en),set(local),f'{lang} copy dates differ')
   for d in en:self.assertEqual(set(en[d]),set(local[d]),f'{lang} keys differ on {d}');self.assertTrue(all(v.strip() for v in local[d].values()))
 def test_sources_and_book_exist(self):
  m=manifest();self.assertEqual(m['timezone'],'America/New_York')
  for d,e in m['entries'].items():
   self.assertTrue(e['sources'],d);self.assertTrue(e['infoUrl'].startswith('https://'),d)
   self.assertTrue((ROOT/(e['bookUrl'].strip('/')+'.html')).is_file(),d);self.assertTrue((ROOT/e['bookImage'].lstrip('/')).is_file(),d)
 def test_section_and_ids(self):
  from bs4 import BeautifulSoup
  s=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
  sections=s.select('template[data-saint-date] #saint-of-the-day')
  self.assertEqual(len(sections),len(manifest()['entries']))
  for n in sections:self.assertEqual(len(n.select('.home-saint-pair > a')),2);self.assertIsNone(n.select_one('a a'))
 def test_date_is_generated_and_initial_state_fails_closed(self):
  from bs4 import BeautifulSoup
  from datetime import date
  m=manifest();s=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
  templates=s.select('template[data-saint-date]')
  self.assertEqual(sorted(t['data-saint-date'] for t in templates),sorted(m['entries']))
  for t in templates:
   self.assertEqual(t.parent.name,'body');self.assertFalse(t.has_attr('hidden'))
   n=t.select_one('#saint-of-the-day');self.assertIsNotNone(n)
   self.assertEqual(''.join(str(c) for c in n.time.contents),date.fromisoformat(t['data-saint-date']).strftime('%d.%m.%Y'))
  en=json.loads((ROOT/'locales/en/saint-of-day.json').read_text())
  for d in en:self.assertNotIn('dateLabel',en[d])
 def test_missing_date_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'locales').mkdir();(p/'locales/saint-of-day.json').write_text('{"entries":{"bad":{}}}')
   with self.assertRaises(ValueError):mod.output(p)
 def test_unsourced_entry_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'locales').mkdir()
   (p/'locales/saint-of-day.json').write_text('{"entries":{"2026-10-15":{"saint":"x","calendar":"Maronite","infoUrl":"https://x","bookUrl":"/x","bookImage":"/x.jpg","sources":[],"translationStatus":"y"}}}')
   (p/'locales/en').mkdir();(p/'locales/en/saint-of-day.json').write_text('{"2026-10-15":{}}')
   with self.assertRaises(ValueError):mod.output(p)
