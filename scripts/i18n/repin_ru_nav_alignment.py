"""Bounded RU shared Travel label/href repin; independent runner required."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('travel_repin', ROOT / 'scripts/i18n/repin_ru_travel_release.py')
tools = importlib.util.module_from_spec(spec); spec.loader.exec_module(tools)
RECORDS = [('locales/travel-equivalence.json', ('groups', f, 'variants', 'ru'))
           for f in ('annaya-master', 'twenty-second-master', 'pilgrimage-master')]
RECORDS += [('locales/history-equivalence.json', ('variants', 'ru'))]
RECORDS += [('locales/prayer-equivalence.json', ('groups', f, 'variants', 'ru'))
            for f in ('saint-charbel-prayers-master', 'saint-charbel-novena-master')]


def get(obj, path):
    for part in path:
        obj = obj[part]
    return obj


def normalized(raw, target):
    soup = BeautifulSoup(raw, 'html.parser')
    changed = 0
    for anchor in soup.select('a[href]'):
        if anchor['href'] not in ('/travel', '/ru/travel'):
            continue
        if not (anchor.find_parent('header') or anchor.find_parent('nav', class_='travel-breadcrumb')):
            continue
        text_nodes = [n for n in anchor.contents if isinstance(n, NavigableString) and str(n).strip()]
        if len(text_nodes) != 1:
            raise ValueError('Ambiguous Travel label text')
        node = text_nodes[0]; label = str(node).strip()
        allowed = {'Путешествия'} if target else {'Паломничество', 'Путешествия'}
        if label not in allowed or (target and anchor['href'] != '/ru/travel'):
            raise ValueError('Unexpected aligned Travel node')
        anchor['href'] = '/travel'; node.replace_with('TRAVEL_LABEL')
        changed += 1
    if not changed:
        raise ValueError('No shared Travel nav nodes')
    return soup, changed


SCHEMA_PAGES = {'ru/annaya.html', 'ru/palomnichestvo.html'}


def schema_name_delta(old, new, file):
    """Full JSON and byte comparison; mask only the named position-2 label."""
    prior = old.select('script[type="application/ld+json"]')
    current = new.select('script[type="application/ld+json"]')
    if len(prior) != len(current):
        raise ValueError('Schema script count changed')
    changes = 0
    for before, after in zip(prior, current):
        if before.string == after.string:
            continue
        if file not in SCHEMA_PAGES:
            raise ValueError('Schema delta outside two allowed pages')
        a, b = json.loads(before.string), json.loads(after.string)
        if a.get('@type') != 'WebPage' or b.get('@type') != 'WebPage':
            raise ValueError('Unexpected schema type')
        if a.get('breadcrumb', {}).get('@type') != 'BreadcrumbList' or b.get('breadcrumb', {}).get('@type') != 'BreadcrumbList':
            raise ValueError('Expected nested BreadcrumbList')
        old_items = a['breadcrumb']['itemListElement']
        new_items = b['breadcrumb']['itemListElement']
        matches_a = [i for i,v in enumerate(old_items) if v.get('position') == 2]
        matches_b = [i for i,v in enumerate(new_items) if v.get('position') == 2]
        if len(matches_a) != 1 or matches_a != matches_b:
            raise ValueError('Ambiguous breadcrumb position 2')
        i = matches_a[0]
        prior_item, current_item = old_items[i], new_items[i]
        if prior_item.get('item') != 'https://marsharbel.com/travel' or current_item.get('item') != prior_item['item']:
            raise ValueError('Travel schema URL changed')
        if prior_item.get('name') != 'Паломничество' or current_item.get('name') != 'Путешествия':
            raise ValueError('Unexpected Travel schema label')
        clean = copy.deepcopy(b)
        clean['breadcrumb']['itemListElement'][i]['name'] = prior_item['name']
        if clean != a:
            raise ValueError('Other JSON-LD fields changed')
        # Preserve byte equality outside this one JSON scalar, after full-object
        # verification. Reject ambiguous repeats rather than broad text changes.
        token_a = json.dumps(prior_item['name'], ensure_ascii=False)
        token_b = json.dumps(current_item['name'], ensure_ascii=False)
        raw_a, raw_b = str(before.string), str(after.string)
        if raw_a.count(token_a) != 1 or raw_b.count(token_b) != 1:
            raise ValueError('Ambiguous schema name scalar')
        if raw_a.replace(token_a, '"TRAVEL_SCHEMA_NAME"', 1) != raw_b.replace(token_b, '"TRAVEL_SCHEMA_NAME"', 1):
            raise ValueError('Other JSON-LD bytes changed')
        before.string = raw_a.replace(token_a, '"TRAVEL_SCHEMA_NAME"', 1)
        after.string = raw_b.replace(token_b, '"TRAVEL_SCHEMA_NAME"', 1)
        changes += 1
    if changes > 1:
        raise ValueError('Multiple Travel schema deltas')
    return changes


def nav_delta(before, after, file=None):
    old, old_count = normalized(before, False); new, new_count = normalized(after, True)
    schema_name_delta(old, new, file)
    if old_count != new_count or str(old) != str(new):
        raise ValueError('Non-nav DOM change')
    return tools.main_hash(before), tools.main_hash(after)


def catalog_delta(before, after):
    old, new = json.loads(before), json.loads(after)
    if set(old) != set(new):
        raise ValueError('Catalog key set changed')
    changes = []
    for key in old:
        if old[key] == new[key]:
            continue
        if not (key.endswith('.header.travel') or key.endswith('.body.travel')
                or key.endswith('.header.travel2')):
            raise ValueError('Non-Travel catalog key changed: ' + key)
        if old[key] != 'Паломничество' or new[key] != 'Путешествия':
            raise ValueError('Unexpected Travel catalog label delta')
        changes.append(key)
    if not changes:
        raise ValueError('No bounded catalog label change')
    return changes


def prepare(root, base):
    updates, rows = {}, []
    by_review = {}
    for file, path in RECORDS:
        if file not in by_review:
            text = (root / file).read_text()
            by_review[file] = [text, json.loads(text), json.loads(tools.blob(root, base, file))]
        text, current, prior = by_review[file]
        old_v = get(prior, path); v = get(current, path)
        if v['file'] != old_v['file'] or v['catalog'] != old_v['catalog']:
            raise ValueError('Review destination changed')
        before = tools.blob(root, base, old_v['file']); after = (root / v['file']).read_bytes()
        old_body, new_body = nav_delta(before, after, v['file'])
        old_catalog = tools.blob(root, base, old_v['catalog']); new_catalog = (root / v['catalog']).read_bytes()
        keys = catalog_delta(old_catalog, new_catalog)
        for field, old_hash, new_hash in [('bodySha256', old_body, new_body),
                                           ('catalogSha256', tools.sha(old_catalog), tools.sha(new_catalog))]:
            if old_v[field] != old_hash or v[field] not in (old_hash, new_hash):
                raise ValueError('Unknown nav pin provenance')
            clean = copy.deepcopy(v); clean['bodySha256'] = old_v['bodySha256']; clean['catalogSha256'] = old_v['catalogSha256']
            if clean != old_v:
                raise ValueError('Non-pin variant fields changed')
            text = tools.pin_text(text, path + (field,), v[field], new_hash)
        by_review[file][0] = text
        rows.append(dict(file=v['file'], catalog=v['catalog'], keys=keys,
                         old_body=old_body, new_body=new_body,
                         old_catalog=tools.sha(old_catalog), new_catalog=tools.sha(new_catalog),
                         schemaNameDelta=schema_name_delta(BeautifulSoup(before, 'html.parser'), BeautifulSoup(after, 'html.parser'), v['file'])))
    for file, (text, current, prior) in by_review.items():
        clean = copy.deepcopy(current)
        for f, path in RECORDS:
            if f != file:
                continue
            v = get(clean, path); old_v = get(prior, path)
            for field in ('bodySha256', 'catalogSha256'):
                v[field] = old_v[field]
        if clean != prior:
            raise ValueError('Review fields or unrelated records changed')
        updates[root / file] = text
    exact_path = 'locales/ru/biography-exact.json'
    old_exact = json.loads(tools.blob(root, base, exact_path))
    new_exact = json.loads((root / exact_path).read_text())
    clean_exact = copy.deepcopy(new_exact)
    if old_exact['chrome']['Travel'] != 'Паломничество (EN)' or new_exact['chrome']['Travel'] != 'Путешествия':
        raise ValueError('Unexpected exact chrome label')
    clean_exact['chrome']['Travel'] = old_exact['chrome']['Travel']
    if clean_exact != old_exact:
        raise ValueError('Unrelated exact catalog fields changed')
    # The seventh page has no body review record, but its final nav delta is
    # validated so the enumerated seven-page alignment cannot silently expand.
    nav_delta(tools.blob(root, base, 'ru/index.html'), (root / 'ru/index.html').read_bytes())
    return updates, rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', required=True)
    p.add_argument('--write', action='store_true')
    a = p.parse_args(); updates, rows = prepare(ROOT, a.base)
    print(json.dumps({'mode': 'write' if a.write else 'check', 'navOnlyDelta': rows,
                      'reason': 'RU Travel shared header/breadcrumb chrome alignment; review fields untouched'}, indent=2))
    if a.write:
        for path, text in updates.items():
            if path.read_text() != text:
                path.write_text(text)


if __name__ == '__main__':
    main()
