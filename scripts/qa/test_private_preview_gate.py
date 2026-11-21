#!/usr/bin/env python3
"""Mutation proof for the private-preview exemption in check_new_page_locales."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/qa'))
import check_new_page_locales as gate

PAGE = 'rosary-book-joyful.html'
NOINDEX = '<!doctype html><html lang="en"><head><meta name="robots" content="noindex,nofollow"><title>x</title></head><body><p>preview</p></body></html>'
INDEXABLE = NOINDEX.replace('noindex,nofollow', 'index,follow')
ENTRY = {'page': PAGE, 'owner': 'lane', 'reason': 'private preview', 'handoff': 'ruling'}

def make_root(tmp, page_html=NOINDEX, allowlist=True, sitemap_with=False, inbound_link=False, entry=None):
    root = Path(tmp)
    (root / 'locales').mkdir(parents=True)
    (root / 'locales/registry.json').write_text(json.dumps({'locales': ['en'], 'defaultLocale': 'en'}))
    (root / PAGE).write_text(page_html)
    if allowlist:
        (root / 'locales/private-preview-pages.json').write_text(json.dumps({'pages': [entry or ENTRY]}))
    loc = '  <url><loc>https://marsharbel.com/rosary-book-joyful</loc></url>\n' if sitemap_with else ''
    (root / 'sitemap.xml').write_text('<?xml version="1.0"?>\n<urlset>\n' + loc + '</urlset>\n')
    if inbound_link:
        (root / 'index.html').write_text('<!doctype html><html><body><a href="/rosary-book-joyful">book</a></body></html>')
    return root

class PrivatePreviewGateTests(unittest.TestCase):
    def run_gate(self, root, added=(PAGE,)):
        return gate.check(root, list(added), {'locales': ['en']})

    def test_a_indexable_new_page_still_fails(self):
        with tempfile.TemporaryDirectory() as t:
            _, errors = self.run_gate(make_root(t, page_html=INDEXABLE, allowlist=False))
            self.assertTrue(any('pageMirrors' in e for e in errors), errors)

    def test_b_noindex_without_allowlist_fails(self):
        with tempfile.TemporaryDirectory() as t:
            _, errors = self.run_gate(make_root(t, page_html=NOINDEX, allowlist=False))
            self.assertTrue(any('pageMirrors' in e for e in errors), errors)

    def test_c1_allowlisted_but_in_sitemap_fails(self):
        with tempfile.TemporaryDirectory() as t:
            _, errors = self.run_gate(make_root(t, sitemap_with=True))
            self.assertTrue(any('sitemap' in e for e in errors), errors)

    def test_c2_allowlisted_but_inbound_linked_fails(self):
        with tempfile.TemporaryDirectory() as t:
            _, errors = self.run_gate(make_root(t, inbound_link=True))
            self.assertTrue(any('inbound link' in e for e in errors), errors)

    def test_c3_allowlisted_but_missing_noindex_fails(self):
        with tempfile.TemporaryDirectory() as t:
            _, errors = self.run_gate(make_root(t, page_html=INDEXABLE))
            self.assertTrue(any('noindex' in e for e in errors), errors)

    def test_c4_isolation_asserted_even_when_page_not_in_diff(self):
        with tempfile.TemporaryDirectory() as t:
            _, errors = self.run_gate(make_root(t, inbound_link=True), added=())
            self.assertTrue(any('inbound link' in e for e in errors), errors)

    def test_c5_malformed_allowlist_entry_fails_loud(self):
        with tempfile.TemporaryDirectory() as t:
            bad = {'page': PAGE, 'owner': 'lane', 'reason': '', 'handoff': 'ruling'}
            root = make_root(t, entry=bad)
            with self.assertRaises(ValueError):
                self.run_gate(root)

    def test_d_allowlisted_isolated_noindex_passes(self):
        with tempfile.TemporaryDirectory() as t:
            checked, errors = self.run_gate(make_root(t))
            self.assertEqual(errors, [])
            self.assertEqual(checked, [PAGE])

if __name__ == '__main__':
    unittest.main()
