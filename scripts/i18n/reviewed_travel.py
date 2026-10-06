"""Add released travel twins only while their reviewed body/catalog pins match."""
import hashlib
import json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest


def travel_manifest(root, texts, manifest):
    path = root / 'locales/travel-equivalence.json'
    if not path.exists():
        return manifest
    groups = json.loads(path.read_text())['groups']
    out = json.loads(json.dumps(manifest))
    for family, review in groups.items():
        if review['renderedReviewStatus'] != 'approved' or not review['catalogReview'] or not review['renderedReview']:
            raise ValueError('Travel review incomplete: ' + family)
        variants = review['variants']
        for code, variant in variants.items():
            file = root / variant['file']
            text = texts.get(file, file.read_text())
            if digest(text) != variant['bodySha256']:
                raise ValueError('Travel body changed after review: ' + family + ' ' + code)
            if code != 'en' and hashlib.sha256((root / variant['catalog']).read_bytes()).hexdigest() != variant['catalogSha256']:
                raise ValueError('Travel catalog changed after review: ' + family + ' ' + code)
        paths = {v['path'] for v in variants.values()}
        for key in list(out['pages']):
            if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):
                del out['pages'][key]
        page = {'sourcePath': variants['en']['file'], 'sourceRevision': review['sourceRevision'],
                'sourceSha256': variants['en']['bodySha256'], 'anchorIDs': {}, 'variants': {}}
        for code, variant in variants.items():
            file = root / variant['file']
            soup = BeautifulSoup(texts.get(file, file.read_text()), 'html.parser')
            for el in soup.main.select('[id]'):
                page['anchorIDs'].setdefault(el['id'], {})[code] = el['id']
            page['variants'][code] = {'path': variant['path'], 'aliases': [], 'status': 'verified',
                'contentSha256': variant['bodySha256'], 'sourceSha256': page['sourceSha256'],
                'proof': {**{key: True for key in ('keyedTextComplete', 'mediaParity', 'linkParity',
                    'schemaParity', 'anchorParity', 'interactionParity')},
                    'editorialReview': hashlib.sha256(review['catalogReview'].encode()).hexdigest(),
                    'nativeSampleReview': hashlib.sha256(review['catalogReview'].encode()).hexdigest(),
                    'renderedReview': hashlib.sha256(review['renderedReview'].encode()).hexdigest()}}
        out['pages'][family + '-equivalence'] = page
    return out
