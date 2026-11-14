"""Rotate the home popeRosary slot to the Massabki centenary row (Oct 25).

Archive row and news-master bindings were handled by refresh_massabki_oct25.py
(news desk packet). This script refreshes ONLY the homepage slot copy in place
(stable keys, refreshed values - same precedent as refresh_assisi_oct24.py),
for title, credit/dek, date and the new context-photo alt, then re-pins
home-bindings against the built pages. Locale values come from the reviewed
packet locales/massabki-oct25-home-translations.json (agent-translated,
native review pending - same status as the assisi-oct24 packet).

Usage: python3 scripts/i18n/refresh_massabki_oct25_home.py [--check]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.keyed_master import strip_static_fallback

FIELDS = ('popeRosary.homeTitle', 'popeRosary.homeCredit', 'massabkiCentenary.date', 'popeRosary.homeAlt')


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
    packet = read_json(root / 'locales/massabki-oct25-home-translations.json')
    english = read_json(root / 'locales/en/news-desk.json')
    copy_en = read_json(root / 'locales/en/home-copy.json')
    if len(packet) != 11 or any(len(v) != 4 for v in packet.values()):
        raise ValueError('Expected the reviewed 11-locale, four-value home packet')
    # stable keys, refreshed values: locate the current keys holding the slot's values
    value_to_key = {}
    for field in FIELDS:
        cur = english[field]
        # the EN home-copy currently holds the PRE-rotation value; find its key
        matches = [k for k, v in copy_en.items() if k.startswith(('home.latest-news.', 'home.accessibility.')) and v in (PRE[field], english[field])]
        if len(matches) != 1:
            raise ValueError(f'home-copy: cannot uniquely locate key for {field}: {matches}')
        value_to_key[field] = matches[0]
    HOME_KEYS = {value_to_key[f]: english[f] for f in FIELDS}

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
    for field, key in value_to_key.items():
        copy[key] = english[field]
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(strip_static_fallback(raw)).hexdigest()
    result = {hp: contract, root / 'locales/en/home-copy.json': copy}
    for lang in registry['homepageMirrors']['renderLocales']:
        lp = root / f'locales/{lang}/home-copy.json'
        local = read_json(lp)
        for field, key in value_to_key.items():
            local[key] = packet[lang][field]
        if set(local) != set(copy):
            raise ValueError(f'home: {lang} key-set mismatch')
        result[lp] = local
    return {p: json.dumps(v, ensure_ascii=False, indent=2) + '\n' for p, v in result.items()}


def _pre_rotation():
    import subprocess
    raw = subprocess.check_output(['git', 'show', 'HEAD:locales/en/news-desk.json'], cwd=ROOT).decode()
    old = json.loads(raw)
    pre = {f: old[f] for f in ('popeRosary.homeTitle', 'popeRosary.homeCredit', 'popeRosary.homeAlt')}
    pre['massabkiCentenary.date'] = 'October 13, 2026'
    return pre

PRE = _pre_rotation()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for path, text in outputs().items():
        if args.check:
            if path.read_text() != text:
                raise SystemExit(f'Massabki home bindings stale: {path}')
        else:
            path.write_text(text)
    print('Massabki home bindings ' + ('checked' if args.check else 'refreshed'))
