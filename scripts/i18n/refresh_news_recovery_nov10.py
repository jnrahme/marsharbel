"""Precisely bind November recovery after normal news/page builds.
Survivor sources are invariant. Agent translations are not native-certified.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.keyed_master import strip_static_fallback
from i18n.refresh_almoner_oct30_home import selector, text_candidates, common_suffix

CONTAINER = '#main-content > section:nth-of-type(3) > div:nth-of-type(1)'
HOME_HREF = './news#apecl-bkerke-solidarity-2026-11-09'


def load(path):
    return json.loads(path.read_text())


def verify(bindings, soup):
    for b in bindings:
        nodes = soup.select(b['selector'])
        if len(nodes) != 1:
            raise ValueError('Selector not unique: ' + b['selector'])
        n = nodes[0]
        value = n.get(b['attribute']) if b['kind'] == 'attribute' else ' '.join(str(n.contents[b['nodeIndex']]).split())
        if value != b['source']:
            raise ValueError('Source drift: ' + b['key'])


def binding(key, node, value):
    return {'key': key, 'selector': selector(node), 'source': value, 'kind': 'text', 'nodeIndex': 0}


def outputs(root=ROOT):
    pack = load(root / 'locales/news-recovery-nov10-translations.json')
    registry = load(root / 'locales/registry.json')
    if pack['status'] != 'agent-translated-native-not-certified':
        raise ValueError('Translation scope changed')
    result = {}
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    contract = load(root / 'locales/en/news-master-bindings.json')
    en = load(root / 'locales/en/news-master-copy.json')
    ar = load(root / 'locales/ar/news-master-copy.json')
    if registry['pageMirrors']['news-master']['renderLocales'] != ['ar']:
        raise ValueError('Archive locale scope changed')
    applied = 'news.recovery.november-2026' in en
    bindings = []
    for old in contract['bindings']:
        b = dict(old)
        if not applied and b['selector'].startswith(CONTAINER + ' > '):
            b['selector'] = re.sub(r'^' + re.escape(CONTAINER) + r' > (p|ul):nth-of-type\((\d+)\)', lambda m: CONTAINER + ' > ' + m[1] + ':nth-of-type(' + str(int(m[2]) + 1) + ')', b['selector'])
        if not b['key'].startswith('news.recovery.') and '#credit-' not in b['selector']:
            bindings.append(b)
    additions = [('news.recovery.november-2026', soup.select_one('#news-band-nov2026'), 'November 2026', 'تشرين الثاني 2026')]
    for name in ('apecl', 'nahariya'):
        rec = pack[name]
        row = soup.select_one('#' + rec['id'])
        credit = soup.select_one('#credit-' + rec['id'])
        if row is None or credit is None:
            raise ValueError('Missing recovery row or credit ' + name)
        for field, css in [('title', '.news-row-title a'), ('summary', '.news-row-summary'), ('date', 'time'), ('chip', '.chip')]:
            additions.append((f'news.recovery.{name}.{field}', row.select_one(css), rec['en'][field], rec['ar'][field]))
        additions += [(f'news.recovery.{name}.title', credit.select_one('.news-credit-title'), rec['en']['title'], rec['ar']['title']),
                      (f'news.recovery.{name}.source', credit.select_one('a'), rec['en']['source'], rec['ar']['source'])]
        label = credit.select_one('.news-credit-label')
        old_label = next(b for b in contract['bindings'] if b['source'] == 'Source:')
        bindings.append(binding(old_label['key'], label, 'Source:'))
    for key, node, english, arabic in additions:
        if node is None or node.get_text(' ', strip=True) != english:
            raise ValueError('Recovery text mismatch ' + key)
        bindings.append(binding(key, node, english))
        en[key], ar[key] = english, arabic
    verify(bindings, soup)
    if set(en) != set(ar):
        raise ValueError('Arabic archive key mismatch')
    contract.update(bindings=bindings, messages=en, masterSha256=hashlib.sha256(strip_static_fallback(raw)).hexdigest())
    result[root / 'locales/en/news-master-bindings.json'] = contract
    result[root / 'locales/en/news-master-copy.json'] = en
    result[root / 'locales/ar/news-master-copy.json'] = ar

    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    contract = load(root / 'locales/en/home-bindings.json')
    en = load(root / 'locales/en/home-copy.json')
    bindings = []
    for old in contract['bindings']:
        if old['key'].startswith('home.news-recovery.'):
            continue
        b = dict(old)
        if b['selector'].startswith('#latest-news'):
            if b['kind'] == 'attribute':
                candidates = [(n, None) for n in soup.select('#latest-news [' + b['attribute'] + ']') if n.get(b['attribute']) == b['source']]
            else:
                candidates = text_candidates(soup, b['source'])
            candidates.sort(key=lambda c: common_suffix(b['selector'], selector(c[0])), reverse=True)
            if not candidates or (len(candidates) > 1 and common_suffix(b['selector'], selector(candidates[0][0])) == common_suffix(b['selector'], selector(candidates[1][0]))):
                raise ValueError('Ambiguous survivor ' + b['key'])
            node, index = candidates[0]
            b['selector'] = selector(node)
            if index is not None:
                b['nodeIndex'] = index
        bindings.append(b)
    row = soup.select_one('a[href="' + HOME_HREF + '"]')
    keys = ['home.news-recovery.apecl.' + f for f in ('date', 'title', 'credit')]
    for key, cls, value in zip(keys, ('home-news-meta', 'home-news-title', 'home-news-credit'), pack['home']['en']):
        node = row.select_one('.' + cls)
        if node.get_text(' ', strip=True) != value:
            raise ValueError('Home text mismatch ' + key)
        bindings.append(binding(key, node, value))
        en[key] = value
    verify(bindings, soup)
    contract.update(bindings=bindings, messages=en, masterSha256=hashlib.sha256(raw).hexdigest())
    result[root / 'locales/en/home-bindings.json'] = contract
    result[root / 'locales/en/home-copy.json'] = en
    for lang in registry['homepageMirrors']['renderLocales']:
        catalog = load(root / f'locales/{lang}/home-copy.json')
        for key, value in zip(keys, pack['home'][lang]):
            catalog[key] = value
        if set(catalog) != set(en):
            raise ValueError('Home key mismatch ' + lang)
        result[root / f'locales/{lang}/home-copy.json'] = catalog
    return {p: json.dumps(v, ensure_ascii=False, indent=2) + '\n' for p, v in result.items()}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for path, text in outputs().items():
        if args.check:
            if path.read_text() != text:
                raise SystemExit('Recovery binding stale: ' + str(path))
        else:
            path.write_text(text)
    print('November recovery bindings ' + ('checked' if args.check else 'built'))
