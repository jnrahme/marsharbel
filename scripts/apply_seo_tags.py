#!/usr/bin/env python3
from __future__ import annotations

import glob
from html import unescape
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://marsharbel.com"
DEFAULT_IMAGE = f"{SITE}/saint-charbel.jpg"

NOINDEX = {
    "account.html",
    "souvenirs.html",
    "shop.html",
    "submit-testimony.html",
    "testimony-review.html",
    "voice-lab.html",
    "shop-mockup.html",
    "rosary-source-text.html",
}

DESCRIPTIONS = {
    "history.html": "Discover Saint Charbel's life timeline from 1828 to canonization in 1977, including his Maronite monastic vocation and enduring spiritual legacy.",
    "story.html": "Read a child-friendly Saint Charbel storybook for ages 5-12 with simple language, faith lessons, and an engaging guided experience.",
    "miracles.html": "Explore Saint Charbel miracle records with clear distinction between formally recognized Church miracles and reported testimonies from Annaya.",
    "testimonies.html": "Read approved Saint Charbel testimonies reviewed by moderators, with real stories of prayer, healing, and spiritual renewal.",
    "gallery.html": "Browse a real image gallery of Saint Charbel devotion, sacred moments, and visual resources for prayer and reflection.",
    "become-like-charbel.html": "Follow practical Saint Charbel-inspired disciplines including prayer rhythms, silence habits, fasting, humility, and daily spiritual practices.",
    "rosary-visual-guide.html": "Pray the Rosary step by step with a visual Saint Charbel-inspired guide designed for focus, contemplation, and daily devotion.",
    "rosary-intro.html": "Start the Rosary with a clear beginner introduction: structure, prayers, mysteries, and practical guidance for daily Catholic devotion.",
    "rosary-prayer-coach.html": "Use the Rosary Prayer Coach for guided pacing, prayer text support, and an immersive Saint Charbel-centered Rosary routine.",
    "rosary-minibook.html": "Open the Rosary minibook for a compact, easy-to-follow prayer companion covering mysteries, prayers, and daily devotion tips.",
    "rosary-source-text.html": "This page moved to the Rosary Prayer Coach. Use the updated guide for the latest Rosary prayer text and structure.",
    "saint-charbel-prayers.html": "Pray with a curated collection of Saint Charbel prayers, including intercession prayers, daily devotion formulas, and Catholic prayer texts.",
    "voice-testimony.html": "Submit a Saint Charbel voice testimony and share your story of prayer, healing, gratitude, and spiritual transformation.",
    "submit-testimony.html": "Submit your Saint Charbel testimony for moderation and publication to encourage others through authentic stories of faith and intercession.",
    "mystery-meditation.html": "Meditate on Rosary mysteries with guided Saint Charbel prayer prompts, reflective pacing, and audio-assisted contemplation.",
    "shop.html": "Explore Saint Charbel shop offerings and devotional product concepts inspired by prayer, faith, and Catholic spiritual life.",
    "shop-mockup.html": "Preview Saint Charbel shop mockup layouts and design concepts for devotional product presentation.",
    "voice-lab.html": "Test and review Saint Charbel voice and narration tools used for guided prayer and testimony experiences.",
    "index.html": "Discover Saint Charbel’s life, explore miracle reports and testimonies, and find prayers, a nine-day novena, and guided Rosary resources.",
}

CANONICAL_OVERRIDE = {
    "rosary-source-text.html": f"{SITE}/rosary-prayer-coach",
}

TITLE_OVERRIDE = {
    "index.html": "Saint Charbel | History, Miracles, Testimonies & Rosary",
    "history.html": "Saint Charbel History | Biography, Timeline & Canonization",
    "story.html": "Saint Charbel Story for Kids | Catholic Storybook",
    "miracles.html": "Saint Charbel Miracles | Verified Reports & Testimonies",
    "testimonies.html": "Saint Charbel Testimonies | Approved Healing Stories",
    "gallery.html": "Saint Charbel Gallery | Devotional Images",
    "become-like-charbel.html": "How to Live Like Saint Charbel | Daily Spiritual Rule",
    "rosary-visual-guide.html": "How to Pray the Rosary | Visual Guide with Saint Charbel",
    "rosary-intro.html": "Rosary for Beginners | Saint Charbel Intro Guide",
    "rosary-prayer-coach.html": "Rosary Prayer Coach | Guided Catholic Prayer",
    "rosary-minibook.html": "Rosary Mini Book | Quick Prayer Companion",
    "saint-charbel-prayers.html": "Saint Charbel Prayers | Catholic Prayer Collection",
    "voice-testimony.html": "Submit a Voice Testimony | Saint Charbel",
    "submit-testimony.html": "Submit Testimony | Saint Charbel Intercession Stories",
    "mystery-meditation.html": "Rosary Mystery Meditation | Guided Saint Charbel Prayer",
}


# Breadcrumb trails mirror the primary navigation (partials/primary-navigation.html):
# Home > section > page. Each entry is (label, file) for the section and page.
SECTIONS = {
    "story": ("Story", "story.html"),
    "miracles": ("Miracles", "miracles.html"),
    "prayer": ("Prayer", "prayer-library.html"),
    "rosary": ("Rosary Guide", "rosary-visual-guide.html"),
}

BREADCRUMBS = {
    "story.html": (None, "Story for Children"),
    "history.html": ("story", "Full History"),
    "miracles.html": (None, "Miracles"),
    "news.html": ("miracles", "Latest News"),
    "testimonies.html": ("miracles", "Testimonies"),
    "voice-testimony.html": ("miracles", "Voice Testimony"),
    "prayer-library.html": (None, "Prayer Library"),
    "saint-charbel-prayers.html": ("prayer", "Saint Charbel Prayers"),
    "saint-charbel-novena.html": ("prayer", "Saint Charbel Novena"),
    "saint-charbel-feast-day.html": ("prayer", "Feast Day"),
    "rosary-visual-guide.html": ("prayer", "Rosary Guide"),
    "rosary-minibook.html": ("prayer", "Rosary Minibook"),
    "mystery-meditation.html": ("prayer", "Mystery Meditation"),
    "become-like-charbel.html": ("prayer", "Become Like Him"),
    "rosary-intro.html": ("rosary", "Rosary for Beginners"),
    "rosary-prayer-coach.html": ("rosary", "Rosary Prayer Coach"),
    "gallery.html": (None, "Gallery"),
    "visit-annaya.html": (None, "Visiting Annaya"),
    "22nd-of-the-month.html": (None, "The 22nd of the Month"),
    "privacy-policy.html": (None, "Privacy Policy"),
    "terms-of-service.html": (None, "Terms of Service"),
}


def breadcrumb_for(path: Path, title: str) -> dict | None:
    """BreadcrumbList for an indexable English page, or None when not mapped."""
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("mysteries/"):
        section, label = "rosary", title.replace("Saint Charbel | ", "").split(" - ")[0]
    elif rel in BREADCRUMBS:
        section, label = BREADCRUMBS[rel]
    else:
        return None
    trail = [("Home", f"{SITE}/")]
    if section:
        name, file = SECTIONS[section]
        trail.append((name, path_to_url(ROOT / file)))
    trail.append((label, path_to_url(path)))
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": index, "name": name, "item": url}
            for index, (name, url) in enumerate(trail, start=1)
        ],
    }


def escape(value: str, quote: bool = True) -> str:
    """Minimal HTML escaping that keeps authored text stable across runs.

    A bare "&" followed by a space and a straight apostrophe inside a
    double-quoted attribute are valid HTML, so only ambiguous ampersands,
    angle brackets and double quotes are encoded.
    """
    value = re.sub(r"&(?=[A-Za-z#])", "&amp;", value)
    value = value.replace("<", "&lt;").replace(">", "&gt;")
    return value.replace('"', "&quot;") if quote else value


def path_to_url(path: Path) -> str:
    if path.name in CANONICAL_OVERRIDE:
        return CANONICAL_OVERRIDE[path.name]
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{SITE}/"
    if rel.endswith(".html"):
        rel = rel[:-5]
    return f"{SITE}/{rel}"


def page_title(html: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if m:
        return " ".join(m.group(1).split())
    return fallback


def description_for(path: Path, title: str) -> str:
    rel = path.relative_to(ROOT).as_posix()
    name = path.name
    if rel.startswith("mysteries/"):
        pretty = title.replace("Saint Charbel | ", "")
        return trim_description(
            f"Pray the {pretty} with guided Saint Charbel Rosary meditation, Scripture reflection, and step-by-step devotion."
        )
    if name in DESCRIPTIONS:
        return DESCRIPTIONS[name]
    base = title.replace("Saint Charbel |", "").strip()
    return trim_description(
        f"Discover {base} on marsharbel.com with trusted Saint Charbel resources for prayer, history, testimonies, and Catholic devotion."
    )


def trim_description(text: str, max_len: int = 160) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_len:
        return cleaned
    clipped = cleaned[: max_len - 1].rsplit(" ", 1)[0]
    return clipped + "…"


def og_image_for(path: Path) -> str:
    return DEFAULT_IMAGE


def robots_for(path: Path) -> str:
    return "noindex,follow,max-image-preview:large" if path.name in NOINDEX else "index,follow,max-image-preview:large"


def strip_old_seo(html: str) -> str:
    patterns = [
        r"\n\s*<meta\s+name=\"description\"[^>]*>",
        r"\n\s*<meta\s+name=\"robots\"[^>]*>",
        r"\n\s*<link\s+rel=\"canonical\"[^>]*>",
        r"\n\s*<meta\s+property=\"og:type\"[^>]*>",
        r"\n\s*<meta\s+property=\"og:site_name\"[^>]*>",
        r"\n\s*<meta\s+property=\"og:title\"[^>]*>",
        r"\n\s*<meta\s+property=\"og:description\"[^>]*>",
        r"\n\s*<meta\s+property=\"og:url\"[^>]*>",
        r"\n\s*<meta\s+property=\"og:image\"[^>]*>",
        r"\n\s*<meta\s+name=\"twitter:card\"[^>]*>",
        r"\n\s*<meta\s+name=\"twitter:title\"[^>]*>",
        r"\n\s*<meta\s+name=\"twitter:description\"[^>]*>",
        r"\n\s*<meta\s+name=\"twitter:image\"[^>]*>",
    ]
    for p in patterns:
        html = re.sub(p, "", html, flags=re.I)

    # Remove only standalone generated WebPage blocks. Preserve authored graphs,
    # WebSite, BreadcrumbList, and other structured data.
    def remove_webpage(match):
        try:
            data = json.loads(match.group(1))
        except ValueError:
            return match.group(0)
        return "" if isinstance(data, dict) and data.get("@type") == "WebPage" else match.group(0)

    html = re.sub(r'\n\s*<script type="application/ld\+json">([\s\S]*?)</script>', remove_webpage, html, flags=re.I)
    return html


def authored_webpage_fields(html: str) -> dict:
    """Keys an author added to the standalone WebPage block (e.g. dateModified)."""
    for block in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', html, flags=re.I):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        if isinstance(data, dict) and data.get("@type") == "WebPage":
            generated = {"@context", "@type", "name", "description", "url", "isPartOf", "breadcrumb"}
            return {key: value for key, value in data.items() if key not in generated}
    return {}


def build_meta_block(url: str, title: str, description: str, robots: str, image: str, include_schema: bool = True,
                     breadcrumb: dict | None = None, extra: dict | None = None) -> str:
    webpage_schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": url,
        "isPartOf": {"@type": "WebSite", "name": "Saint Charbel", "url": f"{SITE}/"},
    }
    webpage_schema.update(extra or {})
    if breadcrumb:
        webpage_schema["breadcrumb"] = breadcrumb
    schema = json.dumps(webpage_schema, ensure_ascii=True, indent=2)
    url, title, description, robots, image = (escape(value, quote=True) for value in (url, title, description, robots, image))
    return (
        f"\n  <meta name=\"description\" content=\"{description}\" />"
        f"\n  <meta name=\"robots\" content=\"{robots}\" />"
        f"\n  <link rel=\"canonical\" href=\"{url}\" />"
        f"\n  <meta property=\"og:type\" content=\"website\" />"
        f"\n  <meta property=\"og:site_name\" content=\"Saint Charbel\" />"
        f"\n  <meta property=\"og:title\" content=\"{title}\" />"
        f"\n  <meta property=\"og:description\" content=\"{description}\" />"
        f"\n  <meta property=\"og:url\" content=\"{url}\" />"
        f"\n  <meta property=\"og:image\" content=\"{image}\" />"
        f"\n  <meta name=\"twitter:card\" content=\"summary_large_image\" />"
        f"\n  <meta name=\"twitter:title\" content=\"{title}\" />"
        f"\n  <meta name=\"twitter:description\" content=\"{description}\" />"
        f"\n  <meta name=\"twitter:image\" content=\"{image}\" />"
        + (f"\n  <script type=\"application/ld+json\">\n{schema}\n  </script>" if include_schema else "")
    )


def update_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    # Localized editorial pages own their metadata and schema.
    if "Generated by npm run i18n:build" in html:
        return False
    if "<head>" not in html:
        return False
    # Pages without a canonical link (account, prelaunch souvenirs, verification
    # tokens) own their head; the generator never managed them.
    if 'rel="canonical"' not in html:
        return False

    # Authored titles win; overrides only fill pages that have no title yet.
    existing_title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    title = unescape(page_title(html, "Saint Charbel")) if existing_title and existing_title[1].strip() \
        else TITLE_OVERRIDE.get(path.name, "Saint Charbel")
    html = re.sub(r"<title>.*?</title>", lambda _: f"<title>{escape(title)}</title>", html, count=1, flags=re.I | re.S)
    existing_description = re.search(r'<meta name="description" content="([^"]*)"', html)
    description = unescape(existing_description[1]) if existing_description else description_for(path, title)
    url = path_to_url(path)
    existing_robots = re.search(r'<meta name="robots" content="([^"]*)"', html)
    robots = existing_robots[1] if existing_robots and "noindex" in existing_robots[1] else robots_for(path)
    image = og_image_for(path)

    html2 = strip_old_seo(html)
    has_graph_page = bool(re.search(r'"@graph"[\s\S]*?"@type"\s*:\s*"WebPage"', html2))
    breadcrumb = breadcrumb_for(path, title) if "noindex" not in robots else None
    meta_block = build_meta_block(url=url, title=title, description=description, robots=robots, image=image,
                                  include_schema=not has_graph_page, breadcrumb=breadcrumb,
                                  extra=authored_webpage_fields(html))

    html3, count = re.subn(r"(<title>.*?</title>)", lambda match: match[1] + meta_block, html2, count=1, flags=re.I | re.S)
    if count == 0:
        return False

    if html3 != html:
        path.write_text(html3, encoding="utf-8")
        return True
    return False


def main() -> None:
    files = [Path(p) for p in glob.glob(str(ROOT / "*.html"))]
    files += [Path(p) for p in glob.glob(str(ROOT / "mysteries" / "*.html"))]

    changed = 0
    for path in sorted(files):
        if update_file(path):
            changed += 1

    print(f"Updated SEO tags in {changed} files")


if __name__ == "__main__":
    main()
