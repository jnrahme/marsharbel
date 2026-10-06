"""Bounded Russian publication, complete master coverage, no invented twin proof."""
import sys,json,unittest,hashlib
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT,load_catalog,read_json,locale_topics
from i18n.page_mirror import render_page
from i18n.guarded_dom import translatable_nodes
class RussianSliceTests(unittest.TestCase):
 def test_bounded_routes_and_publication_sets(self):
  r,c=load_catalog(ROOT);self.assertEqual(locale_topics(r,'ru'),['biography'])
  self.assertEqual(r['locales']['ru']['nativeName'],'Русский');self.assertEqual(r['locales']['ru']['home'],'/ru/')
  for values in r['publicationSets'].values():self.assertNotIn('ru',values)
  self.assertEqual(sorted(p.relative_to(ROOT/'ru').as_posix()for p in (ROOT/'ru').rglob('*.html')),['22-chislo-mesyaca.html','annaya.html','biography.html','index.html','palomnichestvo.html'])
 def test_complete_history_not_short_guide(self):
  r,c=load_catalog(ROOT);x=read_json(ROOT/'locales/en/history-master-bindings.json');source=BeautifulSoup((ROOT/x['master']).read_text(),'html.parser');s=BeautifulSoup(render_page(ROOT,r,'ru','history-master','/ru/biography'),'html.parser')
  self.assertEqual(x['master'],'history.html');self.assertGreater(len(x['bindings']),200)
  self.assertEqual([n.name for n in source.select('main *')],[n.name for n in s.select('main *')if 'translation-note'not in n.get('class',[])])
  self.assertEqual([n.get('id')for n in source.select('main [id]')],[n.get('id')for n in s.select('main [id]')]);self.assertEqual([n['src'].removeprefix('./')for n in source.select('main img')],[n['src'].removeprefix('/')for n in s.select('main img')])
  copy=read_json(ROOT/'locales/ru/history-master-copy.json')
  for key,value in copy.items():
   if key.startswith(('history.hero.','history.death.','history.cause.')):self.assertIn(value,s.main.get_text(),key)
  self.assertIn('маронитский монах и священник',s.main.get_text());self.assertIn('Отче истины',s.main.get_text());self.assertIn('наш перевод с английского',s.main.get_text())
 def test_reciprocal_biography_cluster_and_home(self):
  r=read_json(ROOT/'locales/registry.json');expected={code:r['site']+route for code,route in r['pageMirrors']['history-master']['routes'].items()};expected.update(en=r['site']+'/history');expected['x-default']=r['site']+'/history'
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
