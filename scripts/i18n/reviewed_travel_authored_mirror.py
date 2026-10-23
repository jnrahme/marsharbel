"""Certify the authored-mirror /travel twins (es/fr/it/pl/pt) into the verified
travel-travel-master family; fail-closed on any drift.

The five twins render from locales/<code>/travel.json through the keyed authored
mirror (registry authoredMirrors.travel), a different pipeline than the master
catalog twins (de/ru/hi). Like the ar2 travel-4 merge (scrum ruling 2026-10-12),
this producer leaves the frozen scoped-variants machinery untouched and adds the
reviewed variants into the existing verified family after it is built, superseding
only single-variant pending rows (loud guard otherwise). Gate: the evidence record
must carry gateStatus approved; review basis is AI review under the owner waiver
2026-10-22 16:23 EDT and is never labeled native-validated.
"""
import hashlib, json, re
from i18n.reviewed_history import digest

LOCALES = ('es', 'fr', 'it', 'pl', 'pt')
RECORD = 'locales/travel-authored-mirror-equivalence.json'
PROOF_TYPE = 'travel-authored-mirror'

def travel_authored_mirror_manifest(root, texts, manifest):
    path = root / RECORD
    if not path.exists():
        return manifest
    record = json.loads(path.read_text())
    if record.get('gateStatus') != 'approved':
        return manifest
    if 'owner waiver 2026-10-22 16:23 EDT' not in record.get('reviewBasis', ''):
        raise ValueError('Travel authored-mirror review basis must name the owner waiver')
    out = json.loads(json.dumps(manifest))
    for group_name, group in record['groups'].items():
        if group.get('evidenceSchema') != 'authored-mirror-v1':
            raise ValueError('Unknown travel authored-mirror evidence schema: ' + group_name)
        family_key = group['family']
        family = out['pages'].get(family_key)
        if not family:
            # Strict by default: a missing expected frozen family aborts the
            # production build. The only permitted absent-family composition is
            # the probe_partial_build counterfactual, which opts in explicitly
            # by patching this producer out (never inferred here).
            raise ValueError('Travel authored-mirror target family missing: ' + family_key)
        en_variant = family['variants'].get('en', {})
        if en_variant.get('path') != group['enRoute'] or en_variant.get('status') != 'verified':
            raise ValueError('Travel authored-mirror family en variant not the verified master: ' + family_key)
        if not re.fullmatch(r'[0-9a-f]{40}', family.get('sourceRevision', '')):
            raise ValueError('Travel authored-mirror family sourceRevision not frozen 40-hex: ' + family_key)
        if set(group['variants']) != set(LOCALES):
            raise ValueError('Travel authored-mirror membership mismatch: ' + group_name)
        new_paths = set()
        for code, variant in group['variants'].items():
            file = root / variant['file']
            text = texts.get(file, file.read_text())
            if variant['path'] != '/' + variant['file'].removesuffix('.html'):
                raise ValueError('Travel authored-mirror route/file mismatch: ' + code)
            if digest(text) != variant['bodySha256']:
                raise ValueError('Travel authored-mirror reviewed body drift: ' + code)
            if hashlib.sha256((root / variant['catalog']).read_bytes()).hexdigest() != variant['catalogSha256']:
                raise ValueError('Travel authored-mirror reviewed catalog drift: ' + code)
            new_paths.add(variant['path'])
        for other in list(out['pages']):
            if other == family_key:
                continue
            entry = out['pages'][other]
            if any(v['path'] in new_paths for v in entry['variants'].values()):
                # Loud guard: only single-variant pending rows may be superseded.
                vs = list(entry['variants'].values())
                if len(vs) != 1 or vs[0].get('status') != 'pending':
                    raise ValueError('Travel authored-mirror pairing would replace a non-pending family: ' + other)
                del out['pages'][other]
        for code, variant in group['variants'].items():
            if code in family['variants']:
                raise ValueError('Travel authored-mirror family already carries: ' + code)
            # Like the ar2 existing-family branch, do not touch the frozen family's
            # anchorIDs; anchors are byte-identical ids across the mirrored twins.
            family['variants'][code] = {'path': variant['path'], 'aliases': [], 'status': 'verified',
                'contentSha256': variant['bodySha256'], 'sourceSha256': family['sourceSha256'],
                'proof': {'type': PROOF_TYPE, 'state': 'approved',
                          'scope': record['reviewBasis'],
                          'candidateFileSha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                          'reviewedContentSha256': variant['bodySha256'],
                          'nativeReviewStatus': 'not-certified',
                          'evidenceRef': 'travel-authored-mirror-evidence-2026-10-22'}}
    return out
