"""Optional release records fail closed; never treat pending work as evidence."""
import sys,tempfile,json,unittest,hashlib,copy,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.travel_release import release_manifest
class ReleaseTests(unittest.TestCase):
 def test_absent_record_preserves_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   value={'pages':{}};self.assertIs(release_manifest(Path(d),{},value),value)
 def test_unapproved_record_refuses(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'locales').mkdir();(root/'locales/travel-release.json').write_text(json.dumps({'version':1,'status':'pending'}))
   with self.assertRaisesRegex(ValueError,'owner evidence'):release_manifest(root,{}, {'pages':{}})
 def test_complete_positive_and_refusal_controls(self):
  from i18n.travel_metadata import travel_clusters
  from i18n.reviewed_history import digest
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'locales').mkdir()
   for name in ('registry.json','travel-routes.json'):shutil.copyfile(ROOT/'locales'/name,root/'locales'/name)
   record={'version':1,'status':'approved','ownerEvidenceRefs':['fixture-user-evidence'],'reviewedHead':'a'*40,'independentReviewRef':'fixture-review','nativeReviewStatus':'pending-post-release','nativeStatusAuthority':'added-process-safety','groups':{}}
   for source,cluster in travel_clusters(root,json.loads((root/'locales/registry.json').read_text())).items():
    group={'sourceRevision':'b'*40,'variants':{}}
    for code in ('en','de','zh-Hans'):
     route=cluster[code];file=route.strip('/')+'.html';p=root/file;p.parent.mkdir(exist_ok=True,parents=True);p.write_text('<html><main><p id="topic">Fixture</p></main></html>')
     catalog='locales/'+code+'-fixture.json';(root/catalog).write_text('{}')
     group['variants'][code]={'file':file,'path':route,'bodySha256':digest(p.read_text()),'catalogs':[{'file':catalog,'sha256':hashlib.sha256(b'{}').hexdigest()}],'checks':{k:True for k in ('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity')},'editorialReview':'fixture','renderedReview':'fixture','nativeFollowUp':'fixture'}
    record['groups'][source]=group
   path=root/'locales/travel-release.json';path.write_text(json.dumps(record));out=release_manifest(root,{}, {'pages':{}});self.assertEqual(len(out['pages']),14)
   mutations=[lambda r:r.update(ownerEvidenceRefs=[]),lambda r:r.update(independentReviewRef=''),lambda r:r.update(nativeStatusAuthority='user-approved-deferral'),lambda r:r['groups'].pop('/travel'),lambda r:r['groups']['/travel']['variants']['de'].update(path='/fr/travel'),lambda r:r['groups']['/travel']['variants']['de'].update(bodySha256='c'*64),lambda r:r['groups']['/travel']['variants']['de'].update(catalogs=[]),lambda r:r['groups']['/travel']['variants']['de']['checks'].update(linkParity=False)]
   for mutate in mutations:
    bad=copy.deepcopy(record);mutate(bad);path.write_text(json.dumps(bad))
    with self.assertRaises(ValueError):release_manifest(root,{}, {'pages':{}})
if __name__=='__main__':unittest.main()
