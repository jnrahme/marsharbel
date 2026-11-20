"""Finite inventory controls for generated MB16 citation output changes."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from i18n import mb16_citation_home as m, mb16_home_continuation as h
from i18n import citation_amendment as ca, citation_history as ch

class CitationHomeDeltas(unittest.TestCase):
    def test_all_twenty_fixed_deltas_and_inside_outside_mutations(self):
        for path in sorted(m.PATHS):
            original = h.git(ROOT, 'show', h.BASE+':'+path)
            candidate = m.derive(path, original)
            self.assertNotEqual(candidate, original)
            self.assertEqual(m.verify_delta(path, original, candidate), original)
            self.assertEqual(m.verify_delta(path, original, original), original)
            for changed in (candidate+b' ', candidate.replace(b'<main', b'<main data-drift="1"', 1),
                            candidate.replace(b'/zh-Hans/', b'/foreign/', 1)):
                with self.assertRaisesRegex(ValueError, 'outside fixed home delta'):
                    m.verify_delta(path, original, changed)
            if path != m.TRAVEL:
                a,z=m.footer_span(path,candidate)
                block=candidate[a:z]
                for changed in (candidate+block,candidate.replace(block,b'',1),block+candidate.replace(block,b'',1),
                                candidate.replace('简体中文'.encode(),b'Changed',1),
                                candidate.replace(b'lang="zh-Hans"',b'lang="foreign"',1)):
                    with self.assertRaises(ValueError):m.verify_delta(path,original,changed)
        with self.assertRaisesRegex(ValueError,'outside finite inventory'):
            m.derive('fr/other.html',b'')

    def test_travel_requires_exact_all_occurrences_not_partial_or_extra(self):
        original=h.git(ROOT,'show',h.BASE+':'+m.TRAVEL)
        for before,after,count in m.TRAVEL_EDITS:
            with self.assertRaisesRegex(ValueError,'occurrence drift'):
                m.derive(m.TRAVEL,original.replace(before.encode(),after.encode(),1))
            with self.assertRaisesRegex(ValueError,'occurrence drift'):
                m.derive(m.TRAVEL,original+before.encode())
        candidate=m.derive(m.TRAVEL,original)
        for before,after,count in m.TRAVEL_EDITS:
            partial=candidate.replace(after.encode(),before.encode(),1)
            with self.assertRaises(ValueError):m.verify_delta(m.TRAVEL,original,partial)

    def test_native_raw_fidelity_warm_tamper_symlink_export(self):
        temp=Path(tempfile.mkdtemp(prefix='mb16-citation-home-'))
        def git(*args):
            return subprocess.check_output(['git','-C',str(temp),'-c','user.name=Fixture',
                                           '-c','user.email=fixture@example.invalid',*args],stderr=subprocess.PIPE)
        try:
            subprocess.run(['git','clone','--shared','--quiet',str(ROOT),str(temp)],check=True)
            ch.ensure_history(temp,ca.load(temp))
            for path in m.PATHS:(temp/path).write_bytes(h.git(temp,'show',h.BASE+':'+path))
            git('add','--',*sorted(m.PATHS));git('commit','--quiet','--allow-empty','-m','explicit old locale home state')
            for path in m.PATHS:
                original=(temp/path).read_bytes();(temp/path).write_bytes(m.derive(path,original))
                self.assertEqual(m.preimage(temp,path,(temp/path).read_bytes()),original)
            ca._MEMO.clear()
            with self.assertRaisesRegex(ValueError,'worktree proof input diverges from head'):ca.prove(temp)
            git('add','--',*sorted(m.PATHS));git('commit','--quiet','-m','commit generated locale home candidate')
            victim=temp/'ar/biography.html';good=victim.read_bytes()
            victim.write_bytes(h.git(temp,'show',h.BASE+':ar/biography.html'))
            ca._MEMO.clear()
            with self.assertRaisesRegex(ValueError,'worktree proof input diverges from head'):ca.prove(temp)
            victim.write_bytes(good)
            with patch.object(ca,'_historical_leg',return_value={'excluded':'separate full historical gate'}):
                ca._MEMO.clear();ca.prove(temp);ca.prove(temp)
                for rel in (m.RECORD,m.MODULE):
                    file=temp/rel;raw=file.read_bytes();file.write_bytes(raw+b' ')
                    with self.assertRaises(ValueError):ca.prove(temp)
                    file.write_bytes(raw)
                    target=temp/'same-bytes';target.write_bytes(raw);file.unlink();file.symlink_to(target)
                    with self.assertRaisesRegex(ValueError,'nonregular'):ca.prove(temp)
                    file.unlink();file.write_bytes(raw);target.unlink()
                ca.prove(temp)
                victim.write_bytes(good+b' ')
                with self.assertRaises(ValueError):ca.prove(temp)
                victim.write_bytes(good)
                record=temp/m.RECORD;old=record.read_bytes();data=json.loads(old);data['paths']['ar/biography.html']='0'*64
                record.write_text(json.dumps(data));git('add','--',m.RECORD);git('commit','--quiet','-m','forged pin')
                with self.assertRaisesRegex(ValueError,'fixed-base pin differs'):m.preimage(temp,'ar/biography.html',good)
                record.write_bytes(old);git('add','--',m.RECORD);git('commit','--quiet','-m','restore record')
                (temp/'.git').rename(temp/'.git-held')
                with self.assertRaisesRegex(ValueError,'native proof unavailable'):m.preimage(temp,'ar/biography.html',good)
        finally:
            shutil.rmtree(temp,ignore_errors=True)

if __name__=='__main__':unittest.main()
