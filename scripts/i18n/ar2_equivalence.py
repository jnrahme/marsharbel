"""Pair AR-2 hand-authored Arabic twins with their English pages in the same-page manifest.

Proof strings (scope/evidenceRef) come verbatim from locales/ar2-pairing-evidence.json,
written by the scrum non-author reviewer. Hashes are computed from the built pages at
build time so nav/body re-routes (PR #749) reseal automatically instead of going stale.
Rows prove structural parity only: nativeReviewStatus stays not-certified.
"""
import hashlib,json,subprocess
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest

EVIDENCE='locales/ar2-pairing-evidence.json'
AR2='scoped-ar2-variant'
# /feedback and /submit-testimony are noindex: the control build skips them, so they can
# never render the switcher. Scrum ruling 2026-10-12: exactly these 8 pairs; the two
# noindex pages stay out until the noindex coverage decision (todo-01M4R14M4SBH49AFECW3MEW5H9).
AR2_AR_PATHS=['/ar/gallery','/ar/saints','/ar/prayer-library','/ar/encyclopedia','/ar/news',
              '/ar/videos','/ar/testimonies','/ar/voice-testimony']
AR2_EN_PATHS=['/gallery','/saints','/prayer-library','/saint-charbel-encyclopedia','/news',
              '/videos','/testimonies','/voice-testimony']

def ar2_manifest(root,texts,manifest):
    path=root/EVIDENCE
    if not path.exists():return manifest
    rows=json.loads(path.read_text())['pages']
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    out=json.loads(json.dumps(manifest))
    pinned={s.split('/')[-1] for s in AR2_AR_PATHS}
    missing=pinned-set(rows)
    if missing:raise ValueError('AR-2 evidence rows missing pinned twins: '+','.join(sorted(missing)))
    rows={k:v for k,v in rows.items() if k in pinned}
    for slug,row in rows.items():
        if row['ar'] not in AR2_AR_PATHS or row['en'] not in AR2_EN_PATHS:
            raise ValueError('AR-2 evidence route outside the pinned lists: '+slug)
        en_file=root/(row['en'].strip('/')+'.html');ar_file=root/(row['ar'].strip('/')+'.html')
        en_text=texts.get(en_file) or en_file.read_text()
        ar_text=texts.get(ar_file) or ar_file.read_text()
        en_digest=digest(en_text);ar_digest=digest(ar_text)
        paths={row['en'],row['ar']}
        for key in list(out['pages']):
            if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
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
