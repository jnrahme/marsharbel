"""Build pending page identities. No structural match silently becomes verified."""
from pathlib import Path
import hashlib,json,subprocess,re
from bs4 import BeautifulSoup

def pending_manifest(root):
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    pages={};seen={}
    for file in sorted(root.rglob('*.html')):
        if any(part in {'node_modules','.git','src','templates','docs','test-results','playwright-report'} for part in file.relative_to(root).parts):continue
        soup=BeautifulSoup(file.read_text(),'html.parser')
        canonical=soup.select_one('link[rel=canonical]');robots=soup.select_one('meta[name=robots]')
        if not canonical or not soup.main or (robots and 'noindex' in robots.get('content','')):continue
        url=canonical.get('href','')
        if not url.startswith('https://marsharbel.com/'):continue
        path=url.removeprefix('https://marsharbel.com');lang=soup.html.get('lang','en')
        if lang not in ['en','ar','fr','es','pt','it','de','pl']:continue
        if path in seen:raise ValueError('Duplicate page identity '+path)
        seen[path]=file
        # Separate localized guide identity until a reviewed equivalence group is added.
        id='page-'+hashlib.sha256(path.encode()).hexdigest()[:16];digest=hashlib.sha256(file.read_bytes()).hexdigest()
        pages[id]={'sourceRevision':revision,'sourceSha256':digest,'sourcePath':file.relative_to(root).as_posix(),'anchorIDs':{},'variants':{lang:{'path':path,'status':'pending','contentSha256':digest,'sourceSha256':digest,'aliases':[],'proof':{}}}}
    return {'version':1,'languages':['en','ar','fr','es','pt','it','de','pl'],'aliases':{'en':'en','ar':'ar','fr':'fr','es':'es','pt':'pt','it':'it','de':'de','pl':'pl'},'pages':pages}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[2];m=pending_manifest(root)
    (root/'locales/same-page-manifest.pending.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print(len(m['pages']),'pending page identities; zero independent reviews invented')
