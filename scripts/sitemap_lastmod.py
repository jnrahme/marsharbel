#!/usr/bin/env python3
"""Keep sitemap.xml <lastmod> values equal to each page's last real change.

Search engines only trust lastmod when it tracks the page itself, so the date
comes from the git history of the HTML file behind each canonical URL. Files
with uncommitted edits count as changed today.

Usage:
  python3 scripts/sitemap_lastmod.py          # rewrite lastmod values
  python3 scripts/sitemap_lastmod.py --check  # fail if any value is stale
"""
import argparse
from datetime import date
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://marsharbel.com"
ENTRY = re.compile(r"<url>\s*<loc>([^<]+)</loc>(.*?)</url>", re.S)
LASTMOD = re.compile(r"\s*<lastmod>([^<]*)</lastmod>")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}$")


def source_for(root, url):
    """Return the committed HTML file that is served at a canonical URL."""
    if not url.startswith(SITE + "/"):
        raise ValueError(f"not a site URL: {url}")
    path = url[len(SITE) + 1:]
    candidate = root / (path + "index.html" if path == "" or path.endswith("/") else path + ".html")
    if not candidate.is_file():
        raise ValueError(f"no source file for {url}: expected {candidate.relative_to(root)}")
    return candidate


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def history_available(root):
    try:
        return git(root, "rev-parse", "--is-shallow-repository") == "false"
    except (OSError, subprocess.CalledProcessError):
        return False


def last_changed(root, path):
    """Author date (YYYY-MM-DD) of the last commit touching path; today if edited."""
    relative = str(path.relative_to(root))
    if git(root, "status", "--porcelain", "--", relative):
        return date.today().isoformat()
    changed = git(root, "log", "-1", "--format=%as", "--", relative)
    return changed or date.today().isoformat()


def entries(text):
    for match in ENTRY.finditer(text):
        found = LASTMOD.search(match.group(2))
        yield match, match.group(1), found.group(1) if found else None


def validate(root, text=None):
    """Structural checks always; freshness checks only with full git history."""
    text = text if text is not None else (root / "sitemap.xml").read_text(encoding="utf-8")
    errors = []
    today = date.today().isoformat()
    fresh = history_available(root)
    for _, url, lastmod in entries(text):
        if lastmod is None:
            errors.append(f"sitemap.xml: missing lastmod for {url}")
            continue
        if not DATE.match(lastmod):
            errors.append(f"sitemap.xml: lastmod must be YYYY-MM-DD for {url}: {lastmod}")
            continue
        if lastmod > today:
            errors.append(f"sitemap.xml: lastmod is in the future for {url}: {lastmod}")
        if fresh:
            try:
                changed = last_changed(root, source_for(root, url))
            except ValueError as error:
                errors.append(f"sitemap.xml: {error}")
                continue
            if lastmod < changed:
                errors.append(f"sitemap.xml: stale lastmod for {url}: {lastmod} < {changed}; "
                              "run python3 scripts/sitemap_lastmod.py")
    return errors


def update(root):
    path = root / "sitemap.xml"
    text = path.read_text(encoding="utf-8")

    def replace(match):
        url, body = match.group(1), match.group(2)
        changed = last_changed(root, source_for(root, url))
        body = LASTMOD.sub("", body, count=1)
        return f"<url><loc>{url}</loc><lastmod>{changed}</lastmod>{body}</url>"

    updated = ENTRY.sub(replace, text)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
    return updated != text


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not history_available(ROOT):
        sys.exit("Full git history is required (shallow clone detected); fetch with --unshallow.")
    if args.check:
        errors = validate(ROOT)
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1 if errors else 0)
    print("sitemap.xml updated" if update(ROOT) else "sitemap.xml already current")


if __name__ == "__main__":
    main()
