"""Only source-validated scoped Travel proof prose is non-display metadata."""
from collections import Counter
import json
from i18n.reviewed_travel import travel_manifest
from i18n.travel_variant_evidence import SLUGS

PREFIX='window.SC_SAME_PAGE_MANIFEST = '


def scoped_provenance(root,text):
    if not text.startswith(PREFIX) or not text.endswith(';\n'):
        raise ValueError('Unexpected manifest serialization')
    manifest=json.loads(text[len(PREFIX):-2])
    expected=travel_manifest(root,{}, {'pages':{}})['pages']
    families={slug+'-travel-master-equivalence' for slug in SLUGS}
    actual={key for key,page in manifest['pages'].items() if any(v.get('proof',{}).get('type')=='scoped-travel-variant' for v in page['variants'].values())}
    if actual!=families or not families<=set(expected):
        raise ValueError('Unknown scoped manifest family membership')
    scopes=Counter()
    for key in sorted(families):
        page=manifest['pages'][key];source=expected[key]
        if page!=source:raise ValueError('Scoped manifest differs from validated locale evidence: '+key)
        for variant in page['variants'].values():
            scopes[variant['proof']['scope']]+=1
    return scopes
