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
    from i18n.ar2_equivalence import ar2_manifest, AR2
    from i18n.reviewed_travel_authored_mirror import travel_authored_mirror_manifest
    from i18n.reviewed_eucharistic import eucharistic_manifest
    actual_ar2={key for key,page in manifest['pages'].items() if any(v.get('proof',{}).get('type')==AR2 for v in page['variants'].values())}
    if actual_ar2:
        # Mirror the control_outputs order (travel, then ar2, then the eucharistic
        # certification that extends ar2 families), then keep only families carrying
        # ar2 proofs - the same predicate as actual_ar2.
        chained=eucharistic_manifest(root,{}, travel_authored_mirror_manifest(root,{}, ar2_manifest(root,{}, travel_manifest(root,{}, {'pages':{}}))))['pages']
        expected_ar2={key:page for key,page in chained.items() if any(v.get('proof',{}).get('type')==AR2 for v in page['variants'].values())}
        if actual_ar2!=set(expected_ar2):raise ValueError('Unknown scoped ar2 manifest family membership')
        for key in sorted(actual_ar2):
            if manifest['pages'][key]!=expected_ar2[key]:raise ValueError('Scoped ar2 manifest differs from validated locale evidence: '+key)
    expected=travel_manifest(root,{}, {'pages':{}})['pages']
    families={slug+'-travel-master-equivalence' for slug in SLUGS}
    actual={key for key,page in manifest['pages'].items() if any(v.get('proof',{}).get('type')=='scoped-travel-variant' for v in page['variants'].values())}
    if actual!=families or not families<=set(expected):
        raise ValueError('Unknown scoped manifest family membership')
    scopes=Counter()
    for key in sorted(families):
        page=manifest['pages'][key];source=expected[key]
        # scoped-ar2-variant variants (travel-4 ar twins) and travel-authored-mirror
        # variants (A2 es/fr/it/pl/pt twins) are owned by the ar2 validation above.
        owned=[v for v in page['variants'].values() if v.get('proof',{}).get('type')=='travel-authored-mirror']
        page={**page,'variants':{c:v for c,v in page['variants'].items() if v.get('proof',{}).get('type') not in ('scoped-ar2-variant','travel-authored-mirror')}}
        if page!=source:raise ValueError('Scoped manifest differs from validated locale evidence: '+key)
        for variant in owned:
            scopes[variant['proof']['scope']]+=1
        for variant in page['variants'].values():
            # annaya-hero-v1 scope is a non-prose token, never extracted as display text.
            if key!='annaya-tour-travel-master-equivalence':scopes[variant['proof']['scope']]+=1
    return scopes


def manifest_text_counter(root,text,values):
    counter=Counter(values);provenance=scoped_provenance(root,text)
    if provenance-counter:raise ValueError('Manifest provenance missing from JS extractor')
    return counter-provenance
