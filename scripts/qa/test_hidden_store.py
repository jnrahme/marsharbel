"""Fail-closed release contract for the hidden, non-transactional /store workshop.

Missing implementation is a failure, never a skip. No credentials or remote API needed.
"""
import os
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PRODUCTS = (
    ('Saint Charbel Classic T-Shirt', '29.99'),
    ('Saint Charbel Winter Chapel Mug', '17.99'),
    ('Saint Charbel Organic Tote Bag', '24.99'),
)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    handle_startendtag = handle_starttag

    def handle_data(self, data):
        self.text.append(data)


def hidden_url(value, source='index.html'):
    url = urlsplit(urljoin('https://marsharbel.com/' + source, value))
    if url.hostname not in ('marsharbel.com', 'www.marsharbel.com'):
        return False
    path = unquote(url.path).lower().rstrip('/')
    return path in ('/store', '/store.html', '/store/index.html')


def page_errors(text):
    doc = Document(text)
    directives = [set(re.split(r'[\s,]+', a.get('content', '').lower()))
                  for tag, a in doc.tags if tag == 'meta' and a.get('name', '').lower() == 'robots']
    errors = []
    if not any({'noindex', 'nofollow'} <= tokens for tokens in directives):
        errors.append('requires robots noindex,nofollow')
    if any({'index', 'follow'} & tokens for tokens in directives):
        errors.append('conflicting robots directive')
    for tag, attrs in doc.tags:
        if tag == 'form':
            errors.append('workshop must not contain forms')
        if tag == 'input' and attrs.get('type', '').lower() in ('password', 'credit-card'):
            errors.append('password/payment input')
    # Deliberately scan source, including comments and inline scripts. This is a
    # targeted regression gate, not a claim to detect every possible secret.
    if re.search(r'shpat_[\w-]+|shpca_[\w-]+|sk_(?:live|test)_[\w-]+|-----BEGIN .*PRIVATE KEY|(?:shopify[_-]?password|api[_-]?secret|access[_-]?token)\s*[=:]\s*[\"\'][^\"\']+', text, re.I):
        errors.append('credential-shaped source')
    if re.search(r'buy-button|ShopifyBuy|Stripe\s*\(|paypal\.com/sdk|/cart/(?:add|checkout)|checkout\.stripe\.com', text, re.I):
        errors.append('payment integration')
    visible = ' '.join(' '.join(doc.text).split())
    for title, price in PRODUCTS:
        # Keep each price associated with its own product, before the next title.
        start = visible.find(title)
        end = min([visible.find(other, start + len(title)) for other, _ in PRODUCTS
                   if visible.find(other, start + len(title)) >= 0] or [len(visible)])
        if start < 0 or not re.search(r'\$\s*' + re.escape(price) + r'\b', visible[start:end]):
            errors.append('missing product/price: ' + title)
    return errors


class HiddenStore(unittest.TestCase):
    def test_page_contract(self):
        pages = [ROOT / p for p in ('store.html', 'store/index.html') if (ROOT / p).exists()]
        self.assertTrue(pages, 'Missing /store implementation: combine feat/hidden-store-page before merging')
        for page in pages:
            text = page.read_text()
            self.assertEqual(page_errors(text), [], str(page.relative_to(ROOT)))
            for tag, attrs in Document(text).tags:
                if tag != 'script' or not attrs.get('src'):
                    continue
                url = urlsplit(urljoin('https://marsharbel.com/' + str(page.relative_to(ROOT)), attrs['src']))
                self.assertIn(url.hostname, ('marsharbel.com', 'www.marsharbel.com'),
                              'Workshop scripts must be local and reviewable')
                asset = ROOT / unquote(url.path).lstrip('/')
                self.assertTrue(asset.is_file(), str(asset))
                # Reuse source scanning without requiring product markup in JS.
                issues = page_errors(asset.read_text())
                self.assertEqual([issue for issue in issues if issue in
                                  ('credential-shaped source', 'payment integration')], [], str(asset))

    def test_no_discovery_links(self):
        files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        for file in files:
            if not file.endswith('.html') or file in ('store.html', 'store/index.html', 'src/pages/store.html', 'src/pages/store/index.html'):
                continue
            for tag, attrs in Document((ROOT / file).read_text()).tags:
                if tag in ('a', 'area', 'link'):
                    self.assertFalse(hidden_url(attrs.get('href', ''), file), f'{file}: discovers /store')
                if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
                    self.assertNotRegex(attrs.get('content', ''), r'(?i)store', file)

    def test_all_sitemaps_exclude_store(self):
        maps = list(ROOT.rglob('*sitemap*.xml'))
        maps = [p for p in maps if not {'node_modules', '.git'} & set(p.parts)]
        self.assertTrue(maps)
        for path in maps:
            for node in ET.parse(path).iter():
                if node.tag.rsplit('}', 1)[-1] == 'loc':
                    self.assertFalse(hidden_url(node.text or ''), str(path))

    def test_flag_is_off(self):
        self.assertNotEqual(os.environ.get('SHOP_LINK_ENABLED'), '1', 'Do not enable SHOP_LINK_ENABLED')
        for directory in ('.github', 'scripts'):
            for path in (ROOT / directory).rglob('*'):
                if path.suffix in ('.yml', '.yaml', '.sh'):
                    self.assertNotRegex(path.read_text(), r'SHOP_LINK_ENABLED\s*[:=]\s*[\"\']?1\b', str(path))

    def test_hostile_controls(self):
        good = '<meta content="nofollow, NOINDEX" name="robots">' + ''.join(
            f'<article><h2>{title}</h2><p>${price}</p></article>' for title, price in PRODUCTS)
        self.assertEqual(page_errors(good), [])
        for bad in (good.replace('NOINDEX', 'index'), good.replace('nofollow', 'follow'),
                    good + '<form action="/checkout"></form>', good + '<input type="password">',
                    good + '<script>ShopifyBuy.buildClient({})</script>',
                    good + '<!-- access_token="synthetic-fixture" -->', good.replace('$29.99', '$1.00')):
            self.assertTrue(page_errors(bad), bad)
        for url in ('/store', '/store/?draft=1', '//marsharbel.com/store.html', '/%73tore/index.html#x'):
            self.assertTrue(hidden_url(url), url)
        self.assertFalse(hidden_url('/stories'))
        self.assertFalse(hidden_url('https://example.invalid/store'))


if __name__ == '__main__':
    unittest.main()
