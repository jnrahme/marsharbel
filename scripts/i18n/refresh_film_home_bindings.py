"""Precisely refresh existing home news bindings on the film v2 candidate.
Executor only: python3 scripts/i18n/refresh_film_home_bindings.py [--check]
Never blanket-regenerates reviewed bindings or changes other source values.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from bs4 import BeautifulSoup,NavigableString
ROOT=Path(__file__).resolve().parents[2]
NEW=('shortTitle','homeDek','premiereLabel','premiereValue','openingLabel','openingValue','read')
LOCALES=('ar','fr','es','pt','it','de','pl','ru','hi','th')
REMOVE={
 'home.latest-news.december-2025',
 'home.latest-news.charbel-the-movie-what-is-confirmed-about-the-new',
 'home.latest-news.official-poster-mtv-nmpro',
 'home.accessibility.official-poster-for-charbel-the-movie-mtv-nmpro',
 'home.latest-news.pilgrims-walked-from-byblos-to-saint-charbel-s-shrine',
}

def selector(node):
 parts=[]
 while node.name!='[document]':
  if node.get('id'):parts.append('#'+node['id']);break
  siblings=node.parent.find_all(node.name,recursive=False)
  parts.append(node.name+':nth-of-type('+str(next(i for i,s in enumerate(siblings) if s is node)+1)+')');node=node.parent
 return ' > '.join(reversed(parts))

def outputs(root=ROOT):
 p=root/'locales/en/home-bindings.json';contract=json.loads(p.read_text());copy=json.loads((root/'locales/en/home-copy.json').read_text());raw=(root/'index.html').read_bytes();soup=BeautifulSoup(raw,'html.parser')
 if len(contract['bindings'])==201:
  if contract['masterSha256']!=hashlib.sha256(raw).hexdigest() or REMOVE & set(copy):raise ValueError('Refreshed contract source drift')
  for b in contract['bindings']:
   nodes=soup.select(b['selector'])
   if len(nodes)!=1:raise ValueError('Refreshed selector drift '+b['key'])
   n=nodes[0];value=n.get(b['attribute']) if b['kind']=='attribute' else ' '.join(str(n.contents[b['nodeIndex']]).split())
   if value!=b['source']:raise ValueError('Refreshed source drift '+b['key'])
  if not {'home.latest-news.premiere.'+k for k in NEW}<=set(copy):raise ValueError('Missing premiere keys')
  result={p:contract,root/'locales/en/home-copy.json':copy}
  for code in LOCALES:
   path=root/f'locales/{code}/home-copy.json';catalog=json.loads(path.read_text())
   if set(catalog)!=set(copy):raise ValueError('Refreshed locale key drift '+code)
   result[path]=catalog
  return {path:json.dumps(data,ensure_ascii=False,indent=2)+'\n' for path,data in result.items()}
 if len(contract['bindings'])!=199 or not REMOVE<=set(copy):raise ValueError('Expected original199-binding home contract')
 news=json.loads((root/'locales/en/news-desk.json').read_text());pack=json.loads((root/'locales/film-home-translations.json').read_text())
 if pack['status']!='agent-translated-native-not-certified' or tuple(pack['keys'])!=NEW or set(pack['locales'])!=set(LOCALES):raise ValueError('Unexpected translation pack')
 bindings=[];moved=[];unchanged=0
 for old in contract['bindings']:
  if old['key'] in REMOVE:continue
  b=dict(old)
  if b['selector'].startswith('#latest-news'):
   candidates=[]
   for node in soup.select('#latest-news [alt]') if b['kind']=='attribute' else soup.select('#latest-news *'):
    if b['kind']=='attribute':
     if node.get(b['attribute'])==b['source']:candidates.append((node,None))
    else:
     for i,t in enumerate(node.contents):
      if isinstance(t,NavigableString) and ' '.join(str(t).split())==b['source']:candidates.append((node,i))
   if len(candidates)!=1:raise ValueError('Cannot map exact surviving news binding '+b['key'])
   node,index=candidates[0];b['selector']=selector(node)
   if index is not None:b['nodeIndex']=index
   if b!=old:moved.append(b['key'])
  else:
   nodes=soup.select(b['selector'])
   if len(nodes)!=1:raise ValueError('Unrelated binding selector changed '+b['key'])
   n=nodes[0];value=n.get(b['attribute']) if b['kind']=='attribute' else ' '.join(str(n.contents[b['nodeIndex']]).split())
   if value!=b['source']:raise ValueError('Unrelated source drift '+b['key'])
   unchanged+=1
  bindings.append(b)
 for name in NEW:
  source=news['premiere.'+name]+(' →' if name=='read' else '')
  nodes=[n for n in soup.select('.home-news-lead--film *') if len(n.contents)==1 and isinstance(n.contents[0],NavigableString) and ' '.join(str(n.contents[0]).split())==source]
  if len(nodes)!=1:raise ValueError('Cannot map premiere '+name)
  key='home.latest-news.premiere.'+name;bindings.append({'key':key,'selector':selector(nodes[0]),'source':source,'kind':'text','nodeIndex':0});copy[key]=source
 if len(bindings)!=201 or len(moved)!=20:raise ValueError('Unexpected binding/moved counts: '+str((len(bindings),len(moved))))
 for key in REMOVE:copy.pop(key)
 contract.update(bindings=bindings,messages=copy,masterSha256=hashlib.sha256(raw).hexdigest(),sourceRevision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip())
 result={p:contract,root/'locales/en/home-copy.json':copy}
 for code in LOCALES:
  path=root/f'locales/{code}/home-copy.json';catalog=json.loads(path.read_text())
  if set(catalog)!=set(json.loads((root/'locales/en/home-copy.json').read_text())):raise ValueError('Pre-existing key drift '+code)
  values=pack['locales'][code]
  if len(values)!=7 or any(not isinstance(v,str) or not v.strip() or re.search(r'<\s*/?\s*[A-Za-z!]',v) for v in values):raise ValueError('Invalid text '+code)
  for key in REMOVE:catalog.pop(key)
  for name,value in zip(NEW,values):catalog['home.latest-news.premiere.'+name]=value+(' →' if name=='read' else '')
  if set(catalog)!=set(copy):raise ValueError('Final key mismatch '+code)
  result[path]=catalog
 return {path:json.dumps(data,ensure_ascii=False,indent=2)+'\n' for path,data in result.items()}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 changes=outputs()
 for path,text in changes.items():
  if args.check:
   if path.read_text()!=text:raise SystemExit('Needs refresh: '+str(path))
  else:path.write_text(text)
 print('201 bindings: -5/+7;20 survivor selector moves;10 native-not-certified locale catalogs; no unrelated binding edits')
