"""Append missing Travel Media bindings/catalog keys before final review.
Independent execution required. No master, registry, render or review pin writes.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('travel_repin', ROOT/'scripts/i18n/repin_ru_travel_release.py')
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)
MODEL = 'qadisha-valley-travel-master'
FAMILIES = sorted(set(tools.FAMILIES) - {MODEL})
KEYS = tuple('travel.header.' + word for word in ('media', 'music', 'video', 'gallery'))
VALUES = {
    'en': ('Media', 'Music', 'Video', 'Gallery'),
    'de': ('Media', 'Music', 'Video', 'Galerie'),
    'ru': ('Медиа', 'Музыка', 'Видео', 'Галерея (на английском)'),
    'hi': ('मीडिया', 'संगीत', 'वीडियो', 'चित्र संग्रह'),
}
COMMON = tuple('navigation.' + word for word in ('media', 'music', 'video', 'gallery'))


def append_catalog(prior, current, labels):
    """Allow an absent set or exactly our completed append, never partial edits."""
    if set(prior) & set(KEYS):
        raise ValueError('Prepared base must lack all four keys')
    expected = {**prior, **dict(zip(KEYS, labels))}
    if current not in (prior, expected):
        raise ValueError('Partial/incorrect additions or old catalog values changed')
    return expected


def append_contract(prior, current, records):
    if len(records) != 4 or tuple(x['key'] for x in records) != KEYS:
        raise ValueError('Invalid four-binding model')
    if set(KEYS) & (set(prior['messages']) | {b['key'] for b in prior['bindings']}):
        raise ValueError('Prepared contract must lack all four keys')
    expected = copy.deepcopy(prior)
    expected['bindings'].extend(copy.deepcopy(records))
    expected['messages'].update(dict(zip(KEYS, VALUES['en'])))
    if current not in (prior, expected):
        raise ValueError('Old binding/messages/metadata changed')
    return expected


def validate_nodes(raw, records):
    soup = BeautifulSoup(raw, 'html.parser')
    nav = soup.select('header > div > nav > div:nth-of-type(6)')
    if len(nav) != 1 or len(nav[0].select('a')) != 4:
        raise ValueError('Media nav must have parent and three children')
    for record, label, href in zip(records, VALUES['en'], ('./music','./music','./videos','./gallery')):
        nodes = soup.select(record['selector'])
        if len(nodes) != 1 or nodes[0].get('href') != href or nodes[0].get_text(strip=True) != label:
            raise ValueError('Model selector does not identify exact existing nav node')
        if record.get('kind') != 'text' or record.get('nodeIndex') != 0 or record.get('source') != label:
            raise ValueError('Unknown Media text binding shape')


def prepare(root, base):
    # All inputs checked before returning any writes. No review fields created.
    for file in ('locales/registry.json', 'locales/travel-equivalence.json'):
        if tools.blob(root, base, file) != (root/file).read_bytes():
            raise ValueError('Registry/review changed after preparation base')
    review = json.loads((root/'locales/travel-equivalence.json').read_text())
    if set(FAMILIES) & set(review['groups']):
        raise ValueError('Active affected review groups require separate reviewed amendment')
    model_file = f'locales/en/{MODEL}-bindings.json'
    model_raw = tools.blob(root, base, model_file)
    if model_raw != (root/model_file).read_bytes():
        raise ValueError('Model contract changed')
    model = json.loads(model_raw)
    records = [next(b for b in model['bindings'] if b['key'] == key) for key in KEYS]
    if len([b for b in model['bindings'] if b['key'] in KEYS]) != 4:
        raise ValueError('Duplicate model keys')
    for code in ('en', 'de', 'ru'):
        file = f'locales/{code}/{MODEL}-copy.json'
        raw = tools.blob(root, base, file)
        if raw != (root/file).read_bytes() or tuple(json.loads(raw)[k] for k in KEYS) != VALUES[code]:
            raise ValueError('Existing catalog model changed')
    common_file = 'locales/hi/common.json'
    common_raw = tools.blob(root, base, common_file)
    if common_raw != (root/common_file).read_bytes() or tuple(json.loads(common_raw)[k] for k in COMMON) != VALUES['hi']:
        raise ValueError('Hindi common wording changed')
    updates, rows = {}, []
    for family in FAMILIES:
        master = tools.FAMILIES[family] + '.html'
        before = tools.blob(root, base, master)
        if before != (root/master).read_bytes():
            raise ValueError('Master bytes changed after preparation base')
        validate_nodes(before, records)
        file = f'locales/en/{family}-bindings.json'
        prior = json.loads(tools.blob(root, base, file)); current = json.loads((root/file).read_text())
        if prior['master'] != master or prior['masterSha256'] != tools.sha(before):
            raise ValueError('Stale master binding pin')
        expected = append_contract(prior, current, records)
        updates[root/file] = json.dumps(expected, ensure_ascii=False, indent=2) + '\n'
        codes = ('en','de','ru','hi') if master == 'travel.html' else ('en','de','ru')
        actual = {p.parent.name for p in root.glob(f'locales/*/{family}-copy.json')}
        if actual != set(codes):
            raise ValueError('Keyed locale membership changed: ' + family)
        for code in codes:
            file = f'locales/{code}/{family}-copy.json'
            old_raw = tools.blob(root, base, file)
            prior = json.loads(old_raw); current = json.loads((root/file).read_text())
            if set(prior) != set(json.loads(tools.blob(root, base, f'locales/en/{family}-copy.json'))):
                raise ValueError('Preexisting catalog key parity broken')
            expected = append_catalog(prior, current, VALUES[code])
            new = json.dumps(expected, ensure_ascii=False, indent=2) + '\n'
            updates[root/file] = new
            rows.append(dict(file=file, old=tools.sha(old_raw), new=tools.sha(new.encode()), added=list(KEYS)))
    return updates, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    updates, rows = prepare(ROOT, args.base)
    print(json.dumps({'mode': 'write' if args.write else 'check', 'catalogs':rows,
                     'bindings':len(FAMILIES), 'pinWrites':0,
                     'next':'Regenerate independently, inspect final Media chrome on desktop/phone, then establish actual review records.'}, indent=2))
    if args.write:
        for path, text in updates.items():
            if path.read_text() != text:
                path.write_text(text)


if __name__ == '__main__':
    main()
