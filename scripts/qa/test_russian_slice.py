"""Bounded Russian publication, complete master coverage, no invented twin proof."""
import sys,json,unittest,hashlib
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT,load_catalog,read_json,locale_topics
from i18n.exact_master import render_exact
from i18n.guarded_dom import translatable_nodes
class RussianSliceTests(unittest.TestCase):
 def test_bounded_routes_and_publication_sets(self):
  r,c=load_catalog(ROOT);self.assertEqual(locale_topics(r,'ru'),['biography'])
  self.assertEqual(r['locales']['ru']['nativeName'],'Русский');self.assertEqual(r['locales']['ru']['home'],'/ru/')
  for values in r['publicationSets'].values():self.assertNotIn('ru',values)
  self.assertEqual(sorted(p.relative_to(ROOT/'ru').as_posix()for p in (ROOT/'ru').rglob('*.html')),['biography.html','index.html'])
 def test_complete_history_not_short_guide(self):
  r,c=load_catalog(ROOT);x=read_json(ROOT/'locales/ru/biography-exact.json');source=BeautifulSoup((ROOT/x['master']).read_text(),'html.parser');s=BeautifulSoup(render_exact(ROOT,r,'ru','biography','/ru/biography'),'html.parser')
  self.assertEqual(x['master'],'history.html');self.assertEqual(len(x['slots']),len(translatable_nodes(source.main)));self.assertGreater(len(x['slots']),200)
  self.assertEqual([n.name for n in source.select('main *')],[n.name for n in s.select('main *')if 'translation-note'not in n.get('class',[])])
  self.assertEqual([n.get('id')for n in source.select('main [id]')],[n.get('id')for n in s.select('main [id]')]);self.assertEqual([n['src'].removeprefix('./')for n in source.select('main img')],[n['src'].removeprefix('/')for n in s.select('main img')])
  self.assertIn('не православный',s.main.get_text());self.assertIn('в общении с Римом',s.main.get_text());self.assertIn('Father of truth',s.main.get_text());self.assertNotIn('Отец истины',s.main.get_text())
 def test_reciprocal_biography_cluster_and_home(self):
  expected={'en':'https://marsharbel.com/history','de':'https://marsharbel.com/de/biografie','ru':'https://marsharbel.com/ru/biography','x-default':'https://marsharbel.com/history'}
  for p in ('history.html','de/biografie.html','ru/biography.html'):
   s=BeautifulSoup((ROOT/p).read_text(),'html.parser');self.assertEqual({x['hreflang']:x['href']for x in s.select('head link[hreflang]')},expected)
  r=read_json(ROOT/'locales/registry.json');expected={code:r['site']+cfg['home']for code,cfg in r['locales'].items()};expected['x-default']=r['site']+'/'
  for code,cfg in r['locales'].items():
   s=BeautifulSoup((ROOT/('index.html'if code=='en'else code+'/index.html')).read_text(),'html.parser');self.assertEqual({x['hreflang']:x['href']for x in s.select('head link[hreflang]')},expected)
 def test_pending_only_and_no_placeholder_destinations(self):
  m=read_json(ROOT/'locales/same-page-manifest.pending.json');self.assertIn('ru',m['languages']);ru=[]
  for p in m['pages'].values():
   for lang,v in p['variants'].items():
    self.assertEqual(v['status'],'pending');self.assertEqual(v['proof'],{})
    if lang=='ru':ru.append(v['path'])
  self.assertEqual(sorted(ru),['/ru/','/ru/biography'])
  for file in (ROOT/'ru').glob('*.html'):
   s=BeautifulSoup(file.read_text(),'html.parser')
   for a in s.select('a[href]'):
    href=a['href'];self.assertNotEqual(href,'#')
    if href.startswith('#'):self.assertIsNotNone(s.find(id=href[1:]))
    if href.startswith('/'):
     path=href.split('#')[0].split('?')[0];candidates=[ROOT/(path.lstrip('/')+'index.html'if path.endswith('/')else path.lstrip('/')+'.html'),ROOT/path.lstrip('/')];self.assertTrue(any(p.exists()for p in candidates),href)
