#!/usr/bin/env python3
"""Selection contract of scripts/qa/affected_tests.py (Q-006).

Drives select() with a scripted step inventory - never the real suite - so the
fail-safe direction is pinned: any doubt selects everything.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "affected_tests", ROOT / "scripts/qa/affected_tests.py")
at = importlib.util.module_from_spec(spec)
spec.loader.exec_module(at)

STEPS = [
    (0, "python3 -m unittest discover -s scripts/qa -p test_page_mirror_ru_whitespace.py"),
    (1, "python3 scripts/qa/check_seo.py"),
    (2, "npm run i18n:test"),
    (3, "python3 -m unittest discover -s scripts/qa -p test_generated_sitemap_dates.py"),
    (4, "python3 scripts/qa/run_full_qa.sh --helper"),
]
ALL = [c for _, c in STEPS]


class Select(unittest.TestCase):
    def pick(self, paths):
        return at.select(paths, STEPS)

    def test_known_test_file_selects_its_step(self):
        commands, _ = self.pick(["scripts/qa/test_generated_sitemap_dates.py"])
        self.assertEqual(commands, [STEPS[3][1]])

    def test_suite_wiring_selects_everything(self):
        for path in (".github/workflows/qa.yml", "scripts/qa/run_full_qa.sh",
                     "scripts/qa/shard-manifest.tsv", "package.json",
                     "scripts/build/build-pages.mjs", "scripts/qa/lib/util.py"):
            commands, reasons = self.pick([path])
            self.assertEqual(commands, ALL, path)
            self.assertIn("full suite", reasons[0])

    def test_unmapped_path_selects_everything(self):
        commands, _ = self.pick(["en/about/index.html"])
        self.assertEqual(commands, ALL)

    def test_unreferenced_test_selects_everything(self):
        commands, reasons = self.pick(["scripts/qa/test_brand_new.py"])
        self.assertEqual(commands, ALL)
        self.assertIn("no step references it", reasons[0])

    def test_locale_dir_selects_locale_and_i18n_steps(self):
        commands, _ = self.pick(["ru/index.html"])
        self.assertIn(STEPS[0][1], commands)  # _ru_ in the test name
        self.assertIn(STEPS[2][1], commands)  # i18n step
        self.assertNotIn(STEPS[1][1], commands)

    def test_locale_token_does_not_match_inside_words(self):
        commands, _ = self.pick(["ar/index.html"])
        self.assertNotIn(STEPS[4][1], commands)  # run_full_qa.sh helper: no "ar" token
        self.assertIn(STEPS[2][1], commands)

    def test_sitemap_selects_sitemap_steps(self):
        commands, _ = self.pick(["sitemap.xml"])
        self.assertIn(STEPS[3][1], commands)
        self.assertNotIn(STEPS[0][1], commands)

    def test_mixed_paths_merge_without_duplicates(self):
        commands, _ = self.pick(["ru/index.html", "sitemap.xml", "ru/prayers.html"])
        self.assertEqual(len(commands), len(set(commands)))
        self.assertIn(STEPS[0][1], commands)
        self.assertIn(STEPS[3][1], commands)

    def test_empty_selection_is_empty_not_full(self):
        commands, _ = self.pick([])
        self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()
