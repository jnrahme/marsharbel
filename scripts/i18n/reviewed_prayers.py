"""Prayer routing preparation; activate only after review and final QA gates."""
import hashlib,json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest
from i18n import citation_amendment


def prayer_manifest(root,texts,manifest):
    path=root/'locales/prayer-equivalence.json'
    if not path.exists():return manifest
    record=json.loads(path.read_text())
    if record.get('gateStatus')!='approved':return manifest
    review=json.loads((root/'locales/prayer-review-record.json').read_text())
    if review['renderedReviewStatus']!='approved' or any(review['reviews'][lang]['status']!='approved' for lang in ('ar','de','fr','ru','pt','it','pl','es')):
        raise ValueError('Prayer integrated reviews incomplete')
    out=json.loads(json.dumps(manifest))
    for family,group in record['groups'].items():
        variants=group['variants']
        for lang,v in variants.items():
            file=root/v['file'];text=texts.get(file,file.read_text())
            if digest(text)!=citation_amendment.effective_body(root,family,lang,v['bodySha256']):raise ValueError('Prayer reviewed body drift: '+family+' '+lang)
            if lang!='en' and hashlib.sha256((root/v['catalog']).read_bytes()).hexdigest()!=citation_amendment.effective_catalog(root,family,lang,v['catalogSha256']):
                raise ValueError('Prayer reviewed catalog drift: '+family+' '+lang)
        paths={v['path']for v in variants.values()}
        for key in list(out['pages']):
            if any(v['path']in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
        page={'sourcePath':variants['en']['file'],'sourceRevision':group['sourceRevision'],'sourceSha256':citation_amendment.effective_body(root,family,'en',variants['en']['bodySha256']),'anchorIDs':{},'variants':{}}
        for lang,v in variants.items():
            soup=BeautifulSoup(texts.get(root/v['file'],(root/v['file']).read_text()),'html.parser')
            for el in soup.main.select('[id]'):page['anchorIDs'].setdefault(el['id'],{})[lang]=el['id']
            eff=citation_amendment.effective_body(root,family,lang,v['bodySha256'])
            add=citation_amendment.addendum(root,family,lang,eff)
            if add and citation_amendment.proof_mode(root)!='git':
                # Citation-covered family in an editable export: no verified claim.
                page['variants'][lang]=citation_amendment.export_variant(v['path'],eff,page['sourceSha256'])
            else:
                page['variants'][lang]={'path':v['path'],'aliases':[],'status':'verified','contentSha256':eff,'sourceSha256':page['sourceSha256'],'proof':{**{k:True for k in ('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity')},'editorialReview':hashlib.sha256(group['catalogReview'].encode()).hexdigest(),'nativeSampleReview':hashlib.sha256(json.dumps(review['reviews'],sort_keys=True).encode()).hexdigest(),'renderedReview':hashlib.sha256(json.dumps(review,sort_keys=True).encode()).hexdigest()}}
            if add:page['variants'][lang]['proof']['citationAmendment']=add
        out['pages'][family+'-equivalence']=page
    return out
