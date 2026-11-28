import copy,hashlib,importlib.util,json,re,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('archive',ROOT/'scripts/build_saint_day_archive.py');archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
class ArchiveHistory(unittest.TestCase):
 def fixture(self,root):
  (root/'locales').mkdir();data=json.loads((ROOT/'locales/saint-day-archive.json').read_text());(root/'locales/saint-day-archive.json').write_text(json.dumps(data));return data
 def test_seed_rows_byte_identical_to_reviewed_base(self):
  baseline=subprocess.check_output(['git','show','50d333e64015a371c89929b5b07934ebfcc5c8e7:src/pages/saint-of-the-day.html'],cwd=ROOT,text=True)
  rows=re.findall(r'          <li>.*?          </li>',baseline.split('<!-- i18n-saint-day-archive:start -->')[1].split('<!-- i18n-saint-day-archive:end -->')[0],re.S)
  data=json.loads((ROOT/'locales/saint-day-archive.json').read_text());self.assertEqual([e['reviewedHtml'] for e in data['entries'] if 'reviewedHtml'in e],rows)
 def test_pruned_home_manifest_cannot_delete_history(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);before=archive.render_block(r)
   (r/'locales/saint-of-day.json').write_text('{"entries":{}}');self.assertEqual(archive.render_block(r),before)
   (r/'locales/saint-of-day.json').unlink();self.assertEqual(archive.render_block(r),before)
 def test_duplicate_dates_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);data=self.fixture(r);data['entries'].append(copy.deepcopy(data['entries'][0]));(r/'locales/saint-day-archive.json').write_text(json.dumps(data))
   with self.assertRaisesRegex(ValueError,'Duplicate'):archive.render_block(r)
 def test_history_tamper_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);data=self.fixture(r);data['entries'][0]['reviewedHtml']+=' changed';(r/'locales/saint-day-archive.json').write_text(json.dumps(data))
   with self.assertRaisesRegex(ValueError,'bytes changed'):archive.render_block(r)
 def test_exact_dates_and_no_invented_gap(self):
  block=archive.render_block(ROOT);self.assertEqual(re.findall(r'id="saint-day-([^"]+)"',block),['2026-11-'+d for d in [f'{d:02d}' for d in range(17,29)]])
 def test_appended_text_exact_in_twelve_languages(self):
  h=json.loads((ROOT/'locales/saint-day-archive.json').read_text())
  for e in h['entries']:
   if 'copy' not in e:continue
   for l,p in e['copy'].items():
    current=json.loads((ROOT/f'locales/{l}/saint-of-day.json').read_text())
    if e['date'] in current:self.assertEqual(p,current[e['date']])
 def test_catalog_key_coverage(self):
  base=json.loads((ROOT/'locales/en/saint-of-the-day-master-copy.json').read_text())
  for l in ['ar','de','es','fr','hi','it','pl','pt','ru','th','zh-Hans']:self.assertEqual(set(base),set(json.loads((ROOT/f'locales/{l}/saint-of-the-day-master-copy.json').read_text())))
class DailySynchronization(unittest.TestCase):
 def fixture(self,root):
  import shutil
  (root/'locales').mkdir();shutil.copy(ROOT/'locales/saint-day-archive.json',root/'locales');shutil.copy(ROOT/'locales/registry.json',root/'locales')
  manifest=json.loads((ROOT/'locales/saint-of-day.json').read_text());self.day='2026-11-29';first=sorted(manifest['entries'])[0];manifest['entries']={self.day:copy.deepcopy(manifest['entries'][first])};(root/'locales/saint-of-day.json').write_text(json.dumps(manifest))
  for lang in json.loads((root/'locales/registry.json').read_text())['homePublicationLocales']:
   dest=root/f'locales/{lang}';dest.mkdir();original=json.loads((ROOT/f'locales/{lang}/saint-of-day.json').read_text());(dest/'saint-of-day.json').write_text(json.dumps({self.day:original[first]}))
 def test_next_daily_card_is_appended_and_pruning_cannot_remove_it(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root);before=len(json.loads((root/'locales/saint-day-archive.json').read_text())['entries'])
   with self.assertRaisesRegex(ValueError,'not archived'):archive.merge_daily_history(root,True)
   history=archive.merge_daily_history(root);self.assertEqual(len(history['entries']),before+1);self.assertEqual(len(history['entries'][-1]['copy']),12);archive.merge_daily_history(root,True)
   (root/'locales/saint-of-day.json').write_text('{"entries":{}}');self.assertEqual(archive.merge_daily_history(root)['entries'],history['entries'])
 def test_missing_translation_is_not_admitted(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root);path=root/'locales/saint-day-archive.json';before=path.read_bytes();(root/'locales/ar/saint-of-day.json').write_text('{}')
   with self.assertRaises(KeyError):archive.merge_daily_history(root)
   self.assertEqual(path.read_bytes(),before)
 def test_changed_archived_card_fails_instead_of_silent_rewrite(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root);archive.merge_daily_history(root);path=root/'locales/en/saint-of-day.json';obj=json.loads(path.read_text());obj[self.day]['story']+=' changed';path.write_text(json.dumps(obj))
   with self.assertRaisesRegex(ValueError,'conflict'):archive.merge_daily_history(root)
 def test_future_binding_refresh_preserves_all_old_values(self):
  import shutil
  from bs4 import BeautifulSoup
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root);history=archive.merge_daily_history(root);(root/'src/pages').mkdir(parents=True);shutil.copy(ROOT/'src/pages/saint-of-the-day.html',root/'src/pages');path,source=archive.output(root);path.write_text(source)
   # Source already composed by the daily command; retain only its dated block here.
   served=(ROOT/'saint-of-the-day.html').read_text();import re
   served=re.sub(r'<!-- i18n-saint-day-archive:start -->.*?<!-- i18n-saint-day-archive:end -->',lambda m:archive.render_block(root),served,flags=re.S);(root/'saint-of-the-day.html').write_text(served)
   for lang in json.loads((root/'locales/registry.json').read_text())['homePublicationLocales']:
    shutil.copy(ROOT/f'locales/{lang}/saint-of-the-day-master-copy.json',root/f'locales/{lang}')
   shutil.copy(ROOT/'locales/en/saint-of-the-day-master-bindings.json',root/'locales/en')
   import sys;sys.path.insert(0,str(ROOT/'scripts'));from i18n.refresh_saint_archive_bindings import refresh
   old=json.loads((root/'locales/ar/saint-of-the-day-master-copy.json').read_text());refresh(root);new=json.loads((root/'locales/ar/saint-of-the-day-master-copy.json').read_text());self.assertTrue(all(new[k]==v for k,v in old.items()));self.assertEqual(new['saintDay.archive.'+self.day+'.story'],history['entries'][-1]['copy']['ar']['story'])
if __name__=='__main__':unittest.main()
