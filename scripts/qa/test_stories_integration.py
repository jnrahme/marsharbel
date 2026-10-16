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

    def test_stories_capability_is_exact(self):
        cfg={'english':'/stories','master':'templates/masters/stories.html'}
        self.assertEqual(mirror_tab('pageMirrors','stories-master',cfg),'stories')
        for group, name, bad in [('authoredMirrors','stories-master',cfg),('pageMirrors','other',cfg),('pageMirrors','stories-master',{'english':'/other'}),('pageMirrors','stories-master',{'english':'/stories','master':'other.html'})]:
            self.assertIsNone(mirror_tab(group,name,bad))

    def test_source_drift_and_false_review_are_refused(self):
        real_load = json.loads
        for mutate in [lambda r:r.update(reviewStatus='pending'), lambda r:r.update(masterSha256='0'*64),lambda r:r.update(verdictSha256='0'*64),lambda r:r['sourceFiles'].pop('templates/masters/stories.html'),lambda r:r['sourceFiles'].update({'templates/masters/stories.html':'0'*64})]:
            record=copy.deepcopy(self.record);mutate(record)
            with patch('i18n.reviewed_stories.json.loads',return_value=record), self.assertRaises(ValueError):
                stories_manifest(ROOT,{},self.base)

if __name__ == '__main__':unittest.main()
