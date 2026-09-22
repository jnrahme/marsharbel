import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

from check_seo import check

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("seo_generator", ROOT / "scripts/apply_seo_tags.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class SeoRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in [*ROOT.glob("*.html"), *ROOT.glob("mysteries/*.html"), ROOT / "sitemap.xml", ROOT / "robots.txt"]:
            target = self.root / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        # Keep immutable assets available without copying the media library.
        for path in ROOT.iterdir():
            target = self.root / path.name
            if not target.exists() and path.name != ".git":
                target.symlink_to(path, target_is_directory=path.is_dir())

    def test_repository_metadata(self):
        self.assertEqual(check(self.root)[0], [])

    def test_missing_sitemap_entry_fails(self):
        path = self.root / "sitemap.xml"
        path.write_text(path.read_text().replace(
            "  <url><loc>https://marsharbel.com/saint-charbel-novena</loc></url>\n", ""))
        self.assertTrue(any("missing indexable page https://marsharbel.com/saint-charbel-novena" in error for error in check(self.root)[0]))

    def test_accidentally_indexable_shop_fails(self):
        path = self.root / "shop.html"
        path.write_text(path.read_text().replace("noindex,follow", "index,follow"))
        self.assertTrue(any("missing indexable page https://marsharbel.com/shop" in error for error in check(self.root)[0]))

    def test_generator_preserves_authored_metadata_and_is_repeatable(self):
        original_root = generator.ROOT
        generator.ROOT = self.root
        self.addCleanup(setattr, generator, "ROOT", original_root)
        for name in ["index.html", "saint-charbel-novena.html", "shop.html"]:
            path = self.root / name
            generator.update_file(path)
            self.assertFalse(generator.update_file(path), name)
        homepage = (self.root / "index.html").read_text()
        self.assertIn('"@graph"', homepage)
        self.assertEqual(homepage.count('"@type": "WebPage"'), 1)
        self.assertIn("noindex", (self.root / "shop.html").read_text())
        self.assertIn("Pray the complete nine-day novena", (self.root / "saint-charbel-novena.html").read_text())


if __name__ == "__main__":
    unittest.main()
