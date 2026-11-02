"""Synthetic refusal coverage. Does not repin the repository."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('retired_repin', ROOT / 'scripts/i18n/repin_retired_novena_nav.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RetiredNovenaNavRepinTests(unittest.TestCase):
    def setUp(self):
        self.path = 'locales/de/novena-exact.json'
        self.before = b'<html><head><title>Same</title></head><body><header><b>Logo</b><nav><a>Learn</a></nav></header><main><p>Same body</p></main></body></html>'
        self.after = self.before.replace(b'<a>Learn</a>', b'<a>Learn</a><div class="nav-group"><a class="nav-parent">Media</a><div class="nav-sub"><a href="./music">Music</a><a href="./videos">Video</a><a href="./gallery">Gallery</a></div></div>')
        self.cat = json.dumps(dict(master='saint-charbel-novena.html', masterSha256=m.sha(self.before), review={'status': 'frozen'}, slots={'p': 'Same'}), indent=2) + '\n'
        self.registry = {'exactMirrors': {'novena': {'renderLocales': [], 'routes': {'de': '/de/novene'}}}, 'pageMirrors': {'saint-charbel-novena-master': {'renderLocales': ['de'], 'routes': {'de': '/de/novene'}}}}

    def validate(self, **changes):
        args = dict(path=self.path, old_catalog=self.cat, current_catalog=self.cat,
                    before=self.before, after=self.after,
                    base_registry=self.registry, registry=self.registry)
        args.update(changes)
        return m.validate(**args)

    def test_digest_only_and_rerunnable(self):
        updated, row = self.validate()
        self.assertEqual(updated, self.cat.replace(m.sha(self.before), m.sha(self.after)))
        self.assertEqual(row['body_before'], row['body_after'])
        again, _ = self.validate(current_catalog=updated)
        self.assertEqual(updated, again)

    def test_body_diff_refused(self):
        with self.assertRaisesRegex(ValueError, 'Body diff'):
            self.validate(after=self.after.replace(b'Same body', b'Changed body'))

    def test_non_nav_changes_refused(self):
        for old, new in [(b'Logo', b'Other'), (b'<title>Same', b'<title>Other'),
                         (b'</header>', b'</header><!-- added -->')]:
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, 'Non-nav'):
                self.validate(after=self.after.replace(old, new))

    def test_non_retired_catalog_refused(self):
        r = copy.deepcopy(self.registry)
        r['exactMirrors']['novena']['renderLocales'] = ['de']
        for key in ('registry', 'base_registry'):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Non-retired'):
                self.validate(**{key: r})
        with self.assertRaisesRegex(ValueError, 'Out-of-scope'):
            self.validate(path='locales/de/feast-exact.json')

    def test_unknown_old_digest_refused(self):
        with self.assertRaisesRegex(ValueError, 'neither base nor target'):
            self.validate(current_catalog=self.cat.replace(m.sha(self.before), '0' * 64))

    def test_review_fields_refused(self):
        with self.assertRaisesRegex(ValueError, 'catalog fields changed'):
            self.validate(current_catalog=self.cat.replace('frozen', 'approved'))

    def test_bad_base_pin_refused(self):
        with self.assertRaisesRegex(ValueError, 'Base catalog'):
            self.validate(old_catalog=self.cat.replace(m.sha(self.before), '0' * 64))

    def test_wrong_media_destination_refused(self):
        with self.assertRaisesRegex(ValueError, 'Media nav links'):
            self.validate(after=self.after.replace(b'./videos', b'./unrelated'))


if __name__ == '__main__':
    unittest.main()
