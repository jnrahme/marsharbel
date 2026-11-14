"""Missing date uses clean git author date; carried dates never drift."""
import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import sitemap_dates as m
import sitemap_lastmod as lm
class SitemapDateTests(unittest.TestCase):
 def test_new_clean_source_uses_git_author_date(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/'ru/travel.html'
   with patch.object(m,'source_for',return_value=source),patch.object(m,'git',side_effect=['','ru/travel.html','2026-10-09']) as git:
    self.assertEqual(m.generated_lastmod(root,'https://marsharbel.com/ru/travel',{}),'2026-10-09')
    self.assertEqual(git.call_args.args,(root,'log','-1','--format=%as','--','ru/travel.html'))
 def test_carried_date_unchanged_even_when_git_disagrees(self):
  with patch.object(m,'git',return_value='2026-10-09') as git,patch.object(m,'source_for') as source:
   self.assertEqual(m.generated_lastmod(ROOT,'https://marsharbel.com/ru/travel',{'https://marsharbel.com/ru/travel':'2026-09-01'}),'2026-09-01')
   git.assert_not_called();source.assert_not_called()
 def test_dirty_untracked_no_history_omit_and_bad_format_refuses(self):
  source=ROOT/'ru/travel.html'
  for values in [[' M ru/travel.html'],['',''],['','ru/travel.html','']]:
   with self.subTest(values=values),patch.object(m,'source_for',return_value=source),patch.object(m,'git',side_effect=values):
    self.assertEqual(m.generated_lastmod(ROOT,'https://marsharbel.com/ru/travel',{}),'')
  with patch.object(m,'source_for',return_value=source),patch.object(m,'git',side_effect=['','ru/travel.html','10/09/2026']),self.assertRaises(ValueError):
   m.generated_lastmod(ROOT,'https://marsharbel.com/ru/travel',{})
 def test_missing_source_omits_but_other_source_errors_propagate(self):
  url='https://marsharbel.com/zz/history'
  with patch.object(m,'source_for',side_effect=ValueError('no source file for '+url+': expected zz/history.html')),patch.object(m,'git') as git:
   self.assertEqual(m.generated_lastmod(ROOT,url,{}),'');git.assert_not_called()
  with patch.object(m,'source_for',side_effect=ValueError('not a site URL: bad')),self.assertRaises(ValueError):
   m.generated_lastmod(ROOT,'bad',{})

class SitemapLastmodBaselineTests(unittest.TestCase):
 """Baseline-aware lastmod: byte-identical pages keep their base-ref date."""
 REL='ar/charbel-film-premiere.html'
 def _patch(self,values):
  return patch.object(lm,'git',side_effect=values)
 def test_identical_blob_keeps_baseline_date(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/self.REL
   with patch.object(m,'source_for',return_value=source):
    # status(clean), rev-parse HEAD:blob, rev-parse base:blob(same), log at baseline
    with self._patch(['','blobAAA','blobAAA','2026-10-10']) as git:
     self.assertEqual(lm.last_changed(root,source,baseline='origin/stage'),'2026-10-10')
     self.assertEqual(git.call_args.args,(root,'log','-1','--format=%as','origin/stage','--',self.REL))
 def test_changed_blob_uses_branch_history(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/self.REL
   with self._patch(['','blobAAA','blobBBB','2026-10-23']) as git:
    self.assertEqual(lm.last_changed(root,source,baseline='origin/stage'),'2026-10-23')
    self.assertEqual(git.call_args.args,(root,'log','-1','--format=%as','--',self.REL))
 def test_new_page_absent_at_baseline_uses_branch_history(self):
  import subprocess
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/self.REL
   with self._patch(['','blobAAA',subprocess.CalledProcessError(128,'git'),'2026-10-23']):
    self.assertEqual(lm.last_changed(root,source,baseline='origin/stage'),'2026-10-23')
 def test_dirty_file_still_today_with_baseline(self):
  from datetime import date
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/self.REL
   with self._patch([' M '+self.REL]):
    self.assertEqual(lm.last_changed(root,source,baseline='origin/stage'),date.today().isoformat())
 def test_no_baseline_keeps_legacy_convention(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/self.REL
   with patch.dict('os.environ',{},clear=True):
    with self._patch(['','2026-10-23']) as git:
     self.assertEqual(lm.last_changed(root,source), '2026-10-23')
     self.assertEqual(git.call_args.args,(root,'log','-1','--format=%as','--',self.REL))

if __name__=='__main__':unittest.main()
