"""Bind the October 17 Gemelli discharge row without disturbing other sources.

Adds the new discharge-row bindings to news-master (id-anchored selectors are
stable), shifts the news credits list positional selectors by +1 because the
new credit entry is prepended (editorial order preserved), updates the home
pope row copy in place (stable keys), and re-pins both masterSha256 values.
Every selector in both families is re-resolved against the built pages and
must return exactly one node whose rendered value equals the binding source;
any drift aborts the write. Locale values come from the reviewed packet
locales/gemelli-oct17-translations.json.

Usage: python3 scripts/i18n/refresh_gemelli_oct17.py [--check]
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

ROW_ID = 'pope-leo-gemelli-discharge-2026-10-17'
TITLE = 'Pope Leo discharged from Gemelli, back at the Vatican'
BODY = ("Pope Leo XIV was discharged from Gemelli Hospital on Saturday afternoon following lung surgery "
        "on Tuesday and returned to the papal apartments in Vatican City. Before leaving, he celebrated "
        "Mass in the room set aside for that purpose on the 10th floor. On Sunday at noon he will lead "
        "the Angelus from the window of the Apostolic Palace.")
DATE_EN = 'October 17, 2026'
CREDIT_EN = 'Vatican News: Pope Leo XIV returns to Vatican after being discharged from hospital (October 17, 2026)'
HOME_CREDIT_EN = ('Pope Leo XIV was discharged from Gemelli on Saturday afternoon and is back at the '
                  'Vatican; on Sunday at noon he leads the Angelus. Context photo: Gemelli Hospital, Rome. Photo: Blackcat, '
                  'Wikimedia Commons, CC BY-SA 3.0 IT; resized to WebP.')

NEWS_PREFIX = 'news.latest-news.'
K_TITLE = NEWS_PREFIX + 'pope-leo-to-be-discharged-from-gemelli-today'  # stable key, refreshed value
K_SUMMARY = NEWS_PREFIX + 'on-his-fifth-day-at-gemelli-pope-leo-xiv-s-doctors-said-morn'  # stable key, refreshed value
K_DATE = NEWS_PREFIX + 'october-17-2026'
K_CREDIT = NEWS_PREFIX + 'vatican-news-pope-leo-xiv-to-be-discharged-from-hospital-oct'  # stable key, refreshed value
K_CHIP = NEWS_PREFIX + 'update'

HOME_KEYS = {  # stable keys, refreshed values
    'home.latest-news.pope-leo-has-a-good-second-night-at-gemelli': TITLE,
    'home.latest-news.the-holy-see-says-pope-leo-had-a-good-second-hospital-night': HOME_CREDIT_EN,
    'home.latest-news.october-15-2026': DATE_EN,
}
CREDIT_SEL = '#main-content > section:nth-of-type(3) > div:nth-of-type(1) > details:nth-of-type(1) > ul:nth-of-type(1) > li:nth-of-type'
NEWS_COPY_KEYS = {'popeGemelliDischarge.title': K_TITLE, 'popeGemelliDischarge.summary': K_SUMMARY,
                  'popeGemelliDischarge.date': K_DATE, 'popeGemelliDischarge.admissionSource': K_CREDIT}
HOME_COPY_KEYS = {'popeGemelli.homeTitle': 'home.latest-news.pope-leo-has-a-good-second-night-at-gemelli',
                  'popeGemelli.homeCredit': 'home.latest-news.the-holy-see-says-pope-leo-had-a-good-second-hospital-night',
                  'popeGemelliDischarge.date': 'home.latest-news.october-15-2026'}


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
    packet = read_json(root / 'locales/gemelli-oct17-translations.json')
    english = read_json(root / 'locales/en/news-desk.json')
    if len(packet) != 11 or any(len(v) != 7 for v in packet.values()):
        raise ValueError('Expected the reviewed 11-locale, seven-value packet')
    result = {}

    # ---- news-master ----
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    if soup.select_one(f'#{ROW_ID}') is None:
        raise ValueError('discharge row missing; build pages first')
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
        raise ValueError(f'expected ~181 credit selectors to shift, got {shifted}')
    row = f'#{ROW_ID} > div:nth-of-type(1)'
    row_sels = {f'{row} > h3:nth-of-type(1) > a:nth-of-type(1)', f'{row} > p:nth-of-type(1)',
                f'{row} > p:nth-of-type(2) > span:nth-of-type(1)', f'{row} > p:nth-of-type(2) > time:nth-of-type(1)',
                f'{CREDIT_SEL}(1) > span:nth-of-type(1)', f'{CREDIT_SEL}(1) > a:nth-of-type(1)'}
    bindings = [b for b in bindings if b['selector'] not in row_sels]  # upsert: refresh row copy on re-run
    bindings += [
        {'key': K_TITLE, 'selector': f'{row} > h3:nth-of-type(1) > a:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_SUMMARY, 'selector': f'{row} > p:nth-of-type(1)', 'source': BODY, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CHIP, 'selector': f'{row} > p:nth-of-type(2) > span:nth-of-type(1)', 'source': 'Update', 'kind': 'text', 'nodeIndex': 0},
        {'key': K_DATE, 'selector': f'{row} > p:nth-of-type(2) > time:nth-of-type(1)', 'source': DATE_EN, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_TITLE, 'selector': f'{CREDIT_SEL}(1) > span:nth-of-type(1)', 'source': TITLE, 'kind': 'text', 'nodeIndex': 0},
        {'key': K_CREDIT, 'selector': f'{CREDIT_SEL}(1) > a:nth-of-type(1)', 'source': CREDIT_EN, 'kind': 'text', 'nodeIndex': 0},
    ]
    verify_all(bindings, soup, 'news-master')
    contract['bindings'] = bindings
    copy = read_json(root / 'locales/en/news-master-copy.json')
    for field, key in NEWS_COPY_KEYS.items():
        copy[key] = english[field]
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(raw).hexdigest()
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
    for field, key in HOME_COPY_KEYS.items():
        copy[key] = english[field]
    contract['messages'] = copy
    contract['masterSha256'] = hashlib.sha256(raw).hexdigest()
    result[hp] = contract
    result[root / 'locales/en/home-copy.json'] = copy
    for lang in registry['homepageMirrors']['renderLocales']:
        lp = root / f'locales/{lang}/home-copy.json'
        local = read_json(lp)
        for field, key in HOME_COPY_KEYS.items():
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
                raise SystemExit(f'Gemelli October 17 bindings stale: {path}')
        else:
            path.write_text(text)
    print('Gemelli October 17 bindings ' + ('checked' if args.check else 'refreshed'))
