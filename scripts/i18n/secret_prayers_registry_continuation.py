"""Invert only the explicit AR/FR Secret Prayers registry addition.

The MB16 original registry hash and all other owning pins stay unchanged.
This helper does not qualify citation evidence or excuse HEAD/disk differences.
"""
import hashlib
import json
from pathlib import Path

ORIGINAL_SHA256 = '4bf9d6f07b0af792144c2fb910db0f75ea24f9510556b69614c9caf1eccdb88a'
SLUGS = ('powerful-secret-prayers', 'mary-who-goes-ahead-prayer', 'lebanese-mountain-prayers', 'terco-da-batalha')


def expected_family(slug):
    return {'master': slug + '.html', 'english': '/' + slug,
            'routes': {c: '/' + c + '/' + slug for c in ('ar', 'fr')},
            'renderLocales': ['ar', 'fr'],
            'discoveryRoutes': {'en': '/' + slug, 'ar': '/ar/' + slug,
                                'fr': '/fr/' + slug, 'x-default': '/' + slug}}


def registry_preimage(root, raw):
    if hashlib.sha256(raw).hexdigest() == ORIGINAL_SHA256:
        return raw
    from qa.secret_prayers_ar_fr_policy import load
    if load(Path(root)) is None:
        raise ValueError('Secret registry continuation requires its fixed record')
    data = json.loads(raw)
    if raw != (json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode():
        raise ValueError('Secret registry serializer differs')
    mirrors = data.get('pageMirrors', {})
    for slug in SLUGS:
        family = slug + '-master'
        if mirrors.get(family) != expected_family(slug):
            raise ValueError('Secret registry family differs: ' + family)
        del mirrors[family]
    original = (json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode()
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError('Secret registry changed outside four explicit additions')
    return original
