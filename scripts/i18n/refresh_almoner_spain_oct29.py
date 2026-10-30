"""Bind the October 29 almoner-Kyiv and Spain-telegram rows.

Adds the two new row bindings to news-master (id-anchored selectors are stable),
prepends the almoner credit entry at position 1 and inserts the Spain credit
entry at position 2 (every existing credit positional selector shifts +2,
editorial order preserved), and re-pins
the news-master masterSha256. Every selector is re-resolved against the built
page and must return exactly one node whose rendered value equals the binding
source; any drift aborts the write. The locale values come from the reviewed
packet locales/ukraine-acn-oct28-translations.json (agent-translated, native
review pending - same status as the ukraine-acn-oct28, marian-oct28, massabki-oct25,
assisi-oct24, gemelli-oct17 and audience-oct21 packets).

Usage: python3 scripts/i18n/refresh_almoner_spain_oct29.py [--check]
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

ROWS = [
    {'prefix': 'almonerKyiv', 'id': 'almoner-kyiv-visit-2026-10-29',
     'source_field': 'vnSource', 'credit_pos': 1},
    {'prefix': 'spainTrain', 'id': 'spain-urda-train-telegram-2026-10-29',
     'source_field': 'vnSource', 'credit_pos': 2},
]
NEWS_PREFIX = 'news.latest-news.'
K_CHIP = NEWS_PREFIX + slug('Update')
K_SOURCE_LABEL = NEWS_PREFIX + slug('Source:')

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
    packet = read_json(root / 'locales/almoner-spain-oct29-translations.json')
    english = read_json(root / 'locales/en/news-desk.json')
    if set(packet) != {'ar'} or any(len(v) != 8 for v in packet.values()):
        raise ValueError('Expected the reviewed Arabic-only, eight-value packet')
    result = {}

    # ---- news-master ----
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    for r in ROWS:
        if soup.select_one(f'#{r["id"]}') is None:
            raise ValueError(f'{r["id"]} row missing; build pages first')
    bp = root / 'locales/en/news-master-bindings.json'
    contract = read_json(bp)
    bindings = [dict(b) for b in contract['bindings']]
    already = any(ROWS[0]['id'] in b['selector'] for b in bindings)
    shifted = 0
    for b in [] if already else bindings:
        m = re.search(rf'^{re.escape(CREDIT_SEL)}\((\d+)\)( > .*)?$', b['selector'])
        if m:
            n = int(m.group(1))
            b['selector'] = f'{CREDIT_SEL}({n + 2})' + (m.group(2) or '')
            shifted += 1
    if not already and shifted < 100:
        raise ValueError(f'expected ~190 credit selectors to shift, got {shifted}')
    copy = read_json(root / 'locales/en/news-master-copy.json')
    row_keys = {}
    for r in ROWS:
        row = f'#{r["id"]} > div:nth-of-type(1)'
        cp = r['credit_pos']
        row_sels = {f'{row} > h3:nth-of-type(1) > a:nth-of-type(1)', f'{row} > p:nth-of-type(1)',
                    f'{row} > p:nth-of-type(2) > span:nth-of-type(1)', f'{row} > p:nth-of-type(2) > time:nth-of-type(1)',
                    f'{CREDIT_SEL}({cp}) > span:nth-of-type(1)', f'{CREDIT_SEL}({cp}) > span:nth-of-type(2)',
                    f'{CREDIT_SEL}({cp}) > a:nth-of-type(1)'}
        bindings = [b for b in bindings if b['selector'] not in row_sels]  # upsert on re-run
        K_TITLE = NEWS_PREFIX + slug(english[f'{r["prefix"]}.title'])
        K_SUMMARY = NEWS_PREFIX + slug(english[f'{r["prefix"]}.summary'])
        K_DATE = NEWS_PREFIX + slug(english[f'{r["prefix"]}.date'])
        K_CREDIT = NEWS_PREFIX + slug(english[f'{r["prefix"]}.{r["source_field"]}'])
        bindings += [
            {'key': K_TITLE, 'selector': f'{row} > h3:nth-of-type(1) > a:nth-of-type(1)', 'source': english[f'{r["prefix"]}.title'], 'kind': 'text', 'nodeIndex': 0},
            {'key': K_SUMMARY, 'selector': f'{row} > p:nth-of-type(1)', 'source': english[f'{r["prefix"]}.summary'], 'kind': 'text', 'nodeIndex': 0},
            {'key': K_CHIP, 'selector': f'{row} > p:nth-of-type(2) > span:nth-of-type(1)', 'source': english[f'{r["prefix"]}.chip'], 'kind': 'text', 'nodeIndex': 0},
            {'key': K_DATE, 'selector': f'{row} > p:nth-of-type(2) > time:nth-of-type(1)', 'source': english[f'{r["prefix"]}.date'], 'kind': 'text', 'nodeIndex': 0},
            {'key': K_TITLE, 'selector': f'{CREDIT_SEL}({cp}) > span:nth-of-type(1)', 'source': english[f'{r["prefix"]}.title'], 'kind': 'text', 'nodeIndex': 0},
            {'key': K_SOURCE_LABEL, 'selector': f'{CREDIT_SEL}({cp}) > span:nth-of-type(2)', 'source': 'Source:', 'kind': 'text', 'nodeIndex': 0},
            {'key': K_CREDIT, 'selector': f'{CREDIT_SEL}({cp}) > a:nth-of-type(1)', 'source': english[f'{r["prefix"]}.{r["source_field"]}'], 'kind': 'text', 'nodeIndex': 0},
        ]
        row_keys[r['prefix']] = ((f'{r["prefix"]}.title', K_TITLE), (f'{r["prefix"]}.summary', K_SUMMARY),
                                 (f'{r["prefix"]}.date', K_DATE), (f'{r["prefix"]}.{r["source_field"]}', K_CREDIT))
        for field, key in row_keys[r['prefix']]:
            copy[key] = english[field]
    for lang in registry['pageMirrors']['news-master']['renderLocales']:
        lp = root / f'locales/{lang}/news-master-copy.json'
        local = read_json(lp)
        for r in ROWS:
            for field, key in row_keys[r['prefix']]:
                local[key] = packet[lang][field]
        result[lp] = local
    verify_all(bindings, soup, 'news-master')
    contract['bindings'] = bindings
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(strip_static_fallback(raw)).hexdigest()
    result[bp] = contract
    result[root / 'locales/en/news-master-copy.json'] = copy
    for lang in registry['pageMirrors']['news-master']['renderLocales']:
        lp = root / f'locales/{lang}/news-master-copy.json'
        local = result[lp]
        if set(local) != set(copy):
            raise ValueError(f'news-master: {lang} key-set mismatch')

    return {p: json.dumps(v, ensure_ascii=False, indent=2) + '\n' for p, v in result.items()}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for path, text in outputs().items():
        if args.check:
            if path.read_text() != text:
                raise SystemExit(f'Almoner/Spain bindings stale: {path}')
        else:
            path.write_text(text)
    print('Almoner/Spain bindings ' + ('checked' if args.check else 'refreshed'))
