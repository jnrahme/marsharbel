import copy,hashlib,json,sys,tempfile,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import annaya_hero_evidence as m,travel_variant_evidence as old
class AnnayaEvidence(unittest.TestCase):
 def setUp(self):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name);(self.root/'locales/en').mkdir(parents=True)
  self.before='<html><main><section class="hero"><h1>Old</h1></section><section><p>Frozen narrative</p></section></main></html>'
  self.raw=self.before.replace('class="hero"','class="annaya-tour-hero"').replace('>Old<','>New<');(self.root/'annaya-tour.html').write_text(self.raw)
  self.catalogs={f'locales/en/{f}-{s}.json':'{}' for f in m.FAMILIES for s in ('bindings','copy')}
  for path,text in self.catalogs.items():(self.root/path).write_text(text)
  ev={'amendmentSchema':m.SCHEMA,'state':'approved','scope':m.SCOPE,'nativeReviewStatus':'not-certified','renderedReview':'independent-pixels','catalogReview':'independent-copy','preparedRevision':'a'*40,'baseRevision':'b'*40,'candidateFileSha256':m.sha(self.raw),'bodySha256':m.digest(self.raw),'masterSha256':m.sha(self.raw),'catalogDigests':{p:m.sha(t) for p,t in self.catalogs.items()}}
  self.v={'file':'annaya-tour.html','path':'/annaya-tour','candidateFileSha256':m.sha(self.raw),'bodySha256':m.digest(self.raw),'reviewEvidence':ev}
  self.table={'schema':m.SCHEMA,'groups':{f:{code:copy.deepcopy(ev) for code in codes} for f,codes in m.FAMILIES.items()}}
 def check(self,v=None,text=None,table=None,unset=False,blob=None):
  raw=json.dumps(table or self.table).encode();(self.root/m.TABLE).write_bytes(raw)
  def source(root,ref,path):
   if path in self.catalogs:return self.catalogs[path]
   return self.before if ref=='b'*40 else self.raw
  with patch.object(m,'REVIEW_TABLE_SHA256',None if unset else hashlib.sha256(raw).hexdigest()),patch.object(old,'blob',side_effect=blob or source):return m.validate_variant(self.root,'annaya-tour-travel-master','en',v or self.v,text or self.raw)
 def test_exact_review_passes(self):self.assertEqual(self.check()['state'],'approved')
 def test_unset_table_refuses(self):
  with self.assertRaisesRegex(ValueError,'unset'):self.check(unset=True)
 def test_tampered_digest_refuses(self):
  v=copy.deepcopy(self.v);v['candidateFileSha256']='0'*64
  with self.assertRaises(ValueError):self.check(v=v)
 def test_wrong_scope_state_native_refuses(self):
  for key,value in [('scope','other'),('state','pending'),('nativeReviewStatus','certified')]:
   v=copy.deepcopy(self.v);table=copy.deepcopy(self.table);v['reviewEvidence'][key]=value;table['groups']['annaya-tour-travel-master']['en'][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):self.check(v=v,table=table)
 def test_extra_locale_refuses(self):
  for family,codes in [('annaya-tour-travel-master',('en','de','ru','zh-Hans')),('annaya-tour-zh-travel-master',('en','zh-Hans','ar'))]:
   with self.assertRaises(ValueError):m.validate_group(family,{'evidenceSchema':m.SCHEMA,'variants':dict.fromkeys(codes,{})})
 def test_nonhero_changed_refuses_even_reapproved_hash(self):
  self.raw=self.raw.replace('Frozen narrative','Wrong narrative');(self.root/'annaya-tour.html').write_text(self.raw)
  ev=self.v['reviewEvidence'];ev.update(candidateFileSha256=m.sha(self.raw),bodySha256=m.digest(self.raw),masterSha256=m.sha(self.raw));self.v.update(candidateFileSha256=m.sha(self.raw),bodySha256=m.digest(self.raw));self.table['groups']['annaya-tour-travel-master']['en']=copy.deepcopy(ev)
  with self.assertRaisesRegex(ValueError,'non-hero'):self.check()
 def test_stale_base_ancestor_refuses(self):
  with self.assertRaises(ValueError):self.check(blob=lambda *args: (_ for _ in ()).throw(ValueError('Missing/nonancestor base')))
 def test_post_review_full_file_refuses(self):
  with self.assertRaises(ValueError):self.check(text=self.raw.replace('<html>','<html data-drift="x">'))
 def test_master_catalog_drift_refuses(self):
  (self.root/next(iter(self.catalogs))).write_text('{"x":1}')
  with self.assertRaisesRegex(ValueError,'catalog'):self.check()
 def test_missing_candidate_object_post_squash_passes_and_tamper_fails(self):
  def only_base(root,ref,path):
   if ref!='b'*40:raise ValueError('Candidate object deleted')
   return self.before
  self.assertEqual(self.check(blob=only_base)['state'],'approved')
  (self.root/'annaya-tour.html').write_text(self.raw.replace('New','Tamper'))
  with self.assertRaises(ValueError):self.check(blob=only_base)
 def test_variant_cannot_select_schema_by_scope(self):
  with self.assertRaises(ValueError):old.validate_variant(self.root,'annaya-tour-travel-master','en',self.v,self.raw)
 def test_actual_squash_clone_without_candidate_object(self):
  subprocess.run(['git','init','-q',str(self.root)],check=True)
  def git(*args):return subprocess.check_output(['git',*args],cwd=self.root).decode().strip()
  git('config','user.email','fixture@example.invalid');git('config','user.name','Fixture')
  (self.root/'annaya-tour.html').write_text(self.before);git('add','.');git('commit','-qm','stage base');base=git('rev-parse','HEAD')
  git('checkout','-qb','candidate');(self.root/'annaya-tour.html').write_text(self.raw);git('commit','-qam','candidate');candidate=git('rev-parse','HEAD')
  git('checkout','-q','master');git('merge','--squash','candidate');git('commit','-qm','stage squash');git('branch','-D','candidate');git('reflog','expire','--expire=now','--all');git('gc','--prune=now')
  with tempfile.TemporaryDirectory() as tmp:
   clone=Path(tmp)/'stage';subprocess.run(['git','clone','-q','--no-local',str(self.root),str(clone)],check=True)
   missing=subprocess.run(['git','cat-file','-e',candidate],cwd=clone,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);self.assertNotEqual(missing.returncode,0)
   self.root=clone
   self.v['reviewEvidence'].update(baseRevision=base,preparedRevision=candidate)
   self.table['groups']['annaya-tour-travel-master']['en']=copy.deepcopy(self.v['reviewEvidence'])
   self.assertEqual(self.check(blob=old.blob)['state'],'approved')
   (clone/'annaya-tour.html').write_text(self.raw.replace('New','Tampered'))
   with self.assertRaises(ValueError):self.check(blob=old.blob)
 def test_cross_family_locale_refuses(self):
  for family,code in [('annaya-tour-travel-master','zh-Hans'),('annaya-tour-zh-travel-master','de')]:
   with self.assertRaisesRegex(ValueError,'extra locale/family'):m.validate_variant(self.root,family,code,self.v,self.raw)
 def test_table_tamper_refuses(self):
  raw=json.dumps(self.table).encode();(self.root/m.TABLE).write_bytes(raw+b' ')
  with patch.object(m,'REVIEW_TABLE_SHA256',hashlib.sha256(raw).hexdigest()),self.assertRaisesRegex(ValueError,'edited'):m.validate_variant(self.root,'annaya-tour-travel-master','en',self.v,self.raw)
 def test_snapshot_outside_repository_only(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('snapshot',ROOT/'scripts/i18n/snapshot_annaya_hero_unreviewed.py');snap=importlib.util.module_from_spec(spec);spec.loader.exec_module(snap)
  with self.assertRaisesRegex(ValueError,'outside'):snap.snapshot(ROOT,ROOT/'UNREVIEWED')
 def test_zh_exact_group_accepted(self):m.validate_group('annaya-tour-zh-travel-master',{'evidenceSchema':m.SCHEMA,'variants':{'en':{},'zh-Hans':{}}})
if __name__=='__main__':unittest.main()
