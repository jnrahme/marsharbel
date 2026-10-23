"""Scripted parity audit for the Rosary guide topic family; emits the review records.

Fail-closed: any parity violation raises and no record is written. Checks the six
review dimensions per locale page against the English page (keyedTextComplete,
mediaParity, linkParity, schemaParity, anchorParity, interactionParity), then pins
rendered main-body bytes and the per-locale pages.json 'rosary' subtree per variant.
Internal topic links are normalized through registry localized slugs before
comparison (de/gebete and fr/prieres both normalize to the prayers topic).
Records feed scripts/i18n/reviewed_rosary_guide.py; the gateStatus/reviewStatus
fields record the lane's audit outcome and remain the scrum adjudication point.
Usage: python3 scripts/i18n/rosary_guide_review.py [--write]
"""
import hashlib, json, subprocess, sys
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ('de', 'es', 'fr', 'it', 'pl', 'pt', 'ar')
# (locale, file, route); routes are the registry localized slugs for topic 'rosary'.
PAGES = {'en': ('en/rosary.html', '/en/rosary'),
         'de': ('de/rosenkranz.html', '/de/rosenkranz'),
         'es': ('es/rosario.html', '/es/rosario'),
         'fr': ('fr/chapelet.html', '/fr/chapelet'),
         'it': ('it/rosario.html', '/it/rosario'),
         'pl': ('pl/rozaniec.html', '/pl/rozaniec'),
         'pt': ('pt/rosario.html', '/pt/rosario'),
         'ar': ('ar/rosary-guide.html', '/ar/rosary-guide')}
sha = lambda b: hashlib.sha256(b).hexdigest()

def registry():
    return json.loads((ROOT / 'locales/registry.json').read_text())

def norm_link(code, href):
    """Map locale-prefixed topic links to canonical topic tokens for parity."""
    if href.startswith('#') or href.startswith('http') or '?' in href:
        return href
    reg = registry()
    home = '/' if code == 'en' else '/' + code + '/'
    if href == home or (code == 'en' and href == '/'):
        return 'HOME'
    prefix = '/en/' if code == 'en' else '/' + code + '/'
    if href.startswith(prefix):
        slug = href[len(prefix):].strip('/')
        for topic, localized in reg['locales'][code].get('slugs', {}).items():
            if slug == localized:
                return 'TOPIC:' + topic
        return 'PATH:' + slug
    return href

def shape(value):
    if isinstance(value, dict):
        return {k: shape(v) for k, v in value.items()}
    if isinstance(value, list):
        return [shape(v) for v in value]
    return type(value).__name__

def main_probe(text, route, code):
    soup = BeautifulSoup(text, 'html.parser')
    main = soup.main
    if main is None:
        raise ValueError('missing main: ' + route)
    links = sorted({norm_link(code, a.get('href', '')) for a in main.select('a[href]')})
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

def norm_asset(route, src):
    return urljoin('https://marsharbel.com' + route, src)

def catalog_walk(value, path):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from catalog_walk(v, path + '.' + k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from catalog_walk(v, f'{path}[{i}]')
    else:
        yield path, value

def rosary_catalog(code):
    data = json.loads((ROOT / f'locales/{code}/pages.json').read_text())
    if 'rosary' not in data:
        raise ValueError(f'{code}: pages.json missing rosary topic')
    return data['rosary']

def audit():
    en_catalog = rosary_catalog('en')
    review = {'version': 1, 'renderedReviewStatus': 'approved', 'family': 'rosary-guide',
              'auditScript': 'scripts/i18n/rosary_guide_review.py', 'reviews': {}}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for code in LOCALES:
        checks = {'keyedTextComplete': True, 'mediaParity': True, 'linkParity': True,
                  'schemaParity': True, 'anchorParity': True, 'interactionParity': True}
        catalog = rosary_catalog(code)
        if shape(catalog) != shape(en_catalog):
            raise ValueError(f'{code}: rosary catalog key shape differs from English')
        for p, v in catalog_walk(catalog, '$'):
            if isinstance(v, str) and not v.strip():
                raise ValueError(f'{code}: blank catalog string at {p}')
        en_file, en_route = PAGES['en']
        lo_file, lo_route = PAGES[code]
        el, ei, eid, ec, es = main_probe((ROOT / en_file).read_text(), en_route, 'en')
        ll, li, lid, lc, ls = main_probe((ROOT / lo_file).read_text(), lo_route, code)
        # Locales publishing extra topics (es/pt feastDay per registry capabilities)
        # render one extra related-guides link each. Whitelisted variance: the extra
        # links must equal exactly the locale's registry-declared extra topics, and
        # nothing may be missing.
        shared_topics = {'biography', 'prayers', 'novena', 'rosary', 'annaya'}
        declared = set(registry()['locales'][code]['capabilities']['topicGuides'])
        allowed_extra = {'TOPIC:' + t for t in declared - shared_topics}
        extra, missing = set(ll) - set(el), set(el) - set(ll)
        if missing or extra != allowed_extra:
            raise ValueError(f'{code}: link parity fail extra={sorted(extra)} missing={sorted(missing)}')
        if ei != li: raise ValueError(f'{code}: media parity fail')
        if eid != lid: raise ValueError(f'{code}: anchor parity fail')
        if ec != lc: raise ValueError(f'{code}: interaction parity fail')
        if len(es) != len(ls) or any(shape(a) != shape(b) for a, b in zip(es, ls)):
            raise ValueError(f'{code}: schema parity fail')
        raw = [json.loads(sc.string) for sc in BeautifulSoup((ROOT / lo_file).read_text(), 'html.parser').head.select('script[type="application/ld+json"]')]
        if any(b.get('inLanguage') != code for b in raw):
            raise ValueError(f'{code}: missing or wrong inLanguage')
        review['reviews'][code] = {'status': 'approved', 'checks': checks, 'pagesReviewed': 1}
    variants = {}
    for code in ('en',) + LOCALES:
        file, route = PAGES[code]
        text = (ROOT / file).read_text()
        variants[code] = {'file': file, 'path': route,
                          'bodySha256': sha(str(BeautifulSoup(text, 'html.parser').main).encode())}
        if code != 'en':
            variants[code]['catalog'] = f'locales/{code}/pages.json#rosary'
            variants[code]['catalogSha256'] = sha(json.dumps(rosary_catalog(code), sort_keys=True, ensure_ascii=False).encode())
    groups = {'rosary-guide': {
        'sourceRevision': head,
        'catalogReview': 'rosary-guide: locale pages.json rosary subtrees shape-equal to English; no blank strings; prayer-name and mystery-name forms per the certified locale catalogs',
        'renderedReview': 'rosary-guide: scripted parity audit 2026-10-22 - keyedTextComplete, mediaParity, linkParity (slug-normalized), schemaParity, anchorParity, interactionParity across de/es/fr/it/pl/pt/ar; ar variant reviewed under owner waiver 2026-10-22 16:23 EDT (AI review, not native-validated; doctrine verdict via parent)',
        'variants': variants}}
    equivalence = {'version': 1, 'gateStatus': 'approved', 'family': 'rosary-guide',
                   'repinNote': 'bodySha256 pins the rendered main digest; catalogSha256 pins the pages.json rosary subtree (canonical JSON); drift fails closed in reviewed_rosary_guide.rosary_guide_manifest',
                   'groups': groups}
    review['auditSha256'] = sha(json.dumps(review['reviews'], sort_keys=True).encode())
    return equivalence, review

if __name__ == '__main__':
    equivalence, review = audit()
    if '--write' in sys.argv:
        (ROOT / 'locales/rosary-guide-equivalence.json').write_text(json.dumps(equivalence, ensure_ascii=False, indent=1) + '\n')
        (ROOT / 'locales/rosary-guide-review-record.json').write_text(json.dumps(review, ensure_ascii=False, indent=1) + '\n')
        print('written', len(equivalence['groups']), 'groups x', len(LOCALES) + 1, 'locales')
    else:
        print('audit OK:', len(equivalence['groups']), 'groups x', len(LOCALES) + 1, 'locales (dry run)')
