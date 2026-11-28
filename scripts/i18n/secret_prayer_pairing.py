"""Exact technical pairing for four new prayer families, not language certification."""
import hashlib,json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest
FAMILIES=('powerful-secret-prayers','mary-who-goes-ahead-prayer','lebanese-mountain-prayers','terco-da-batalha')
LANGUAGES=('en','ar','fr')

def secret_prayer_manifest(root,texts,manifest):
    record_path=root/'locales/secret-prayer-technical-pairing.json'
    if not record_path.exists():return manifest
    import sys
    sys.path.insert(0,str(root/'scripts/qa'))
    from secret_prayers_ar_fr_policy import load
    if load(root) is None:raise ValueError('Secret pairing requires finite release record')
    record=json.loads(record_path.read_text())
    if record.get('scope')!='four-secret-prayer-families-en-ar-fr-technical-only' or set(record.get('families',{}))!=set(FAMILIES):
        raise ValueError('Secret prayer pairing scope mismatch')
    out=json.loads(json.dumps(manifest))
    for slug,group in record['families'].items():
        if set(group['variants'])!=set(LANGUAGES):raise ValueError('Secret prayer locale coverage mismatch')
        paths=set()
        for code,v in group['variants'].items():
            route='/'+('' if code=='en' else code+'/')+slug
            if v['path']!=route or v['file']!=route.lstrip('/')+'.html':raise ValueError('Secret prayer route mismatch')
            file=root/v['file'];text=texts[file] if file in texts else file.read_text()
            soup=BeautifulSoup(text,'html.parser')
            if not soup.main or soup.html.get('lang')!=code or soup.select_one('link[rel=canonical]')['href']!='https://marsharbel.com'+route:
                raise ValueError('Secret prayer page identity mismatch')
            if digest(text)!=v['bodySha256']:raise ValueError('Secret prayer body drift: '+route)
            for field in ('catalog','bindings'):
                if hashlib.sha256((root/v[field]).read_bytes()).hexdigest()!=v[field+'Sha256']:raise ValueError('Secret prayer '+field+' drift: '+route)
            paths.add(route)
        for key in list(out['pages']):
            if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):
                if any(v.get('status')!='pending' for v in out['pages'][key]['variants'].values()):raise ValueError('Secret prayer replaces reviewed identity')
                del out['pages'][key]
        source=group['variants']['en']['bodySha256']
        page={'sourcePath':slug+'.html','sourceRevision':record['sourceRevision'],'sourceSha256':source,'anchorIDs':{},'variants':{}}
        for code,v in group['variants'].items():
            page['variants'][code]={'path':v['path'],'aliases':[],'status':'technically-paired','sourceSha256':source,'contentSha256':v['bodySha256'],'proof':{'type':'secret-prayer-technical-pairing','scope':'four-secret-prayer-families-en-ar-fr-technical-only','nativeReviewStatus':'not-certified','editorialReviewStatus':'not-certified','bodySha256':v['bodySha256'],'catalogSha256':v['catalogSha256'],'bindingsSha256':v['bindingsSha256']}}
        out['pages']['secret-prayer-'+slug]=page
    return out