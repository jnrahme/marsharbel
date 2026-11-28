"""Exact, user-approved English-first hold for four saint books only."""
import json
import re
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

CONFIG = 'locales/english-first-saint-books.json'
APPROVAL = 'wamid.HBgLMTQwNDQzNzUzNzMVAgASGBYzRUIwODBBQzQ2MzM3MjBERkMxOTEwAA=='
PAGES = {f'{name}-story.html': f'bk-{name}' for name in ('lucy', 'george', 'catherine', 'nicholas')}


def load(root):
    path = root / CONFIG
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if (data.get('schema') != 1 or data.get('approvalMessageId') != APPROVAL
            or data.get('until') != 'native-review' or data.get('pages') != PAGES):
        raise ValueError('English-first saint-book exception must match the four approved routes exactly')
    return data['pages']


def isolation_errors(root, page, registry):
    errors = []
    stem = page[:-5]
    soup = BeautifulSoup((root / page).read_text(), 'html.parser')
    if not soup.html or soup.html.get('lang') != 'en':
        errors.append(page + ': English-first master must be English')
    for link in soup.select('link[hreflang]'):
        if link.get('hreflang') not in ('en', 'x-default'):
            errors.append(page + ': non-English hreflang is held until native review')
    for family in registry.get('pageMirrors', {}).values():
        if family.get('master') == page and (family.get('routes') or family.get('renderLocales')):
            errors.append(page + ': non-English route/render registration is held')
    for code in set(registry.get('locales', {})) - {'en'}:
        if any((root / code / rel).is_file() for rel in (page, stem + '/index.html')):
            errors.append(page + ': non-English stub/page is forbidden: ' + code)
    for sitemap in root.glob('sitemap*.xml'):
        for value in re.findall(r'(?:<loc>|href=[\"\x27])([^<\"\x27]+)', sitemap.read_text()):
            path = urlsplit(value).path.strip('/')
            if path.endswith('/' + stem) or path.endswith('/' + page) or path.endswith('/' + stem + '/index.html'):
                errors.append(page + ': non-English sitemap entry is forbidden')
    book_path = root / 'content/books' / stem / 'book.json'
    if not book_path.exists():
        errors.append(page + ': canonical book registration required')
    else:
        book = json.loads(book_path.read_text())
        if book.get('id') != PAGES[page] or book.get('pageUrl') != '/' + stem or book.get('locales') != ['en']:
            errors.append(page + ': canonical book identity/English-only locales mismatch')
    return errors
