"""Negative controls for probe_partial_build's review-frozen header exclusion.

The probe excludes the <header> element when comparing synthetic re-renders of
review-pinned (family, locale) pages against committed bytes, because the
synthetic world strips the scoped/annaya-hero grants that freeze those headers.
These controls prove the exclusion stays narrow:

1. A body change on a pinned page still fails the probe (only the header is
   excluded from comparison, never the body).
2. A header-only difference on an UNPINNED page still fails the probe (full
   comparison keeps applying outside the pinned set).

Each control injects a synthetic-world-only mutation (gated on the fixture
locale 'zz' existing in the registry) into a detached worktree's generator, so
the production byte-equality proof stays green and the failure must come from
the probe's synthetic comparison itself.
"""
import subprocess,sys,tempfile,unittest,shutil
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
ANCHOR='    validate_partial_outputs(root, registry, result)\n    return result'

def inject(root,snippet):
    target=root/'scripts/build-international.py'
    text=target.read_text()
    assert text.count(ANCHOR)==1,'outputs() anchor not found'
    target.write_text(text.replace(ANCHOR,'    validate_partial_outputs(root, registry, result)\n'+snippet+'    return result',1))

class ProbePartialBuildNegativeControls(unittest.TestCase):
    def run_mutated_probe(self,snippet,expect_file):
        tmp=tempfile.mkdtemp(prefix='probe-neg-')
        work=Path(tmp)/'tree'
        try:
            subprocess.run(['git','worktree','add','--detach',str(work),'HEAD'],cwd=REPO,check=True,capture_output=True,text=True)
            inject(work,snippet)
            run=subprocess.run([sys.executable,'scripts/qa/probe_partial_build.py'],cwd=work,capture_output=True,text=True,timeout=900)
            self.assertNotEqual(run.returncode,0,'probe accepted a mutated synthetic render:\n'+run.stdout[-2000:])
            self.assertIn('Unexpected synthetic production diff: '+expect_file,run.stdout+run.stderr,
                          'failure did not come from the synthetic comparison for '+expect_file+':\n'+(run.stdout+run.stderr)[-2000:])
        finally:
            subprocess.run(['git','worktree','remove','--force',str(work)],cwd=REPO,capture_output=True)
            shutil.rmtree(tmp,ignore_errors=True)

    def test_pinned_page_body_change_still_fails(self):
        snippet=("    if 'zz' in registry.get('locales',{}):\n"
                 "        frozen=root/'de/our-lady-of-lebanon-harissa.html'\n"
                 "        result[frozen]=result[frozen].replace('</main>','X</main>',1)\n")
        self.run_mutated_probe(snippet,'de/our-lady-of-lebanon-harissa.html')

    def test_unpinned_page_header_difference_still_fails(self):
        snippet=("    if 'zz' in registry.get('locales',{}):\n"
                 "        unpinned=root/'de/allerheiligen.html'\n"
                 "        result[unpinned]=result[unpinned].replace('<header','<header data-probe-control=\"1\"',1)\n")
        self.run_mutated_probe(snippet,'de/allerheiligen.html')

if __name__=='__main__':
    unittest.main()
