"""Bind the October 23 Assisi-cancellation row without disturbing other sources.

Adds the new Assisi-row bindings to news-master (id-anchored selectors are
stable), prepends the new credit entry to the news credits list (all existing
credit positional selectors shift by +1 once, editorial order preserved),
updates the home pope row copy in place (stable keys), and re-pins both
masterSha256 values. Every selector in both families is re-resolved against
the built pages and must return exactly one node whose rendered value equals
the binding source; any drift aborts the write. Locale values come from the
reviewed packet locales/assisi-oct24-translations.json (agent-translated,
native review waived by the owner).

Usage: python3 scripts/i18n/refresh_assisi_oct24.py [--check]
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
from i18n.make_bindings import slug
from i18n.keyed_master import strip_static_fallback

ROW_ID = 'pope-leo-assisi-cancel-2026-10-23'
NEWS_PREFIX = 'news.latest-news.'
K_CHIP = NEWS_PREFIX + slug('Update')
K_SOURCE_LABEL = NEWS_PREFIX + slug('Source:')

HOME_KEYS_MAP = {  # stable keys, refreshed values
    'popeGemelli.homeTitle': 'home.latest-news.pope-leo-has-a-good-second-night-at-gemelli',
    'popeGemelli.homeCredit': 'home.latest-news.the-holy-see-says-pope-leo-had-a-good-second-hospital-night',
    'popeAssisi.date': 'home.latest-news.october-15-2026',
}

CREDIT_SEL = '#main-content > section:nth-of-type(3) > div:nth-of-type(1) > details:nth-of-type(1) > ul:nth-of-type(1) > li:nth-of-type'


def read_json(p):
    return json.loads(p.read_text())


def node_value(node, binding):
    if binding['kind'] == 'attribute':
        return node.get(binding['attribute'])
    return ' '.join(str(node.contents[binding['nodeIndex']]).split())


def verify_all(bindings, soup, family):
    for b in bindings:
        nodes = soup.select(b['selector'])
        if len(nodes) != 1:
            raise ValueError(f'{family}: selector not unique {b["selector"]}')
        if node_value(nodes[0], b) != b['source']:
            raise ValueError(f'{family}: source mismatch at {b["selector"]} ({b["key"]})')


def outputs(root=ROOT):
    registry = read_json(root / 'locales/registry.json')
    packet = read_json(root / 'locales/assisi-oct24-translations.json')
    english = read_json(root / 'locales/en/news-desk.json')
    if len(packet) != 11 or any(len(v) != 7 for v in packet.values()):
        raise ValueError('Expected the reviewed 11-locale, seven-value packet')
    TITLE = english['popeAssisi.title']
    BODY = english['popeAssisi.summary']
    DATE_EN = english['popeAssisi.date']
    CREDIT_EN = english['popeAssisi.vnSource']
    K_TITLE = NEWS_PREFIX + slug(TITLE)
    K_SUMMARY = NEWS_PREFIX + slug(BODY)
    K_DATE = NEWS_PREFIX + slug(DATE_EN)
    K_CREDIT = NEWS_PREFIX + slug(CREDIT_EN)
    NEWS_COPY_KEYS = {'popeAssisi.title': K_TITLE, 'popeAssisi.summary': K_SUMMARY,
                      'popeAssisi.date': K_DATE, 'popeAssisi.vnSource': K_CREDIT}
    HOME_KEYS = {HOME_KEYS_MAP['popeGemelli.homeTitle']: english['popeGemelli.homeTitle'],
                 HOME_KEYS_MAP['popeGemelli.homeCredit']: english['popeGemelli.homeCredit'],
                 HOME_KEYS_MAP['popeAssisi.date']: english['popeAssisi.date']}
    result = {}

    # ---- news-master ----
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    if soup.select_one(f'#{ROW_ID}') is None:
        raise ValueError('Assisi row missing; build pages first')
    bp = root / 'locales/en/news-master-bindings.json'
    contract = read_json(bp)
    bindings = [dict(b) for b in contract['bindings']]
    already = any(ROW_ID in b['selector'] for b in bindings)
    shifted = 0
    for b in [] if already else bindings:
        m = re.search(rf'^{re.escape(CREDIT_SEL)}\((\d+)\)( > .*)?$', b['selector'])
        if m:
            b['selector'] = f'{CREDIT_SEL}({int(m.group(1)) + 1})' + (m.group(2) or '')
            shifted += 1
    if not already and shifted < 100:
        raise ValueError(f'expected ~190 credit selectors to shift, got {shifted}')
    row = f'#{ROW_ID} > div:nth-of-type(1)'
    row_sels = {f'{row} > h3:nth-of-type(1) > a:nth-of-type(1)', f'{row} > p:nth-of-type(1)',
                f'{row} > p:nth-of-type(2) > span:nth-of-type(1)', f'{row} > p:nth-of-type(2) > time:nth-of-type(1)',
                f'{CREDIT_SEL}(1) > span:nth-of-type(1)', f'{CREDIT_SEL}(1) > span:nth-of-type(2)', f'{CREDIT_SEL}(1) > a:nth-of-type(1)'}
    bindings = [b for b in bindings if b['selector'] not in row_sels]  # upsert: refresh row copy on re-run
    bindings += [
        {'key': K_TITLE, 'selector': f'{row} > h3:nth-of-type(1) > a:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_SUMMARY, 'selector': f'{row} > p:nth-of-type(1)', 'source': BODY, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CHIP, 'selector': f'{row} > p:nth-of-type(2) > span:nth-of-type(1)', 'source': english['popeAssisi.chip'], 'kind': 'text', 'nodeIndex': 0},
        {'key': K_DATE, 'selector': f'{row} > p:nth-of-type(2) > time:nth-of-type(1)', 'source': DATE_EN, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_TITLE, 'selector': f'{CREDIT_SEL}(1) > span:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_SOURCE_LABEL, 'selector': f'{CREDIT_SEL}(1) > span:nth-of-type(2)', 'source': 'Source:', 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CREDIT, 'selector': f'{CREDIT_SEL}(1) > a:nth-of-type(1)', 'source': CREDIT_EN, 'kind': 'text', 'nodeIndex': 0},
    ]
    verify_all(bindings, soup, 'news-master')
    contract['bindings'] = bindings
    copy = read_json(root / 'locales/en/news-master-copy.json')
    for field, key in NEWS_COPY_KEYS.items():
        copy[key] = english[field]
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(strip_static_fallback(raw)).hexdigest()
    result[bp] = contract
    result[root / 'locales/en/news-master-copy.json'] = copy
    for lang in registry['pageMirrors']['news-master']['renderLocales']:
        lp = root / f'locales/{lang}/news-master-copy.json'
        local = read_json(lp)
        for field, key in NEWS_COPY_KEYS.items():
            local[key] = packet[lang][field]
        if set(local) != set(copy):
            raise ValueError(f'news-master: {lang} key-set mismatch')
        result[lp] = local

    # ---- home ----
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    hp = root / 'locales/en/home-bindings.json'
    contract = read_json(hp)
    bindings = [dict(b) for b in contract['bindings']]
    seen = set()
    for b in bindings:
        if b['key'] in HOME_KEYS:
            b['source'] = HOME_KEYS[b['key']]
            seen.add(b['key'])
    if seen != set(HOME_KEYS):
        raise ValueError(f'home: keys not found {set(HOME_KEYS) - seen}')
    verify_all(bindings, soup, 'home')
    contract['bindings'] = bindings
    copy = read_json(root / 'locales/en/home-copy.json')
    for field, key in HOME_KEYS_MAP.items():
        copy[key] = english[field]
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(strip_static_fallback(raw)).hexdigest()
    result[hp] = contract
    result[root / 'locales/en/home-copy.json'] = copy
    for lang in registry['homepageMirrors']['renderLocales']:
        lp = root / f'locales/{lang}/home-copy.json'
        local = read_json(lp)
        for field, key in HOME_KEYS_MAP.items():
            local[key] = packet[lang][field]
        if set(local) != set(copy):
            raise ValueError(f'home: {lang} key-set mismatch')
        result[lp] = local

    return {p: json.dumps(v, ensure_ascii=False, indent=2) + '\n' for p, v in result.items()}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for path, text in outputs().items():
        if args.check:
            if path.read_text() != text:
                raise SystemExit(f'Assisi bindings stale: {path}')
        else:
            path.write_text(text)
    print('Assisi bindings ' + ('checked' if args.check else 'refreshed'))
