import importlib.util
import json
import re
from pathlib import Path
import shutil
import tempfile
import unittest

from check_seo import check, public_html_files

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("seo_generator", ROOT / "scripts/apply_seo_tags.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class SeoRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in [*public_html_files(ROOT), ROOT / "sitemap.xml", ROOT / "robots.txt"]:
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
        path.write_text(re.sub(r"  <url><loc>https://marsharbel.com/saint-charbel-novena</loc>.*?</url>\n",
                               "", path.read_text()))
        self.assertTrue(any("missing indexable page https://marsharbel.com/saint-charbel-novena" in error for error in check(self.root)[0]))

    def test_accidentally_indexable_shop_fails(self):
        path = self.root / "shop.html"
        path.write_text(path.read_text().replace("noindex,follow", "index,follow"))
        self.assertTrue(any("missing indexable page https://marsharbel.com/shop" in error for error in check(self.root)[0]))

    def test_nonreciprocal_language_link_fails(self):
        path = self.root / "fr/prieres.html"
        path.write_text(path.read_text().replace('hreflang="ar"', 'hreflang="de"'))
        self.assertTrue(any("non-reciprocal" in error for error in check(self.root)[0]))

    def test_localized_metadata_is_not_replaced_by_english_generator(self):
        path = self.root / "ar/prayers.html"
        before = path.read_text()
        self.assertFalse(generator.update_file(path))
        self.assertEqual(path.read_text(), before)

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

    def test_sitemap_lastmod_is_required_and_well_formed(self):
        path = self.root / "sitemap.xml"
        original = path.read_text()
        url = "https://marsharbel.com/saint-charbel-novena"
        entry = next(line for line in original.splitlines() if f"<loc>{url}</loc>" in line)
        cases = {
            "missing lastmod": re.sub(r"<lastmod>[^<]*</lastmod>", "", entry),
            "must be YYYY-MM-DD": re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>09/20/2026</lastmod>", entry),
            "in the future": re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>2999-01-01</lastmod>", entry),
        }
        for message, replacement in cases.items():
            path.write_text(original.replace(entry, replacement))
            self.assertTrue(any(message in error and url in error for error in check(self.root)[0]), message)
    def test_generator_is_repeatable_across_every_managed_page(self):
        original_root = generator.ROOT
        generator.ROOT = self.root
        self.addCleanup(setattr, generator, "ROOT", original_root)
        for path in [*self.root.glob("*.html"), *self.root.glob("mysteries/*.html")]:
            if path.is_symlink():
                continue
            before = path.read_text()
            self.assertFalse(generator.update_file(path), f"{path.name} drifts from generator output")
            self.assertEqual(path.read_text(), before)

    def test_breadcrumbs_follow_navigation_and_point_at_sitemap_urls(self):
        sitemap = (self.root / "sitemap.xml").read_text()
        pages = [*generator.BREADCRUMBS, *(p.relative_to(ROOT).as_posix() for p in ROOT.glob("mysteries/*.html"))]
        for name in pages:
            html = (self.root / name).read_text()
            blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', html)]
            crumbs = [b["breadcrumb"] for b in blocks if isinstance(b, dict) and "breadcrumb" in b]
            self.assertEqual(len(crumbs), 1, name)
            items = crumbs[0]["itemListElement"]
            self.assertEqual([i["position"] for i in items], list(range(1, len(items) + 1)), name)
            self.assertEqual(items[0]["item"], "https://marsharbel.com/", name)
            self.assertEqual(items[-1]["item"], generator.path_to_url(ROOT / name), name)
            for item in items:
                self.assertIn(f"<loc>{item['item']}</loc>", sitemap, name)

    def test_generator_leaves_unmanaged_and_authored_heads_alone(self):
        original_root = generator.ROOT
        generator.ROOT = self.root
        self.addCleanup(setattr, generator, "ROOT", original_root)
        account = self.root / "account.html"
        before = account.read_text()
        self.assertFalse(generator.update_file(account))
        self.assertEqual(account.read_text(), before)
        voice = self.root / "voice-testimony.html"
        title = re.search(r"<title>(.*?)</title>", voice.read_text())[1]
        generator.update_file(voice)
        self.assertIn(f"<title>{title}</title>", voice.read_text())

    def test_indexable_generated_pages_name_the_site_as_publisher(self):
        for name in ["history.html", "saint-charbel-novena.html", "mysteries/joyful-1.html"]:
            html = (self.root / name).read_text()
            blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', html)]
            pages = [b for b in blocks if isinstance(b, dict) and b.get("@type") == "WebPage"]
            self.assertEqual(pages[0]["isPartOf"]["publisher"], generator.PUBLISHER, name)


if __name__ == "__main__":
    unittest.main()
