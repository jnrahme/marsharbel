"""Finite continuation controls, also called by the citation CI slot."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n import seo_continuations as sc


class FixedDeltas(unittest.TestCase):
    def verify(self, before, ops, after=None, path='history.html'):
        before = before.encode()
        result = sc.derive(path, before, ops) if after is None else after.encode()
        row = {'operations': ops, 'beforeSha256': sc.sha(before), 'afterSha256': sc.sha(result)}
        self.assertEqual(sc.verify_delta(path, before, result, row), before)
        return result.decode()

    def test_href_only_exact_internal_anchors(self):
        before = '<a href="/en/prayers?x=1&amp;y=2#faith">Prayer</a><a href="https://elsewhere.test/en/prayers">Other</a>'
        after = self.verify(before, ['prayers-href'])
        self.assertIn('/saint-charbel-prayers?x=1&amp;y=2#faith', after)
        self.assertIn('https://elsewhere.test/en/prayers', after)
        self.assertIn('>Prayer</a>', after)

    def test_relative_href_uses_document_path(self):
        self.assertIn('href="/saint-charbel-prayers#x"', self.verify('<a href="prayers.html#x">X</a>', ['prayers-href'], path='en/prayers.html'))

    def test_preserves_comments_scripts_raw_text_prose_and_nonanchors(self):
        before = '<!-- <a href="/en/prayers">X</a> --><script>const x=\'<a href="/en/prayers">\';</script><textarea><a href="/en/prayers">X</a></textarea><title><a href="/en/prayers">X</a></title><link href="/en/prayers"><a data-href="/en/prayers">No href</a><p>/en/prayers</p>'
        self.assertEqual(sc.derive('history.html', before.encode(), ['prayers-href']), before.encode())

    def test_prefix_and_external_hostname_not_rewritten(self):
        before = '<a href="/en/prayers-extra">A</a><a href="https://marsharbel.com.attacker.test/en/prayers">B</a>'
        self.assertEqual(sc.derive('history.html', before.encode(), ['prayers-href']), before.encode())

    def test_duplicate_href_and_unquoted_href_rejected(self):
        for before in ('<a href="/en/prayers" href="/other">X</a>', '<a href=/en/prayers>X</a>'):
            with self.assertRaises(ValueError):
                sc.derive('history.html', before.encode(), ['prayers-href'])

    def test_visible_change_cannot_hide_behind_updated_hash(self):
        with self.assertRaisesRegex(ValueError, 'outside fixed operation'):
            self.verify('<a href="/en/prayers">Prayer</a>', ['prayers-href'], '<a href="/saint-charbel-prayers">Changed prayer</a>')

    def test_noop_receipt_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no-op'):
            self.verify('<p>Unchanged</p>', ['prayers-href'])

    def test_unknown_duplicate_unordered_ops_rejected(self):
        for ops in ([], ['replace-any'], ['faq-remove', 'faq-remove'], ['faq-remove', 'prayers-href']):
            with self.assertRaises(ValueError):
                sc.derive('history.html', b'<html></html>', ops)

    def test_safe_paths(self):
        for path in ('../history.html', '/history.html', 'a//b.html', 'a/./b.html', 'a.json'):
            with self.assertRaises(ValueError):
                sc.derive(path, b'', ['faq-remove'])

    def test_faq_only_removal_preserves_visible_qa_and_other_schema(self):
        faq = '<script type="application/ld+json">{"@type":"FAQPage","mainEntity":[]}</script>'
        other = '<script type="application/ld+json">{"@type":"Article"}</script>'
        self.assertEqual(self.verify('<main><h2>Question?</h2><p>Answer.</p>'+faq+other+'</main>', ['faq-remove']), '<main><h2>Question?</h2><p>Answer.</p>'+other+'</main>')

    def test_mixed_graph_is_rejected_not_deleted(self):
        for data in ({'@graph': [{'@type': 'FAQPage'}, {'@type': 'Article'}]}, [{'@type': 'FAQPage'}], {'@type': ['FAQPage', 'Article']}):
            with self.assertRaisesRegex(ValueError, 'mixed FAQ graph'):
                sc.derive('history.html', ('<script type="application/ld+json">'+json.dumps(data)+'</script>').encode(), ['faq-remove'])

    def test_malformed_json_and_unclosed_script_rejected(self):
        for raw in ('<script type="application/ld+json">bad</script>', '<script type="application/ld+json">{}'):
            with self.assertRaises(ValueError):
                sc.derive('history.html', raw.encode(), ['faq-remove'])

    def test_robots_only_winner_and_idempotent(self):
        after = self.verify('<html><head></head><body>Text</body></html>', ['prayers-robots'], path='saint-charbel-prayers.html')
        self.assertIn(sc.ROBOT_VALUE, after)
        self.assertEqual(sc.derive('saint-charbel-prayers.html', after.encode(), ['prayers-robots']).decode(), after)
        with self.assertRaisesRegex(ValueError, 'only on prayer winner'):
            sc.derive('history.html', b'<head></head>', ['prayers-robots'])

    def test_duplicate_robots_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate robots'):
            sc.derive('saint-charbel-prayers.html', b'<head><meta name="robots" content="noindex"><meta name="robots" content="index"></head>', ['prayers-robots'])

    def test_arbitrary_receipt_fields_rejected(self):
        before = b'<a href="/en/prayers">X</a>'
        after = sc.derive('history.html', before, ['prayers-href'])
        row = {'operations': ['prayers-href'], 'beforeSha256': sc.sha(before), 'afterSha256': sc.sha(after), 'approved': True}
        with self.assertRaises(ValueError):
            sc.verify_delta('history.html', before, after, row)


class NativeBinding(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Fixture')
        self.path = 'history.html'
        self.before = b'<head></head><main><a href="/en/prayers">Prayer</a></main>'
        self.write(self.path, self.before)
        self.write(sc.MODULE, (ROOT / sc.MODULE).read_bytes())
        self.commit()
        self.base = self.git('rev-parse', 'HEAD').decode().strip()
        self.after = sc.derive(self.path, self.before, ['prayers-href'])
        self.data = {'version': 1, 'baseCommit': self.base, 'files': {self.path: {
            'beforeSha256': sc.sha(self.before), 'afterSha256': sc.sha(self.after), 'operations': ['prayers-href']}}}
        self.write(self.path, self.after)
        self.write_receipt()
        self.commit()
        # Object hydration has its own native controls. This fixture isolates
        # continuation-specific ancestry, preimage, HEAD and disk checks.
        self.hydrate = patch('i18n.citation_history.ensure_history', return_value=True)
        self.c2 = patch('i18n.citation_history.REVIEWED_C', self.base)
        self.load = patch('i18n.citation_amendment.load', return_value={})
        self.hydrate.start(); self.c2.start(); self.load.start()

    def tearDown(self):
        self.load.stop(); self.c2.stop(); self.hydrate.stop()
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL)

    def write(self, path, raw):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)

    def write_receipt(self):
        self.write(sc.RECEIPT, json.dumps(self.data).encode())

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def test_exact_native_proof_and_original_pin_preimage(self):
        self.assertEqual(sc.verify_receipt(self.root), {self.path: self.before})
        self.assertEqual(sc.pinned_preimage(self.root, self.path, self.after), self.before)

    def test_worktree_content_receipt_and_tool_tampering(self):
        for path in (self.path, sc.RECEIPT, sc.MODULE):
            raw = (self.root / path).read_bytes()
            self.write(path, raw + b' ')
            with self.assertRaisesRegex(ValueError, 'worktree differs'):
                sc.verify_receipt(self.root)
            self.write(path, raw)

    def test_committed_wrong_delta_even_with_matching_hashes_rejected(self):
        self.write(self.path, self.after + b'<p>Unapproved text</p>')
        self.data['files'][self.path]['afterSha256'] = sc.sha((self.root / self.path).read_bytes())
        self.write_receipt(); self.commit()
        with self.assertRaisesRegex(ValueError, 'outside fixed operation'):
            sc.verify_receipt(self.root)

    def test_newer_base_cannot_absorb_drift(self):
        self.data['baseCommit'] = self.git('rev-parse', 'HEAD').decode().strip()
        self.write_receipt(); self.commit()
        with self.assertRaisesRegex(ValueError, 'not reviewed C2'):
            sc.verify_receipt(self.root)

    def test_path_outside_fixed_membership_rejected(self):
        self.data['files']['not-reviewed.html'] = copy.deepcopy(self.data['files'][self.path])
        self.write_receipt(); self.commit()
        with self.assertRaisesRegex(ValueError, 'fixed membership'):
            sc.verify_receipt(self.root)

    def test_export_cannot_self_certify(self):
        shutil.rmtree(self.root / '.git')
        with self.assertRaisesRegex(ValueError, 'native proof unavailable'):
            sc.verify_receipt(self.root)

    def test_missing_ancestor_rejected(self):
        self.data['baseCommit'] = '0' * 40
        self.write_receipt(); self.commit()
        with self.assertRaisesRegex(ValueError, 'native proof unavailable'):
            sc.verify_receipt(self.root)

    def test_symlink_input_rejected(self):
        target = self.root / 'other.html'
        target.write_bytes(self.after)
        (self.root / self.path).unlink()
        (self.root / self.path).symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'nonregular'):
            sc.verify_receipt(self.root)


def run_into(record):
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TestResult()
    suite.run(result)
    errors = {str(test): detail for test, detail in result.errors + result.failures}
    record('SC finite SEO continuation controls', result.wasSuccessful(),
           str(result.testsRun) + ' tests; ' + '; '.join(errors)[:300])


if __name__ == '__main__':
    unittest.main()
