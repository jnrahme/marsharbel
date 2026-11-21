"""Pin-only history Media placeholder repair. Author does not execute it."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[2]
CODES = {'en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl', 'ru', 'hi', 'th'}
ADDED = {'history.header.' + key: key.title() for key in ('media', 'music', 'video', 'gallery')}
LEGACY = {'history.visit.heading', 'history.table.status.scroll-label',
          'history.table.facts.scroll-label', 'history.table.cause.scroll-label'}
BINDINGS = 'locales/en/history-master-bindings.json'
REVIEW = 'locales/history-equivalence.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(root, ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=root)


def body(raw):
    soup = BeautifulSoup(raw, 'html.parser')
    if len(soup.select('main')) != 1:
        raise ValueError('Expected one main')
    return sha(str(soup.main).encode())


def outside_header(raw):
    text = raw.decode()
    headers = list(re.finditer(r'<header\b[^>]*>[\s\S]*?</header\s*>', text, re.I))
    if len(headers) != 1:
        raise ValueError('Expected one header')
    h = headers[0]
    return text[:h.start()] + '<HEADER/>' + text[h.end():]


def placeholders(old, new):
    if set(new) - set(old) != set(ADDED) or set(old) - set(new):
        raise ValueError('Unexpected placeholder key set')
    if any(new[k] != v for k, v in old.items()):
        raise ValueError('Existing catalog value changed')
    if any(new[k] != v for k, v in ADDED.items()):
        raise ValueError('Only exact English placeholders permitted')


def pin_text(text, path, old, new):
    """Replace exactly one JSON scalar at path; preserve all other bytes."""
    if isinstance(path, str):
        path = (path,)
    decoder = json.JSONDecoder()
    matches = []

    def whitespace(i):
        while i < len(text) and text[i].isspace():
            i += 1
        return i

    def value(i, keys):
        i = whitespace(i)
        start = i
        if text[i] == '{':
            i = whitespace(i + 1)
            seen = set()
            while text[i] != '}':
                key, i = decoder.raw_decode(text, i)
                if not isinstance(key, str) or key in seen:
                    raise ValueError('Duplicate or invalid JSON object key')
                seen.add(key)
                i = whitespace(i)
                if text[i] != ':':
                    raise ValueError('Invalid JSON object')
                i = whitespace(value(i + 1, keys + (key,)))
                if text[i] == '}':
                    break
                if text[i] != ',':
                    raise ValueError('Invalid JSON separator')
                i = whitespace(i + 1)
            i += 1
        elif text[i] == '[':
            i = whitespace(i + 1)
            index = 0
            while text[i] != ']':
                i = whitespace(value(i, keys + (index,)))
                index += 1
                if text[i] == ']':
                    break
                if text[i] != ',':
                    raise ValueError('Invalid JSON separator')
                i = whitespace(i + 1)
            i += 1
        else:
            _, i = decoder.raw_decode(text, i)
        if keys == tuple(path):
            matches.append((start, i))
        return i

    try:
        end = value(0, ())
    except (IndexError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid JSON for pin replacement') from exc
    if whitespace(end) != len(text) or len(matches) != 1:
        raise ValueError('Ambiguous pin replacement: ' + '/'.join(path))
    start, end = matches[0]
    if json.loads(text[start:end]) != old or not re.fullmatch(r'[0-9a-f]{64}', new):
        raise ValueError('Unknown scoped pin value: ' + '/'.join(path))
    return text[:start] + json.dumps(new) + text[end:]


def validate_bindings(old, new, before, after):
    if old['master'] != 'history.html' or new['master'] != old['master']:
        raise ValueError('Unexpected master')
    if old['masterSha256'] != sha(before) or new['masterSha256'] not in (sha(before), sha(after)):
        raise ValueError('Unknown master pin provenance')
    if body(before) != body(after) or outside_header(before) != outside_header(after):
        raise ValueError('Body or non-header master change')
    # Four existing bound keys were omitted from the base messages map.
    # They are not new catalog keys or new bindings and may only copy the
    # already-bound English source verbatim.
    repaired_messages = dict(old['messages'])
    for key in LEGACY:
        matches = [b for b in old['bindings'] if b['key'] == key]
        if len(matches) != 1 or key in repaired_messages:
            raise ValueError('Unexpected legacy message provenance')
        b = matches[0]
        soup_before = BeautifulSoup(before, 'html.parser')
        nodes = soup_before.select(b['selector'])
        if len(nodes) != 1:
            raise ValueError('Ambiguous legacy binding')
        node = nodes[0]
        value = node.get(b['attribute']) if b['kind'] == 'attribute' else ' '.join(str(node.contents[b['nodeIndex']]).split())
        if value != b['source']:
            raise ValueError('Legacy source changed')
        repaired_messages[key] = b['source']
    placeholders(repaired_messages, new['messages'])
    extra = [b for b in new['bindings'] if b['key'] in ADDED]
    if len(extra) != 4 or {b['key'] for b in extra} != set(ADDED):
        raise ValueError('Expected four unique Media bindings')
    if [b for b in new['bindings'] if b['key'] not in ADDED] != old['bindings']:
        raise ValueError('Existing bindings changed')
    clean = copy.deepcopy(new)
    clean['bindings'] = old['bindings']; clean['messages'] = old['messages']
    clean['masterSha256'] = old['masterSha256']
    if clean != old:
        raise ValueError('Binding review fields changed')
    soup = BeautifulSoup(after, 'html.parser')
    parents = [a for a in soup.select('header nav a.nav-parent') if a.get_text(' ', strip=True) == 'Media']
    if len(parents) != 1:
        raise ValueError('Expected unique Media group')
    group = parents[0].find_parent(class_='nav-group')
    nodes = [parents[0]] + group.select('.nav-sub a')
    if [(a.get_text(' ', strip=True), a.get('href')) for a in nodes] != [
            ('Media', './music'), ('Music', './music'), ('Video', './videos'), ('Gallery', './gallery')]:
        raise ValueError('Media group destinations changed')
    targets = dict(zip(ADDED, nodes))
    for b in extra:
        selected = soup.select(b['selector'])
        if len(selected) != 1 or selected[0] is not targets[b['key']]:
            raise ValueError('Binding is not exact Media nav node')
        if b.get('kind') != 'text' or b.get('source') != ADDED[b['key']] or b.get('nodeIndex') != 0:
            raise ValueError('Invalid Media text binding')
        text = selected[0].contents[0]
        if not isinstance(text, NavigableString) or str(text).strip() != b['source']:
            raise ValueError('Media binding source differs')


def prepare(root, base):
    old_contract = json.loads(blob(root, base, BINDINGS))
    contract_text = (root / BINDINGS).read_text(); contract = json.loads(contract_text)
    before = blob(root, base, 'history.html'); after = (root / 'history.html').read_bytes()
    validate_bindings(old_contract, contract, before, after)
    old_review = json.loads(blob(root, base, REVIEW))
    review_text = (root / REVIEW).read_text(); review = json.loads(review_text)
    if set(old_review['variants']) != CODES or set(review['variants']) != CODES:
        raise ValueError('History locale set changed')
    baseline = copy.deepcopy(review)
    rows = []
    english_before = json.loads(blob(root, base, 'locales/en/history-master-copy.json'))
    english = json.loads((root / 'locales/en/history-master-copy.json').read_text())
    if (set(english_before) - set(old_contract['messages']) != LEGACY
            or any(english_before.get(k) != v for k, v in old_contract['messages'].items())
            or any(english_before[k] != next(b['source'] for b in old_contract['bindings'] if b['key'] == k) for k in LEGACY)
            or english != contract['messages']):
        raise ValueError('English catalog/binding message mismatch')
    for code in sorted(CODES):
        old_v = old_review['variants'][code]; v = review['variants'][code]
        path = old_v['file']
        previous = blob(root, base, path); current = (root / path).read_bytes()
        if body(previous) != old_v['bodySha256'] or body(current) != old_v['bodySha256']:
            raise ValueError('Reviewed body changed: ' + code)
        if outside_header(previous) != outside_header(current):
            raise ValueError('Non-header rendered change: ' + code)
        catalog = f'locales/{code}/history-master-copy.json'
        prior_copy = blob(root, base, catalog); new_copy = (root / catalog).read_bytes()
        old_c, new_c = json.loads(prior_copy), json.loads(new_copy)
        if set(old_c) != set(english_before) or set(new_c) != set(english):
            raise ValueError('Catalog key parity changed: ' + code)
        placeholders(old_c, new_c)
        if code != 'en':
            if v['catalog'] != catalog or old_v['catalog'] != catalog:
                raise ValueError('Unexpected catalog path')
            old_hash, new_hash = sha(prior_copy), sha(new_copy)
            if old_v['catalogSha256'] != old_hash or v['catalogSha256'] not in (old_hash, new_hash):
                raise ValueError('Unknown catalog pin provenance: ' + code)
            baseline['variants'][code]['catalogSha256'] = old_hash
            review_text = pin_text(review_text, ('variants', code, 'catalogSha256'), v['catalogSha256'], new_hash)
            rows.append(dict(file=catalog, old=v['catalogSha256'], new=new_hash,
                             body_before=body(previous), body_after=body(current)))
    if baseline != old_review:
        raise ValueError('History review fields changed')
    contract_text = pin_text(contract_text, 'masterSha256', contract['masterSha256'], sha(after))
    rows.append(dict(file=BINDINGS, old=contract['masterSha256'], new=sha(after),
                     body_before=body(before), body_after=body(after)))
    return {root / REVIEW: review_text, root / BINDINGS: contract_text}, rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', required=True)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    updates, rows = prepare(ROOT, args.base)
    print(json.dumps({'mode': 'write' if args.write else 'check', 'pins': rows,
                      'reason': 'four header-only English Media placeholders; no review grant'}, indent=2))
    if args.write:
        for path, text in updates.items():
            if path.read_text() != text:
                path.write_text(text)


if __name__ == '__main__':
    main()
