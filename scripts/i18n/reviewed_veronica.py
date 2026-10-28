"""Veronica story equivalence routing; activates only after the review gate approves.

The candidate record pins the rendered main digest of every locale variant and the
per-locale catalog bytes. While gateStatus is not 'approved' the family stays out of
the built manifest: the switcher keeps non-current locales disabled and the pages
remain reachable only by direct URL, matching the review overlay policy. Approval is
the reviewer's act - this module never invents it; it only fails closed on drift.
"""
import hashlib,json,re
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest


# Fail-closed scoped artifact scope: on approved merge the FULL required key
# set must be present - an empty or partial artifacts map never merges.
_VERONICA_LOCALES=['en','ar','de','es','fr','hi','it','pl','pt','ru','th','zh-Hans']
REQUIRED_ARTIFACT_KEYS=frozenset(
    ['content/books/veronica-giuliani-story/book.json','storybook.js','storybook-stage.js',
     'storybook.css','storybook-joy.css','storybook-stage.css',
     'veronica-giuliani-story-data.js','veronica-giuliani-story-i18n-data.js']
    +[f'content/books/veronica-giuliani-story/{c}.json' for c in _VERONICA_LOCALES]
    +[f'locales/{c}/veronica-story-ui.json' for c in _VERONICA_LOCALES]
    +[f'media/storybook-veronica/images/page-{n:02d}.webp' for n in range(1,11)])


def veronica_manifest(root,texts,manifest):
    path=root/'locales/veronica-equivalence.json'
    if not path.exists():return manifest
    record=json.loads(path.read_text())
    if record.get('gateStatus')!='approved':return manifest
    review=record.get('reviewRecord') or {}
    langs=set(record.get('variants') or {})
    if (record.get('renderedReviewStatus')!='approved'
            or review.get('renderedReviewStatus')!='approved'
            or review.get('contentReviewMode')!='model-only'
            or review.get('nativeReviewStatus')!='not-certified'
            or review.get('scope')!='enabled-tests-only'
            or not re.fullmatch(r'[0-9a-f]{40}', str(review.get('scopeHead') or ''))
            or not re.fullmatch(r'[0-9a-f]{40}', str(record.get('sourceRevision') or ''))
            or set(review.get('reviews') or {})!=set(_VERONICA_LOCALES)
            or set(review.get('reviews') or {})!=langs
            or any(v!='approved' for v in review.get('reviews',{}).values())):
        raise ValueError('Veronica integrated review record incomplete')
    artifacts=record.get('artifacts') or {}
    missing=sorted(REQUIRED_ARTIFACT_KEYS-artifacts.keys())
    if missing:raise ValueError('Veronica equivalence artifacts missing required keys: '+', '.join(missing))
    for rel, pin in artifacts.items():
        if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=pin:
            raise ValueError('Veronica scoped artifact drift: '+rel)
    variants=record['variants']
    for lang,v in variants.items():
        file=root/v['file'];text=texts.get(file,file.read_text())
        if digest(text)!=v['bodySha256']:raise ValueError('Veronica reviewed body drift: '+lang)
        if lang!='en' and hashlib.sha256((root/v['catalog']).read_bytes()).hexdigest()!=v['catalogSha256']:
            raise ValueError('Veronica reviewed catalog drift: '+lang)
    out=json.loads(json.dumps(manifest));paths={v['path'] for v in variants.values()}
    for key in list(out['pages']):
        if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
    page={'sourcePath':variants['en']['file'],'sourceRevision':record['sourceRevision'],'sourceSha256':variants['en']['bodySha256'],'anchorIDs':{},'variants':{},'reviewScope':'veronica-model-only-enabled-tests'}
    for lang,v in variants.items():
        file=root/v['file']
        soup=BeautifulSoup(texts.get(file,file.read_text()),'html.parser')
        for el in soup.main.select('[id]'):page['anchorIDs'].setdefault(el['id'],{})[lang]=el['id']
        # Honest model-only proof: only actually-tested parities asserted;
        # no nativeSampleReview - model-only approval is not native review.
        page['variants'][lang]={'path':v['path'],'aliases':[],'status':'verified','contentSha256':v['bodySha256'],'sourceSha256':page['sourceSha256'],'proof':{'contentReviewMode':'model-only','nativeReviewStatus':'not-certified','scope':'enabled-tests-only','keyedTextComplete':True,'mediaParity':True,'linkParity':True,'editorialReview':hashlib.sha256(json.dumps(review['reviews'],sort_keys=True).encode()).hexdigest(),'renderedReview':hashlib.sha256(json.dumps(review,sort_keys=True).encode()).hexdigest(),'receipt':review['evidence'],'reviewedContentSha256':v['bodySha256']}}
    out['pages']['veronica-story-master-equivalence']=page
    return out
