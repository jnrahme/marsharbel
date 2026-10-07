"""HI/TH launch truth: home/history only, explicit English fallback."""
import json,sys,unittest
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.home_mirror import render_home
from i18n.page_mirror import render_page
from i18n.catalog import locale_topics
from i18n.launch_availability import apply_launch_availability

class LimitedLaunch(unittest.TestCase):
 def setUp(self):self.r=json.loads((ROOT/'locales/registry.json').read_text())
 def test_only_home_and_history_registered(self):
  for lang in ('hi','th'):
   self.assertEqual(locale_topics(self.r,lang),[])
   self.assertEqual(self.r['locales'][lang]['slugs'],{})
   families=[name for name,cfg in self.r['pageMirrors'].items() if lang in cfg['routes']]
   self.assertEqual(families,['history-master'])
   for subset in self.r['publicationSets'].values():self.assertNotIn(lang,subset)
 def test_visible_availability_and_nonuse_of_dormant_copy(self):
  for lang in ('hi','th'):
   home=BeautifulSoup(render_home(ROOT,self.r,lang),'html.parser')
   copy=json.loads((ROOT/f'locales/{lang}/launch-availability.json').read_text())
   self.assertEqual(home.select_one('.launch-availability h2').get_text(),copy['availability.heading'])
   self.assertEqual(home.select_one('.launch-availability p').get_text(),copy['availability.note'])
   dormant=json.loads((ROOT/f'locales/{lang}/common.json').read_text())
   for key,value in dormant.items():
    if key.startswith('home.'):self.assertNotIn(value,str(home),key)
   self.assertIn(f'/{lang}/history',{a['href'] for a in home.select('a[href]')})
   history=BeautifulSoup(render_page(ROOT,self.r,lang,'history-master',f'/{lang}/history'),'html.parser')
   for page in (home,history):
    for a in page.select('header a[href],main a[href]'):
     u=urlsplit(a['href'])
     if u.scheme or not u.path or a.has_attr('hreflang') or u.path in (f'/{lang}/',f'/{lang}/history') or not a.get_text(strip=True):continue
     file=ROOT/u.path.strip('/');file=file/'index.html' if u.path.endswith('/') else file.with_suffix('.html')
     if file.is_file():self.assertIn(copy['availability.englishQualifier'],a.get_text(),str(a))
   self.assertEqual(apply_launch_availability(str(home),ROOT,self.r,'de',True),str(home))
 def test_existing_locale_identity_and_pt_br_preserved(self):
  self.assertEqual(self.r['locales']['pt']['ogLocale'],'pt_BR')
  for lang in ('ar','fr','es','pt','it','de','pl','ru'):
   self.assertIn(lang,self.r['homepageMirrors']['renderLocales'])
   self.assertIn(lang,self.r['pageMirrors']['history-master']['routes'])
if __name__=='__main__':unittest.main()
