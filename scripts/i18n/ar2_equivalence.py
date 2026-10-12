"""Pair AR-2 hand-authored Arabic twins with their English pages in the same-page manifest.

Proof strings (scope/evidenceRef) come verbatim from locales/ar2-pairing-evidence.json,
written by the scrum non-author reviewer. Hashes are computed from the built pages at
build time so nav/body re-routes (PR #749) reseal automatically instead of going stale.
Rows prove structural parity only: nativeReviewStatus stays not-certified.
"""
import hashlib,json,re
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest

EVIDENCE='locales/ar2-pairing-evidence.json'
AR2='scoped-ar2-variant'
# Pinned (slug, en, ar) pairs. Batch 1 (#750): 8 pairs. /feedback and /submit-testimony are
# noindex, the control build skips them, so they stay unpaired (todo-01M4R14M4SBH49AFECW3MEW5H9).
# Batch 2: 15 legacy twins, scope ar-legacy-twin-scripted-parity.
AR2_PAIRS=[('gallery','/gallery','/ar/gallery'),('saints','/saints','/ar/saints'),
 ('prayer-library','/prayer-library','/ar/prayer-library'),('encyclopedia','/saint-charbel-encyclopedia','/ar/encyclopedia'),
 ('news','/news','/ar/news'),('videos','/videos','/ar/videos'),('testimonies','/testimonies','/ar/testimonies'),
 ('voice-testimony','/voice-testimony','/ar/voice-testimony'),
 ('home','/','/ar/'),('feast-day','/saint-charbel-feast-day','/ar/feast-day'),
 ('litany','/litany-of-saint-charbel','/ar/litany-of-saint-charbel'),
 ('chaplet','/saint-charbel-chaplet','/ar/saint-charbel-chaplet'),
 ('eucharistic-hub','/miracles/eucharistic/','/ar/miracles/eucharistic/')]+[
 ('eucharistic-'+n,'/miracles/eucharistic/'+n,'/ar/miracles/eucharistic/'+n) for n in
 ('amsterdam','bolsena-orvieto','faverney','ivorra','lanciano','legnica','ludbreg','santarem','siena','sokolka')]
AR2_AR_PATHS=[a for _,_,a in AR2_PAIRS]
AR2_EN_PATHS=[e for _,e,_ in AR2_PAIRS]

def route_file(root,route):
    if route=='/':return root/'index.html'
    if route.endswith('/'):return root/route.strip('/')/'index.html'
    return root/(route.strip('/')+'.html')

def ar2_manifest(root,texts,manifest):
    path=root/EVIDENCE
    if not path.exists():return manifest
    data=json.loads(path.read_text())
    rows=data['pages']
    revision=data.get('sourceRevision','')
    if not re.fullmatch(r'[0-9a-f]{40}',revision):
        raise ValueError('AR-2 evidence must pin a frozen 40-hex sourceRevision')
    out=json.loads(json.dumps(manifest))
    pinned={slug for slug,_,_ in AR2_PAIRS}
    missing=pinned-set(rows)
    if missing:raise ValueError('AR-2 evidence rows missing pinned twins: '+','.join(sorted(missing)))
    rows={k:v for k,v in rows.items() if k in pinned}
    expect={slug:(en,ar) for slug,en,ar in AR2_PAIRS}
    for slug,row in rows.items():
        if (row['en'],row['ar'])!=expect[slug]:
            raise ValueError('AR-2 evidence route outside the pinned lists: '+slug)
        en_file=route_file(root,row['en']);ar_file=route_file(root,row['ar'])
        en_text=texts.get(en_file) or en_file.read_text()
        ar_text=texts.get(ar_file) or ar_file.read_text()
        en_digest=digest(en_text);ar_digest=digest(ar_text)
        paths={row['en'],row['ar']}
        for key in list(out['pages']):
            entry=out['pages'][key]
            if any(v['path'] in paths for v in entry['variants'].values()):
                # Loud guard: only single-variant pending rows may be superseded;
                # never replace a verified family (scrum review, PR #750).
                vs=list(entry['variants'].values())
                if len(vs)!=1 or vs[0].get('status')!='pending':
                    raise ValueError('AR-2 pairing would replace a non-pending family: '+key)
                del out['pages'][key]
        page={'sourcePath':en_file.relative_to(root).as_posix(),'sourceRevision':revision,
              'sourceSha256':en_digest,'anchorIDs':{},'variants':{}}
        for code,text,route,dig,file in (('en',en_text,row['en'],en_digest,en_file),('ar',ar_text,row['ar'],ar_digest,ar_file)):
            soup=BeautifulSoup(text,'html.parser')
            for el in soup.main.select('[id]'):
                page['anchorIDs'].setdefault(el['id'],{})[code]=el['id']
            page['variants'][code]={'path':route,'aliases':[],'status':'verified','contentSha256':dig,'sourceSha256':en_digest,
                'proof':{'type':AR2,'state':'approved','scope':row['scope'],
                         'candidateFileSha256':hashlib.sha256(file.read_bytes()).hexdigest(),
                         'reviewedContentSha256':dig,'nativeReviewStatus':row['nativeReviewStatus'],
                         'evidenceRef':row['evidenceRef']}}
        out['pages']['ar2-'+slug+'-equivalence']=page
    return out
