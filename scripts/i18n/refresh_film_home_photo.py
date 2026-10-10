"""Non-author executor adds exactly two contextual film-photo bindings (201->203)."""
import hashlib,json,subprocess
from pathlib import Path
from bs4 import BeautifulSoup,NavigableString
ROOT=Path(__file__).resolve().parents[2]
def outputs(root=ROOT):
 contract=json.loads((root/'locales/en/home-bindings.json').read_text());raw=(root/'index.html').read_bytes();soup=BeautifulSoup(raw,'html.parser')
 pack=json.loads((root/'locales/film-home-photo-translations.json').read_text())
 if pack.pop('status')!='agent-translated-native-not-certified':raise ValueError('Native status changed')
 if len(contract['bindings'])!=201:raise ValueError('Expected201 original bindings')
 bindings=[];moved=0
 for old in contract['bindings']:
  b=dict(old)
  if b['key'].startswith('home.latest-news.premiere.'):
   nodes=[n for n in soup.select('.home-news-lead--film *')for t in n.contents if isinstance(t,NavigableString)and ' '.join(str(t).split())==b['source']]
   if len(nodes)!=1:raise ValueError('Cannot relocate '+b['key'])
   from i18n.refresh_film_home_bindings import selector
   b['selector']=selector(nodes[0]);b['nodeIndex']=next(i for i,t in enumerate(nodes[0].contents)if isinstance(t,NavigableString)and ' '.join(str(t).split())==b['source']);moved+=b!=old
  else:
   nodes=soup.select(b['selector'])
   if len(nodes)!=1:raise ValueError('Other selector drift '+b['key'])
   n=nodes[0];v=n.get(b['attribute'])if b['kind']=='attribute'else ' '.join(str(n.contents[b['nodeIndex']]).split())
   if v!=b['source']:raise ValueError('Other source drift '+b['key'])
  bindings.append(b)
 from i18n.refresh_film_home_bindings import selector
 for name,node,kind in [('photoAlt',soup.select_one('.home-news-lead--film img'),'attribute'),('photoCaption',soup.select_one('.home-news-lead--film .home-news-copy > .home-news-credit'),'text')]:
  value=pack['en'][0 if name=='photoAlt'else 1]
  if (node.get('alt')if kind=='attribute'else node.get_text())!=value:raise ValueError('Photo text mismatch')
  b={'key':'home.latest-news.premiere.'+name,'selector':selector(node),'source':value,'kind':kind};b.update({'attribute':'alt'}if kind=='attribute'else {'nodeIndex':0});bindings.append(b)
 if len(bindings)!=203 or moved!=7:raise ValueError('Unexpected photo delta')
 result={};keys=None
 for code,values in pack.items():
  p=root/f'locales/{code}/home-copy.json';j=json.loads(p.read_text())
  if keys is None:keys=set(j)
  if set(j)!=keys or len(values)!=2 or not all(isinstance(v,str)and v.strip() for v in values):raise ValueError('Catalog mismatch '+code)
  j.update({'home.latest-news.premiere.photoAlt':values[0],'home.latest-news.premiere.photoCaption':values[1]});result[p]=j
 contract.update(bindings=bindings,messages=result[root/'locales/en/home-copy.json'],masterSha256=hashlib.sha256(raw).hexdigest(),sourceRevision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip());result[root/'locales/en/home-bindings.json']=contract
 return {p:json.dumps(j,ensure_ascii=False,indent=2)+'\n'for p,j in result.items()}
if __name__=='__main__':
 for p,t in outputs().items():p.write_text(t)
 print('203bindings; +2photo keys;7existing premiere selector moves;11catalogs exact parity; native-not-certified')
