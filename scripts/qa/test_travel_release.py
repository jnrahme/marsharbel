"""Optional release records fail closed; never treat pending work as evidence."""
import sys,tempfile,json,unittest,hashlib,copy,shutil,subprocess
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.travel_release import release_manifest, RELEASE_LOCALES
class ReleaseTests(unittest.TestCase):
 def test_absent_record_preserves_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   value={'pages':{}};self.assertIs(release_manifest(Path(d),{},value),value)
 def test_unapproved_record_refuses(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'locales').mkdir();(root/'locales/travel-release.json').write_text(json.dumps({'version':1,'status':'pending'}))
   with self.assertRaisesRegex(ValueError,'owner evidence'):release_manifest(root,{}, {'pages':{}})
 def test_release_locale_set_is_explicit(self):
  self.assertEqual(RELEASE_LOCALES, ('en','de','zh-Hans','ru','pl'))
 def test_ru_pl_travel_frame_removes_english_hub_duplicate(self):
  from i18n.travel_components import travel_frame
  from bs4 import BeautifulSoup
  registry=json.loads((ROOT/'locales/registry.json').read_text())
  for code in ('ru','pl'):
   registry['authoredMirrors']['travel']['routes'][code]='/'+code+'/travel'
   text='<html><head></head><body><header><div class="nav-group"><a class="nav-parent" href="/travel">Travel</a><div class="nav-sub"><a href="/travel">Travel</a><a href="/'+code+'/travel">Travel</a></div></div></header><main><h1>Fixture</h1></main></body></html>'
   from i18n.catalog import read_json
   def fixture_read(path):
    return read_json(ROOT/'locales/de/travel.json') if path == ROOT/f'locales/{code}/travel.json' else read_json(path)
   with patch('i18n.travel_components.read_json',side_effect=fixture_read):
    output=travel_frame(text,ROOT,code,'/'+code+'/travel',registry)
   soup=BeautifulSoup(output,'html.parser')
   self.assertFalse(soup.select('header a[href="/travel"]'))
   self.assertEqual(len(soup.select('header .nav-sub a[href="/'+code+'/travel"]')),1)
 def test_complete_positive_and_refusal_controls(self):
  from i18n.travel_metadata import travel_clusters
  from i18n.reviewed_history import digest
  from i18n.travel_release import catalog_paths
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'locales').mkdir()
   for name in ('registry.json','travel-routes.json'):shutil.copyfile(ROOT/'locales'/name,root/'locales'/name)
   # Fixture-only keyed registrations for the incoming complete RU/PL tabs.
   # Real catalogs/routes must still exist before a production release record.
   registry=json.loads((root/'locales/registry.json').read_text())
   for source,cluster in travel_clusters(root,registry).items():
    for code in ('ru','pl'):
     name=next(name for name,cfg in registry['pageMirrors'].items() if cfg['english']==source and 'de' in cfg.get('renderLocales',[]))
     registry['pageMirrors'][name]['routes'][code]='/'+code+source
     registry['pageMirrors'][name]['renderLocales'].append(code)
   (root/'locales/registry.json').write_text(json.dumps(registry))
   record={'version':1,'status':'approved','ownerEvidenceRefs':[{'channel':'WhatsApp','messageID':'fixture-user-evidence'}],'reviewedHead':'a'*40,'independentReviewRef':'fixture-review','nativeReviewStatus':'pending-post-release','nativeStatusAuthority':'added-process-safety','groups':{}}
   for source,cluster in travel_clusters(root,json.loads((root/'locales/registry.json').read_text())).items():
    group={'sourceRevision':'b'*40,'variants':{}}
    for code in RELEASE_LOCALES:
     route=cluster[code];file=route.strip('/')+'.html';p=root/file;p.parent.mkdir(exist_ok=True,parents=True);p.write_text('<html><main><p id="topic">Fixture</p></main></html>')
     pins=[]
     for catalog in catalog_paths(root,registry,source,code):
      target=root/catalog;target.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(ROOT/catalog if (ROOT/catalog).exists() else ROOT/catalog.replace('/'+code+'/', '/de/'),target)
      pins.append({'file':catalog,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
     group['variants'][code]={'file':file,'path':route,'bodySha256':digest(p.read_text()),'catalogs':pins,'checks':{k:True for k in ('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity')},'editorialReview':'fixture','renderedReview':'fixture','nativeFollowUp':'fixture'}
    record['groups'][source]=group
   subprocess.run(['git','init','-q'],cwd=root,check=True)
   subprocess.run(['git','add','.'],cwd=root,check=True)
   subprocess.run(['git','-c','user.email=fixture@example.invalid','-c','user.name=Fixture','commit','-qm','fixture'],cwd=root,check=True)
   head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();record['reviewedHead']=head
   for group in record['groups'].values():group['sourceRevision']=head
   path=root/'locales/travel-release.json';path.write_text(json.dumps(record));out=release_manifest(root,{}, {'pages':{}});self.assertEqual(len(out['pages']),14)
   self.assertEqual(set(out['pages']['travel-release-travel']['variants']),set(RELEASE_LOCALES))
   for code in ('ru','pl'):
    self.assertEqual(out['pages']['travel-release-travel']['variants'][code]['status'],'verified')
   existing={'sourcePath':'travel.html','sourceRevision':head,'sourceSha256':record['groups']['/travel']['variants']['en']['bodySha256'],'anchorIDs':{'prior':{'fr':'ancien'}},'variants':{'en':{'path':'/travel'},'fr':{'path':'/fr/travel','proof':{'old':'unchanged'},'status':'verified'}}}
   kept=release_manifest(root,{}, {'pages':{'old':existing}})['pages']['travel-release-travel'];self.assertEqual(kept['variants']['fr'],existing['variants']['fr']);self.assertEqual(kept['anchorIDs']['prior'],existing['anchorIDs']['prior'])
   pending={'sourcePath':'travel.html','sourceRevision':head,'sourceSha256':'c'*64,'anchorIDs':{},'variants':{'en':{'path':'/travel','status':'pending'}}}
   self.assertEqual(len(release_manifest(root,{}, {'pages':{'pending':pending}})['pages']),14)
   stale=copy.deepcopy(existing);stale['sourceSha256']='c'*64
   with self.assertRaisesRegex(ValueError,'reviewed other-locale source drift'):release_manifest(root,{}, {'pages':{'stale':stale}})
   resolver=ROOT/'same-page-resolver.js'
   result=subprocess.check_output(['node','-e',"const api=require(process.argv[1]);let m=JSON.parse(process.argv[2]);m.version=1;m.languages=['en','de','zh-Hans','ru','pl'];console.log(JSON.stringify(api.resolve(m,'https://marsharbel.com/travel','de','en')))",str(resolver),json.dumps(out)],text=True);self.assertTrue(json.loads(result)['available'])
   seed_outputs=[]
   for seed in ('1','2'):
    env=dict(__import__('os').environ,PYTHONHASHSEED=seed)
    driver="import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from i18n.travel_release import release_manifest;print(json.dumps(release_manifest(Path(sys.argv[2]),{}, {'pages':{}}),ensure_ascii=False))"
    seed_outputs.append(subprocess.check_output([sys.executable,'-c',driver,str(ROOT/'scripts'),str(root)],env=env))
   self.assertEqual(*seed_outputs,'enabled release must serialize identically across hash seeds')
   mutations=[lambda r:r['groups']['/travel']['variants'].pop('ru'),lambda r:r['groups']['/travel']['variants'].pop('pl'),lambda r:r['groups']['/travel']['variants'].update(fr=copy.deepcopy(r['groups']['/travel']['variants']['de'])),lambda r:r['groups']['/travel']['variants']['ru'].update(editorialReview=''),lambda r:r['groups']['/travel']['variants']['pl']['checks'].update(linkParity=False),lambda r:r['groups']['/travel']['variants']['de']['checks'].update(type='other',nativeSampleReview='invented'),lambda r:r.update(ownerEvidenceRefs={'fake':'value'}),lambda r:r.update(independentReviewRef=True),lambda r:r.update(reviewedHead='a'*40),lambda r:r['groups']['/travel'].update(sourceRevision='b'*40),lambda r:r.update(ownerEvidenceRefs=[]),lambda r:r.update(independentReviewRef=''),lambda r:r.update(nativeStatusAuthority='user-approved-deferral'),lambda r:r['groups'].pop('/travel'),lambda r:r['groups']['/travel']['variants']['de'].update(path='/fr/travel'),lambda r:r['groups']['/travel']['variants']['de'].update(bodySha256='c'*64),lambda r:r['groups']['/travel']['variants']['de'].update(catalogs=[]),lambda r:r['groups']['/travel']['variants']['de']['checks'].update(linkParity=False)]
   for mutate in mutations:
    bad=copy.deepcopy(record);mutate(bad);path.write_text(json.dumps(bad))
    with self.assertRaises(ValueError):release_manifest(root,{}, {'pages':{}})
if __name__=='__main__':unittest.main()
