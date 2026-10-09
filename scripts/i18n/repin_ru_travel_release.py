"""C-0016 prepared-review, hreflang-only Travel pin repair. Independent runner only.
Use a committed prepared base containing all reviewed records and final catalogs,
BEFORE hreflang injection. This tool never creates review approval or translates.
"""
import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SLUGS = {'travel', 'annaya-tour', 'bekaa-kafra', 'bkerke-maronite-patriarchate',
         'cedars-of-god-lebanon', 'our-lady-of-lebanon-harissa', 'qadisha-valley',
         'qannoubine-monastery', 'qozhaya-monastery', 'saint-charbel-hermitage',
         'saint-charbel-places-lebanon', 'saint-charbel-trail'}
FAMILIES = {s + '-travel-master': s for s in SLUGS}
PRIOR_FILES = {'22-chislo-mesyaca.html', 'annaya.html', 'biography.html', 'index.html',
               'molitvy.html', 'novena.html', 'palomnichestvo.html'}
TARGET_FILES = PRIOR_FILES | {s + '.html' for s in SLUGS}
REVIEW = 'locales/travel-equivalence.json'
TEST = 'scripts/qa/test_russian_slice.py'
OLD_LIST = repr(sorted(PRIOR_FILES)).replace(', ', ',')
NEW_LIST = repr(sorted(TARGET_FILES)).replace(', ', ',')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(root, ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=root)


def main_hash(raw):
    soup = BeautifulSoup(raw, 'html.parser')
    if len(soup.select('main')) != 1:
        raise ValueError('Expected one main')
    return sha(str(soup.main).encode())


def hreflang_delta(before, after, ru_url):
    pattern = re.compile(rb'^[ \t]*<link\b[^>]*\bhreflang=["\']ru["\'][^>]*>[ \t]*\r?\n', re.M)
    def masked(raw):
        soup = BeautifulSoup(raw, 'html.parser')
        links = soup.select('head link[hreflang="ru"]')
        if len(links) > 1 or any(x.get('href') != ru_url or x.get('rel') != ['alternate'] for x in links):
            raise ValueError('Unexpected RU hreflang')
        found = pattern.findall(raw)
        if len(found) != len(links):
            raise ValueError('RU hreflang must be one isolated head line')
        return pattern.sub(b'', raw)
    if main_hash(before) != main_hash(after) or masked(before) != masked(after):
        raise ValueError('Non-hreflang source change')
    if len(BeautifulSoup(after, 'html.parser').select('head link[hreflang="ru"]')) != 1:
        raise ValueError('Target lacks RU hreflang')


def bounded_test(text):
    if text.count(OLD_LIST) == 1 and NEW_LIST not in text:
        return text.replace(OLD_LIST, NEW_LIST, 1)
    if text.count(NEW_LIST) == 1 and OLD_LIST not in text:
        return text
    raise ValueError('Unexpected Russian bounded test shape')


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


def prepare(root, base):
    registry = json.loads((root / 'locales/registry.json').read_text())
    old_registry = json.loads(blob(root, base, 'locales/registry.json'))
    if registry != old_registry:
        raise ValueError('Registry must be final and committed in prepared base')
    if registry['locales']['ru'].get('capabilities', {}).get('topicGuides') != ['biography']:
        raise ValueError('Unexpected RU topic scope; separate review required')
    if any('ru' in values for values in registry['publicationSets'].values()):
        raise ValueError('Unexpected RU publicationSets scope')
    files = {p.relative_to(root / 'ru').as_posix() for p in (root / 'ru').rglob('*.html')}
    if files != TARGET_FILES:
        raise ValueError('Russian rendered scope is not exactly nineteen files')
    pending = json.loads((root / 'locales/same-page-manifest.pending.json').read_text())
    pending_ru = sorted(v['path'] for p in pending['pages'].values() for c, v in p['variants'].items() if c == 'ru')
    if pending_ru != ['/ru/', '/ru/22-chislo-mesyaca', '/ru/annaya', '/ru/biography', '/ru/palomnichestvo']:
        raise ValueError('Pending RU scope changed')
    review_text = (root / REVIEW).read_text()
    review = json.loads(review_text); old = json.loads(blob(root, base, REVIEW))
    expected_groups = {'annaya-master', 'twenty-second-master', 'pilgrimage-master'} | set(FAMILIES)
    if set(review['groups']) != expected_groups or set(old['groups']) != expected_groups:
        raise ValueError('Prepared base must contain all twelve reviewed new groups')
    baseline = copy.deepcopy(review)
    updates, rows = {}, []
    for family, slug in sorted(FAMILIES.items()):
        cfg = registry['pageMirrors'][family]
        if cfg['master'] != slug + '.html' or cfg['routes'].get('ru') != '/ru/' + slug:
            raise ValueError('Unexpected family or RU route')
        bp = 'locales/en/' + family + '-bindings.json'
        before_contract = json.loads(blob(root, base, bp))
        contract_text = (root / bp).read_text(); contract = json.loads(contract_text)
        before = blob(root, base, cfg['master']); after = (root / cfg['master']).read_bytes()
        old_sha, new_sha = sha(before), sha(after)
        if before_contract['masterSha256'] != old_sha or contract['masterSha256'] not in (old_sha, new_sha):
            raise ValueError('Unknown binding master pin provenance: ' + family)
        clean = copy.deepcopy(contract); clean['masterSha256'] = before_contract['masterSha256']
        if clean != before_contract:
            raise ValueError('Bindings or messages changed after prepared base')
        hreflang_delta(before, after, registry['site'] + '/ru/' + slug)
        updates[root / bp] = pin_text(contract_text, 'masterSha256', contract['masterSha256'], new_sha)
        rows.append(dict(file=bp, old=contract['masterSha256'], new=new_sha,
                         body_before=main_hash(before), body_after=main_hash(after)))
    for family, group in review['groups'].items():
        prior_group = old['groups'][family]
        # Pin-only continuation of already supplied reviews, never creation.
        if (group.get('renderedReviewStatus') != 'approved'
                or not group.get('catalogReview') or not group.get('renderedReview')):
            raise ValueError('Prepared review incomplete: ' + family)
        if set(group['variants']) != set(prior_group['variants']):
            raise ValueError('Reviewed variant set changed')
        if family in FAMILIES:
            slug = FAMILIES[family]
            en = group['variants'].get('en', {}); ru = group['variants'].get('ru', {})
            if en.get('file') != slug + '.html' or en.get('path') != '/' + slug:
                raise ValueError('Unexpected EN equivalence record')
            if ru.get('file') != 'ru/' + slug + '.html' or ru.get('path') != '/ru/' + slug or ru.get('catalog') != 'locales/ru/' + family + '-copy.json':
                raise ValueError('Unexpected RU equivalence record')
            if set(group['variants']) & {'zh-Hans', 'th'}:
                raise ValueError('Parallel masters cannot join exact group')
            expected_locales = {'en', 'de', 'ru'}
            if slug in {'travel', 'qadisha-valley', 'qannoubine-monastery', 'qozhaya-monastery'}:
                expected_locales |= {'ar', 'fr', 'es', 'pt', 'it', 'pl'}
            if slug == 'travel':
                expected_locales.add('hi')
            if set(group['variants']) != expected_locales:
                raise ValueError('Unexpected exact mirror locale membership: ' + family)
        for code, variant in group['variants'].items():
            prior = prior_group['variants'][code]
            file = variant['file']
            if file.startswith('/') or '..' in Path(file).parts:
                raise ValueError('Unsafe variant path')
            before = blob(root, base, file); after = (root / file).read_bytes()
            if main_hash(before) != prior['bodySha256'] or main_hash(after) != prior['bodySha256']:
                raise ValueError('Reviewed body changed: ' + family + '/' + code)
            # No digest grant for rewritten body/navigation/schema/copy here.
            # Existing-seven nav alignment belongs to the prepared base.
            if before != after and (family not in FAMILIES or code == 'ru'):
                raise ValueError('Unexpected rendered change after prepared base')
            if before != after:
                hreflang_delta(before, after, registry['site'] + '/ru/' + FAMILIES[family])
            if code == 'en':
                continue
            catalog = variant['catalog']
            if catalog.startswith('/') or '..' in Path(catalog).parts:
                raise ValueError('Unsafe catalog path')
            prior_copy = blob(root, base, catalog); current_copy = (root / catalog).read_bytes()
            if prior_copy != current_copy:
                raise ValueError('Catalog content changed after prepared review')
            old_hash, new_hash = sha(prior_copy), sha(current_copy)
            if prior['catalogSha256'] != old_hash or variant['catalogSha256'] not in (old_hash, new_hash):
                raise ValueError('Unknown reviewed catalog pin provenance')
            baseline['groups'][family]['variants'][code]['catalogSha256'] = prior['catalogSha256']
            review_text = pin_text(review_text, ('groups', family, 'variants', code, 'catalogSha256'), variant['catalogSha256'], new_hash)
        # Non-pin review fields and candidate-file provenance stay frozen.
    if baseline != old:
        raise ValueError('Review fields or other non-pin records changed')
    updates[root / REVIEW] = review_text
    test_text = (root / TEST).read_text(); base_test = blob(root, base, TEST).decode()
    updated_test = bounded_test(base_test)
    if test_text not in (base_test, updated_test):
        raise ValueError('Unrelated russian_slice assertion changed')
    updates[root / TEST] = updated_test
    return updates, rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', required=True, help='Committed fully reviewed prepared state, before hreflang injection')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    updates, rows = prepare(ROOT, args.base)
    print(json.dumps({'mode': 'write' if args.write else 'check', 'masterPins': rows,
                      'renderedRuFiles': sorted(TARGET_FILES), 'pendingRuCount': 5,
                      'reviewFields': 'preserved, not created'}, indent=2))
    if args.write:
        for path, text in updates.items():
            if path.read_text() != text:
                path.write_text(text)


if __name__ == '__main__':
    main()
