"""Scoped rosary-book pairing. Review approval is an input, never inferred from routes."""
import copy
import hashlib
import json
import re
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest

LOCALES = ('en', 'ar', 'de', 'es', 'fr', 'it', 'pl', 'pt')
SLUGS = tuple('''joyful-annunciation joyful-visitation joyful-nativity joyful-presentation
joyful-finding-temple luminous-baptism luminous-cana luminous-proclamation
luminous-transfiguration luminous-eucharist sorrowful-agony-garden sorrowful-scourging
sorrowful-crowning-thorns sorrowful-carrying-cross sorrowful-crucifixion glorious-resurrection
glorious-ascension glorious-pentecost glorious-assumption glorious-coronation'''.split())
SCOPE = 'rosary-books-technical-pairing-only'


def rosary_books_manifest(root, texts, manifest):
    path = root / 'locales/rosary-books-pairing.json'
    if not path.exists():
        return manifest
    record = json.loads(path.read_text())
    if record.get('activationStatus') != 'activated-pending-live-click':
        return manifest
    review = record.get('review', {})
    if (review.get('scope') != SCOPE or review.get('nativeReviewStatus') != 'not-certified'
            or review.get('editorialReviewStatus') != 'not-certified'
            or review.get('technicalReviewStatus') != 'pending-live-click'
            or record.get('gateStatus') != 'pending-live-click'
            or review.get('reviewer') != 'owner-delegated authorization (Instinct main), no independent byte review'
            or not review.get('evidenceRef')
            or not re.fullmatch(r'[a-f0-9]{40}', record.get('sourceRevision', ''))
            or set(record.get('books', {})) != set(SLUGS)):
        raise ValueError('Rosary books pairing review incomplete')
    registry = json.loads((root / 'locales/registry.json').read_text())
    out = copy.deepcopy(manifest)
    for slug in SLUGS:
        cfg = registry['pageMirrors'][slug + '-master']
        routes = {code: '/' + ('' if code == 'en' else code + '/') + slug for code in LOCALES}
        if (cfg['english'] != routes['en'] or cfg['master'] != slug + '.html'
                or cfg['routes'] != {c: routes[c] for c in LOCALES if c != 'en'}
                or set(cfg['renderLocales']) != set(LOCALES) - {'en'}):
            raise ValueError('Rosary books registry scope drift: ' + slug)
        pins = record['books'][slug]
        if set(pins.get('variants', {})) != set(LOCALES):
            raise ValueError('Rosary books locale membership drift: ' + slug)
        for rel, pin in pins.get('artifacts', {}).items():
            if rel not in {f'content/books/{slug}/{c}.json' for c in LOCALES} | {f'content/books/{slug}/book.json', f'{slug}-story-i18n-data.js'}:
                raise ValueError('Rosary books unexpected artifact: ' + rel)
            if hashlib.sha256((root / rel).read_bytes()).hexdigest() != pin:
                raise ValueError('Rosary books artifact drift: ' + rel)
        required = {f'content/books/{slug}/{c}.json' for c in LOCALES} | {f'content/books/{slug}/book.json', f'{slug}-story-i18n-data.js'}
        if set(pins.get('artifacts', {})) != required:
            raise ValueError('Rosary books artifacts incomplete: ' + slug)
        for code in LOCALES:
            pin = pins['variants'][code]
            file = root / (routes[code].strip('/') + '.html')
            if digest(texts.get(file, file.read_text())) != pin['bodySha256']:
                raise ValueError('Rosary books body drift: ' + slug + ' ' + code)
            catalog = root / f'locales/{code}/{slug}-master-copy.json'
            if hashlib.sha256(catalog.read_bytes()).hexdigest() != pin['catalogSha256']:
                raise ValueError('Rosary books catalog drift: ' + slug + ' ' + code)
        for key in list(out['pages']):
            entry = out['pages'][key]
            if any(v['path'] in routes.values() for v in entry['variants'].values()):
                vs = list(entry['variants'].values())
                if len(vs) != 1 or vs[0].get('status') != 'pending':
                    raise ValueError('Rosary books pairing would replace reviewed family: ' + key)
                del out['pages'][key]
        source = pins['variants']['en']['bodySha256']
        page = {'sourcePath': slug + '.html', 'sourceRevision': record['sourceRevision'],
                'sourceSha256': source, 'anchorIDs': {}, 'variants': {}}
        for code in LOCALES:
            file = root / (routes[code].strip('/') + '.html')
            soup = BeautifulSoup(texts.get(file, file.read_text()), 'html.parser')
            for node in soup.main.select('[id]'):
                page['anchorIDs'].setdefault(node['id'], {})[code] = node['id']
            body = pins['variants'][code]['bodySha256']
            page['variants'][code] = {'path': routes[code], 'aliases': [], 'status': 'verified',
                'sourceSha256': source, 'contentSha256': body,
                'proof': {'type': 'scoped-rosary-books-variant', 'scope': SCOPE,
                    'nativeReviewStatus': 'not-certified', 'editorialReviewStatus': 'not-certified',
                    'activationStatus': 'activated-pending-live-click',
                    'technicalReviewStatus': 'pending-live-click', 'reviewer': review['reviewer'],
                    'evidenceRef': review['evidenceRef'],
                    'receiptSha256': hashlib.sha256(json.dumps(review, sort_keys=True).encode()).hexdigest(),
                    'reviewedContentSha256': body}}
        out['pages'][slug + '-master-equivalence'] = page
    return out
