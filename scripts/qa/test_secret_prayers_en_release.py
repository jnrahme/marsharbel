import unittest,tempfile,shutil,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts/qa'))
from secret_prayers_en_policy import errors,load,RECORD,SLUGS
class SecretEN(unittest.TestCase):
 def test_candidate_isolation(self):self.assertEqual(errors(R),[])
 def test_policy_scope(self):self.assertEqual(set(load(R)['pages']),{s+'.html'for s in SLUGS})
 def fixture(self):
  from test_secret_prayers_ar_fr_release import SecretARFR
  case=SecretARFR();r=case.fixture();self.addCleanup(case.doCleanups);return r
 def test_each_foreign_sitemap_url_rejected(self):
  for code in load(R)['heldLocales']:
   for slug in SLUGS:
    r=self.fixture();(r/'sitemap.xml').write_text('<loc>https://marsharbel.com/'+code+'/'+slug+'</loc>');self.assertTrue(errors(r))
 def test_each_foreign_hreflang_rejected(self):
  for code in load(R)['heldLocales']:
   r=self.fixture();(r/'index.html').write_text('<link rel="alternate" hreflang="'+code+'" href="https://marsharbel.com/'+code+'/powerful-secret-prayers">');self.assertTrue(errors(r))
 def test_foreign_served_file_rejected(self):
  r=self.fixture();(r/'de').mkdir();(r/'de/powerful-secret-prayers.html').write_text('held');self.assertTrue(errors(r))
 def test_record_tamper_rejected(self):
  r=self.fixture();p=r/RECORD;p.write_text(p.read_text()+' ')
  with self.assertRaises(ValueError):load(r)
 def test_embedded_messages_match_active_bindings(self):
  import json,hashlib
  import sys
  sys.path.insert(0,str(R/'scripts'))
  from i18n.keyed_master import strip_static_fallback
  d=json.loads((R/'locales/en/terco-da-batalha-master-bindings.json').read_text())
  self.assertEqual(d['messages'],{b['key']:b['source']for b in d['bindings']})
  self.assertEqual(d['masterSha256'],hashlib.sha256(strip_static_fallback((R/d['master']).read_bytes())).hexdigest())
 def test_english_terco_source_fidelity(self):
  text=(R/'terco-da-batalha.html').read_text()
  for bad in ['Salve Rainha','Cruz sagrada','o poder do bem','sem adoecer']:self.assertNotIn(bad,text)
  for expected in ['Sem morrer, sem enlouquecer, sem muito me abater.','Eu hei de vencer. Jesus Cristo me ama e me resgata com Seu poder!','A vitória é nossa pelo sangue de Jesus! Amém.']:self.assertIn(expected,text)
 def test_fifth_page_not_exempt(self):
  from check_new_page_locales import check_page
  self.assertTrue(check_page(R,'fifth-secret-page.html',{'pageMirrors':{}},{'ar'}))
 def test_relative_www_and_directory_leaks_rejected(self):
  for url in ['/'+load(R)['heldLocales'][0]+'/powerful-secret-prayers','http://www.marsharbel.com/'+load(R)['heldLocales'][0]+'/terco-da-batalha/index.html']:
   r=self.fixture();(r/'sitemap.xml').write_text('<xhtml:link href="'+url+'"/>');self.assertTrue(errors(r))
 def test_open_graph_locale_leak_rejected(self):
  r=self.fixture();(r/'powerful-secret-prayers.html').write_text('<meta property="og:locale:alternate" content="de_DE">');self.assertTrue(errors(r))
if __name__=='__main__'  :unittest.main()
