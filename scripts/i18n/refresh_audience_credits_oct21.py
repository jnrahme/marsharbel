"""Bind the three October 21 General Audience credit entries on /news.

The entries sit at the top of the Sources & credits list (positions 1-3), above
the October 17 discharge credit, which moves to position 4 (refresh_gemelli_oct17.py
pins it there). Existing credit selectors shift by +3 once. Every selector is
re-resolved against the built page and must return exactly one node whose
rendered value equals the binding source. Locale labels come from
locales/audience-oct21-translations.json (agent-translated, native review pending).

Usage: python3 scripts/i18n/refresh_audience_credits_oct21.py [--check]
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

CREDIT_SEL = '#main-content > section:nth-of-type(3) > div:nth-of-type(1) > details:nth-of-type(1) > ul:nth-of-type(1) > li:nth-of-type'
K_TITLE = 'news.latest-news.pope-leo-to-be-discharged-from-gemelli-today'
FIELDS = ['popeAudience.vnSource', 'popeAudience.rteSource', 'popeAudience.ansaSource']
TITLE = 'Pope Leo discharged from Gemelli, back at the Vatican'


def read_json(p):
    return json.loads(p.read_text())


def key_for(field, english):
    return 'news.latest-news.' + slug(english[field])


def node_value(node, binding):
    return ' '.join(str(node.contents[binding['nodeIndex']]).split())


def outputs(root=ROOT):
    registry = read_json(root / 'locales/registry.json')
    packet = read_json(root / 'locales/audience-oct21-translations.json')
    english = read_json(root / 'locales/en/news-desk.json')
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    bp = root / 'locales/en/news-master-bindings.json'
    contract = read_json(bp)
    bindings = [dict(b) for b in contract['bindings']]
    keys = {f: key_for(f, english) for f in FIELDS}
    already = any(b['key'] == keys[FIELDS[0]] for b in bindings)
    if not already:
        shifted = 0
        for b in bindings:
            m = re.search(rf'^{re.escape(CREDIT_SEL)}\((\d+)\)( > .*)?$', b['selector'])
            if m:
                b['selector'] = f'{CREDIT_SEL}({int(m.group(1)) + 3})' + (m.group(2) or '')
                shifted += 1
        if shifted < 100:
            raise ValueError(f'expected ~180 credit selectors to shift, got {shifted}')
    mine = {f'{CREDIT_SEL}({i})' + s for i in (2, 3, 4) for s in (' > span:nth-of-type(1)', ' > span:nth-of-type(2)', ' > a:nth-of-type(1)')}
    row = '#pope-leo-gemelli-discharge-2026-10-17 > div:nth-of-type(1)'
    gem = [b for b in bindings if b['selector'].startswith(row) or b['selector'] in {f'{CREDIT_SEL}(5) > span:nth-of-type(1)', f'{CREDIT_SEL}(5) > span:nth-of-type(2)', f'{CREDIT_SEL}(5) > a:nth-of-type(1)'}]
    gem_ids = {id(b) for b in gem}
    doc_re = re.compile(rf'^{re.escape(CREDIT_SEL)}\(1\) > (span:nth-of-type\([12]\)|a:nth-of-type\(1\))$')
    doc = [b for b in bindings if doc_re.match(b['selector'])]  # doctors credit (refresh_doctors_credit_oct22.py) stays last
    doc_ids = {id(b) for b in doc}
    bindings = [b for b in bindings if b['selector'] not in mine and id(b) not in gem_ids and id(b) not in doc_ids] + gem  # Gemelli row bindings keep their place before mine
    for i, field in enumerate(FIELDS, start=2):
        bindings.append({'key': K_TITLE, 'selector': f'{CREDIT_SEL}({i}) > span:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0})
        bindings.append({'key': 'news.latest-news.source', 'selector': f'{CREDIT_SEL}({i}) > span:nth-of-type(2)', 'source': 'Source:', 'kind': 'text', 'nodeIndex': 0})
        bindings.append({'key': keys[field], 'selector': f'{CREDIT_SEL}({i}) > a:nth-of-type(1)', 'source': english[field], 'kind': 'text', 'nodeIndex': 0})
    bindings += doc
    for b in bindings:
        nodes = soup.select(b['selector'])
        if len(nodes) != 1:
            raise ValueError(f'selector not unique {b["selector"]}')
        if b['kind'] == 'text' and node_value(nodes[0], b) != b['source']:
            raise ValueError(f'source mismatch at {b["selector"]} ({b["key"]})')
    contract['bindings'] = bindings
    copy = read_json(root / 'locales/en/news-master-copy.json')
    for f in FIELDS:
        copy[keys[f]] = english[f]
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(raw).hexdigest()
    result = {bp: contract, root / 'locales/en/news-master-copy.json': copy}
    for lang in registry['pageMirrors']['news-master']['renderLocales']:
        lp = root / f'locales/{lang}/news-master-copy.json'
        local = read_json(lp)
        for f in FIELDS:
            local[keys[f]] = packet[lang][f]
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
                raise SystemExit(f'Audience credit bindings stale: {path}')
        else:
            path.write_text(text)
    print('Audience credit bindings ' + ('checked' if args.check else 'refreshed'))
