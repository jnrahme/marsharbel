"""Stories-only routing from the accepted isolated review; release remains separate."""
import hashlib
import json
from bs4 import BeautifulSoup
from i18n.reviewed_history import digest

CODES = ('en','ar','fr','es','pt','it','de','pl','ru','hi','th','zh-Hans')

def stories_manifest(root, texts, manifest):
    path = root/'locales/stories-equivalence.json'
    if not path.exists():
        return manifest
    if hashlib.sha256(path.read_bytes()).hexdigest() != '1548b0d229445fadd59b725da7d98e6e9e338b23d11dce9cfaaae8112ad02e6a':
        raise ValueError('Stories accepted evidence table edited')
    record = json.loads(path.read_text())
    if record['reviewStatus'] != 'isolated-review-pass':
        raise ValueError('Stories isolated review not accepted')
    expected_files = {'templates/masters/stories.html','locales/en/stories-master-bindings.json'}
    expected_files.update('locales/'+code+'/stories-master-copy.json' for code in CODES)
    expected_files.update('locales/'+code+'/stories-master-schema-bindings.json' for code in CODES if code != 'en')
    if set(record['sourceFiles']) != expected_files:
        raise ValueError('Stories accepted source inventory incomplete')
    if record['masterSha256'] != 'd8f15f97cd12c8f79d546a9e1d9b903de46635ec3e4277b67d9110394ebd1c13':
        raise ValueError('Stories accepted master pin differs')
    if record['verdictSha256'] != 'f5e57850e83cdf936e0c981fe6896ca49cea59b7df5aff6e405515fd2ddde304':
        raise ValueError('Stories accepted verdict pin differs')
    for name, expected in record['sourceFiles'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Stories accepted source drift: '+name)
    variants = record['variants']
    if set(variants) != set(CODES):
        raise ValueError('Stories requires all twelve routes together')
    out = json.loads(json.dumps(manifest))
    page = {'sourcePath':'stories.html','sourceRevision':record['sourceRevision'],
            'sourceSha256':variants['en']['bodySha256'],'anchorIDs':{},'variants':{}}
    for code in CODES:
        v = variants[code]
        route = '/stories' if code == 'en' else '/'+code+'/stories'
        if v['path'] != route or v['file'] != route.lstrip('/')+'.html':
            raise ValueError('Stories route identity drift: '+code)
        file = root/v['file']
        text = texts.get(file)
        if text is None:
            text = file.read_text()
        if digest(text) != v['bodySha256']:
            raise ValueError('Stories accepted body drift: '+code)
        soup = BeautifulSoup(text,'html.parser')
        for el in soup.main.select('[id]'):
            page['anchorIDs'].setdefault(el['id'],{})[code] = el['id']
        page['variants'][code] = {'path':route,'aliases':[],'status':'verified',
            'contentSha256':v['bodySha256'],'sourceSha256':page['sourceSha256'],
            'proof':{'type':'scoped-stories-variant','state':'isolated-review-pass',
                     'nativeReviewStatus':'not-certified','reviewedContentSha256':v['bodySha256'],
                     'evidenceSha256':record['verdictSha256'],'masterSha256':record['masterSha256']}}
    paths = {v['path'] for v in variants.values()}
    for key in list(out['pages']):
        if any(v['path'] in paths for v in out['pages'][key]['variants'].values()):
            del out['pages'][key]
    out['pages']['stories-master-equivalence'] = page
    return out
