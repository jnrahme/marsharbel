#!/usr/bin/env python3
"""Check indexable public pages against sitemap and metadata before release."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://marsharbel.com"
sys.path.insert(0, str(ROOT / "scripts"))
from i18n.catalog import public_html_files
from sitemap_lastmod import validate as validate_lastmod


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.canonicals = []
        self.alternates = {}
        self.title = ""
        self.in_title = False
        self.in_schema = False
        self.schema = ""
        self.schemas = []
        self.has_head = False
        self.h1_count = 0
        self.missing_alt = []
        self.references = []
        self.anchors = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in attrs:
            self.missing_alt.append(attrs.get("src", "unknown image"))
        if tag == "a" and attrs.get("href"):
            self.anchors.append(attrs["href"])
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
        if tag == "link" and attrs.get("rel") == "alternate" and attrs.get("hreflang"):
            self.alternates[attrs["hreflang"]] = attrs.get("href", "")
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


# 22nd/minibook run inline scripts after their includes; testimonies.html
# loads the Supabase auth client and is left to the testimony lane.
SYNC_SCRIPT_PAGES = {"22nd-of-the-month.html", "rosary-minibook.html", "testimonies.html"}


def check(root):
    errors = []
    urls = [node.text for node in ET.parse(root / "sitemap.xml").iter(
        "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if len(urls) != len(set(urls)):
        errors.append("sitemap.xml: duplicate URLs")
    expected = set()
    pages = {}
    titles = {}
    for path in public_html_files(root):
        page = Page(path.read_text(encoding="utf-8"))
        # Search Console verification files are tokens, not public HTML pages.
        if not page.has_head:
            if not path.name.startswith("google"):
                errors.append(f"{path.name}: missing HTML head")
            continue
        if "noindex" in page.meta.get("robots", "").lower():
            continue
        relative_path = path.relative_to(root)
        if relative_path.name == "index.html":
            directory = relative_path.parent.as_posix()
            canonical = SITE + ("/" if directory == "." else f"/{directory}/")
        else:
            canonical = SITE + "/" + relative_path.with_suffix("").as_posix()
        expected.add(canonical)
        pages[canonical] = page
        # Local scripts load deferred so they never block first paint. Pages
        # with inline scripts that depend on execution order are exempt.
        if relative_path.as_posix() not in SYNC_SCRIPT_PAGES:
            source = path.read_text(encoding="utf-8").split("<body", 1)[-1]
            for tag in re.findall(r"<script\b[^>]*\bsrc=[\"'](?!https?:)[^>]*>", source):
                if not re.search(r"\b(defer|async)\b|type=[\"']module", tag):
                    errors.append(f"{path.name}: render-blocking script, add defer: {tag}")
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
        # Internal links use clean URLs (docs/content-conventions.md): a link to
        # *.html or to "index" is a 301 on every crawl.
        for href in page.anchors:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.path.endswith(".html") or parsed.path.rsplit("/", 1)[-1] == "index":
                errors.append(f"{path.name}: internal link to a redirecting URL, use the clean URL: {href}")
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
    for url, page in pages.items():
        for language, alternate in page.alternates.items():
            if alternate not in pages:
                errors.append(f"{url}: language alternate {language} is not an indexable page: {alternate}")
            elif pages[alternate].alternates != page.alternates:
                errors.append(f"{url}: non-reciprocal language alternates with {alternate}")
    for url in sorted(expected - set(urls)):
        errors.append(f"sitemap.xml: missing indexable page {url}")
    for url in sorted(set(urls) - expected):
        errors.append(f"sitemap.xml: URL is not an indexable canonical page: {url}")
    errors.extend(validate_lastmod(root))
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
