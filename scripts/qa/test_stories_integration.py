"""Accepted Stories evidence is input, not producer-created native approval."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.reviewed_stories import stories_manifest, CODES
from i18n.catalog import mirror_tab

class StoriesIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT/'locales/stories-equivalence.json').read_text())
        self.base = {'pages':{}}

    def test_accepted_source_inventory(self):
        import hashlib
        self.assertEqual(len(self.record['sourceFiles']),25)
        for path, digest in self.record['sourceFiles'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        self.assertEqual(set(self.record['variants']),set(CODES))
        self.assertEqual(self.record['releaseStatus'],'held')

    def test_coherent_table_reseals_are_refused(self):
        import hashlib
        cases = [('locales/de/stories-master-copy.json', b'edited German catalog'),
                 ('templates/masters/stories.html', b'edited frozen master'),
                 ('de/stories.html', b'<main>edited German MAIN</main>')]
        for name, edited in cases:
            record=copy.deepcopy(self.record)
            texts={ROOT/name:edited.decode()}
            if name == 'de/stories.html':
                from i18n.reviewed_history import digest
                record['variants']['de']['bodySha256']=digest(edited.decode())
            else:
                record['sourceFiles'][name]=hashlib.sha256(edited).hexdigest()
            raw=json.dumps(record,ensure_ascii=False,indent=2).encode()+b'\n'
            real_bytes=Path.read_bytes
            real_text=Path.read_text
            def read_bytes(path):
                if path.name=='stories-equivalence.json':return raw
                if path==ROOT/name:return edited
                return real_bytes(path)
            def read_text(path,*args,**kwargs):
                if path.name=='stories-equivalence.json':return raw.decode()
                if path==ROOT/name:return edited.decode()
                return real_text(path,*args,**kwargs)
            with patch.object(Path,'read_bytes',read_bytes), patch.object(Path,'read_text',read_text), self.assertRaisesRegex(ValueError,'evidence table edited'):
                stories_manifest(ROOT,texts,self.base)

    def test_stories_capability_is_exact(self):
        cfg={'english':'/stories','master':'templates/masters/stories.html'}
        self.assertEqual(mirror_tab('pageMirrors','stories-master',cfg),'stories')
        for group, name, bad in [('authoredMirrors','stories-master',cfg),('pageMirrors','other',cfg),('pageMirrors','stories-master',{'english':'/other'}),('pageMirrors','stories-master',{'english':'/stories','master':'other.html'})]:
            self.assertIsNone(mirror_tab(group,name,bad))

    def test_stories_cannot_expand_chinese_capabilities(self):
        from i18n.catalog import validate_registry,validate_mirror_capabilities
        base=json.loads((ROOT/'locales/registry.json').read_text())
        for kind in ('family','name','master','route','home','topic'):
            r=copy.deepcopy(base)
            if kind=='family':r['authoredMirrors']['stories-master']=r['pageMirrors'].pop('stories-master')
            elif kind=='name':r['pageMirrors']['other']=r['pageMirrors'].pop('stories-master')
            elif kind=='master':r['pageMirrors']['stories-master']['master']='history.html'
            elif kind=='route':r['pageMirrors']['stories-master']['routes']['zh-Hans']='/zh-Hans/other'
            elif kind=='home':r['locales']['zh-Hans']['capabilities']['home']=True
            else:r['locales']['zh-Hans']['capabilities']['topicGuides']=['biography']
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                validate_registry(r)
                validate_mirror_capabilities(ROOT,r)

    def test_source_drift_and_false_review_are_refused(self):
        real_load = json.loads
        for mutate in [lambda r:r.update(reviewStatus='pending'), lambda r:r.update(masterSha256='0'*64),lambda r:r.update(verdictSha256='0'*64),lambda r:r['sourceFiles'].pop('templates/masters/stories.html'),lambda r:r['sourceFiles'].update({'templates/masters/stories.html':'0'*64})]:
            record=copy.deepcopy(self.record);mutate(record)
            with patch('i18n.reviewed_stories.json.loads',return_value=record), self.assertRaises(ValueError):
                stories_manifest(ROOT,{},self.base)

if __name__ == '__main__':unittest.main()
