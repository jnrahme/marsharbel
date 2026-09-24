import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_feeds", ROOT / "scripts/build_feeds.py")
feeds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feeds)


class NewsFeedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copyfile(ROOT / "news.html", self.root / "news.html")

    def test_committed_feed_matches_news_page(self):
        self.assertEqual((ROOT / "feed.xml").read_text(encoding="utf-8"), feeds.news_feed(ROOT))

    def test_feed_is_rss2_with_self_link_and_anchored_items(self):
        root = ET.fromstring(feeds.news_feed(self.root))
        self.assertEqual(root.tag, "rss")
        self.assertEqual(root.get("version"), "2.0")
        channel = root.find("channel")
        self.assertEqual(channel.find("{http://www.w3.org/2005/Atom}link").get("href"), feeds.FEED_URL)
        items = channel.findall("item")
        self.assertGreater(len(items), 0)
        html = (self.root / "news.html").read_text()
        dates = []
        for entry in items:
            link = entry.findtext("link")
            self.assertTrue(link.startswith(feeds.NEWS_URL + "#"))
            self.assertIn(f'id="{link.split("#", 1)[1]}"', html)
            self.assertEqual(entry.findtext("guid"), link)
            dates.append(feeds.cards(self.root)[len(dates)]["published"])
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_reported_cases_keep_their_label(self):
        root = ET.fromstring(feeds.news_feed(self.root))
        reported = [i for i in root.iter("item") if "Two New Miracles" in i.findtext("title")][0]
        self.assertEqual(reported.findtext("category"), "Reported, recorded at Annaya")
        self.assertTrue(reported.findtext("description").startswith("Reported, recorded at Annaya."))

    def test_card_without_id_fails(self):
        path = self.root / "news.html"
        path.write_text(path.read_text().replace(' id="revesby-feast-2026-07"', "", 1))
        with self.assertRaisesRegex(ValueError, "needs an id"):
            feeds.cards(self.root)


if __name__ == "__main__":
    unittest.main()
