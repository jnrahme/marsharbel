#!/usr/bin/env python3
"""Check indexable public pages against sitemap and metadata before release."""
from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://marsharbel.com"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.canonicals = []
        self.title = ""
        self.in_title = False
        self.in_schema = False
        self.schema = ""
        self.schemas = []
        self.has_head = False
        self.h1_count = 0
        self.missing_alt = []
        self.references = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in attrs:
            self.missing_alt.append(attrs.get("src", "unknown image"))
        if tag in ("a", "link", "img", "script", "source"):
            reference = attrs.get("href" if tag in ("a", "link") else "src")
            if reference:
                self.references.append(reference)
        if tag == "head":
            self.has_head = True
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property", ""))] = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href", ""))
        if tag == "title":
            self.in_title = True
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_schema = True
            self.schema = ""

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_schema:
            self.schema += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_schema:
            self.schemas.append(self.schema)
            self.in_schema = False


def check(root):
    errors = []
    urls = [node.text for node in ET.parse(root / "sitemap.xml").iter(
        "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if len(urls) != len(set(urls)):
        errors.append("sitemap.xml: duplicate URLs")
    expected = set()
    titles = {}
    for path in sorted([*root.glob("*.html"), *root.glob("mysteries/*.html")]):
        page = Page(path.read_text(encoding="utf-8"))
        # Search Console verification files are tokens, not public HTML pages.
        if not page.has_head:
            if not path.name.startswith("google"):
                errors.append(f"{path.name}: missing HTML head")
            continue
        if "noindex" in page.meta.get("robots", "").lower():
            continue
        relative = path.relative_to(root).with_suffix("").as_posix()
        canonical = SITE + ("/" if relative == "index" else "/" + relative)
        expected.add(canonical)
        if page.h1_count != 1:
            errors.append(f"{path.name}: expected one main heading, found {page.h1_count}")
        for image in page.missing_alt:
            errors.append(f"{path.name}: image missing alt attribute: {image}")
        for reference in page.references:
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            relative_path = unquote(parsed.path)
            target = root / relative_path.lstrip("/") if relative_path.startswith("/") else path.parent / relative_path
            if not target.exists() and not target.with_suffix(".html").exists():
                errors.append(f"{path.name}: missing local link or asset {reference}")
        if page.canonicals != [canonical]:
            errors.append(f"{path.name}: expected exactly one canonical {canonical}")
        if not page.title.strip() or page.title in titles:
            errors.append(f"{path.name}: missing or duplicate title")
        titles[page.title] = path.name
        if not page.meta.get("description", "").strip():
            errors.append(f"{path.name}: missing description")
        if page.meta.get("og:url") != canonical:
            errors.append(f"{path.name}: Open Graph URL differs from canonical")
        for schema in page.schemas:
            try:
                json.loads(schema)
            except ValueError:
                errors.append(f"{path.name}: invalid JSON-LD")
    for url in sorted(expected - set(urls)):
        errors.append(f"sitemap.xml: missing indexable page {url}")
    for url in sorted(set(urls) - expected):
        errors.append(f"sitemap.xml: URL is not an indexable canonical page: {url}")
    if f"Sitemap: {SITE}/sitemap.xml" not in (root / "robots.txt").read_text():
        errors.append("robots.txt: missing sitemap declaration")
    return errors, len(expected)


if __name__ == "__main__":
    errors, count = check(ROOT)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        sys.exit(1)
    print(f"SEO checks passed: {count} indexable pages match the sitemap and metadata rules.")
