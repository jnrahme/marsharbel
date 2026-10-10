"""Content executor validates exact existing-home catalog delta and refusal."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('refresh',ROOT/'scripts/i18n/refresh_film_home_bindings.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FilmHomeRefreshTests(unittest.TestCase):
 def fixture(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);r=Path(tmp.name)
  files=['index.html','locales/en/home-bindings.json','locales/en/home-copy.json','locales/en/news-desk.json','locales/film-home-translations.json']+[f'locales/{c}/home-copy.json'for c in m.LOCALES]
  for f in files:
   p=r/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
  return r
 def changes(self,r):
  with patch.object(m.subprocess,'check_output',return_value='test-revision\n'):return m.outputs(r)
 def test_precise_delta_and_fixed_point(self):
  r=self.fixture();old=json.loads((r/'locales/en/home-bindings.json').read_text());changes=self.changes(r);new=json.loads(changes[r/'locales/en/home-bindings.json'])
  self.assertEqual(len(old['bindings']),199);self.assertEqual(len(new['bindings']),201)
  before={b['key']:b for b in old['bindings']};after={b['key']:b for b in new['bindings']}
  self.assertEqual(set(before)-set(after),m.REMOVE);self.assertEqual(set(after)-set(before),{'home.latest-news.premiere.'+k for k in m.NEW})
  moved=[k for k in before.keys()&after.keys()if before[k]!=after[k]];self.assertEqual(len(moved),20)
  for k in moved:
   self.assertEqual(before[k]['source'],after[k]['source']);self.assertEqual(before[k]['kind'],after[k]['kind'])
  keys=set(json.loads(changes[r/'locales/en/home-copy.json']))
  for c in m.LOCALES:self.assertEqual(set(json.loads(changes[r/f'locales/{c}/home-copy.json'])),keys)
  for p,t in changes.items():p.write_text(t)
  self.assertEqual(self.changes(r),changes)
 def test_unrelated_source_drift_refused(self):
  r=self.fixture();p=r/'index.html';p.write_text(p.read_text().replace('<title>Saint Charbel','<title>Changed Charbel',1))
  with self.assertRaises(ValueError):self.changes(r)
 def test_locale_key_drift_refused(self):
  r=self.fixture();p=r/'locales/fr/home-copy.json';j=json.loads(p.read_text());j.pop(next(iter(j)));p.write_text(json.dumps(j))
  with self.assertRaises(ValueError):self.changes(r)
if __name__=='__main__':unittest.main()
