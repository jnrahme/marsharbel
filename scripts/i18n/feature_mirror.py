"""Bounded extracted-feature validation; no whole-page mirror exceptions."""
import hashlib
import html
import json
import re
from bs4 import BeautifulSoup

FEATURES = {'film-premiere-v1': {
    'source': 'news.html', 'template': 'templates/news-desk/cards.html',
    'catalog': 'locales/en/news-desk.json', 'selector': 'article#charbel-premiere-release-2026-10',
    'target': 'ar/charbel-film-premiere.html', 'targetSelector': 'article#charbel-premiere-release-2026-10',
    'localeCatalog': 'locales/ar/film-premiere-copy.json', 'prefix': 'premiere.',
    'sourceRoute': '/news', 'route': '/ar/charbel-film-premiere', 'locale': 'ar', 'direction': 'rtl',
}}

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def one(soup, selector):
    nodes = soup.select(selector)
    if len(nodes) != 1:
        raise ValueError('Expected exactly one feature: ' + selector)
    return nodes[0]

def adapted(block):
    """The only permitted source-to-standalone changes, tested individually."""
    block = BeautifulSoup(str(block), 'html.parser').article
    heading = block.find('h3', recursive=False)
    if heading is None or len(heading.select('a.card-cover')) != 1:
        raise ValueError('Unexpected source heading')
    heading.name = 'h1'
    heading.a.unwrap()
    subheads = block.find_all('h4')
    if len(subheads) != 1:
        raise ValueError('Expected one video heading')
    subheads[0].name = 'h2'
    block['class'] = ['film-news-article']
    return block

def shell_digest(text, route):
    soup = BeautifulSoup(text, 'html.parser')
    feature = one(soup, 'main > article.film-news-article')
    feature.decompose()
    # Independent final-shell pin includes every attribute, label, metadata value,
    # full URL/query, runtime dictionary and control. Only feature is excluded.
    return digest(str(soup))

def check_feature(root, entry, contract):
    """Verify provenance and final bytes. Raises on malformed or stale claims."""
    family = entry['family']
    if family not in FEATURES:
        raise ValueError('Unregistered feature family')
    spec = FEATURES[family]
    if entry['master'] != spec['source'] or entry['route'] != spec['route'] or entry['locale'] != spec['locale']:
        raise ValueError('Feature identity mismatch')
    if entry.get('normalizers') or entry.get('exceptions'):
        raise ValueError('Feature bypasses forbidden')
    if contract.get('family') != family or contract.get('version') != 1:
        raise ValueError('Feature contract identity mismatch')
    source = (root/spec['source']).read_text()
    template = (root/spec['template']).read_text()
    english = json.loads((root/spec['catalog']).read_text())
    localized = json.loads((root/spec['localeCatalog']).read_text())
    raw = one(BeautifulSoup(template, 'html.parser'), spec['selector'])
    keys = set(re.findall(r'\$\{([^}]+)\}', str(raw)))
    if not keys or any(not k.startswith(spec['prefix']) for k in keys):
        raise ValueError('Foreign or absent feature key')
    if set(contract['textKeys']) != keys or len(contract['textKeys']) != len(keys):
        raise ValueError('Text key coverage mismatch')
    if set(localized) != keys:
        raise ValueError('Locale catalog must cover exactly feature text keys')
    for k in keys:
        if k not in english or not isinstance(localized[k], str) or not localized[k].strip() or re.search(r'<\s*/?\s*[A-Za-z!]',localized[k]):
            raise ValueError('Invalid feature value: ' + k)
    en_values = {k:english[k] for k in sorted(keys)}
    provenance = {'templateSha256':digest(str(raw)), 'englishCatalogSha256':digest(json.dumps(en_values,ensure_ascii=False,sort_keys=True))}
    for key, expected in provenance.items():
        if contract.get(key) != expected:
            raise ValueError('Stale source provenance: '+key)
    render = lambda values: re.sub(r'\$\{([^}]+)\}', lambda m:html.escape(values[m[1]],quote=True),str(raw))
    # Served source must contain the claimed feature, not a stale catalog extract.
    actual_source = one(BeautifulSoup(source,'html.parser'),spec['selector'])
    rendered_en = BeautifulSoup(render(english),'html.parser').article
    if str(actual_source) != str(rendered_en):
        raise ValueError('Served source differs from keyed EN feature')
    if contract.get('sourceFeatureSha256') != digest(str(actual_source)):
        raise ValueError('Stale served feature provenance')
    target = (root/spec['target']).read_text()
    soup = BeautifulSoup(target,'html.parser')
    actual = one(soup,spec['targetSelector'])
    if actual.parent is not soup.main or len(soup.select('main article')) != 1:
        raise ValueError('Target is not one standalone feature')
    expected = adapted(BeautifulSoup(render(localized),'html.parser').article)
    # Exact translated subtree catches missing/extra prose, alt/title, link query,
    # iframe permissions, media and structure changes. No text stripping here.
    if str(actual) != str(expected):
        raise ValueError('Translated feature content/links/video differ')
    if soup.html.get('lang') != spec['locale'] or soup.html.get('dir') != spec['direction']:
        raise ValueError('Feature language/direction mismatch')
    canonical = one(soup,'link[rel=canonical]').get('href')
    if canonical != 'https://marsharbel.com'+spec['route']:
        raise ValueError('Feature canonical mismatch')
    if len(soup.select('h1')) != 1 or soup.header is None or soup.footer is None:
        raise ValueError('Feature shell missing')
    if contract.get('shellSha256') != shell_digest(target,spec['route']):
        raise ValueError('Final feature shell differs from independent pin')
    return []
