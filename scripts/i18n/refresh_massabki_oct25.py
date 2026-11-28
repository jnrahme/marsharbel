"""Bind the October 25 Massabki-centenary row without disturbing other sources.

Adds the new Massabki-row bindings to news-master (id-anchored selectors are
stable), prepends the new credit entry to the news credits list (all existing
credit positional selectors shift by +1 once, editorial order preserved), and
re-pins the news-master masterSha256. Every selector is re-resolved against the
built page and must return exactly one node whose rendered value equals the
binding source; any drift aborts the write. The locale value comes from the
reviewed packet locales/massabki-oct25-translations.json (agent-translated,
native review pending - same status as the assisi-oct24, gemelli-oct17 and
audience-oct21 packets).

Usage: python3 scripts/i18n/refresh_massabki_oct25.py [--check]
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

ROW_ID = 'massabki-centenary-aqoura-2026-10-25'
NEWS_PREFIX = 'news.latest-news.'
K_CHIP = NEWS_PREFIX + slug('Update')
K_SOURCES_LABEL = NEWS_PREFIX + slug('Sources:')

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
    packet = read_json(root / 'locales/massabki-oct25-translations.json')
    english = read_json(root / 'locales/en/news-desk.json')
    if set(packet) != {'ar'} or any(len(v) != 7 for v in packet.values()):
        raise ValueError('Expected the reviewed Arabic-only, seven-value packet')
    TITLE = english['massabkiCentenary.title']
    BODY = english['massabkiCentenary.summary']
    DATE_EN = english['massabkiCentenary.date']
    CREDIT_ELNASHRA = english['massabkiCentenary.elnashraSource']
    CREDIT_NOURSAT = english['massabkiCentenary.noursatSource']
    CREDIT_JBEIL = english['massabkiCentenary.jbeilSource']
    CREDIT_EPARCHY = english['massabkiCentenary.eparchySource']
    K_TITLE = NEWS_PREFIX + slug(TITLE)
    K_SUMMARY = NEWS_PREFIX + slug(BODY)
    K_DATE = NEWS_PREFIX + slug(DATE_EN)
    K_CREDIT_ELNASHRA = NEWS_PREFIX + slug(CREDIT_ELNASHRA)
    K_CREDIT_NOURSAT = NEWS_PREFIX + slug(CREDIT_NOURSAT)
    K_CREDIT_JBEIL = NEWS_PREFIX + slug(CREDIT_JBEIL)
    K_CREDIT_EPARCHY = NEWS_PREFIX + slug(CREDIT_EPARCHY)
    NEWS_COPY_KEYS = {'massabkiCentenary.title': K_TITLE, 'massabkiCentenary.summary': K_SUMMARY,
                      'massabkiCentenary.date': K_DATE, 'massabkiCentenary.elnashraSource': K_CREDIT_ELNASHRA,
                      'massabkiCentenary.noursatSource': K_CREDIT_NOURSAT, 'massabkiCentenary.jbeilSource': K_CREDIT_JBEIL, 'massabkiCentenary.eparchySource': K_CREDIT_EPARCHY}
    result = {}

    # ---- news-master ----
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    if soup.select_one(f'#{ROW_ID}') is None:
        raise ValueError('Massabki row missing; build pages first')
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
                f'{CREDIT_SEL}(1) > span:nth-of-type(1)', f'{CREDIT_SEL}(1) > span:nth-of-type(2)',
                f'{CREDIT_SEL}(1) > a:nth-of-type(1)', f'{CREDIT_SEL}(1) > a:nth-of-type(2)',
                f'{CREDIT_SEL}(1) > a:nth-of-type(3)', f'{CREDIT_SEL}(1) > a:nth-of-type(4)'}
    bindings = [b for b in bindings if b['selector'] not in row_sels]  # upsert: refresh row copy on re-run
    bindings += [
        {'key': K_TITLE, 'selector': f'{row} > h3:nth-of-type(1) > a:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_SUMMARY, 'selector': f'{row} > p:nth-of-type(1)', 'source': BODY, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CHIP, 'selector': f'{row} > p:nth-of-type(2) > span:nth-of-type(1)', 'source': english['massabkiCentenary.chip'], 'kind': 'text', 'nodeIndex': 0},
        {'key': K_DATE, 'selector': f'{row} > p:nth-of-type(2) > time:nth-of-type(1)', 'source': DATE_EN, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_TITLE, 'selector': f'{CREDIT_SEL}(1) > span:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_SOURCES_LABEL, 'selector': f'{CREDIT_SEL}(1) > span:nth-of-type(2)', 'source': 'Sources:', 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CREDIT_ELNASHRA, 'selector': f'{CREDIT_SEL}(1) > a:nth-of-type(1)', 'source': CREDIT_ELNASHRA, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CREDIT_NOURSAT, 'selector': f'{CREDIT_SEL}(1) > a:nth-of-type(2)', 'source': CREDIT_NOURSAT, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CREDIT_JBEIL, 'selector': f'{CREDIT_SEL}(1) > a:nth-of-type(3)', 'source': CREDIT_JBEIL, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CREDIT_EPARCHY, 'selector': f'{CREDIT_SEL}(1) > a:nth-of-type(4)', 'source': CREDIT_EPARCHY, 'kind': 'text', 'nodeIndex': 0},
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

    return {p: json.dumps(v, ensure_ascii=False, indent=2) + '\n' for p, v in result.items()}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for path, text in outputs().items():
        if args.check:
            if path.read_text() != text:
                raise SystemExit(f'Massabki bindings stale: {path}')
        else:
            path.write_text(text)
    print('Massabki bindings ' + ('checked' if args.check else 'refreshed'))
