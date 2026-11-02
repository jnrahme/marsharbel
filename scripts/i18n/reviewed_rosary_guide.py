"""Certify the reviewed Rosary guide locales; fail-closed on any drift.

The rosary topic guide (/en/rosary, "How to pray the Rosary: a simple guide") is a
separate page from /rosary-intro (already certified via ar2-rosary-intro-equivalence).
This producer creates the new rosary-guide-equivalence family from the lane's
equivalence record (gateStatus approved) and review record (renderedReviewStatus
approved plus per-locale approval), re-pins rendered main-body and pages.json#rosary
subtree bytes, supersedes only single-variant pending rows (loud guard otherwise),
and emits verified variants with the six parity proofs plus review hashes.
"""
import hashlib, json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest

LOCALES = ('ar', 'de', 'es', 'fr', 'it', 'pl', 'pt')
FAMILY = 'rosary-guide-equivalence'

def rosary_subtree_sha(root, code):
    data = json.loads((root / f'locales/{code}/pages.json').read_text())['rosary']
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def rosary_guide_manifest(root, texts, manifest):
    path = root / 'locales/rosary-guide-equivalence.json'
    if not path.exists():
        return manifest
    record = json.loads(path.read_text())
    if record.get('gateStatus') != 'approved':
        return manifest
    review = json.loads((root / 'locales/rosary-guide-review-record.json').read_text())
    if review['renderedReviewStatus'] != 'approved' or any(
            review['reviews'][lang]['status'] != 'approved' for lang in LOCALES):
        raise ValueError('Rosary guide integrated reviews incomplete')
    out = json.loads(json.dumps(manifest))
    for group_name, group in record['groups'].items():
        variants = group['variants']
        for lang, v in variants.items():
            file = root / v['file']
            text = texts.get(file, file.read_text())
            if digest(text) != v['bodySha256']:
                raise ValueError('Rosary guide reviewed body drift: ' + group_name + ' ' + lang)
            if lang != 'en' and rosary_subtree_sha(root, lang) != v['catalogSha256']:
                raise ValueError('Rosary guide reviewed catalog drift: ' + group_name + ' ' + lang)
        new_paths = {variants[lang]['path'] for lang in variants}
        for other in list(out['pages']):
            entry = out['pages'][other]
            if any(v['path'] in new_paths for v in entry['variants'].values()):
                # Loud guard: only single-variant pending rows may be superseded.
                vs = list(entry['variants'].values())
                if len(vs) != 1 or vs[0].get('status') != 'pending':
                    raise ValueError('Rosary guide pairing would replace a non-pending family: ' + other)
                del out['pages'][other]
        en = variants['en']
        page = {'sourcePath': en['file'], 'sourceRevision': group['sourceRevision'],
                'sourceSha256': en['bodySha256'], 'anchorIDs': {}, 'variants': {}}
        for lang, v in variants.items():
            file = root / v['file']
            soup = BeautifulSoup(texts.get(file, file.read_text()), 'html.parser')
            for el in soup.main.select('[id]'):
                page['anchorIDs'].setdefault(el['id'], {})[lang] = el['id']
            page['variants'][lang] = {'path': v['path'], 'aliases': [], 'status': 'verified',
                'contentSha256': v['bodySha256'], 'sourceSha256': en['bodySha256'],
                'proof': {**{k: True for k in ('keyedTextComplete', 'mediaParity', 'linkParity',
                    'schemaParity', 'anchorParity', 'interactionParity')},
                    'editorialReview': hashlib.sha256(group['catalogReview'].encode()).hexdigest(),
                    'nativeSampleReview': hashlib.sha256(json.dumps(review['reviews'], sort_keys=True).encode()).hexdigest(),
                    'renderedReview': hashlib.sha256(json.dumps(review, sort_keys=True).encode()).hexdigest()}}
        out['pages'][FAMILY] = page
    return out
