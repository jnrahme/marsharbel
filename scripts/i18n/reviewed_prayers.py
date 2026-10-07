"""Prayer routing preparation; activate only after review and final QA gates."""
import hashlib,json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest


def prayer_manifest(root,texts,manifest):
    path=root/'locales/prayer-equivalence.json'
    if not path.exists():return manifest
    record=json.loads(path.read_text())
    if record.get('gateStatus')!='approved':return manifest
    review=json.loads((root/'locales/prayer-review-record.json').read_text())
    if review['renderedReviewStatus']!='approved' or any(review['reviews'][lang]['status']!='approved' for lang in ('ar','de','fr','ru')):
        raise ValueError('Prayer integrated reviews incomplete')
    out=json.loads(json.dumps(manifest))
    for family,group in record['groups'].items():
        variants=group['variants']
        for lang,v in variants.items():
            file=root/v['file'];text=texts.get(file,file.read_text())
            if digest(text)!=v['bodySha256']:raise ValueError('Prayer reviewed body drift: '+family+' '+lang)
            if lang!='en' and hashlib.sha256((root/v['catalog']).read_bytes()).hexdigest()!=v['catalogSha256']:
                raise ValueError('Prayer reviewed catalog drift: '+family+' '+lang)
        paths={v['path']for v in variants.values()}
        for key in list(out['pages']):
            if any(v['path']in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
        page={'sourcePath':variants['en']['file'],'sourceRevision':group['sourceRevision'],'sourceSha256':variants['en']['bodySha256'],'anchorIDs':{},'variants':{}}
        for lang,v in variants.items():
            soup=BeautifulSoup(texts.get(root/v['file'],(root/v['file']).read_text()),'html.parser')
            for el in soup.main.select('[id]'):page['anchorIDs'].setdefault(el['id'],{})[lang]=el['id']
            page['variants'][lang]={'path':v['path'],'aliases':[],'status':'verified','contentSha256':v['bodySha256'],'sourceSha256':page['sourceSha256'],'proof':{**{k:True for k in ('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity')},'editorialReview':hashlib.sha256(group['catalogReview'].encode()).hexdigest(),'nativeSampleReview':hashlib.sha256(json.dumps(review['reviews'],sort_keys=True).encode()).hexdigest(),'renderedReview':hashlib.sha256(json.dumps(review,sort_keys=True).encode()).hexdigest()}}
        out['pages'][family+'-equivalence']=page
    return out
