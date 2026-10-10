"""Missing date uses clean git author date; carried dates never drift."""
import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import sitemap_dates as m
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
if __name__=='__main__':unittest.main()
