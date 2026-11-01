"""Add released travel twins only while their reviewed body/catalog pins match."""
import hashlib
import json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest
from i18n import citation_amendment


def travel_manifest(root, texts, manifest):
    path = root / 'locales/travel-equivalence.json'
    if not path.exists():
        return manifest
    groups = json.loads(path.read_text())['groups']
    out = json.loads(json.dumps(manifest))
    for family, review in groups.items():
        scoped = review.get('evidenceSchema') in ('scoped-variants-v1','annaya-hero-v1')
        if scoped:
            from i18n.travel_variant_evidence import validate_group, validate_variant
            validate_group(family,review)
        elif family.endswith('-travel-master'):
            raise ValueError('New-family evidence schema missing')
        elif review['renderedReviewStatus'] != 'approved' or not review['catalogReview'] or not review['renderedReview']:
            raise ValueError('Travel review incomplete: ' + family)
        variants = review['variants']
        for code, variant in variants.items():
            file = root / variant['file']
            text = texts.get(file, file.read_text())
            if scoped:validate_variant(root,family,code,variant,text,final=False,schema=review['evidenceSchema'])
            if digest(text) != citation_amendment.effective_body(root, family, code, variant['bodySha256']):
                raise ValueError('Travel body changed after review: ' + family + ' ' + code)
            if code != 'en' and hashlib.sha256((root / variant['catalog']).read_bytes()).hexdigest() != citation_amendment.effective_catalog(root, family, code, variant['catalogSha256']):
                raise ValueError('Travel catalog changed after review: ' + family + ' ' + code)
        paths = {v['path'] for v in variants.values()}
        for key in list(out['pages']):
            if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):
                del out['pages'][key]
        page = {'sourcePath': variants['en']['file'], 'sourceRevision': review['sourceRevision'],
                'sourceSha256': citation_amendment.effective_body(root, family, 'en', variants['en']['bodySha256']), 'anchorIDs': {}, 'variants': {}}
        for code, variant in variants.items():
            file = root / variant['file']
            soup = BeautifulSoup(texts.get(file, file.read_text()), 'html.parser')
            for el in soup.main.select('[id]'):
                page['anchorIDs'].setdefault(el['id'], {})[code] = el['id']
            eff = citation_amendment.effective_body(root, family, code, variant['bodySha256'])
            page['variants'][code] = {'path': variant['path'], 'aliases': [], 'status': 'verified',
                'contentSha256': eff, 'sourceSha256': page['sourceSha256'],
                'proof': {**{key: True for key in ('keyedTextComplete', 'mediaParity', 'linkParity',
                    'schemaParity', 'anchorParity', 'interactionParity')},
                    'editorialReview': hashlib.sha256(review.get('catalogReview','').encode()).hexdigest(),
                    'nativeSampleReview': hashlib.sha256(review.get('catalogReview','').encode()).hexdigest(),
                    'renderedReview': hashlib.sha256(review.get('renderedReview','').encode()).hexdigest()}}
            add = citation_amendment.addendum(root, family, code, eff)
            if add and citation_amendment.proof_mode(root) != 'git':
                page['variants'][code] = citation_amendment.export_variant(variant['path'], eff, page['sourceSha256'])
            if add: page['variants'][code]['proof']['citationAmendment'] = add
        if scoped:
            for code, variant in variants.items():
                file=root/variant['file']
                page['variants'][code]['proof']=validate_variant(root,family,code,variant,texts.get(file,file.read_text()),final=False,schema=review['evidenceSchema'])
                if page['variants'][code]['proof'].get('type')=='unverified-export':
                    page['variants'][code]['status']='unverified-export'
        out['pages'][family + '-equivalence'] = page
    return out
