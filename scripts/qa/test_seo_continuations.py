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

    def test_faq_nested_nonfaq_and_extra_shapes_fail_closed(self):
        plain = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': 'Question?', 'acceptedAnswer': {'@type': 'Answer', 'text': 'Answer.'}}]}
        bad = []
        for kind in ('Article', 'WebPage', 'BreadcrumbList'):
            row = copy.deepcopy(plain); row['about'] = {'@type': kind}; bad.append(row)
            row = copy.deepcopy(plain); row['mainEntity'][0]['about'] = {'@type': kind}; bad.append(row)
            row = copy.deepcopy(plain); row['mainEntity'][0]['acceptedAnswer']['about'] = {'@type': kind}; bad.append(row)
            row = copy.deepcopy(plain); row['description'] = {'@type': kind}; bad.append(row)
        row = copy.deepcopy(plain); row['extra'] = 'scalar'; bad.append(row)
        row = copy.deepcopy(plain); row['@type'] = ['FAQPage', 'WebPage']; bad.append(row)
        row = copy.deepcopy(plain); row['mainEntity'][0]['acceptedAnswer']['text'] = {'@type': 'Article'}; bad.append(row)
        for data in bad:
            raw = ('<script type="APPLICATION/LD+JSON">'+json.dumps(data)+'</script>').encode()
            with self.subTest(data=data):
                with self.assertRaisesRegex(ValueError, 'mixed FAQ graph'):
                    sc.derive('history.html', raw, ['faq-remove'])
                with self.assertRaises(ValueError):
                    sc.verify_delta('history.html', raw, b'', {'operations': ['faq-remove'], 'beforeSha256': sc.sha(raw), 'afterSha256': sc.sha(b'')})
        raw = '<script type="APPLICATION/LD+JSON">'+json.dumps(plain)+'</script>'
        self.assertEqual(sc.derive('history.html', (raw+'\n'+raw).encode(), ['faq-remove']), b'\n')
        with self.assertRaisesRegex(ValueError, 'overlapping edits'):
            sc.derive('history.html', (raw+raw).encode(), ['faq-remove'])

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

    def article_fixture(self):
        return ('<html lang="en"><head><link rel="canonical" href="https://marsharbel.com/history">'
                '<meta property="og:title" content="History &amp; faith">'
                '<meta name="description" content="Existing description">'
                '<meta property="og:image" content="https://marsharbel.com/image.jpg">'
                '</head><body><main>Visible text</main></body></html>')

    def test_article_uses_only_existing_metadata_and_is_idempotent(self):
        before = self.article_fixture()
        after = self.verify(before, ['article-add'])
        parsed = sc.Spans(after)
        data = json.loads(after[parsed.scripts[0][2]:parsed.scripts[0][3]])
        self.assertEqual(data['headline'], 'History & faith')
        self.assertEqual(data['mainEntityOfPage'], 'https://marsharbel.com/history')
        self.assertNotIn('datePublished', data)
        self.assertNotIn('author', data)
        self.assertIn('<main>Visible text</main>', after)
        self.assertEqual(sc.derive('history.html', after.encode(), ['article-add']).decode(), after)

    def test_article_missing_duplicate_or_external_metadata_rejected(self):
        before = self.article_fixture()
        for raw in (before.replace('<meta name="description" content="Existing description">', ''),
                    before.replace('</head>', '<meta name="description" content="Other"></head>'),
                    before.replace('https://marsharbel.com/history', 'https://example.test/history')):
            with self.assertRaises(ValueError):
                sc.derive('history.html', raw.encode(), ['article-add'])

    def test_article_metadata_cannot_close_script(self):
        before = self.article_fixture().replace('History &amp; faith', '&lt;/script&gt;&lt;script&gt;bad')
        after = self.verify(before, ['article-add'])
        self.assertEqual(len(sc.Spans(after).scripts), 1)
        self.assertIn('\\u003c/script\\u003e', after)

    def test_winner_combines_all_four_real_changes_without_losing_visible_qa(self):
        before = self.article_fixture().replace('<main>Visible text</main>',
            '<main><h2>Question?</h2><p>Answer.</p><a href="/en/prayers#faith">Prayer</a></main>')
        before = before.replace('</head>', '<meta name="robots" content="noindex">'
            '<script type="application/ld+json">{"@type":"FAQPage","mainEntity":[]}</script></head>')
        # This is a synthetic winner with all four effects present, not a
        # claim that the current production winner needs all four effects.
        before = before.replace('https://marsharbel.com/history', 'https://marsharbel.com/saint-charbel-prayers')
        after = self.verify(before, list(sc.CLASSES), path='saint-charbel-prayers.html')
        self.assertNotIn('FAQPage', after)
        self.assertNotIn('noindex', after)
        self.assertIn('href="/saint-charbel-prayers#faith"', after)
        self.assertIn(sc.ROBOT_VALUE, after)
        self.assertIn('"@type": "Article"', after)
        self.assertIn('<h2>Question?</h2><p>Answer.</p>', after)
        self.assertEqual(sc.derive('saint-charbel-prayers.html', after.encode(), list(sc.CLASSES)), after.encode())

    def test_existing_article_not_replaced(self):
        before = self.article_fixture().replace('</head>', '<script type="application/ld+json">{"@type":"Article","headline":"Existing"}</script></head>')
        self.assertEqual(sc.derive('history.html', before.encode(), ['article-add']).decode(), before)

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



class OwningGuards(unittest.TestCase):
    """Current-leg integration only. The original wrapper runs the real
    historical chain separately, without this test's expensive-leg fixture."""
    def setUp(self):
        from i18n import citation_amendment as ca
        self.ca = ca
        self.tmp = Path(tempfile.mkdtemp(prefix='seo-owner-guards-'))
        subprocess.run(['git', '-C', str(ROOT), 'worktree', 'add', '--detach', str(self.tmp), 'HEAD'],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.base = subprocess.check_output(['git', '-C', str(self.tmp), 'rev-parse', 'HEAD']).decode().strip()
        self.paths = ('history.html', 'templates/masters/history-exact.html',
                      'saint-charbel-prayers.html', 'en/prayers.html', 'saint-charbel-chaplet.html', 'ar/saint-charbel-chaplet.html')
        self.before = {}; self.after = {}; rows = {}
        for path in self.paths:
            raw = (self.tmp / path).read_bytes()
            ops = list(sc.CLASSES) if path == 'saint-charbel-prayers.html' else ['prayers-href', 'faq-remove', 'article-add']
            changed = sc.derive(path, raw, ops)
            self.before[path] = raw; self.after[path] = changed
            (self.tmp / path).write_bytes(changed)
            rows[path] = {'beforeSha256': sc.sha(raw), 'afterSha256': sc.sha(changed), 'operations': ops}
        (self.tmp / sc.RECEIPT).write_text(json.dumps({'version': 1, 'baseCommit': self.base, 'files': rows}))
        subprocess.run(['git', '-C', str(self.tmp), 'add', *self.paths, sc.RECEIPT], check=True)
        subprocess.run(['git', '-C', str(self.tmp), '-c', 'user.name=SEO fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'temporary fixed SEO integration fixture'], check=True)
        self.history = patch.object(ca, '_historical_leg', return_value={'isolatedCurrentLegUnitFixture': True})
        self.history.start()

    def tearDown(self):
        self.history.stop()
        subprocess.run(['git', '-C', str(ROOT), 'worktree', 'remove', '--force', str(self.tmp)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_effective_bodies_candidates_and_original_pin_bindings(self):
        from i18n.reviewed_history import digest
        proof = self.ca.prove(self.tmp)
        self.assertEqual(set(proof['continuationPaths']), set(self.paths))
        original = json.loads((self.tmp / 'locales/history-equivalence.json').read_text())['variants']['en']['bodySha256']
        effective = self.ca.effective_body(self.tmp, 'history-master', 'en', original)
        self.assertEqual(effective, digest(self.after['history.html'].decode()))
        self.assertIn('seoContinuation', self.ca.addendum(self.tmp, 'history-master', 'en', effective))
        self.assertEqual(self.ca.current_candidate_bytes(self.tmp, 'history-master', 'en'), self.after['history.html'])
        with self.assertRaisesRegex(ValueError, 'historical pin'):
            self.ca.effective_body(self.tmp, 'history-master', 'en', '0' * 64)
        raw = self.after['ar/saint-charbel-chaplet.html']
        add = self.ca.ar2_addendum(self.tmp, 'chaplet', 'ar', digest(raw.decode()), sc.sha(raw))
        self.assertIn('seoContinuation', add)

    def test_warm_memo_rejects_content_receipt_and_catalog_tampering(self):
        self.ca.prove(self.tmp)
        sidecar=self.ca.load(self.tmp)
        catalog=sidecar['families']['history-master']['variants']['de']['catalog']['path']
        for path in ('history.html', sc.RECEIPT, catalog):
            file = self.tmp / path
            self.assertTrue(file.exists(), path)
            raw = file.read_bytes(); file.write_bytes(raw + b' ')
            with self.assertRaises(ValueError):
                self.ca.prove(self.tmp)
            file.write_bytes(raw)
        raw = (self.tmp / sc.RECEIPT).read_bytes(); (self.tmp / sc.RECEIPT).unlink()
        with self.assertRaisesRegex(ValueError, 'without fixed continuation'):
            self.ca.prove(self.tmp)
        (self.tmp / sc.RECEIPT).write_bytes(raw)

    def test_warm_memo_rejects_same_bytes_symlinks_and_parent_symlinks(self):
        self.ca.prove(self.tmp)
        for path in ('history.html', sc.RECEIPT, sc.MODULE):
            file = self.tmp / path
            raw = file.read_bytes()
            target = self.tmp / 'same-bytes-fixture'
            target.write_bytes(raw)
            file.unlink(); file.symlink_to(target)
            try:
                with self.assertRaisesRegex(ValueError, 'nonregular'):
                    self.ca.prove(self.tmp)
            finally:
                file.unlink(); file.write_bytes(raw); target.unlink()
        # An unchanged child under a symlinked ancestor is equally unsafe.
        for directory in ('ar', 'locales', 'scripts/i18n'):
            parent = self.tmp / directory
            target = parent.with_name(parent.name + '-same-bytes-fixture')
            parent.rename(target); parent.symlink_to(target, target_is_directory=True)
            try:
                with self.assertRaisesRegex(ValueError, 'symlink proof parent'):
                    self.ca.prove(self.tmp)
            finally:
                parent.unlink(); target.rename(parent)

    def test_winner_operations_coexist_and_frozen_prayer_composer_accepts_continued_body(self):
        from i18n.prayer_metadata import compose_prayer_clusters
        registry = json.loads((self.tmp / 'locales/registry.json').read_text())
        winner = self.after['saint-charbel-prayers.html'].decode()
        self.assertIn(sc.ROBOT_VALUE, winner)
        self.assertEqual(sc.derive('saint-charbel-prayers.html', winner.encode(), list(sc.CLASSES)), winner.encode())
        self.assertNotEqual(self.before['en/prayers.html'], self.after['en/prayers.html'])
        result = compose_prayer_clusters(self.tmp, registry, {})
        for path in ('saint-charbel-prayers.html', 'en/prayers.html'):
            import re
            self.assertEqual(re.search(r'<main\b[\s\S]*?</main>', result[self.tmp / path])[0],
                             re.search(r'<main\b[\s\S]*?</main>', self.after[path].decode())[0])
        altered = dict(result)
        altered[self.tmp / 'en/prayers.html'] = altered[self.tmp / 'en/prayers.html'].replace('<main', '<main data-unapproved="yes"', 1)
        with self.assertRaisesRegex(ValueError, 'frozen body'):
            compose_prayer_clusters(self.tmp, registry, altered)

    def test_original_master_formulas_and_localized_final_operations(self):
        from i18n.catalog import read_json
        from i18n.keyed_master import apply_keyed_master, strip_static_fallback
        from i18n.exact_master import render_exact
        raw, _, _ = apply_keyed_master(self.tmp, 'history-master', 'en')
        self.assertEqual(raw, strip_static_fallback(self.before['history.html']))
        registry = read_json(self.tmp / 'locales/registry.json')
        route = registry['exactMirrors']['biography']['routes']['de']
        text = render_exact(self.tmp, registry, 'de', 'biography', route)
        # No English Article is inherited from the continued master. The
        # final operation gets the LOCALIZED output's own metadata instead.
        self.assertIn('FAQPage', text)
        localized = sc.derive('de/biografie.html', text.encode(), ['faq-remove', 'article-add']).decode()
        parsed = sc.Spans(localized)
        articles = [json.loads(localized[bs:be]) for _, _, bs, be, attrs in parsed.scripts
                    if sc.attrs_dict(attrs).get('type') == 'application/ld+json'
                    and json.loads(localized[bs:be]).get('@type') == 'Article']
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['inLanguage'], 'de')
        self.assertEqual(articles[0]['mainEntityOfPage'], 'https://marsharbel.com' + route)

    def test_editable_export_with_receipt_cannot_emit_reviewed_claims(self):
        marker = self.tmp / '.git'; original = marker.read_bytes(); marker.unlink()
        try:
            with self.assertRaisesRegex(ValueError, 'export rejected'):
                self.ca.prove(self.tmp)
        finally:
            marker.write_bytes(original)


def run_into(record):
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TestResult()
    suite.run(result)
    errors = {str(test): detail for test, detail in result.errors + result.failures}
    record('SC finite SEO continuation controls', result.wasSuccessful(),
           str(result.testsRun) + ' tests; ' + '; '.join(str(test) + ': ' + detail.strip().splitlines()[-1] for test, detail in errors.items())[:1600])


if __name__ == '__main__':
    unittest.main()
