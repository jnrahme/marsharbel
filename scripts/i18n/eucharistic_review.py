"""Scripted parity audit for the Eucharistic miracles family; emits the review records.

Fail-closed: any parity violation raises and no record is written. Checks the six
review dimensions per locale page against the English page (keyedTextComplete,
mediaParity, linkParity, schemaParity, anchorParity, interactionParity), then pins
rendered main-body and catalog bytes per variant. Records feed
scripts/i18n/reviewed_eucharistic.py; the gateStatus/reviewStatus fields record the
lane's audit outcome and remain the scrum adjudication point in the certification PR.
Usage: python3 scripts/i18n/eucharistic_review.py [--write]
"""
import hashlib, json, subprocess, sys
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ('ar', 'de', 'es', 'fr', 'it', 'pl', 'pt')
SLUGS = ('lanciano', 'bolsena-orvieto', 'siena', 'santarem', 'sokolka', 'legnica',
         'ludbreg', 'amsterdam', 'ivorra', 'faverney')
PAGES = [('eucharistic-hub', 'miracles/eucharistic/index.html', '/miracles/eucharistic/')] + [
    ('eucharistic-' + slug, f'miracles/eucharistic/{slug}.html', f'/miracles/eucharistic/{slug}') for slug in SLUGS]
LOCALE_HUB = {'ar': '/ar/miracles/eucharistic/', 'de': '/de/miracles/eucharistic/',
              'es': '/es/miracles/eucharistic/', 'fr': '/fr/miracles/eucharistic/',
              'it': '/it/miracles/eucharistic/', 'pl': '/pl/miracles/eucharistic/',
              'pt': '/pt/miracles/eucharistic/'}
sha = lambda b: hashlib.sha256(b).hexdigest()

def locale_file(code, en_file):
    if en_file == 'miracles/eucharistic/index.html':
        return code + '/miracles/eucharistic/index.html'
    return code + '/miracles/eucharistic/' + Path(en_file).name

def norm_asset(route, src):
    return urljoin('https://marsharbel.com' + route, src)

def shape(value):
    if isinstance(value, dict):
        return {k: shape(v) for k, v in value.items()}
    if isinstance(value, list):
        return [shape(v) for v in value]
    return type(value).__name__

def main_probe(text, route):
    soup = BeautifulSoup(text, 'html.parser')
    main = soup.main
    if main is None:
        raise ValueError('missing main')
    links = sorted({a.get('href', '') for a in main.select('a[href]')})
    imgs = sorted({norm_asset(route, i.get('src', '')) for i in main.select('img')})
    ids = sorted(el.get('id') for el in main.select('[id]'))
    ctrls = sorted((b.name, str(b.get('type')), str(b.get('class'))) for b in main.select('button,select,input,textarea,form'))
    head_schema = []
    for sc in soup.head.select('script[type="application/ld+json"]'):
        block = json.loads(sc.string)
        # Locale pages declare inLanguage; the English page omits it. Whitelisted
        # locale-only key, asserted separately in audit(); not a parity break.
        block = {k: v for k, v in block.items() if k != 'inLanguage'}
        head_schema.append(block)
    return links, imgs, ids, ctrls, head_schema

def catalog_walk(value, path, code):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from catalog_walk(v, path + '.' + k, code)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from catalog_walk(v, f'{path}[{i}]', code)
    else:
        yield path, value

def audit():
    en_catalog = json.loads((ROOT / 'locales/en/eucharistic-miracles.json').read_text())
    review = {'version': 1, 'renderedReviewStatus': 'approved', 'family': 'eucharistic-miracles',
              'auditScript': 'scripts/i18n/eucharistic_review.py', 'reviews': {}}
    groups = {}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for code in LOCALES:
        checks = {'keyedTextComplete': True, 'mediaParity': True, 'linkParity': True,
                  'schemaParity': True, 'anchorParity': True, 'interactionParity': True}
        catalog = json.loads((ROOT / f'locales/{code}/eucharistic-miracles.json').read_text())
        if shape(catalog) != shape(en_catalog):
            raise ValueError(f'{code}: catalog key shape differs from English')
        for p, v in catalog_walk(catalog, '$', code):
            if isinstance(v, str) and not v.strip():
                raise ValueError(f'{code}: blank catalog string at {p}')
        for fam, en_file, route in PAGES:
            en_text = (ROOT / en_file).read_text()
            lo_text = (ROOT / locale_file(code, en_file)).read_text()
            el, ei, eid, ec, es = main_probe(en_text, route)
            ll, li, lid, lc, ls = main_probe(lo_text, LOCALE_HUB[code] if 'index' in en_file else LOCALE_HUB[code] + Path(en_file).stem)
            if el != ll: raise ValueError(f'{code}/{fam}: link parity fail {sorted(set(el)^set(ll))}')
            if ei != li: raise ValueError(f'{code}/{fam}: media parity fail')
            if eid != lid: raise ValueError(f'{code}/{fam}: anchor parity fail')
            if ec != lc: raise ValueError(f'{code}/{fam}: interaction parity fail')
            if len(es) != len(ls) or any(shape(a) != shape(b) for a, b in zip(es, ls)):
                raise ValueError(f'{code}/{fam}: schema parity fail')
            raw_locale_schema = [json.loads(sc.string) for sc in BeautifulSoup(lo_text, 'html.parser').head.select('script[type="application/ld+json"]')]
            if any(b.get('inLanguage') != code for b in raw_locale_schema):
                raise ValueError(f'{code}/{fam}: missing or wrong inLanguage')
        review['reviews'][code] = {'status': 'approved', 'checks': checks,
                                   'pagesReviewed': len(PAGES)}
    for fam, en_file, route in PAGES:
        variants = {}
        en_text = (ROOT / en_file).read_text()
        variants['en'] = {'file': en_file, 'path': route,
                          'bodySha256': sha(str(BeautifulSoup(en_text, 'html.parser').main).encode())}
        for code in LOCALES:
            lf = locale_file(code, en_file)
            lo_text = (ROOT / lf).read_text()
            lo_route = (LOCALE_HUB[code] if 'index' in en_file else LOCALE_HUB[code] + Path(en_file).stem)
            variants[code] = {'file': lf, 'path': lo_route,
                              'bodySha256': sha(str(BeautifulSoup(lo_text, 'html.parser').main).encode()),
                              'catalog': f'locales/{code}/eucharistic-miracles.json',
                              'catalogSha256': sha((ROOT / f'locales/{code}/eucharistic-miracles.json').read_bytes())}
        groups[fam] = {'sourceRevision': head,
                       'catalogReview': f'{fam}: locale catalogs shape-equal to English; provenance fields byte-equal (renderer validate()); no blank strings',
                       'renderedReview': f'{fam}: scripted parity audit 2026-10-22 - keyedTextComplete, mediaParity, linkParity, schemaParity, anchorParity, interactionParity across ar/de/es/fr/it/pl/pt',
                       'variants': variants}
    equivalence = {'version': 1, 'gateStatus': 'approved', 'family': 'eucharistic-miracles',
                   'repinNote': 'bodySha256 pins the rendered main digest; catalogSha256 pins catalog bytes; drift fails closed in reviewed_eucharistic.eucharistic_manifest',
                   'groups': groups}
    review['auditSha256'] = sha(json.dumps(review['reviews'], sort_keys=True).encode())
    return equivalence, review

if __name__ == '__main__':
    equivalence, review = audit()
    if '--write' in sys.argv:
        (ROOT / 'locales/eucharistic-equivalence.json').write_text(json.dumps(equivalence, ensure_ascii=False, indent=1) + '\n')
        (ROOT / 'locales/eucharistic-review-record.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
        print('written', len(equivalence['groups']), 'groups x', len(LOCALES) + 1, 'locales')
    else:
        print('audit OK:', len(equivalence['groups']), 'groups x', len(LOCALES) + 1, 'locales (dry run)')
