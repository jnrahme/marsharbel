"""Rebind only reviewed Saint-of-the-Day copy; preserve every other home source."""
import argparse,hashlib,json,sys
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from i18n.refresh_film_home_bindings import selector

def outputs(root=ROOT):
 contract=json.loads((root/'locales/en/home-bindings.json').read_text())
 raw=(root/'index.html').read_bytes(); soup=BeautifulSoup(raw,'html.parser')
 manifest=json.loads((root/'locales/saint-of-day.json').read_text())
 dates=sorted(manifest['entries'])
 templates=soup.select('template[data-saint-date]')
 if sorted(t['data-saint-date'] for t in templates)!=dates:raise ValueError('Saint templates differ from manifest window')
 # Detach every saint template so old selectors validate against the tree
 # without them; no reviewed binding path crosses a template element.
 anchor_prev=templates[0].previous_sibling if templates else None
 anchor_parent=templates[0].parent if templates else None
 for t in templates:t.extract()
 preserved=[]
 for old in contract['bindings']:
  if old['key'].startswith('home.saintDay.'):continue
  nodes=soup.select(old['selector'])
  if len(nodes)!=1:raise ValueError('Old binding ambiguous '+old['key'])
  n=nodes[0];value=n.get(old['attribute']) if old['kind']=='attribute' else ' '.join(str(n.contents[old['nodeIndex']]).split())
  if value!=old['source']:raise ValueError('Unrelated home source changed '+old['key'])
  preserved.append((dict(old),n))
 for t in templates:
  if anchor_prev is not None:anchor_prev.insert_after(t);anchor_prev=t
  else:anchor_parent.append(t)
 bindings=[]
 for b,n in preserved:b['selector']=selector(n);bindings.append(b)
 copy=json.loads((root/'locales/en/home-copy.json').read_text())
 for k in list(copy):
  if k.startswith('home.saintDay.'):del copy[k]
 packs=json.loads((root/'locales/en/saint-of-day.json').read_text())
 if set(packs)!=set(dates):raise ValueError('English saint copy dates differ from manifest')
 from datetime import date as date_type
 all_values=[]
 for t in templates:
  d=t['data-saint-date']
  section=t.select_one('#saint-of-the-day')
  if section is None:raise ValueError('Saint unit absent '+d)
  messages=dict(packs[d]);messages['dateLabel']=date_type.fromisoformat(d).strftime('%d.%m.%Y')
  for n in section.select('[data-saint-key],[data-saint-alt],[data-saint-generated-date]'):
   attr='alt' if n.has_attr('data-saint-alt') else None
   name=n.get('data-saint-alt') or n.get('data-saint-key') or n['data-saint-generated-date'];key='home.saintDay.'+d+'.'+name
   value=n[attr] if attr else ''.join(str(c) for c in n.contents)
   if value!=messages[name]:raise ValueError('Saint source mismatch '+d+' '+name)
   b={'key':key,'selector':'template[data-saint-date="%s"] %s'%(d,selector(n)),'source':value,'kind':'attribute' if attr else 'text'}
   if attr:b['attribute']=attr
   else:b['nodeIndex']=0
   bindings.append(b);copy[key]=value
  all_values.extend(messages.values())
 result={root/'locales/en/home-copy.json':copy}
 for lang in json.loads((root/'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
  local=json.loads((root/f'locales/{lang}/home-copy.json').read_text());pack=json.loads((root/f'locales/{lang}/saint-of-day.json').read_text())
  if set(pack)!=set(dates):raise ValueError('Locale saint dates differ '+lang)
  for k in list(local):
   if k.startswith('home.saintDay.'):del local[k]
  for d in dates:
   messages=dict(pack[d]);messages['dateLabel']=date_type.fromisoformat(d).strftime('%d.%m.%Y')
   for key in messages:local['home.saintDay.'+d+'.'+key]=messages[key]
  if set(local)!=set(copy):raise ValueError('Locale home keys differ '+lang)
  result[root/f'locales/{lang}/home-copy.json']=local
 contract.update(bindings=bindings,messages=copy,masterSha256=hashlib.sha256(raw).hexdigest())
 result[root/'locales/en/home-bindings.json']=contract
 result[root/'locales/en/saint-of-day-copy.json']={'values':{'index.html':dict(Counter(all_values))}}
 return {p:json.dumps(j,ensure_ascii=False,indent=2)+'\n' for p,j in result.items()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for path,text in outputs().items():
  if a.check:
   if path.read_text()!=text:raise SystemExit('Saint home bindings stale')
  else:path.write_text(text)
 print('Saint home bindings checked' if a.check else 'Saint home bindings refreshed')
