"""Chinese film-shell home continuation keeps independent original shell pins."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n import mb16_film_home as m,mb16_home_continuation as h
from i18n.feature_mirror import shell_digest

class FilmHomeProof(unittest.TestCase):
    def test_exact_three_replacements_and_mutations(self):
        original=h.git(ROOT,'show',h.BASE+':'+m.PATH);candidate=m.derive(original)
        self.assertEqual(m.verify_delta(original,candidate),original)
        self.assertEqual(m.verify_delta(original,original),original)
        for changed in (candidate+b' ',candidate.replace(b'<main',b'<main data-drift="1"',1),
                        candidate.replace(b'/zh-Hans/',b'/foreign/',1),
                        candidate.replace(b'<header>',b'<header data-extra="1">',1)):
            with self.assertRaises(ValueError):m.verify_delta(original,changed)
        for before,after in m.EDITS:
            with self.assertRaisesRegex(ValueError,'occurrence drift'):m.derive(original+before.encode())
            with self.assertRaises(ValueError):m.verify_delta(original,candidate.replace(after.encode(),before.encode(),1))
        contract=json.loads((ROOT/'config/film-master-family.json').read_text())
        self.assertEqual(shell_digest(original.decode(),'/zh-Hans/charbel-film-premiere'),contract['shellSha256']['zh-Hans'])
        self.assertNotEqual(shell_digest(candidate.decode(),'/zh-Hans/charbel-film-premiere'),contract['shellSha256']['zh-Hans'])

    def test_native_head_caller_binding_and_warm_input_identity(self):
        temp=Path(tempfile.mkdtemp(prefix='mb16-film-proof-'))
        def git(*args):return subprocess.check_output(['git','-C',str(temp),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid',*args],stderr=subprocess.PIPE)
        try:
            subprocess.run(['git','clone','--quiet','--shared',str(ROOT),str(temp)],check=True)
            file=temp/m.PATH;original=h.git(temp,'show',h.BASE+':'+m.PATH);candidate=m.derive(original)
            file.write_bytes(original);git('add','--',m.PATH);git('commit','--quiet','--allow-empty','-m','explicit original film shell')
            self.assertEqual(m.preimage(temp,m.PATH,original),original)
            file.write_bytes(candidate)
            with self.assertRaisesRegex(ValueError,'raw native HEAD fidelity'):m.preimage(temp,m.PATH,candidate)
            git('add','--',m.PATH);git('commit','--quiet','-m','generated film shell candidate')
            self.assertEqual(m.preimage(temp,m.PATH,candidate),original)
            file.write_bytes(original)
            with self.assertRaisesRegex(ValueError,'raw native HEAD fidelity'):m.preimage(temp,m.PATH,original)
            file.write_bytes(candidate)
            with self.assertRaisesRegex(ValueError,'caller differs'):m.preimage(temp,m.PATH,original)
            for rel in (m.RECORD,m.MODULE):
                p=temp/rel;raw=p.read_bytes();p.write_bytes(raw+b' ')
                with self.assertRaises(ValueError):m.preimage(temp,m.PATH,candidate)
                p.write_bytes(raw);target=temp/'same-bytes';target.write_bytes(raw);p.unlink();p.symlink_to(target)
                with self.assertRaisesRegex(ValueError,'nonregular'):m.preimage(temp,m.PATH,candidate)
                p.unlink();p.write_bytes(raw);target.unlink()
            record=temp/m.RECORD;raw=record.read_bytes();data=json.loads(raw);data['originalSha256']='0'*64;record.write_text(json.dumps(data));git('add','--',m.RECORD);git('commit','--quiet','-m','forged original hash')
            with self.assertRaisesRegex(ValueError,'fixed-base hash differs'):m.preimage(temp,m.PATH,candidate)
            record.write_bytes(raw);git('add','--',m.RECORD);git('commit','--quiet','-m','restore record')
            (temp/'.git').rename(temp/'.git-held')
            with self.assertRaisesRegex(ValueError,'native proof unavailable'):m.preimage(temp,m.PATH,candidate)
        finally:shutil.rmtree(temp,ignore_errors=True)

if __name__=='__main__':unittest.main()
