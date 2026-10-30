"""Add the October 30 text-only almoner supporting-row bindings on the homepage.

The new row (home-news-row--text, no photo, rights-safe) links
./news#almoner-zaporizhzhia-poltava-2026-10-30 and is inserted as the first
supporting row inside .home-news-rows; every existing row anchor's
a:nth-of-type index therefore shifts +1. This script re-resolves EVERY
#latest-news binding against the built index.html by exact source match
(tie-break: longest common selector-segment suffix, which keeps the
details/ul archive entries distinct from the row copies), adds the three new
row bindings (date/title/credit; values from locales/en/news-desk.json
almonerFollowup.*), re-pins masterSha256/sourceRevision, and inserts the
locale values from the reviewed packet
locales/almoner-oct30-home-translations.json (agent-translated, native review
pending - same status as the film-home and earlier home packets).
Executor only: python3 scripts/i18n/refresh_almoner_oct30_home.py [--check]
Never blanket-regenerates reviewed bindings or changes other source values.
"""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[2]
FIELDS = (('almonerFollowup.date', 'home-news-meta'),
          ('almonerFollowup.homeTitle', 'home-news-title'),
          ('almonerFollowup.homeCredit', 'home-news-credit'))
ROW_HREF = './news#almoner-zaporizhzhia-poltava-2026-10-30'
LOCALES = ('ar', 'fr', 'es', 'pt', 'it', 'de', 'pl', 'ru', 'hi', 'th')


def slug(text, n=60):
    s = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return s[:n].strip('-') or 'text'


def selector(node):
    parts = []
    while node.name != '[document]':
        if node.get('id'):
            parts.append('#' + node['id'])
            break
        siblings = node.parent.find_all(node.name, recursive=False)
        parts.append(node.name + ':nth-of-type(' + str(next(i for i, s in enumerate(siblings) if s is node) + 1) + ')')
        node = node.parent
    return ' > '.join(reversed(parts))


def norm(t):
    return ' '.join(str(t).split())


def text_candidates(soup, source):
    out = []
    for node in soup.select('#latest-news *'):
        for i, t in enumerate(node.contents):
            if isinstance(t, NavigableString) and norm(t) == source:
                out.append((node, i))
    return out


def common_suffix(a, b):
    pa, pb = a.split(' > '), b.split(' > ')
    n = 0
    while n < min(len(pa), len(pb)) and pa[-1 - n] == pb[-1 - n]:
        n += 1
    return n


def outputs(root=ROOT):
    hp = root / 'locales/en/home-bindings.json'
    contract = json.loads(hp.read_text())
    copy_en = json.loads((root / 'locales/en/home-copy.json').read_text())
    news = json.loads((root / 'locales/en/news-desk.json').read_text())
    pack = json.loads((root / 'locales/almoner-oct30-home-translations.json').read_text())
    if pack['status'] != 'agent-translated-native-not-certified' or tuple(pack['keys']) != ('date', 'title', 'credit') or set(pack['locales']) != set(LOCALES):
        raise ValueError('Unexpected almoner home translation packet')
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')

    new_values = {field: news[field] for field, _ in FIELDS}
    new_keys = {field: 'home.latest-news.' + slug(value) for field, value in new_values.items()}
    applied = all(k in copy_en for k in new_keys.values())
    if not applied and (set(new_keys.values()) & set(copy_en)):
        raise ValueError('Partial almoner home key application')
    rows = soup.select(f'a[href="{ROW_HREF}"]')
    if len(rows) != 1:
        raise ValueError(f'Expected exactly one almoner home row, found {len(rows)}')

    bindings = []
    moved = 0
    for old in contract['bindings']:
        b = dict(old)
        if b['selector'].startswith('#latest-news'):
            if b['kind'] == 'attribute':
                cands = [(n, None) for n in soup.select('#latest-news [%s]' % b['attribute']) if n.get(b['attribute']) == b['source']]
            else:
                cands = text_candidates(soup, b['source'])
            if len(cands) == 0:
                raise ValueError('Lost binding source ' + b['key'])
            if len(cands) > 1:
                scored = sorted(cands, key=lambda c: common_suffix(b['selector'], selector(c[0])), reverse=True)
                if common_suffix(b['selector'], selector(scored[0][0])) == common_suffix(b['selector'], selector(scored[1][0])):
                    raise ValueError('Ambiguous binding remap ' + b['key'])
                cands = scored[:1]
            node, index = cands[0]
            b['selector'] = selector(node)
            if index is not None:
                b['nodeIndex'] = index
            if b != old:
                moved += 1
        else:
            nodes = soup.select(b['selector'])
            if len(nodes) != 1:
                raise ValueError('Unrelated binding selector changed ' + b['key'])
            n = nodes[0]
            value = n.get(b['attribute']) if b['kind'] == 'attribute' else norm(n.contents[b['nodeIndex']])
            if value != b['source']:
                raise ValueError('Unrelated source drift ' + b['key'])
        bindings.append(b)

    existing = {b['selector'] for b in bindings}
    for field, cls in FIELDS:
        span = rows[0].select_one('span.' + cls)
        if span is None or norm(span.contents[0]) != new_values[field]:
            raise ValueError('Almoner row value mismatch ' + field)
        sel = selector(span)
        if applied:
            match = [b for b in bindings if b['key'] == new_keys[field]]
            if len(match) != 1 or match[0]['selector'] != sel or match[0]['source'] != new_values[field]:
                raise ValueError('Applied almoner binding drift ' + field)
        else:
            if sel in existing:
                raise ValueError('Selector collision ' + sel)
            bindings.append({'key': new_keys[field], 'selector': sel, 'source': new_values[field], 'kind': 'text', 'nodeIndex': 0})
            existing.add(sel)
    if not applied:
        for field, key in new_keys.items():
            copy_en[key] = new_values[field]

    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    # Provenance rule: sourceRevision records the revision the contract was
    # pinned against. A stored revision that is an ancestor of HEAD remains
    # valid provenance, so regeneration keeps it - this makes --check
    # reproducible on committed artifacts without post-commit mutation or a
    # self-referential HEAD pin. A missing or non-ancestor revision is reset
    # to HEAD, which fails --check until the refresh is re-applied.
    rev = contract.get('sourceRevision')
    ancestor = False
    if rev:
        try:
            subprocess.check_output(['git', 'merge-base', '--is-ancestor', rev, 'HEAD'], cwd=root, stderr=subprocess.DEVNULL)
            ancestor = True
        except subprocess.CalledProcessError:
            ancestor = False
    contract.update(bindings=bindings, messages=copy_en,
                    masterSha256=hashlib.sha256(raw).hexdigest(),
                    sourceRevision=rev if ancestor else head)
    result = {hp: contract, root / 'locales/en/home-copy.json': copy_en}
    for code in LOCALES:
        path = root / f'locales/{code}/home-copy.json'
        catalog = json.loads(path.read_text())
        if set(catalog) != (set(copy_en) if applied else set(copy_en) - set(new_keys.values())):
            raise ValueError('Pre-existing home key drift ' + code)
        values = pack['locales'][code]
        if len(values) != 3 or any(not isinstance(v, str) or not v.strip() or re.search(r'<\s*/?\s*[A-Za-z!]', v) for v in values):
            raise ValueError('Invalid almoner home text ' + code)
        if applied:
            for (field, _), value in zip(FIELDS, values):
                if catalog.get(new_keys[field]) != value:
                    raise ValueError('Applied almoner locale drift ' + code)
        else:
            for (field, _), value in zip(FIELDS, values):
                catalog[new_keys[field]] = value
        if set(catalog) != set(copy_en):
            raise ValueError('Final home key mismatch ' + code)
        result[path] = catalog
    print(f'{len(bindings)} bindings: +3 almoner text row; {moved} survivor selector re-pins; 10 native-not-certified locale catalogs')
    return {p: json.dumps(v, ensure_ascii=False, indent=2) + '\n' for p, v in result.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in outputs().items():
        if args.check:
            if path.read_text() != text:
                raise SystemExit('Needs refresh: ' + str(path))
        else:
            path.write_text(text)
    print('almoner home refresh OK')
