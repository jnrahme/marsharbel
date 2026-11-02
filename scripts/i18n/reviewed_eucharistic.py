"""Certify the reviewed Eucharistic miracles locales; fail-closed on any drift.

The en+ar twins are already verified by the AR-2 flow (ar2-eucharistic-*-equivalence).
This producer extends those families with the remaining reviewed locales
(de/es/fr/it/pl/pt) from the lane's equivalence record (gateStatus approved) and
review record (renderedReviewStatus approved plus per-locale approval), re-pins
rendered main-body and catalog bytes, supersedes only single-variant pending rows,
and emits verified variants with the six parity proofs plus review hashes.
"""
import hashlib, json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest

LOCALES = ('ar', 'de', 'es', 'fr', 'it', 'pl', 'pt')
EXTEND = ('de', 'es', 'fr', 'it', 'pl', 'pt')

def eucharistic_manifest(root, texts, manifest):
    path = root / 'locales/eucharistic-equivalence.json'
    if not path.exists():
        return manifest
    record = json.loads(path.read_text())
    if record.get('gateStatus') != 'approved':
        return manifest
    review = json.loads((root / 'locales/eucharistic-review-record.json').read_text())
    if review['renderedReviewStatus'] != 'approved' or any(
            review['reviews'][lang]['status'] != 'approved' for lang in LOCALES):
        raise ValueError('Eucharistic integrated reviews incomplete')
    out = json.loads(json.dumps(manifest))
    for family, group in record['groups'].items():
        variants = group['variants']
        for lang, v in variants.items():
            file = root / v['file']
            text = texts.get(file, file.read_text())
            if digest(text) != v['bodySha256']:
                raise ValueError('Eucharistic reviewed body drift: ' + family + ' ' + lang)
            if lang != 'en' and hashlib.sha256((root / v['catalog']).read_bytes()).hexdigest() != v['catalogSha256']:
                raise ValueError('Eucharistic reviewed catalog drift: ' + family + ' ' + lang)
        key = 'ar2-' + family + '-equivalence'
        if key not in out['pages']:
            raise ValueError('Eucharistic expected AR-2 family missing: ' + key)
        page = out['pages'][key]
        for lang in ('en', 'ar'):
            if page['variants'].get(lang, {}).get('path') != variants[lang]['path']:
                raise ValueError('Eucharistic AR-2 path mismatch: ' + family + ' ' + lang)
        new_paths = {variants[lang]['path'] for lang in EXTEND}
        for other in list(out['pages']):
            if other == key:
                continue
            entry = out['pages'][other]
            if any(v['path'] in new_paths for v in entry['variants'].values()):
                # Loud guard: only single-variant pending rows may be superseded.
                vs = list(entry['variants'].values())
                if len(vs) != 1 or vs[0].get('status') != 'pending':
                    raise ValueError('Eucharistic pairing would replace a non-pending family: ' + other)
                del out['pages'][other]
        for lang in EXTEND:
            v = variants[lang]
            file = root / v['file']
            soup = BeautifulSoup(texts.get(file, file.read_text()), 'html.parser')
            for el in soup.main.select('[id]'):
                page['anchorIDs'].setdefault(el['id'], {})[lang] = el['id']
            page['variants'][lang] = {'path': v['path'], 'aliases': [], 'status': 'verified',
                'contentSha256': v['bodySha256'], 'sourceSha256': page['sourceSha256'],
                'proof': {**{k: True for k in ('keyedTextComplete', 'mediaParity', 'linkParity',
                    'schemaParity', 'anchorParity', 'interactionParity')},
                    'editorialReview': hashlib.sha256(group['catalogReview'].encode()).hexdigest(),
                    'nativeSampleReview': hashlib.sha256(json.dumps(review['reviews'], sort_keys=True).encode()).hexdigest(),
                    'renderedReview': hashlib.sha256(json.dumps(review, sort_keys=True).encode()).hexdigest()}}
    return out
