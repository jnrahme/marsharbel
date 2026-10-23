"""Rosary guide certification stays closed until final QA and rejects drift."""
import json,re,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.reviewed_rosary_guide import rosary_guide_manifest,LOCALES,FAMILY

def _record():
 return json.loads((ROOT/'locales/rosary-guide-equivalence.json').read_text())

class RosaryGuideCertification(unittest.TestCase):
 def test_pending_gate_is_noop(self):
  record=_record();record['gateStatus']='pending-final-qa'
  marker={'pages':{'keep':{}}}
  from unittest.mock import patch
  original=json.loads
  with patch('i18n.reviewed_rosary_guide.json.loads',side_effect=lambda text:record if 'gateStatus' in text else original(text)):
   self.assertIs(rosary_guide_manifest(ROOT,{},marker),marker)
 def test_review_and_drift_and_supersede(self):
  record=_record()
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp)
   files={v['file'] for v in record['groups']['rosary-guide']['variants'].values()}
   files|={v['catalog'].split('#')[0] for v in record['groups']['rosary-guide']['variants'].values() if 'catalog' in v}
   files.add('locales/rosary-guide-review-record.json')
   files.add('locales/registry.json')
   for file in files:
    dst=root/file;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/file,dst)
   (root/'locales/rosary-guide-equivalence.json').write_text(json.dumps(record))
   seed={'pages':{}}
   for lang,v in record['groups']['rosary-guide']['variants'].items():
    seed['pages']['page-stale-'+lang]={'anchorIDs':{},'sourceSha256':'old','variants':{lang:{'path':v['path'],'status':'pending'}}}
   m=rosary_guide_manifest(root,{},seed)
   self.assertFalse([k for k in m['pages'] if k.startswith('page-stale-')])
   page=m['pages'][FAMILY]
   self.assertEqual({l for l,v in page['variants'].items() if v['status']=='verified'},{'en',*LOCALES})
   self.assertEqual(len(page['variants']),8)
   for lang,v in page['variants'].items():
    proof=v['proof']
    for key in ('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity'):
     self.assertTrue(proof[key],lang+' '+key)
    for key in ('editorialReview','nativeSampleReview','renderedReview'):
     self.assertRegex(proof[key],r'^[0-9a-f]{64}$')
   guard={'pages':{'page-multi':{'anchorIDs':{},'sourceSha256':'old','variants':{'de':{'path':record['groups']['rosary-guide']['variants']['de']['path'],'status':'pending'},'fr':{'path':'x','status':'pending'}}}}}
   with self.assertRaisesRegex(ValueError,'would replace'):
    rosary_guide_manifest(root,{},guard)
   first=record['groups']['rosary-guide']['variants']['de']
   with self.assertRaisesRegex(ValueError,'body drift'):
    rosary_guide_manifest(root,{root/first['file']:(root/first['file']).read_text().replace('<main','<main data-drift="yes"',1)},{'pages':{}})
   data=json.loads((root/first['catalog'].split('#')[0]).read_text())
   data['rosary']['title']='DRIFT'
   (root/first['catalog'].split('#')[0]).write_text(json.dumps(data))
   with self.assertRaisesRegex(ValueError,'catalog drift'):
    rosary_guide_manifest(root,{},{'pages':{}})
 def test_built_manifest_family_verified(self):
  src=(ROOT/'same-page-manifest.js').read_text()
  data=json.loads(re.search(r'=\s*(\{.*\})\s*;?\s*$',src,re.S).group(1))
  page=data['pages'][FAMILY]
  self.assertEqual({l for l,v in page['variants'].items() if v['status']=='verified'},{'en','de','es','fr','it','pl','pt','ar'})
  self.assertFalse([l for l,v in page['variants'].items() if v['status']=='pending'])
  self.assertFalse([(k,l) for k,f in data['pages'].items() if k!=FAMILY for l,v in f.get('variants',{}).items() if v.get('status')=='pending' and any(s in v.get('path','') for s in ('/en/rosary','rosenkranz','chapelet','rozaniec'))])
if __name__=='__main__':unittest.main()
