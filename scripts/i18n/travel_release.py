"""Optional reviewed Travel release overlay; absent records never enable routes."""
import hashlib,json,re,subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest
from i18n.travel_metadata import travel_clusters

RELEASE_LOCALES = ('en', 'de', 'zh-Hans', 'ru', 'pl')

CHECKS=('keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity')
def nonempty(value):return isinstance(value,str) and bool(value.strip())
def git_blob(root,revision,file):
    try:return subprocess.check_output(['git','show',revision+':'+file],cwd=root,stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:raise ValueError('Travel release git provenance missing') from exc

def catalog_paths(root,registry,source,code):
    family=next((name for name,cfg in registry['pageMirrors'].items() if cfg['english']==source and code in cfg.get('renderLocales',[])),None)
    if code=='en':
        families=[name for name,cfg in registry['pageMirrors'].items() if cfg['english']==source and any(c in cfg.get('renderLocales',[]) for c in RELEASE_LOCALES[1:])]
        return {p for name in families for p in ('locales/en/'+name+'-bindings.json','locales/en/'+name+'-copy.json')}
    if family is None:raise ValueError('Travel release registered family missing')
    paths={'locales/en/'+family+'-bindings.json','locales/'+code+'/'+family+'-copy.json'}
    schema='locales/'+code+'/'+family+'-schema-bindings.json'
    if (root/schema).exists():
        paths.add(schema)
        for b in json.loads((root/schema).read_text())['bindings']:
            if b.get('catalog'):paths.add('locales/'+code+'/'+b['catalog'])
    return paths

def release_manifest(root,texts,manifest):
    path=root/'locales/travel-release.json'
    if not path.exists():return manifest
    record=json.loads(path.read_text())
    if record.get('version')!=1 or record.get('status')!='approved' or not record.get('ownerEvidenceRefs'):
        raise ValueError('Travel release missing reviewed gate or owner evidence')
    refs=record.get('ownerEvidenceRefs')
    if not isinstance(refs,list) or not refs or any(not isinstance(x,dict) or set(x)!={'channel','messageID'} or x['channel'] not in ('WhatsApp','iMessage','agent_chat','mobile_chat') or not nonempty(x['messageID']) for x in refs):
        raise ValueError('Travel release typed owner evidence missing')
    if not re.fullmatch(r'[a-f0-9]{40}',record.get('reviewedHead','')) or not nonempty(record.get('independentReviewRef')):
        raise ValueError('Travel release independent review missing')
    if record.get('nativeReviewStatus')!='pending-post-release' or record.get('nativeStatusAuthority')!='added-process-safety':
        raise ValueError('Travel release native status must be honest')
    try:subprocess.run(['git','merge-base','--is-ancestor',record['reviewedHead'],'HEAD'],cwd=root,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:raise ValueError('Travel release reviewed head not in actual history') from exc
    registry=json.loads((root/'locales/registry.json').read_text())
    clusters=travel_clusters(root,registry)
    if set(record['groups'])!=set(clusters):raise ValueError('Travel release requires complete14-route group')
    out=json.loads(json.dumps(manifest))
    for source,group in record['groups'].items():
        if not re.fullmatch(r'[a-f0-9]{40}',group.get('sourceRevision','')):raise ValueError('Travel release source revision invalid')
        if digest(git_blob(root,group['sourceRevision'],source.strip('/')+'.html').decode())!=group['variants']['en']['bodySha256']:raise ValueError('Travel release revision source mismatch')
        if set(group['variants'])!=set(RELEASE_LOCALES):raise ValueError('Travel release exact locales required')
        for code,v in group['variants'].items():
            if v['path']!=clusters[source][code] or v['file']!=v['path'].lstrip('/')+'.html':raise ValueError('Travel release route mismatch')
            file=root/v['file'];text=texts[file] if file in texts else file.read_text()
            if digest(text)!=v['bodySha256']:raise ValueError('Travel release body drift')
            if digest(git_blob(root,record['reviewedHead'],v['file']).decode())!=v['bodySha256']:raise ValueError('Travel release reviewed head body mismatch')
            expected=catalog_paths(root,registry,source,code)
            if {pin['file'] for pin in v.get('catalogs',[])}!=expected or len(v.get('catalogs',[]))!=len(expected):raise ValueError('Travel release registered catalog pins mismatch')
            for pin in v.get('catalogs',[]):
                if Path(pin['file']).is_absolute() or '..' in Path(pin['file']).parts:raise ValueError('Travel release unsafe catalog path')
                if hashlib.sha256(git_blob(root,record['reviewedHead'],pin['file'])).hexdigest()!=pin['sha256']:raise ValueError('Travel release reviewed catalog mismatch')
                if hashlib.sha256((root/pin['file']).read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('Travel release catalog drift')
            if not isinstance(v.get('checks'),dict) or set(v['checks'])!=set(CHECKS) or not all(v['checks'][k] is True for k in CHECKS):raise ValueError('Travel release equivalence incomplete')
            if not all(nonempty(v.get(k)) for k in ('editorialReview','renderedReview','nativeFollowUp')):raise ValueError('Travel release evidence missing')
        # Preserve already-reviewed other languages in established families.
        candidates=[p for p in out['pages'].values() if p.get('sourcePath')==source.lstrip('/')+'.html' and any(code not in RELEASE_LOCALES and v.get('status')=='verified' for code,v in p.get('variants',{}).items())]
        if any(p['sourceSha256']!=group['variants']['en']['bodySha256'] for p in candidates):raise ValueError('Travel release reviewed other-locale source drift')
        if len(candidates)>1:raise ValueError('Travel release ambiguous reviewed family')
        existing=candidates[0] if candidates else None
        page=json.loads(json.dumps(existing)) if existing else {'sourcePath':source.lstrip('/')+'.html','sourceRevision':group['sourceRevision'],'sourceSha256':group['variants']['en']['bodySha256'],'anchorIDs':{},'variants':{}}
        if existing:page['variants']={code:v for code,v in page['variants'].items() if code in RELEASE_LOCALES or v.get('status')=='verified'}
        if page['sourceSha256']!=group['variants']['en']['bodySha256']:raise ValueError('Travel release source drift')
        paths={v['path'] for v in group['variants'].values()}
        for key in list(out['pages']):
            if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):del out['pages'][key]
        for code,v in group['variants'].items():
            text=texts.get(root/v['file']) or (root/v['file']).read_text();soup=BeautifulSoup(text,'html.parser')
            for el in soup.main.select('[id]'):page['anchorIDs'].setdefault(el['id'],{})[code]=el['id']
            page['variants'][code]={'path':v['path'],'aliases':[],'status':'verified','sourceSha256':page['sourceSha256'],'contentSha256':v['bodySha256'],'proof':{**{key:True for key in CHECKS},'type':'reviewed-travel-release','reviewedContentSha256':v['bodySha256'],'contentReviewMode':'model-only','nativeReviewStatus':record['nativeReviewStatus'],'nativeFollowUp':v['nativeFollowUp'],'editorialReview':v['editorialReview'],'renderedReview':v['renderedReview']}}
        out['pages']['travel-release-'+source.strip('/')]=page
    return out
