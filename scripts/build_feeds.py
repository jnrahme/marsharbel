#!/usr/bin/env python3
"""Build /feed.xml (RSS 2.0) from the dated rows on news.html.

news.html is the single source: each <article class="news-row"> in the news
feed must carry an id, a chip, a heading, a <time datetime> and a summary.
The feed repeats the row summary verbatim and links to the row's anchor on
/news. The collapsed sources/credits block is not part of the feed list and
is never read.

Usage:
  python3 scripts/build_feeds.py          # write feed.xml
  python3 scripts/build_feeds.py --check  # fail if feed.xml is stale
"""
import argparse
from datetime import datetime, timezone
from email.utils import format_datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://marsharbel.com"
NEWS_URL = f"{SITE}/news"
FEED_URL = f"{SITE}/feed.xml"

# Feed labels that predate the chip vocabulary and must keep their exact
# wording so long-standing feed items do not change meaning for subscribers.
LEGACY_LABELS = {
    "new-miracles-reported-2026-01": "Reported, recorded at Annaya",
    # Past event: the plain "Announcement" chip reads as upcoming in the feed,
    # so keep the archived wording subscribers already received.
    "el-paso-lebanese-festival-2026-10": "Archived parish announcement",
    # Same past-event case as the festival row: the October 13 Rosary has
    # passed, so the feed label freezes the archived wording.
    "pope-leo-rosary-announcement-2026-10-13": "Archived Rosary announcement",
}
# pubDate values subscribers already received; keyed by row id so the item
# date stays stable even when the row shows the event date (e.g. the
# premiere row shows October 9 but was reported October 10).
LEGACY_PUBDATES = {
    "charbel-premiere-release-2026-10": "2026-10-10",
}
# Declared sources that the compact row markup no longer carries inline,
# keyed by the row's card-cover href. The premiere row links its whole card
# to the report page /charbel-film-premiere, but subscribers were sent the
# L'Orient-Le Jour charity-screening report as the item's source; keep that
# external source (and its original label) so the item's declared source and
# click target do not change. This is the only place this URL is hard-coded.
LEGACY_SOURCES = {
    "/charbel-film-premiere": {
        "url": "https://www.lorientlejour.com/article/1550058/la-projection-du-film-charbel-au-profit-de-anta-akhi.html",
        "label": "L'Orient-Le Jour: October 12 charity screening for Anta Akhi (October 8, French)",
    },
}


class NewsRows(HTMLParser):
    """Collect id, chip, heading, date, summary and source link of each news row."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.field = [], None, None
        self.in_main = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "main":
            self.in_main = True
            return
        if not self.in_main:
            return
        if tag == "article" and "news-row" in attrs.get("class", "").split():
            self.row = {"id": attrs.get("id"), "chip": "", "title": "", "summary": [], "datetime": None, "source": None}
        elif self.row is None:
            return
        elif tag == "span" and "chip" in attrs.get("class", "").split():
            self.field = "chip"
        elif tag == "a" and "card-cover" in attrs.get("class", "").split():
            self.row["source"] = {"url": attrs.get("href"), "label": ""}
            self.field = "title"
        elif tag == "p" and "news-row-summary" in attrs.get("class", "").split():
            self.row["summary"].append("")
            self.field = "summary"
        elif tag == "time" and attrs.get("datetime"):
            self.row["datetime"] = attrs["datetime"]
            self.field = "time"

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
        elif tag == "article" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
            self.field = None
        elif tag in ("span", "a", "p", "time") and self.field is not None:
            self.field = None

    def handle_data(self, data):
        if self.row is None or self.field is None:
            return
        if self.field == "chip":
            self.row["chip"] += data
        elif self.field == "title":
            self.row["title"] += data
            self.row["source"]["label"] += data
        elif self.field == "summary":
            self.row["summary"][-1] += data


def clean(text):
    return " ".join(unescape(text).split())


def cards(root=ROOT):
    parser = NewsRows()
    parser.feed((root / "news.html").read_text(encoding="utf-8"))
    result = []
    for row in parser.rows:
        title = clean(row["title"])
        if not row["id"]:
            raise ValueError(f"news.html: card '{title}' needs an id for its feed link")
        stamp = LEGACY_PUBDATES.get(row["id"], row["datetime"])
        if not stamp:
            raise ValueError(f"news.html: card '{title}' has no date in its tag")
        published = datetime.strptime(stamp, "%Y-%m-%d").replace(hour=12, tzinfo=timezone.utc)
        body = [clean(p) for p in row["summary"] if clean(p)]
        label = LEGACY_LABELS.get(row["id"], clean(row["chip"]))
        source = row["source"] and {"url": row["source"]["url"], "label": clean(row["source"]["label"])}
        if row["source"] and row["source"]["url"] in LEGACY_SOURCES:
            source = dict(LEGACY_SOURCES[row["source"]["url"]])
        result.append({"id": row["id"], "title": title, "published": published, "body": body, "label": label,
                       "source": source})
    if not result:
        raise ValueError("news.html: no cards found under the news feed")
    ids = [card["id"] for card in result]
    if len(ids) != len(set(ids)):
        raise ValueError("news.html: duplicate card ids")
    return sorted(result, key=lambda card: card["published"], reverse=True)


def item(card):
    link = f"{NEWS_URL}#{card['id']}"
    # Keep the row's recognition label (e.g. "Reported, recorded at Annaya")
    # so feed readers see the same recognized-vs-reported distinction.
    body = " ".join(card["body"])
    # Skip the label prefix when the summary already opens with the label
    # (case-insensitive), so a legacy label does not double in the feed.
    if card["label"] and body.lower().startswith(card["label"].lower()):
        description = body
    else:
        description = (f"{card['label']}. " if card["label"] else "") + body
    if card["source"]:
        description += f" Source: {card['source']['label']} ({card['source']['url']})"
    return (
        "    <item>\n"
        f"      <title>{escape(card['title'])}</title>\n"
        f"      <link>{escape(link)}</link>\n"
        f"      <guid isPermaLink=\"true\">{escape(link)}</guid>\n"
        f"      <pubDate>{format_datetime(card['published'])}</pubDate>\n"
        + (f"      <category>{escape(card['label'])}</category>\n" if card["label"] else "")
        + f"      <description>{escape(description)}</description>\n"
        "    </item>\n"
    )


def news_feed(root=ROOT):
    items = cards(root)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Saint Charbel News | marsharbel.com</title>\n"
        f"    <link>{NEWS_URL}</link>\n"
        f'    <atom:link href="{FEED_URL}" rel="self" type="application/rss+xml" />\n'
        "    <description>Sourced Saint Charbel news: pilgrimages, feast days, relic visits and newly reported cases, "
        "each labeled as formally recognized or reported.</description>\n"
        "    <language>en</language>\n"
        f"    <lastBuildDate>{format_datetime(items[0]['published'])}</lastBuildDate>\n"
        f"    <image>\n      <url>{SITE}/saint-charbel.jpg</url>\n      <title>Saint Charbel News | marsharbel.com</title>\n"
        f"      <link>{NEWS_URL}</link>\n    </image>\n"
        + "".join(item(card) for card in items)
        + "  </channel>\n</rss>\n"
    )


def outputs(root=ROOT):
    return {root / "feed.xml": news_feed(root)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, expected in outputs().items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != expected:
            if args.check:
                stale.append(path.name)
            else:
                path.write_text(expected, encoding="utf-8")
    if stale:
        sys.exit("Stale feeds; run python3 scripts/build_feeds.py: " + ", ".join(stale))
    print("Feeds checked." if args.check else "Feeds built.")


if __name__ == "__main__":
    main()
