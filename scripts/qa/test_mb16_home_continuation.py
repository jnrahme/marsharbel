"""Finite MB16 home discovery deltas, never broad hash refreshes."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n import mb16_home_continuation as m

class MB16HomeContinuation(unittest.TestCase):
    def setUp(self):
        self.originals={p:m.git(ROOT,'show',m.BASE+':'+p)for p in m.PATHS}
    def test_roundtrip_footer_alternate_and_combined(self):
        for path,raw in self.originals.items():
            for form in (None,'sorted','generator'):
                for alt in ((False,True)if path=='index.html'else(False,)):
                    self.assertEqual(m.verify_delta(path,raw,m.derive(path,raw,form,alt)),raw)
    def test_outside_and_inside_mutations_reject_regardless_of_hash(self):
        for path,raw in self.originals.items():
            good=m.derive(path,raw,'sorted',path=='index.html')
            for changed in (good.replace(b'<main',b'<main data-drift="1"',1),good.replace('简体中文'.encode(),b'Changed',1),good.replace(b'hreflang="zh-Hans"',b'hreflang="foreign"',1),good.replace(b'href="/zh-Hans/"',b'href="https://foreign.invalid/"',1),good.replace(b'<nav aria-label="Languages"',b'<nav data-extra="1" aria-label="Languages"',1)):
                forged={'sha256':m.sha(changed)}
                self.assertEqual(forged['sha256'],hashlib.sha256(changed).hexdigest())
                with self.assertRaises(ValueError):m.verify_delta(path,raw,changed)
    def test_no_delta_passthrough_is_not_outside_edit_normalization(self):
        temp,root,git,base=self.native_fixture()
        try:
            path='history.html';raw=self.originals[path]
            outside=raw.replace(b'<main',b'<main data-unreviewed="1"',1)
            (root/path).write_bytes(outside);git('add','.');git('commit','-qm','outside fixture')
            with patch.object(m,'BASE',base):
                self.assertEqual(m.preimage(root,path,outside),outside)
                self.assertNotEqual(m.sha(m.preimage(root,path,outside)),m.sha(raw))
                mixed=m.derive(path,outside,'sorted')
                (root/path).write_bytes(mixed)
                with self.assertRaises(ValueError):m.preimage(root,path,mixed)
        finally:temp.cleanup()

    def test_marker_and_alternate_negatives(self):
        raw=self.originals['index.html'];good=m.derive('index.html',raw,'sorted',True)
        a,z=m.span(good,b'i18n-navigation',b'footer');block=good[a:z]
        head_a,head_z=m.span(good,b'i18n-alternates',b'head');alt=good[head_a:head_z]
        cases=[good+block,good.replace(block,b'',1),block+good.replace(block,b'',1),good+alt,good.replace(alt,b'',1),good.replace(b'hreflang="zh-Hans" href="https://marsharbel.com/zh-Hans/"',b'hreflang="zh-Hans" href="https://foreign.invalid/"',1),good.replace(alt,alt.replace(b'hreflang="fr"',b'hreflang="extra"'),1)]
        lines=alt.splitlines();lines[1],lines[2]=lines[2],lines[1];cases.append(good.replace(alt,b'\n'.join(lines),1))
        for changed in cases:
            with self.assertRaises(ValueError):m.verify_delta('index.html',raw,changed)
        with self.assertRaises(ValueError):m.derive('history.html',self.originals['history.html'],add_alternate=True)
    def native_fixture(self):
        temp=tempfile.TemporaryDirectory();root=Path(temp.name)
        def git(*args):return subprocess.check_output(['git','-C',str(root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid',*args],stderr=subprocess.PIPE)
        git('init','-q')
        files={p:raw for p,raw in self.originals.items()}
        for p in [m.MODULE,'scripts/build-international.py','scripts/i18n/same_page_injection.py','locales/registry.json']:files[p]=(ROOT/p).read_bytes()
        for p,raw in files.items():(root/p).parent.mkdir(parents=True,exist_ok=True);(root/p).write_bytes(raw)
        git('add','.');git('commit','-qm','base');base=git('rev-parse','HEAD').decode().strip()
        record=json.loads((ROOT/m.RECORD).read_bytes());record['base']=base
        for key,p in [('registrySha256','locales/registry.json'),('generatorSha256','scripts/build-international.py'),('controlSha256','scripts/i18n/same_page_injection.py')]:record[key]=m.sha((root/p).read_bytes())
        (root/m.RECORD).write_text(json.dumps(record));git('add','.');git('commit','-qm','record')
        return temp,root,git,base
    def test_native_binding_no_memo_and_symlink_and_export(self):
        temp,root,git,base=self.native_fixture()
        try:
            path='visit-annaya.html';raw=self.originals[path];good=m.derive(path,raw,'sorted')
            with patch.object(m,'BASE',base):
                self.assertEqual(m.preimage(root,path,good),raw)
                (root/path).write_bytes(good);self.assertEqual(m.preimage(root,path,good),raw)
                (root/path).write_bytes(good.replace(b'<main',b'<main data-bad="1"',1))
                with self.assertRaises(ValueError):m.preimage(root,path,good)
                (root/path).write_bytes(raw)
                record=root/m.RECORD;old=record.read_bytes();record.unlink();record.symlink_to(root/'locales/registry.json')
                with self.assertRaises(ValueError):m.preimage(root,path,good)
                record.unlink();record.write_bytes(old)
                cfg=root/'locales/registry.json';original=cfg.read_bytes();r=json.loads(original);r['locales']['fr']['home']='/foreign/';cfg.write_text(json.dumps(r));data=json.loads(record.read_bytes());data['registrySha256']=m.sha(cfg.read_bytes());record.write_text(json.dumps(data));git('add','.');git('commit','-qm','forged registry hash')
                with self.assertRaises(ValueError):m.preimage(root,path,good)
                cfg.write_bytes(original);record.write_bytes(old);git('add','.');git('commit','-qm','restore fixture')
                (root/'.git').rename(root/'.git-hidden')
                with self.assertRaises(ValueError):m.preimage(root,path,good)
        finally:temp.cleanup()

if __name__=='__main__':unittest.main()
