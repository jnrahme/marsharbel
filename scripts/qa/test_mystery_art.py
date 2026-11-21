"""Gate for the rosary mystery artwork swap.

- No rosarycenter.org URL may remain in mystery-data.js or the built mystery pages.
- Every mystery image points at a self-hosted webp under media/mysteries/ that exists.
- Every artwork credit link is a Wikimedia Commons File: page URL.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MYSTERY_PAGES = sorted((ROOT / "mysteries").glob("*.html")) + [ROOT / "mystery-meditation.html"]
DATA_FILE = ROOT / "mystery-data.js"
COMMONS_FILE_RE = re.compile(r"^https://commons\.wikimedia\.org/wiki/File:.+")


def load_data():
    text = DATA_FILE.read_text(encoding="utf-8")
    prefix = "window.ROSARY_MYSTERIES ="
    assert text.startswith(prefix), "mystery-data.js prefix changed"
    body = text[len(prefix):].strip()
    if body.endswith(';'):
        body = body[:-1]
    return json.loads(body)


class MysteryArtTests(unittest.TestCase):
    def test_no_rosarycenter_urls_remain(self):
        offenders = []
        if "rosarycenter.org" in DATA_FILE.read_text(encoding="utf-8"):
            offenders.append("mystery-data.js")
        for page in MYSTERY_PAGES:
            if "rosarycenter.org" in page.read_text(encoding="utf-8"):
                offenders.append(page.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [])

    def test_twenty_self_hosted_images_exist(self):
        data = load_data()
        self.assertEqual(len(data), 20)
        for key, entry in data.items():
            image = entry.get("image", "")
            self.assertTrue(image.startswith("/media/mysteries/"), f"{key}: {image}")
            self.assertTrue(image.endswith(".webp"), f"{key}: {image}")
            path = ROOT / image.lstrip("/")
            self.assertTrue(path.is_file(), f"{key}: missing {image}")
            blob = path.read_bytes()
            self.assertEqual(blob[:4], b"RIFF", f"{key}: not a RIFF container")
            self.assertEqual(blob[8:12], b"WEBP", f"{key}: not webp")
            self.assertLessEqual(len(blob), 90 * 1024, f"{key}: over size cap")
            self.assertGreater(entry.get("imageWidth", 0), 0, f"{key}: imageWidth")
            self.assertGreater(entry.get("imageHeight", 0), 0, f"{key}: imageHeight")

    def test_credit_links_are_commons_file_pages(self):
        data = load_data()
        for key, entry in data.items():
            url = entry.get("imageCreditUrl", "")
            self.assertRegex(url, COMMONS_FILE_RE, f"{key}: {url}")
            self.assertIn("Wikimedia Commons", entry.get("imageCredit", ""), f"{key}: credit text")
            for lang in ("fr", "ar"):
                localized = entry.get("i18n", {}).get(lang, {})
                self.assertIn("Wikimedia Commons", localized.get("imageCredit", ""), f"{key} {lang}: credit")

    def test_each_mystery_page_carries_credit_with_commons_link(self):
        for page in sorted((ROOT / "mysteries").glob("*.html")):
            html = page.read_text(encoding="utf-8")
            credits = re.findall(r'<p class="mystery-art-credit">(.+?)</p>', html, re.S)
            self.assertEqual(len(credits), 1, f"{page.name}: credit count")
            hrefs = re.findall(r'href="([^"]+)"', credits[0])
            self.assertEqual(len(hrefs), 1, f"{page.name}: credit link count")
            self.assertRegex(hrefs[0], COMMONS_FILE_RE, f"{page.name}: {hrefs[0]}")


if __name__ == "__main__":
    unittest.main()
