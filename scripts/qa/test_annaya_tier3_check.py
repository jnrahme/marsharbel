"""Wired regression for the annaya batch-1 tier-3 --check validator.

A previous --check silently accepted corrupt targets, so these tests must
stay executable: check-mode success against the shipped catalogs AND
check-mode rejection of corrupted temporary catalog/master pairs via
refresh_exact(check=True), not only direct helper calls.
"""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT
from i18n import refresh_annaya_batch1_tier3 as tier3

MIRACLES = tier3.EXACT_JOBS[0]
PILGRIMS_ALT_DE = 'Pilger am Grab des heiligen Charbel in Annaya.'


class Tier3CheckModeTests(unittest.TestCase):
    def make_tmp_root(self, tmp):
        """Copy the miracles catalog + master into a scratch ROOT."""
        catalog_rel = Path(f'locales/de/miracles-exact.json')
        src_catalog = ROOT / catalog_rel
        catalog = json.loads(src_catalog.read_text())
        master_rel = Path(catalog['master'])
        for rel in (catalog_rel, master_rel):
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        return catalog

    def run_check(self, tmp, catalog):
        (tmp / 'locales/de/miracles-exact.json').write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        with mock.patch.object(tier3, 'ROOT', tmp):
            return tier3.refresh_exact(MIRACLES, check=True)

    def corrupt_and_expect_rejected(self, label, mutate):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            catalog = self.make_tmp_root(tmp)
            mutate(catalog)
            with self.subTest(corruption=label):
                self.assertFalse(self.run_check(tmp, catalog), f'--check accepted: {label}')

    def test_full_check_mode_success_on_shipped_catalogs(self):
        result = subprocess.run(
            [sys.executable, 'scripts/i18n/refresh_annaya_batch1_tier3.py', '--check'],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('de/miracles-exact: OK', result.stdout)

    def test_check_mode_accepts_pristine_temporary_copy(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            catalog = self.make_tmp_root(tmp)
            self.assertTrue(self.run_check(tmp, catalog))

    def test_check_mode_rejects_wrong_translation(self):
        def mutate(catalog):
            for slot in catalog['slots'].values():
                if slot['source'] in MIRACLES['new_text']:
                    slot['text'] = 'FALSCH'
        self.corrupt_and_expect_rejected('wrong translation', mutate)

    def test_check_mode_rejects_untranslated_passthrough(self):
        def mutate(catalog):
            for slot in catalog['slots'].values():
                if slot['source'] in MIRACLES['new_text']:
                    slot['text'] = slot['source']
        self.corrupt_and_expect_rejected('untranslated passthrough', mutate)

    def test_check_mode_rejects_stale_slot_source(self):
        def mutate(catalog):
            first = next(iter(catalog['slots'].values()))
            first['source'] = 'A source the master no longer carries.'
        self.corrupt_and_expect_rejected('stale slot source', mutate)

    def test_check_mode_rejects_retired_image_attribute_key(self):
        def mutate(catalog):
            catalog['attributes']['main img[src="../media/annaya/annaya-entrance-pilgrims.webp"]'] = {'alt': 'x'}
        self.corrupt_and_expect_rejected('retired image attribute key', mutate)

    def test_check_mode_rejects_top_alt_drift(self):
        # The exact regression that shipped before this validator existed:
        # the empty candlelit chapel photo carrying a people-describing alt.
        def mutate(catalog):
            catalog['alt'] = PILGRIMS_ALT_DE
        self.corrupt_and_expect_rejected('top-alt drift to pilgrims wording', mutate)

    def test_check_mode_rejects_attribute_alt_drift(self):
        def mutate(catalog):
            key = next(k for k in catalog['attributes'] if 'tomb-pilgrims' in k)
            catalog['attributes'][key]['alt'] = PILGRIMS_ALT_DE
        self.corrupt_and_expect_rejected('attribute alt drift to pilgrims wording', mutate)

    def test_check_mode_rejects_unapplied_master_digest(self):
        def mutate(catalog):
            catalog['masterSha256'] = '0' * 64
        self.corrupt_and_expect_rejected('stale masterSha256', mutate)


if __name__ == '__main__':
    unittest.main()
