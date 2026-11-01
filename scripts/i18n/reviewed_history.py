"""History-only candidate routing, pinned to reviewed catalog and rendered body bytes.
Rendered release approval is separate and must never be invented by this overlay.
"""
import hashlib,json
from i18n import citation_amendment
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
        text=texts[file] if file in texts else file.read_text()
        if digest(text)!=citation_amendment.effective_body(root,'history-master',code,v['bodySha256']):raise ValueError('History body changed after review: '+code)
        if code!='en' and hashlib.sha256((root/v['catalog']).read_bytes()).hexdigest()!=citation_amendment.effective_catalog(root,'history-master',code,v['catalogSha256']):
            raise ValueError('History catalog changed after review: '+code)
    mode=citation_amendment.proof_mode(root)
    out=json.loads(json.dumps(manifest));paths={v['path']for v in variants.values()}
    for key in list(out['pages']):
        if any(v['path']in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
    page={'sourcePath':'history.html','sourceRevision':review['sourceRevision'],'sourceSha256':citation_amendment.effective_body(root,'history-master','en',variants['en']['bodySha256']),'anchorIDs':{},'variants':{}}
    for code,v in variants.items():
        soup=BeautifulSoup(texts[root/v['file']] if root/v['file'] in texts else (root/v['file']).read_text(),'html.parser')
        for el in soup.main.select('[id]'):
            page['anchorIDs'].setdefault(el['id'],{})[code]=el['id']
        eff=citation_amendment.effective_body(root,'history-master',code,v['bodySha256'])
        if mode!='git':
            # Editable export: reviewed/verified vocabulary is withheld; the resolver
            # cannot resolve this variant as reviewed (trust-boundary propagation).
            page['variants'][code]=citation_amendment.export_variant(v['path'],eff,page['sourceSha256'])
        else:
            page['variants'][code]={'path':v['path'],'aliases':[],'status':v.get('status','verified'),'contentSha256':eff,'sourceSha256':page['sourceSha256'],'proof':{'type':'reviewed-history-master','family':'history-master','catalogReview':hashlib.sha256(review['catalogReview'].encode()).hexdigest(),'renderedReviewStatus':v.get('renderedReviewStatus',review['renderedReviewStatus']),'renderedReview':hashlib.sha256(v.get('renderedReview',review['renderedReview']).encode()).hexdigest(),'reviewedContentSha256':eff}}
        add=citation_amendment.addendum(root,'history-master',code,eff)
        if add:page['variants'][code]['proof']['citationAmendment']=add
    out['pages']['history-master-equivalence']=page
    return out
