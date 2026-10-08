"""Optional reviewed Travel release overlay; absent records never enable routes."""
import hashlib,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest
from i18n.travel_metadata import travel_clusters

def release_manifest(root,texts,manifest):
    path=root/'locales/travel-release.json'
    if not path.exists():return manifest
    record=json.loads(path.read_text())
    if record.get('version')!=1 or record.get('status')!='approved' or not record.get('ownerEvidenceRefs'):
        raise ValueError('Travel release missing reviewed gate or owner evidence')
    if not re.fullmatch(r'[a-f0-9]{40}',record.get('reviewedHead','')) or not record.get('independentReviewRef'):
        raise ValueError('Travel release independent review missing')
    if record.get('nativeReviewStatus')!='pending-post-release' or record.get('nativeStatusAuthority')!='added-process-safety':
        raise ValueError('Travel release native status must be honest')
    clusters=travel_clusters(root,json.loads((root/'locales/registry.json').read_text()))
    if set(record['groups'])!=set(clusters):raise ValueError('Travel release requires complete14-route group')
    out=json.loads(json.dumps(manifest))
    for source,group in record['groups'].items():
        if not re.fullmatch(r'[a-f0-9]{40}',group.get('sourceRevision','')):raise ValueError('Travel release source revision invalid')
        if set(group['variants'])!={'en','de','zh-Hans'}:raise ValueError('Travel release exact locales required')
        for code,v in group['variants'].items():
            if v['path']!=clusters[source][code] or v['file']!=v['path'].lstrip('/')+'.html':raise ValueError('Travel release route mismatch')
            file=root/v['file'];text=texts[file] if file in texts else file.read_text()
            if digest(text)!=v['bodySha256']:raise ValueError('Travel release body drift')
            if code!='en' and not v.get('catalogs'):raise ValueError('Travel release catalog pins missing')
            for pin in v.get('catalogs',[]):
                if Path(pin['file']).is_absolute() or '..' in Path(pin['file']).parts:raise ValueError('Travel release unsafe catalog path')
                if hashlib.sha256((root/pin['file']).read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('Travel release catalog drift')
            if not all(v.get('checks',{}).get(k) is True for k in ('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity')):raise ValueError('Travel release equivalence incomplete')
            if not v.get('editorialReview') or not v.get('renderedReview') or not v.get('nativeFollowUp'):raise ValueError('Travel release evidence missing')
        # Preserve already-reviewed other languages in established families.
        existing=next((p for p in out['pages'].values() if p.get('sourcePath')==source.lstrip('/')+'.html' and 'en' in p['variants']),None)
        page=json.loads(json.dumps(existing)) if existing else {'sourcePath':source.lstrip('/')+'.html','sourceRevision':group['sourceRevision'],'sourceSha256':group['variants']['en']['bodySha256'],'anchorIDs':{},'variants':{}}
        if page['sourceSha256']!=group['variants']['en']['bodySha256']:raise ValueError('Travel release source drift')
        paths={v['path'] for v in group['variants'].values()}
        for key in list(out['pages']):
            if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
        for code,v in group['variants'].items():
            text=texts.get(root/v['file']) or (root/v['file']).read_text();soup=BeautifulSoup(text,'html.parser')
            for el in soup.main.select('[id]'):page['anchorIDs'].setdefault(el['id'],{})[code]=el['id']
            page['variants'][code]={'path':v['path'],'aliases':[],'status':'verified','sourceSha256':page['sourceSha256'],'contentSha256':v['bodySha256'],'proof':{'type':'reviewed-travel-release','reviewedContentSha256':v['bodySha256'],'contentReviewMode':'model-only','nativeReviewStatus':record['nativeReviewStatus'],'nativeFollowUp':v['nativeFollowUp'],'editorialReview':v['editorialReview'],'renderedReview':v['renderedReview'],**v['checks']}}
        out['pages']['travel-release-'+source.strip('/')]=page
    return out
