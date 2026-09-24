#!/usr/bin/env python3
"""Build /feed.xml (RSS 2.0) from the dated cards on news.html.

news.html is the single source: each <article> in the "Recent News" section
must carry an id, a date tag and a heading. The feed repeats the card text
verbatim and links to the card's anchor on /news.

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
import re
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://marsharbel.com"
NEWS_URL = f"{SITE}/news"
FEED_URL = f"{SITE}/feed.xml"
SECTION = "Recent News, Newest First"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE = re.compile(rf"({MONTHS}) (\d{{1,2}})(?:\s*-\s*(?:(?:{MONTHS}) )?\d{{1,2}})?, (\d{{4}})")


class NewsCards(HTMLParser):
    """Collect id, tag, heading, paragraphs and source link of each news card."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards, self.card, self.field, self.in_section, self.depth = [], None, None, False, 0
        self.h2 = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h2":
            self.h2 = ""
        if not self.in_section:
            return
        if tag == "article":
            self.card = {"id": attrs.get("id"), "tag": "", "title": "", "paragraphs": [], "source": None}
        elif self.card is None:
            return
        elif tag == "span" and "tag" in attrs.get("class", "").split():
            self.field = "tag"
        elif tag == "h3":
            self.field = "title"
        elif tag == "p":
            self.card["paragraphs"].append("")
            self.field = "p"
        elif tag == "a" and self.field == "p" and self.card["source"] is None:
            self.card["source"] = {"url": attrs.get("href"), "label": ""}
            self.field = "a"

    def handle_endtag(self, tag):
        if tag == "h2" and self.h2 is not None:
            self.in_section = self.h2.strip() == SECTION
            self.h2 = None
        elif tag == "section":
            self.in_section = False
        elif tag == "article" and self.card is not None:
            self.cards.append(self.card)
            self.card = None
        elif tag in ("span", "h3", "p"):
            self.field = None
        elif tag == "a" and self.field == "a":
            self.field = "p"

    def handle_data(self, data):
        if self.h2 is not None:
            self.h2 += data
        if self.card is None or self.field is None:
            return
        if self.field == "tag":
            self.card["tag"] += data
        elif self.field == "title":
            self.card["title"] += data
        elif self.field == "p":
            self.card["paragraphs"][-1] += data
        elif self.field == "a":
            self.card["source"]["label"] += data


def clean(text):
    return " ".join(unescape(text).split())


def cards(root=ROOT):
    parser = NewsCards()
    parser.feed((root / "news.html").read_text(encoding="utf-8"))
    result = []
    for card in parser.cards:
        title = clean(card["title"])
        if not card["id"]:
            raise ValueError(f"news.html: card '{title}' needs an id for its feed link")
        match = DATE.search(clean(card["tag"]))
        if not match:
            raise ValueError(f"news.html: card '{title}' has no date in its tag")
        month, day, year = match.group(1), int(match.group(2)), int(match.group(3))
        published = datetime.strptime(f"{month} {day} {year} 12:00", "%B %d %Y %H:%M").replace(tzinfo=timezone.utc)
        body = [clean(p) for p in card["paragraphs"] if clean(p) and (not card["source"] or clean(p) != clean(card["source"]["label"]))]
        tag = clean(card["tag"])
        label = tag.split("\u00b7", 1)[1].strip() if "\u00b7" in tag else ""
        result.append({"id": card["id"], "title": title, "published": published, "body": body, "label": label,
                       "source": card["source"] and {"url": card["source"]["url"], "label": clean(card["source"]["label"])}})
    if not result:
        raise ValueError(f"news.html: no cards found under '{SECTION}'")
    ids = [card["id"] for card in result]
    if len(ids) != len(set(ids)):
        raise ValueError("news.html: duplicate card ids")
    return sorted(result, key=lambda card: card["published"], reverse=True)


def item(card):
    link = f"{NEWS_URL}#{card['id']}"
    # Keep the card's recognition label (e.g. "Reported, recorded at Annaya")
    # so feed readers see the same recognized-vs-reported distinction.
    description = (f"{card['label']}. " if card["label"] else "") + " ".join(card["body"])
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
