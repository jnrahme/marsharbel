"""First prayer batch keeps full-master shape and one narrow empty-copy slot."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.page_mirror import render_page
from i18n.mirror_structure import check_pair
from i18n.catalog import read_json
class PrayerKeyedMasters(unittest.TestCase):
 def test_reviewed_english_entries_are_not_redirected(self):
  from verify_deployment import redirected_pages
  r=read_json(ROOT/'locales/registry.json')
  redirected=redirected_pages(ROOT)
  for family in ('saint-charbel-prayers-master','saint-charbel-novena-master'):
   entry=ROOT/(r['pageMirrors'][family]['english'].lstrip('/')+'.html')
   self.assertNotIn(entry,redirected,'Redirecting a reviewed EN entry bypasses its exact-twin family')
 def test_six_routes_match_frozen_masters(self):
  r=read_json(ROOT/'locales/registry.json')
  for family in ('saint-charbel-prayers-master','saint-charbel-novena-master'):
   master=ROOT/read_json(ROOT/f'locales/en/{family}-bindings.json')['master']
   for lang,route in r['pageMirrors'][family]['routes'].items():
    from i18n.prayer_runtime import share_head
    self.assertEqual(check_pair(share_head(master.read_text(),ROOT,'en',family=='saint-charbel-prayers-master'),render_page(ROOT,r,lang,family,route),r['pageMirrors'][family]['english'],route),[])
 def test_metadata_preserves_existing_bodies(self):
  import hashlib,re
  contract=read_json(ROOT/'locales/prayer-metadata-contract.json')
  for file,proof in contract['files'].items():
   body=re.search(r'<main\b[\s\S]*?</main>',(ROOT/file).read_text())[0]
   self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),proof['mainSha256'],file)
 def test_metadata_reciprocity_and_indexability(self):
  from bs4 import BeautifulSoup
  from i18n.prayer_metadata import compose_prayer_clusters
  r=read_json(ROOT/'locales/registry.json')
  outputs=compose_prayer_clusters(ROOT,r,{})
  self.assertEqual(outputs,compose_prayer_clusters(ROOT,r,outputs))
  for family in ('saint-charbel-prayers-master','saint-charbel-novena-master'):
   cfg=r['pageMirrors'][family]
   expected={code:r['site']+route for code,route in cfg['discoveryRoutes'].items()}
   for route in set(cfg['discoveryRoutes'].values()):
    soup=BeautifulSoup(outputs[ROOT/(route.lstrip('/')+'.html')],'html.parser')
    self.assertEqual({n['hreflang']:n['href'] for n in soup.select('head link[hreflang]')},expected)
    if family=='saint-charbel-prayers-master' and route in [cfg['english'],*cfg['routes'].values()]:
     self.assertFalse(any('noindex' in n.get('content','') for n in soup.select('meta[name=robots]')))
  legacy=BeautifulSoup(outputs[ROOT/'en/prayers.html'],'html.parser')
  self.assertEqual({n['hreflang']:n['href']for n in legacy.select('head link[hreflang]')},{c:r['site']+'/en/prayers'for c in ('en','x-default')})
 def test_retired_writers_leave_remaining_locales(self):
  from i18n.mirror import render_mirrors
  r=read_json(ROOT/'locales/registry.json')
  retired={ROOT/(route.lstrip('/')+'.html')for route in r['pageMirrors']['saint-charbel-prayers-master']['routes'].values()}
  legacy=render_mirrors(ROOT,r,retired_routes=retired)
  self.assertTrue(retired.isdisjoint(legacy))
  for file in ('en/prayers.html','es/oraciones.html','pl/modlitwy.html'):
   self.assertIn(ROOT/file,legacy)
  import importlib.util
  spec=importlib.util.spec_from_file_location('prayer_builder',ROOT/'scripts/build-international.py')
  builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
  from unittest.mock import patch
  real=builder.render
  calls=[]
  def record(registry,catalog,code,template,topic=None):
   calls.append((code,topic));return real(registry,catalog,code,template,topic)
  with patch.object(builder,'render',side_effect=record):builder.outputs(ROOT)
  for code in ('ar','de','fr','ru','pt','it'):
   for topic in ('prayers','novena'):self.assertNotIn((code,topic),calls)
  for code in ('es','pl'):self.assertIn((code,'novena'),calls)
 def test_empty_slot_is_arabic_day6_only(self):
  r=read_json(ROOT/'locales/registry.json');family='saint-charbel-novena-master';ar=read_json(ROOT/f'locales/ar/{family}-copy.json')
  self.assertEqual(ar['saint-charbel-novena.traditional.day-6.collect.placeholder'],'')
  render_page(ROOT,r,'ar',family,r['pageMirrors'][family]['routes']['ar'],ar)
  ar[next(k for k,v in ar.items()if v)]=''
  with self.assertRaisesRegex(ValueError,'empty'):render_page(ROOT,r,'ar',family,r['pageMirrors'][family]['routes']['ar'],ar)
  de=read_json(ROOT/f'locales/de/{family}-copy.json');de['saint-charbel-novena.traditional.day-6.collect.placeholder']=''
  with self.assertRaisesRegex(ValueError,'empty'):render_page(ROOT,r,'de',family,r['pageMirrors'][family]['routes']['de'],de)
if __name__=='__main__':unittest.main()
