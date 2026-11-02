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
    from i18n.reviewed_eucharistic import eucharistic_manifest
    actual_ar2={key for key,page in manifest['pages'].items() if any(v.get('proof',{}).get('type')==AR2 for v in page['variants'].values())}
    if actual_ar2:
        # Mirror the control_outputs order (travel, then ar2, then the eucharistic
        # certification that extends ar2 families), then keep only families carrying
        # ar2 proofs - the same predicate as actual_ar2.
        chained=eucharistic_manifest(root,{}, ar2_manifest(root,{}, travel_manifest(root,{}, {'pages':{}})))['pages']
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
        # scoped-ar2-variant variants (travel-4 ar twins) are owned by the ar2 validation above.
        page={**page,'variants':{c:v for c,v in page['variants'].items() if v.get('proof',{}).get('type')!='scoped-ar2-variant'}}
        if page!=source:raise ValueError('Scoped manifest differs from validated locale evidence: '+key)
        for variant in page['variants'].values():
            # annaya-hero-v1 scope is a non-prose token, never extracted as display text.
            if key!='annaya-tour-travel-master-equivalence':scopes[variant['proof']['scope']]+=1
    return scopes+citation_provenance(root,manifest)


import re as _re
def _extracted_prose(text):
    """Mirror of extract-js-text.mjs's prose predicate - keep the two in sync."""
    return bool((_re.search(r'[^\W\d_].*\s.*[^\W\d_]',text) or _re.fullmatch(r'[A-Z][a-z]+',text)) and not _re.search(r'[<>{}\[\]#=]|https?://',text))


def citation_provenance(root,manifest):
    """Citation-source-correction addenda are scoped provenance too: every manifest
    citationAmendment must rebuild exactly from the pinned sidecar, the sidecar's full
    amendment set must be present, and only then is the addendum prose (scope and
    quoted inheritedScope) subtracted from the manifest text counter."""
    from i18n import citation_amendment
    s=citation_amendment.load(root)
    if not s:return Counter()
    ar2_pages=s['families'].get('ar2',{}).get('pages',{})
    # Exact identity set, not a count: every sidecar amendment appears exactly once and
    # no foreign amendment is covered. Balanced missing/duplicate/foreign all fail.
    expected=set()
    for fam,d in s['families'].items():
        if fam=='ar2':continue
        for code in d.get('variants',{}):expected.add((fam,code))
    for slug,pg in ar2_pages.items():
        for code,row in pg.items():
            if isinstance(row,dict) and 'file' in row:expected.add(('ar2:'+slug,code))
    # Page keys carrying addenda must be EXACTLY the guard-named expected keys
    # ('<family>-equivalence' / 'ar2-<slug>-equivalence'): a renamed or duplicated key
    # is rejected here instead of inheriting a covered identity. Route identity at the
    # resolver is path-based by design; this gate is manifest-vs-sidecar binding only,
    # not exact page-key protection of routing.
    expected_keys={fam+'-equivalence' for fam in s['families'] if fam!='ar2'}
    expected_keys|={'ar2-'+slug+'-equivalence' for slug in ar2_pages}
    for key,page in manifest['pages'].items():
        if key not in expected_keys and any('citationAmendment' in v.get('proof',{}) for v in page['variants'].values()):
            raise ValueError('Manifest citationAmendment on unexpected page key: '+key)
    scopes=Counter();seen={}
    for key,page in manifest['pages'].items():
        slug=key[:-len('-equivalence')] if key.endswith('-equivalence') else key
        for code,v in page['variants'].items():
            p=v.get('proof',{});add=p.get('citationAmendment')
            if not add:continue
            # Identity comes from the manifest PAGE KEY (guard-named), not proof fields:
            # '<family>-equivalence' for catalog families, 'ar2-<slug>-equivalence' for ar2.
            base=key[:-len('-equivalence')] if key.endswith('-equivalence') else key
            if base.startswith('ar2-'):
                slug=base[len('ar2-'):]
                if slug not in ar2_pages or not citation_amendment.match_ar2(root,slug,code):
                    raise ValueError('Manifest citationAmendment outside sidecar coverage: '+key+' '+code)
                ident=('ar2:'+slug,code)
                rebuilt=citation_amendment.ar2_addendum(root,slug,code,add['newBodySha256'],p.get('candidateFileSha256'))
            else:
                fam=base
                if not citation_amendment.match(root,fam,code):
                    raise ValueError('Manifest citationAmendment outside sidecar coverage: '+key+' '+code)
                ident=(fam,code)
                rebuilt=citation_amendment.addendum(root,fam,code,add['newBodySha256'])
            if ident in seen:raise ValueError('Manifest citationAmendment duplicated: '+key+' '+code+' also in '+seen[ident])
            seen[ident]=key
            if add!=rebuilt:raise ValueError('Manifest citationAmendment differs from validated sidecar: '+key+' '+code)
            # Subtract ONLY what scripts/i18n/extract-js-text.mjs actually extracts
            # (letter..whitespace..letter, or Singleword; never tokens/URLs/markup) -
            # e.g. slug-like inheritedScope tokens are non-prose to the extractor.
            if _extracted_prose(add['scope']):scopes[add['scope']]+=1
            if add.get('inheritedScope') and _extracted_prose(add['inheritedScope']):scopes[add['inheritedScope']]+=1
    if set(seen)!=expected:
        raise ValueError('Manifest citationAmendment set differs from sidecar: missing '+str(sorted(expected-set(seen))[:3])+' foreign '+str(sorted(set(seen)-expected)[:3]))
    return scopes


def manifest_text_counter(root,text,values):
    counter=Counter(values);provenance=scoped_provenance(root,text)
    if provenance-counter:raise ValueError('Manifest provenance missing from JS extractor')
    return counter-provenance
