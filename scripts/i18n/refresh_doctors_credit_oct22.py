"""Bind the October 21 doctors' statement credit on /news (credits list position 1).

Sits above the three General Audience credits (positions 2-4) and the October 17
discharge credit (position 5). Existing credit selectors shift by +1 once. Every
selector is re-resolved against the built page and must return exactly one node
whose rendered value equals the binding source. Locale labels come from
locales/audience-oct21-translations.json (agent-translated, native review pending).

Usage: python3 scripts/i18n/refresh_doctors_credit_oct22.py [--check]
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
FIELD = 'popeAudience.doctorsSource'
TITLE = 'Pope Leo discharged from Gemelli, back at the Vatican'


def read_json(p):
    return json.loads(p.read_text())


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
    key = 'news.latest-news.' + slug(english[FIELD])
    if not any(b['key'] == key for b in bindings):
        shifted = 0
        for b in bindings:
            m = re.search(rf'^{re.escape(CREDIT_SEL)}\((\d+)\)( > .*)?$', b['selector'])
            if m:
                b['selector'] = f'{CREDIT_SEL}({int(m.group(1)) + 1})' + (m.group(2) or '')
                shifted += 1
        if shifted < 100:
            raise ValueError(f'expected ~190 credit selectors to shift, got {shifted}')
    mine = {f'{CREDIT_SEL}(1)' + s for s in (' > span:nth-of-type(1)', ' > span:nth-of-type(2)', ' > a:nth-of-type(1)')}
    bindings = [b for b in bindings if b['selector'] not in mine]
    bindings += [
        {'key': K_TITLE, 'selector': f'{CREDIT_SEL}(1) > span:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0},
        {'key': 'news.latest-news.source', 'selector': f'{CREDIT_SEL}(1) > span:nth-of-type(2)', 'source': 'Source:', 'kind': 'text', 'nodeIndex': 0},
        {'key': key, 'selector': f'{CREDIT_SEL}(1) > a:nth-of-type(1)', 'source': english[FIELD], 'kind': 'text', 'nodeIndex': 0},
    ]
    for b in bindings:  # structure for all; rendered text only for the entries this script owns (refresh_gemelli_oct17.py re-verifies every source)
        nodes = soup.select(b['selector'])
        if len(nodes) != 1:
            raise ValueError(f'selector not unique {b["selector"]}')
        if b['selector'] in mine and b['kind'] == 'text' and node_value(nodes[0], b) != b['source']:
            raise ValueError(f'source mismatch at {b["selector"]} ({b["key"]})')
    contract['bindings'] = bindings
    copy = read_json(root / 'locales/en/news-master-copy.json')
    copy[key] = english[FIELD]
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(raw).hexdigest()
    result = {bp: contract, root / 'locales/en/news-master-copy.json': copy}
    for lang in registry['pageMirrors']['news-master']['renderLocales']:
        lp = root / f'locales/{lang}/news-master-copy.json'
        local = read_json(lp)
        local[key] = packet[lang][FIELD]
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
                raise SystemExit(f'Doctors credit bindings stale: {path}')
        else:
            path.write_text(text)
    print('Doctors credit bindings ' + ('checked' if args.check else 'refreshed'))
