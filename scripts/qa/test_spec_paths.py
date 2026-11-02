import tempfile
import unittest
from pathlib import Path

from check_spec_paths import check


class SpecPathTests(unittest.TestCase):
    def test_flags_absolute_paths_and_allows_relative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests/bad.spec.js").write_text("await page.screenshot({path:`/downloads/x.png`});\n")
            (root / "tests/good.spec.js").write_text("await page.screenshot({path: testInfo.outputPath('x.png')});\nawait page.goto('/downloads-page');\n")
            errors = check(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("bad.spec.js:1", errors[0])

    def test_repo_specs_are_clean(self):
        self.assertEqual(check(), [])


if __name__ == "__main__":
    unittest.main()
