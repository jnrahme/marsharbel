#!/usr/bin/env python3
"""Mutation proof for the private-preview orphan skip in dead_code_check.sh."""
import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

PAGE = 'joyful-preview.html'
NOINDEX = '<!doctype html><html lang="en"><head><meta name="robots" content="noindex,nofollow"><title>x</title></head><body><p>preview</p></body></html>\n'
INDEXABLE = NOINDEX.replace('noindex,nofollow', 'index,follow')

class DeadCodePrivatePreviewTests(unittest.TestCase):
    def make_repo(self, tmp, page_html=NOINDEX, listed=True):
        root = Path(tmp)
        (root / 'scripts/qa').mkdir(parents=True)
        shutil.copyfile(ROOT / 'scripts/qa/dead_code_check.sh', root / 'scripts/qa/dead_code_check.sh')
        (root / 'locales').mkdir()
        pages = [{'page': PAGE, 'owner': 'lane', 'reason': 'private preview', 'handoff': 'ruling'}] if listed else []
        (root / 'locales/private-preview-pages.json').write_text(json.dumps({'pages': pages}))
        (root / PAGE).write_text(page_html)
        return root

    def run_check(self, root):
        return subprocess.run(['bash', 'scripts/qa/dead_code_check.sh'], cwd=root,
                              capture_output=True, text=True)

    def test_listed_noindex_orphan_passes(self):
        with tempfile.TemporaryDirectory() as t:
            result = self.run_check(self.make_repo(t))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn('ORPHAN HTML', result.stdout)

    def test_listed_orphan_without_noindex_fails(self):
        with tempfile.TemporaryDirectory() as t:
            result = self.run_check(self.make_repo(t, page_html=INDEXABLE))
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('noindex missing', result.stdout)

    def test_unlisted_orphan_still_fails(self):
        with tempfile.TemporaryDirectory() as t:
            result = self.run_check(self.make_repo(t, listed=False))
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(f'ORPHAN HTML: {PAGE}', result.stdout)

if __name__ == '__main__':
    unittest.main()
