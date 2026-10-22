"""Eucharistic miracles certification stays closed until final QA and rejects drift."""
import json,re,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.reviewed_eucharistic import eucharistic_manifest,EXTEND,LOCALES

def _record():
 return json.loads((ROOT/'locales/eucharistic-equivalence.json').read_text())

def _seed(record):
 return {'pages':{'ar2-'+family+'-equivalence':{'anchorIDs':{},'sourceSha256':'seed',
  'variants':{lang:{'path':group['variants'][lang]['path'],'status':'verified'} for lang in ('en','ar')}}
  for family,group in record['groups'].items()}}

class EucharisticCertification(unittest.TestCase):
 def test_pending_gate_is_noop(self):
  record=_record();record['gateStatus']='pending-final-qa'
  marker=_seed(_record())
  from unittest.mock import patch
  original=json.loads
  with patch('i18n.reviewed_eucharistic.json.loads',side_effect=lambda text:record if 'gateStatus' in text else original(text)):
   self.assertIs(eucharistic_manifest(ROOT,{},marker),marker)
 def test_requires_ar2_family(self):
  record=_record()
  with self.assertRaisesRegex(ValueError,'expected AR-2 family missing'):
   eucharistic_manifest(ROOT,{},{'pages':{}})
 def test_review_and_drift_and_supersede(self):
  record=_record()
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp)
   files={v['file'] for g in record['groups'].values() for v in g['variants'].values()}
   files|={v['catalog'] for g in record['groups'].values() for v in g['variants'].values() if 'catalog' in v}
   files.add('locales/eucharistic-review-record.json')
   for file in files:
    dst=root/file;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/file,dst)
   (root/'locales/eucharistic-equivalence.json').write_text(json.dumps(record))
   seed=_seed(record)
   # a stale single-variant pending row must be superseded
   victim=next(iter(record['groups'].values()))['variants']['de']['path']
   seed['pages']['page-stale']={'anchorIDs':{},'sourceSha256':'old','variants':{'de':{'path':victim,'status':'pending'}}}
   m=eucharistic_manifest(root,{},seed)
   self.assertNotIn('page-stale',m['pages'])
   total_new=0
   for family in record['groups']:
    page=m['pages']['ar2-'+family+'-equivalence']
    self.assertEqual({l for l,v in page['variants'].items() if v['status']=='verified'},{'en','ar',*EXTEND})
    total_new+=len(EXTEND)
    for lang in EXTEND:
     proof=page['variants'][lang]['proof']
     for key in ('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity'):
      self.assertTrue(proof[key],family+' '+lang+' '+key)
     for key in ('editorialReview','nativeSampleReview','renderedReview'):
      self.assertRegex(proof[key],r'^[0-9a-f]{64}$')
   self.assertEqual(total_new,66)
   # loud guard: never replace a multi-variant family
   guard=_seed(record)
   guard['pages']['page-multi']={'anchorIDs':{},'sourceSha256':'old','variants':{'de':{'path':victim,'status':'pending'},'fr':{'path':'x','status':'pending'}}}
   with self.assertRaisesRegex(ValueError,'non-pending family|would replace'):
    eucharistic_manifest(root,{},guard)
   first=record['groups'][next(iter(record['groups']))]['variants']['de']
   with self.assertRaisesRegex(ValueError,'body drift'):
    eucharistic_manifest(root,{root/first['file']:(root/first['file']).read_text().replace('<main','<main data-drift="yes"',1)},_seed(record))
   (root/first['catalog']).write_text('{}')
   with self.assertRaisesRegex(ValueError,'catalog drift'):
    eucharistic_manifest(root,{},_seed(record))
 def test_built_manifest_families_fully_verified(self):
  src=(ROOT/'same-page-manifest.js').read_text()
  data=json.loads(re.search(r'=\s*(\{.*\})\s*;?\s*$',src,re.S).group(1))
  pages=data['pages']
  families={k:v for k,v in pages.items() if k.startswith('ar2-eucharistic-')}
  self.assertEqual(len(families),11)
  for key,page in families.items():
   verified={l for l,v in page['variants'].items() if v['status']=='verified'}
   self.assertEqual(verified,{'en','ar','de','es','fr','it','pl','pt'},key)
   self.assertFalse([l for l,v in page['variants'].items() if v['status']=='pending'],key)
  self.assertFalse([k for k in pages if 'eucharistic' in k and not k.startswith('ar2-eucharistic-')])
if __name__=='__main__':unittest.main()
