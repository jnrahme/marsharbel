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


def signature(text, route):
    soup = BeautifulSoup(text, 'html.parser')
    def asset(value):
        return urlsplit(urljoin('https://marsharbel.com'+route,value)).path
    return {
        'header': tree(soup.header), 'main': tree(soup.main), 'footer': tree(soup.footer),
        'styles': [asset(n['href']) for n in soup.select('link[rel=stylesheet]')],
        'scripts': [asset(n['src']) for n in soup.select('script[src]')],
        'images': [asset(n['src']) for n in soup.select('main img[src]')],
        'video': [asset(n['data-src-mp4']) for n in soup.select('main [data-src-mp4]')],
    }


def check_pair(master, locale, master_route, locale_route):
    english = signature(master, master_route)
    translated = signature(locale, locale_route)
    return [key for key in english if english[key] != translated[key]]
