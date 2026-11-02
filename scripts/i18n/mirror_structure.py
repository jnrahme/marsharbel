"""Structural mirror signature: ignore wording, never ignore layout or controls."""
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlsplit
import json
import re

INVARIANT = {'id','class','style','hidden','inert','role','tabindex','type','colspan','rowspan','width','height','loading','decoding','aria-hidden','aria-expanded','aria-controls','aria-labelledby','aria-describedby','aria-haspopup','disabled','required','readonly','maxlength','rows'}


def tree(node):
    if not isinstance(node, Tag) or node.name in ('script','style'):
        return None
    attrs = {key:value for key,value in node.attrs.items() if key in INVARIANT or key.startswith('data-')}
    attrs.pop('data-authored-mirror', None)
    # Media URLs are canonicalized separately, not allowed to change.
    attrs.pop('data-src-mp4', None)
    children = [item for child in node.children if (item := tree(child)) is not None]
    return [node.name, attrs, children]


def signature(text, route, normalizers=(), context=None):
    # PR3: the marked generated locale-nav is post-pin control chrome, never
    # page structure - strip it symmetrically on both sides before comparing.
    from i18n.keyed_master import strip_static_fallback_text
    text = strip_static_fallback_text(text)
    if 'stories-keyed-data-copy' in normalizers:
        from i18n.stories_shelf_copy import reject_duplicate_attributes
        reject_duplicate_attributes(text)
    soup = BeautifulSoup(text, 'html.parser')
    for name in normalizers:
        if name in NORMALIZERS:
            soup = NORMALIZERS[name](soup)
        elif name in CONTEXT_NORMALIZERS:
            if not context or not context.get('family') or not context.get('lang'):
                raise ValueError(f'normalizer {name} requires family+lang context')
            soup = CONTEXT_NORMALIZERS[name](soup, context)
        else:
            raise ValueError(f'unregistered normalizer {name}')
    def asset(value):
        return urlsplit(urljoin('https://marsharbel.com'+route,value)).path
    return {
        'header': tree(soup.header), 'main': tree(soup.main), 'footer': tree(soup.footer),
        'styles': [asset(n['href']) for n in soup.select('link[rel=stylesheet]')],
        'scripts': [asset(n['src']) for n in soup.select('script[src]')],
        'images': [asset(n['src']) for n in soup.select('main img[src]')],
        'video': [asset(n['data-src-mp4']) for n in soup.select('main [data-src-mp4]')],
    }


def check_pair(master, locale, master_route, locale_route, normalizers=(), context=None):
    if 'stories-keyed-data-copy' in normalizers:
        if not context:
            raise ValueError('Stories copy comparison requires trusted context')
        english = signature(master, master_route, ('stories-keyed-data-copy',), {**context, 'side': 'en'})
        translated = signature(locale, locale_route, normalizers, {**context, 'side': 'locale'})
    else:
        english = signature(master, master_route)
        translated = signature(locale, locale_route, normalizers, context)
    return [key for key in english if english[key] != translated[key]]

def _strip_launch_annotations(soup):
    """Remove reviewed launch-availability annotations (English-only qualifiers and
    the launch-availability aside) that limited-launch locale pages add on top of
    the shared master structure. Scoped: only these two authored classes."""
    for node in soup.select('.launch-english-qualifier'):
        node.decompose()
    for node in soup.select('aside.launch-availability'):
        node.decompose()
    return soup


def _strip_partial_home_disclosure(soup):
    for hint in soup.select('span.partial-home-language'):
        from bs4 import NavigableString
        anchor=hint.parent
        if anchor.name != 'a' or anchor.get('href') != '/' or anchor.get('hreflang') != 'en':
            raise ValueError('Unexpected partial Home disclosure target')
        if len(anchor.select(':scope > span.partial-home-language')) != 1 or len(hint.contents) != 1 or not isinstance(hint.contents[0], NavigableString):
            raise ValueError('Partial Home disclosure must be one text-only qualifier')
        qualifier=str(hint.contents[0]).strip()
        label=anchor.get_text(' ',strip=True)
        if not qualifier or anchor.get('aria-label') != label:
            raise ValueError('Partial Home qualifier/accessible label mismatch')
        hint.decompose()
    return soup


def _strip_english_nav_disclosure(soup):
    """Remove reviewed English-destination disclosure marks added inside the shared
    header on locale pages (hreflang/aria-label plus one visible qualifier span).
    Scoped: only inside <header>; validates the full reviewed shape and raises on
    any deviation, so an unexpected header change still fails the gate."""
    from bs4 import NavigableString
    header = soup.header
    if header is None:
        return soup
    for hint in header.select('span.enc-language'):
        anchor = hint.parent
        if anchor.name != 'a' or anchor.get('hreflang') != 'en':
            raise ValueError('English nav disclosure must sit on an hreflang="en" anchor')
        href = anchor.get('href') or ''
        if not href.startswith('/') or re.match(r'^/(ar|de|es|fr|hi|it|pl|pt|ru|th|zh-Hans)(/|$)', href):
            raise ValueError('English nav disclosure target must be an unprefixed English route')
        if hint.get('class') != ['enc-language'] or len(anchor.select(':scope > span.enc-language')) != 1 or len(hint.contents) != 1 or not isinstance(hint.contents[0], NavigableString):
            raise ValueError('English nav disclosure must be one text-only qualifier')
        qualifier = str(hint.contents[0]).strip()
        visible = ''.join(text for text in anchor.find_all(string=True) if text.find_parent('span', class_='enc-language') is None).strip()
        if not qualifier or not visible or anchor.get('aria-label') != visible + ' ' + qualifier:
            raise ValueError('English nav disclosure qualifier/accessible label mismatch')
        hint.decompose()
    return soup

def _strip_localized_source_links(soup, context):
    """Revert this page's registered per-locale citation hrefs to the master target.

    Scoped to the exact (family, lang) page identity from context: only that
    family's registered swaps for that locale revert, with strict
    missing/duplicate/wrong-locale/unregistered checks - never a registry-wide
    reversal.
    """
    import json as _json
    from pathlib import Path as _Path
    from i18n.localized_source_links import strip_localized_source_links
    registry = _json.loads((_Path(__file__).resolve().parents[2] / 'locales/registry.json').read_text())
    return strip_localized_source_links(soup, registry, context['family'], context['lang'])


def _strip_home_intro_twin_link(soup):
    """Remove the reviewed intro-twin promo link: keeps a hand-authored same-page
    intro twin (e.g. /ar/rosary) reachable from the locale home after the YouTube
    promo retargets to the guide. The label is the twin's own H1. Scoped and
    fail-closed: only anchors carrying the authored marker class, exact shape."""
    from bs4 import NavigableString
    for anchor in list(soup.select('a.intro-twin-link')):
        if anchor.name != 'a' or anchor.get('class') != ['promo-link', 'intro-twin-link']:
            raise ValueError('Intro-twin link must be a promo-link anchor with the marker class')
        spans = anchor.select(':scope > span')
        if len(spans) != 1 or spans[0].get('aria-hidden') != 'true' or spans[0].get_text(strip=True) != '\u2192':
            raise ValueError('Intro-twin link must end with one hidden arrow span')
        texts = [c for c in anchor.contents if isinstance(c, NavigableString) and c.strip()]
        if len(texts) != 1:
            raise ValueError('Intro-twin link must carry one text label')
        anchor.decompose()
    return soup


NORMALIZERS = {'home-intro-twin-link': _strip_home_intro_twin_link,'launch-availability-annotations': _strip_launch_annotations,
               'partial-home-disclosure': _strip_partial_home_disclosure,
               'english-nav-disclosure': _strip_english_nav_disclosure}

# Normalizers that need the exact page identity (family+lang) to act; signature()
# requires a context argument when one of these is requested.
def _normalize_stories_keyed_data(soup, context):
    from i18n.stories_shelf_copy import normalize_stories_data
    return normalize_stories_data(soup, context)


CONTEXT_NORMALIZERS = {'localized-source-links': _strip_localized_source_links,
                       'stories-keyed-data-copy': _normalize_stories_keyed_data}
