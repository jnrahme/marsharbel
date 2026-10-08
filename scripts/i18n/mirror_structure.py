"""Structural mirror signature: ignore wording, never ignore layout or controls."""
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlsplit
import json

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


def signature(text, route, normalizers=()):
    soup = BeautifulSoup(text, 'html.parser')
    for name in normalizers:
        soup = NORMALIZERS[name](soup)
    def asset(value):
        return urlsplit(urljoin('https://marsharbel.com'+route,value)).path
    return {
        'header': tree(soup.header), 'main': tree(soup.main), 'footer': tree(soup.footer),
        'styles': [asset(n['href']) for n in soup.select('link[rel=stylesheet]')],
        'scripts': [asset(n['src']) for n in soup.select('script[src]')],
        'images': [asset(n['src']) for n in soup.select('main img[src]')],
        'video': [asset(n['data-src-mp4']) for n in soup.select('main [data-src-mp4]')],
    }


def check_pair(master, locale, master_route, locale_route, normalizers=()):
    english = signature(master, master_route)
    translated = signature(locale, locale_route, normalizers)
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

NORMALIZERS = {'launch-availability-annotations': _strip_launch_annotations,
               'partial-home-disclosure': _strip_partial_home_disclosure}
