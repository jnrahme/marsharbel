"""History-only candidate routing, pinned to reviewed catalog and rendered body bytes.
Rendered release approval is separate and must never be invented by this overlay.
"""
import hashlib,json
from bs4 import BeautifulSoup

def digest(text):
    soup=BeautifulSoup(text,'html.parser')
    return hashlib.sha256(str(soup.main).encode()).hexdigest()

def history_manifest(root,texts,manifest):
    path=root/'locales/history-equivalence.json'
    if not path.exists():return manifest
    review=json.loads(path.read_text())
    variants=review['variants']
    for code,v in variants.items():
        file=root/v['file']
        text=texts.get(file,file.read_text())
        if digest(text)!=v['bodySha256']:raise ValueError('History body changed after review: '+code)
        if code!='en' and hashlib.sha256((root/v['catalog']).read_bytes()).hexdigest()!=v['catalogSha256']:
            raise ValueError('History catalog changed after review: '+code)
    out=json.loads(json.dumps(manifest));paths={v['path']for v in variants.values()}
    for key in list(out['pages']):
        if any(v['path']in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
    page={'sourcePath':'history.html','sourceRevision':review['sourceRevision'],'sourceSha256':variants['en']['bodySha256'],'anchorIDs':{},'variants':{}}
    for code,v in variants.items():
        soup=BeautifulSoup(texts.get(root/v['file'],(root/v['file']).read_text()),'html.parser')
        for el in soup.main.select('[id]'):
            page['anchorIDs'].setdefault(el['id'],{})[code]=el['id']
        page['variants'][code]={'path':v['path'],'aliases':[],'status':'verified','contentSha256':v['bodySha256'],'sourceSha256':page['sourceSha256'],'proof':{'type':'reviewed-history-master','family':'history-master','catalogReview':hashlib.sha256(review['catalogReview'].encode()).hexdigest(),'renderedReviewStatus':review['renderedReviewStatus'],'renderedReview':hashlib.sha256(review['renderedReview'].encode()).hexdigest(),'reviewedContentSha256':v['bodySha256']}}
    out['pages']['history-master-equivalence']=page
    return out
