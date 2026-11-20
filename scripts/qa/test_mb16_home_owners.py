"""Actual owner integration on native cloned HEAD; historical leg tested separately.

The mock below excludes ONLY the immutable historical B execution to keep this
unit bounded. It never supplies a current candidate, body pin or receipt.
Full check_citation_amendment.py remains an independent mandatory CI gate.
"""
import sys,json,tempfile,subprocess,shutil,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import mb16_home_continuation as m,citation_amendment as ca
from i18n.catalog import load_catalog
from i18n.keyed_master import apply_keyed_master
from i18n.exact_master import render_exact
from i18n.prayer_metadata import compose_prayer_clusters
from i18n.reviewed_history import digest
import unittest

class HomeOwnerIntegration(unittest.TestCase):
    def test_all_generated_home_owners_and_current_citation_leg(self):
        T=Path(tempfile.mkdtemp(prefix='mb16-owners-'));results=[]
        def ok(name):results.append(name);print('PASS',name,flush=True)
        try:
         subprocess.run(['git','clone','--quiet','--shared',str(ROOT),str(T)],check=True)
         originals={p:m.git(T,'show',m.BASE+':'+p)for p in m.PATHS}
         for p,raw in originals.items():(T/p).write_bytes(m.derive(p,raw,'sorted',p=='index.html'))
         registry=load_catalog(T)[0];ok('catalog with all seven generated footer masters + combined index')
         for family in ('annaya-master','visit-annaya-zh-travel-master','twenty-second-master','history-master','saint-charbel-novena-master','saint-charbel-prayers-master','home'):
          apply_keyed_master(T,family,'en');ok('original keyed pin '+family)
         for code,name in [('ru','biography'),('de','novena')]:
          assert registry['exactMirrors'][name]['renderLocales']==[]
          route=registry['exactMirrors'][name]['routes'][code]
          try:render_exact(T,registry,code,name,route);raise AssertionError('retired stale catalog unexpectedly accepted')
          except ValueError as error:
           assert 'complete master digest changed' in str(error),str(error)
          raw=m.preimage(T,json.loads((T/f'locales/{code}/{name}-exact.json').read_text())['master'],(T/json.loads((T/f'locales/{code}/{name}-exact.json').read_text())['master']).read_bytes())
          assert raw==originals[json.loads((T/f'locales/{code}/{name}-exact.json').read_text())['master']]
          ok('retired exact '+code+'/'+name+' preserves prior rejection, no pin refresh')
         # The AR rosary is an authored frozen translation with no exact catalog and
         # renderLocales empty. Its English footer is NOT a locale-body pin owner.
         assert registry['exactMirrors']['rosary-intro']['renderLocales']==[]
         assert digest((T/'rosary-intro.html').read_text())==digest(originals['rosary-intro.html'].decode());ok('rosary exact-family inactive + unchanged main')
         compose_prayer_clusters(T,registry,{});ok('prayer metadata frozen-main checks')
         # Full fresh CURRENT citation leg; historical B proof is unchanged and is the
         # one separately pending because it exceeds local execution time. Not full PASS.
         with patch.object(ca,'_historical_leg',return_value={'pending':'separate full native historical execution'}):
          ca._MEMO.clear();ca.prove(T);ok('fresh citation current owners, historical leg excluded explicitly')
          ca.prove(T);ok('warm citation memo with complete input identity')
          victim=T/'history.html';good=victim.read_bytes();victim.write_bytes(good.replace(b'<main',b'<main data-drift="1"',1))
          try:ca.prove(T);raise AssertionError('outside drift accepted')
          except ValueError:ok('warm citation outside mutation rejected')
          victim.write_bytes(good)
          for rel in (m.RECORD,m.MODULE,'locales/registry.json'):
           file=T/rel;payload=file.read_bytes();ca.prove(T)
           file.write_bytes(payload+b' ')
           try:ca.prove(T);raise AssertionError('warm proof input tamper accepted '+rel)
           except ValueError:ok('warm citation proof input tamper rejected '+rel)
           file.write_bytes(payload)
          file=T/m.MODULE;payload=file.read_bytes();target=T/'same-module';target.write_bytes(payload);file.unlink();file.symlink_to(target)
          try:ca.prove(T);raise AssertionError('warm module symlink accepted')
          except ValueError:ok('warm citation same-byte module symlink rejected')
          file.unlink();file.write_bytes(payload);target.unlink()
         print(json.dumps({'passed':results,'fullHistoricalLeg':'PENDING, not run in this bounded test'},indent=2),flush=True)
        finally:shutil.rmtree(T,ignore_errors=True)

if __name__=="__main__":unittest.main()
