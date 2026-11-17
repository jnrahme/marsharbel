import json,re,sys,hashlib,argparse
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.refresh_almoner_oct30_home import selector,text_candidates,common_suffix
from i18n.keyed_master import strip_static_fallback

def outputs(root=ROOT):
    pack=json.loads((root/'locales/paris-statue-nov15-intake.json').read_text())
    registry=json.loads((root/'locales/registry.json').read_text())
    if registry['pageMirrors']['news-master']['renderLocales']!=['ar']:raise ValueError('Archive scope changed')
    codes=registry['homepageMirrors']['renderLocales']
    if set(codes)!={'ar','fr','es','pt','it','de','pl','ru','hi','th'}:raise ValueError('Home scope changed')
    result={}
    for family,page,prefix,section in [('news-master','news.html','news.paris-statue.','archive'),('home','index.html','home.paris-statue.','home')]:
        raw=(root/page).read_bytes();soup=BeautifulSoup(raw,'html.parser')
        con=json.loads((root/f'locales/en/{family}-bindings.json').read_text())
        en=json.loads((root/f'locales/en/{family}-copy.json').read_text())
        applied=prefix+'title' in en
        bindings=[]
        for old in con['bindings']:
            if old['key'].startswith(prefix) or old['selector'].startswith('#credit-'+pack['id']):continue
            b=dict(old)
            if family=='home' and b['selector'].startswith('#latest-news'):
                if b['kind']=='attribute':cands=[(n,None) for n in soup.select('#latest-news ['+b['attribute']+']') if n.get(b['attribute'])==b['source']]
                else:cands=text_candidates(soup,b['source'])
                cands.sort(key=lambda c:common_suffix(b['selector'],selector(c[0])),reverse=True)
                if not cands or len(cands)>1 and common_suffix(b['selector'],selector(cands[0][0]))==common_suffix(b['selector'],selector(cands[1][0])):raise ValueError('Ambiguous home survivor '+b['key'])
                n,idx=cands[0];b['selector']=selector(n)
                if idx is not None:b['nodeIndex']=idx
            elif family=='news-master' and not applied:
                # Adding a first November row shifts only existing rows in that first list.
                ul='#main-content > section:nth-of-type(3) > div:nth-of-type(1) > ul:nth-of-type(1) > li:nth-of-type('
                if b['selector'].startswith(ul):
                    b['selector']=re.sub(r'^(.*? > ul:nth-of-type\(1\) > li:nth-of-type\()(\d+)(\))',lambda m:m[1]+str(int(m[2])+1)+m[3],b['selector'])
            bindings.append(b)
        id=pack['id'];row=soup.select_one('#'+id) if section=='archive' else soup.select_one('a[href="./news#'+id+'"]')
        fields=[('title','.news-row-title a'),('summary','.news-row-summary'),('date','time'),('chip','.chip')] if section=='archive' else [('date','.home-news-meta'),('title','.home-news-title'),('credit','.home-news-credit')]
        additions=[]
        for field,css in fields:additions.append((field,row.select_one(css)))
        if section=='archive':
            credit=soup.select_one('#credit-'+id)
            additions += [('title',credit.select_one('.news-credit-title')),('source',credit.select_one('a'))]
            old_label=next(b for b in con['bindings'] if b['source']=='Source:')
            bindings.append({'key':old_label['key'],'selector':selector(credit.select_one('.news-credit-label')),'source':'Source:','kind':'text','nodeIndex':0})
        for field,node in additions:
            value=pack[section]['en'][field]
            if node is None or node.get_text(' ',strip=True)!=value:raise ValueError('New field mismatch '+field)
            key=prefix+field;en[key]=value
            bindings.append({'key':key,'selector':selector(node),'source':value,'kind':'text','nodeIndex':0})
        for b in bindings:
            nodes=soup.select(b['selector'])
            if len(nodes)!=1:raise ValueError('Selector not unique '+b['key']+' '+b['selector'])
            n=nodes[0];value=n.get(b['attribute']) if b['kind']=='attribute' else ' '.join(str(n.contents[b['nodeIndex']]).split())
            if value!=b['source']:raise ValueError('Survivor source drift '+b['key'])
        con.update(bindings=bindings,messages=en,masterSha256=hashlib.sha256(strip_static_fallback(raw) if family=='news-master' else raw).hexdigest())
        result[root/f'locales/en/{family}-bindings.json']=con;result[root/f'locales/en/{family}-copy.json']=en
        for code in ['ar'] if section=='archive' else codes:
            p=root/f'locales/{code}/{family}-copy.json';cat=json.loads(p.read_text())
            for field,_ in additions:cat[prefix+field]=pack[section][code][field]
            if set(cat)!=set(en):raise ValueError('Locale keys differ '+code)
            result[p]=cat
    return {p:json.dumps(v,ensure_ascii=False,indent=2)+'\n' for p,v in result.items()}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
    for p,text in outputs().items():
        if a.check:
            if p.read_text()!=text:raise SystemExit('Stale '+str(p))
        else:p.write_text(text)
    print('Paris bindings checked' if a.check else 'Paris bindings built')
