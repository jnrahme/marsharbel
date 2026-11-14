"""Rebind the news-master credit lines for the three Annaya cards swapped to owner-granted
monastery photos (Batch 1, 2026-10-15): byblos-annaya-prayer-walk, cebu-relic-visit and
new-miracles-reported-2026-01. The LLEW / Paul Saad Wikimedia derivatives are no longer
used, so their per-item attribution bindings (via link, comma, CC BY-SA link, trailing
period) are pruned; the shared attribution KEYS stay in copy because other still-credited
cards keep binding them. The three description keys keep their names; only their sources
change. Rights basis: owner-reported reuse permission; attribution terms not independently
documented; prior credits removed because the previously credited images are no longer used.
Executor only: python3 scripts/i18n/refresh_annaya_news_batch1.py [--check]
"""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]

REBIND = {
    'news.latest-news.at-the-monastery-entrance-in-annaya-where-the-walk-ends-a-pi': {
        'en': 'The monastery church entrance in Annaya at dusk, where the walk ends.',
        'ar': 'مدخل كنيسة الدير في عنايا عند الغسق، حيث تنتهي المسيرة.'},
    'news.latest-news.the-vigil-lamp-at-saint-charbel-s-tomb-in-annaya-from-which': {
        'en': 'The tomb of Saint Charbel at Annaya, from which the pilgrim relic travels.',
        'ar': 'ضريح مار شربل في عنايا، الذي تنطلق منه الذخيرة المتجولة.'},
    'news.latest-news.the-monastery-of-saint-maron-in-annaya-which-keeps-the-regis': {
        'en': 'The Monastery of Saint Maron in Annaya from above by day, which keeps the register of reported miracles.',
        'ar': 'دير مار مارون في عنايا من الأعلى نهارًا، الذي يحفظ سجل الحالات المُبلَّغ عنها.'},
}
LI = '#main-content > section:nth-of-type(3) > div:nth-of-type(1) > details:nth-of-type(1) > ul:nth-of-type(1)'
PRUNE = {
    ('news.latest-news.via-wikimedia-commons', f'{LI} > li:nth-of-type(15) > a:nth-of-type(3)', None),
    ('news.latest-news.text-3', f'{LI} > li:nth-of-type(15)', 11),
    ('news.latest-news.cc-by-sa-4-0', f'{LI} > li:nth-of-type(15) > a:nth-of-type(4)', None),
    ('news.latest-news.text', f'{LI} > li:nth-of-type(15)', 13),
    ('news.latest-news.via-wikimedia-commons', f'{LI} > li:nth-of-type(21) > a:nth-of-type(2)', None),
    ('news.latest-news.text-3', f'{LI} > li:nth-of-type(21)', 9),
    ('news.latest-news.cc-by-sa-4-0', f'{LI} > li:nth-of-type(21) > a:nth-of-type(3)', None),
    ('news.latest-news.text', f'{LI} > li:nth-of-type(21)', 11),
    ('news.latest-news.via-wikimedia-commons', f'{LI} > li:nth-of-type(22) > a:nth-of-type(2)', None),
    ('news.latest-news.text-3', f'{LI} > li:nth-of-type(22)', 9),
    ('news.latest-news.cc-by-sa-4-0', f'{LI} > li:nth-of-type(22) > a:nth-of-type(3)', None),
    ('news.latest-news.text', f'{LI} > li:nth-of-type(22)', 11),
}

def value_of(n, old):
    if old['kind'] == 'attribute':
        return n.get(old['attribute'])
    return ' '.join(str(n.contents[old['nodeIndex']]).split())

def outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/news-master-bindings.json').read_text())
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    rebind_keys = set(REBIND)
    pruned, rebound = [], []
    bindings = []
    for old in contract['bindings']:
        sig = (old['key'], old['selector'], old.get('nodeIndex') if old['kind'] != 'attribute' and '> a:nth-of-type' not in old['selector'] and '> span' not in old['selector'] else None)
        if sig in PRUNE:
            nodes = soup.select(old['selector'])
            if nodes and old['kind'] == 'attribute':
                if value_of(nodes[0], old) == old['source']:
                    raise ValueError('Attribution element still present ' + old['key'])
            elif nodes:
                try:
                    if value_of(nodes[0], old) == old['source']:
                        raise ValueError('Attribution text still present ' + old['key'])
                except IndexError:
                    pass
            pruned.append(sig)
            continue
        nodes = soup.select(old['selector'])
        if len(nodes) != 1:
            raise ValueError('Old binding ambiguous ' + old['key'])
        n = nodes[0]
        value = value_of(n, old)
        if old['key'] in rebind_keys:
            if value != REBIND[old['key']]['en']:
                raise ValueError('Rebound credit text mismatch - run build_news_desk first: ' + old['key'])
            new = dict(old)
            new['source'] = value
            bindings.append(new)
            rebound.append(old['key'])
            continue
        if value != old['source']:
            raise ValueError('Unrelated news source changed ' + old['key'])
        bindings.append(dict(old))
    missing = PRUNE - set(pruned)
    contract_sigs = {(b['key'], b['selector'], b.get('nodeIndex') if b['kind'] != 'attribute' and '> a:nth-of-type' not in b['selector'] and '> span' not in b['selector'] else None) for b in contract['bindings']}
    for sig in missing:
        if sig in contract_sigs:
            raise ValueError('Prunable attribution binding not pruned ' + str(sig))
    if sorted(rebound) != sorted(rebind_keys):
        raise ValueError('Expected the three credit bindings, got ' + str(rebound))
    remaining = {b['key'] for b in bindings}
    for key in ('news.latest-news.via-wikimedia-commons', 'news.latest-news.cc-by-sa-4-0',
                'news.latest-news.text', 'news.latest-news.text-3'):
        if key not in remaining:
            raise ValueError('Shared attribution key fully unbound - prune it from copy instead: ' + key)
    copy = json.loads((root / 'locales/en/news-master-copy.json').read_text())
    for key, texts in REBIND.items():
        copy[key] = texts['en']
    local = json.loads((root / 'locales/ar/news-master-copy.json').read_text())
    for key, texts in REBIND.items():
        local[key] = texts['ar']
    if set(local) != set(copy):
        raise ValueError('Arabic news keys differ from English')
    contract.update(bindings=bindings, messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
    result = {root / 'locales/en/news-master-copy.json': copy,
              root / 'locales/ar/news-master-copy.json': local,
              root / 'locales/en/news-master-bindings.json': contract}
    return {p: json.dumps(j, ensure_ascii=False, indent=2) + '\n' for p, j in result.items()}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    for path, text in outputs().items():
        if a.check:
            if path.read_text() != text:
                raise SystemExit('Annaya batch-1 news bindings stale: ' + str(path))
        else:
            path.write_text(text)
    print('Annaya batch-1 news bindings checked' if a.check else 'Annaya batch-1 news bindings refreshed')
