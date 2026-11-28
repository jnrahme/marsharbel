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
    def test_actual_generator_and_control_serializers(self):
        import importlib.util
        from i18n.same_page_injection import inject_control
        spec=importlib.util.spec_from_file_location('mb16_serializer_builder',ROOT/'scripts/build-international.py')
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        manifest=json.loads((ROOT/'same-page-manifest.js').read_text().removeprefix('window.SC_SAME_PAGE_MANIFEST = ').rstrip(';\n'))
        copy=json.loads((ROOT/'locales/same-page-copy.json').read_text())
        for path,raw in self.originals.items():
            text=builder.replace_block(raw.decode(),'i18n-navigation',builder.footer_locale_bar(registry))
            if path=='index.html':text=builder.replace_block(text,'i18n-alternates',builder.alternate_links(registry))
            self.assertEqual(m.verify_delta(path,raw,text.encode()),raw)
            final=inject_control(text,ROOT,manifest,copy)
            self.assertEqual(m.verify_delta(path,raw,final.encode()),raw)

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
    def test_exact_generated_saint_composition_and_fail_closed(self):
        from i18n import mb16_saint_home as saint
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [saint.MODULE, *saint.INPUTS]:
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
            # A new finite test date, with existing fixture copy. No claim of
            # reviewed editorial content is made by this generator proof.
            manifest = json.loads((root / 'locales/saint-of-day.json').read_text())
            copy_path = root / 'locales/en/saint-of-day.json'
            copies = json.loads(copy_path.read_text())
            old = sorted(manifest['entries'])[0]
            manifest['entries'] = {'2026-11-25': manifest['entries'][old]}
            copies = {'2026-11-25': copies[old]}
            (root / 'locales/saint-of-day.json').write_text(json.dumps(manifest))
            copy_path.write_text(json.dumps(copies))
            original = self.originals['index.html']
            good = m.derive('index.html', original, 'sorted', True)
            a, z = saint.span(good)
            candidate = good[:a] + saint.generated_block(root) + good[z:]
            restored = saint.restore(root, original, candidate)
            self.assertEqual(m.verify_delta('index.html', original, restored), original)
            pinned = saint.reapply(original, candidate)
            self.assertNotEqual(pinned, original)
            self.assertEqual(saint.reapply(restored, candidate), candidate)
            for bad in (candidate.replace(b'<main', b'<main data-drift="1"', 1),
                        candidate.replace(b'href="/zh-Hans/"', b'href="/foreign/"', 1)):
                with self.assertRaises(ValueError):
                    m.verify_delta('index.html', original, saint.restore(root, original, bad))
            for bad in (candidate.replace(b'data-saint-date="2026-11-25"', b'data-saint-date="2026-11-26"', 1),
                        candidate + saint.START, candidate.replace(saint.END, b'', 1),
                        candidate.replace(b'<!-- saint-of-day:start -->', b'', 1)):
                with self.assertRaises(ValueError): saint.restore(root, original, bad)
            template = root / 'templates/saint-of-day/home.html'
            raw = template.read_bytes()
            template.write_bytes(raw + b' ')
            with self.assertRaisesRegex(ValueError, 'fixed generator/template changed'):
                saint.restore(root, original, candidate)
            template.write_bytes(raw)
            template.rename(template.with_suffix('.held'))
            template.symlink_to(template.with_suffix('.held'))
            with self.assertRaisesRegex(ValueError, 'nonregular'):
                saint.restore(root, original, candidate)

    def test_native_saint_snapshots_and_build_candidate(self):
        from i18n import mb16_saint_home as saint
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'clone', '--quiet', '--shared', str(ROOT), str(root)], check=True)
            def git(*args):
                return subprocess.check_output(['git', '-C', str(root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@example.invalid', *args], stderr=subprocess.PIPE)
            # Generate a new data-only pack in a native tree before committing.
            path = root / 'locales/saint-of-day.json'
            manifest = json.loads(path.read_text())
            old = sorted(manifest['entries'])[0]
            manifest['entries'] = {'2026-11-25': manifest['entries'][old]}
            path.write_text(json.dumps(manifest))
            path = root / 'locales/en/saint-of-day.json'
            copies = json.loads(path.read_text())
            path.write_text(json.dumps({'2026-11-25': copies[old]}))
            raw = (root / 'index.html').read_bytes()
            a, z = saint.span(raw)
            candidate = raw[:a] + saint.generated_block(root) + raw[z:]
            (root / 'index.html').write_bytes(candidate)
            pinned = m.preimage(root, 'index.html', candidate)
            self.assertEqual(saint.span(pinned)[0], saint.span(self.originals['index.html'])[0])
            self.assertIn(b'2026-11-25', pinned)
            git('add', 'index.html', 'locales/saint-of-day.json', 'locales/en/saint-of-day.json')
            git('commit', '-qm', 'native generated saint fixture')
            self.assertEqual(m.preimage(root, 'index.html', candidate), pinned)
            wrong = candidate.replace(b'data-saint-date="2026-11-25"', b'data-saint-date="2026-11-26"', 1)
            (root / 'index.html').write_bytes(wrong)
            with self.assertRaises(ValueError): m.preimage(root, 'index.html', wrong)
            (root / 'index.html').write_bytes(candidate)
            control = root / saint.MODULE
            control.write_bytes(control.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'module differs from native HEAD'):
                m.preimage(root, 'index.html', candidate)

    def native_fixture(self):
        temp=tempfile.TemporaryDirectory();root=Path(temp.name)
        def git(*args):return subprocess.check_output(['git','-C',str(root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid',*args],stderr=subprocess.PIPE)
        git('init','-q')
        files={p:raw for p,raw in self.originals.items()}
        for p in [m.MODULE,'scripts/build-international.py','scripts/i18n/same_page_injection.py','locales/registry.json']:files[p]=(ROOT/p).read_bytes()
        from i18n.secret_prayers_registry_continuation import registry_preimage
        files['locales/registry.json']=registry_preimage(ROOT,files['locales/registry.json'])
        for p,raw in files.items():(root/p).parent.mkdir(parents=True,exist_ok=True);(root/p).write_bytes(raw)
        git('add','.');git('commit','-qm','base');base=git('rev-parse','HEAD').decode().strip()
        record=json.loads((ROOT/m.RECORD).read_bytes());record['base']=base
        for key,p in [('registrySha256','locales/registry.json'),('generatorSha256','scripts/build-international.py'),('controlSha256','scripts/i18n/same_page_injection.py')]:record[key]=m.sha((root/p).read_bytes())
        (root/m.RECORD).write_text(json.dumps(record));git('add','.');git('commit','-qm','record')
        return temp,root,git,base
    def test_native_every_proof_input_symlink_and_parent_symlink_rejected(self):
        temp,root,git,base=self.native_fixture()
        try:
            path='visit-annaya.html';raw=self.originals[path];good=m.derive(path,raw,'sorted')
            with patch.object(m,'BASE',base):
                for rel in [m.RECORD,m.MODULE,'locales/registry.json','scripts/build-international.py','scripts/i18n/same_page_injection.py',path]:
                    file=root/rel;payload=file.read_bytes();target=root/'same-bytes';target.write_bytes(payload)
                    file.unlink();file.symlink_to(target)
                    with self.assertRaisesRegex(ValueError,'nonregular'):m.preimage(root,path,good)
                    file.unlink();file.write_bytes(payload);target.unlink()
                parent=root/'scripts/i18n';parent.rename(root/'i18n-held');parent.symlink_to(root/'i18n-held',target_is_directory=True)
                with self.assertRaisesRegex(ValueError,'symlink proof parent'):m.preimage(root,path,good)
        finally:temp.cleanup()

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
