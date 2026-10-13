"""Rebind only reviewed Saint-of-the-Day copy; preserve every other home source."""
import argparse,hashlib,json,sys
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup,NavigableString
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from i18n.refresh_film_home_bindings import selector

def outputs(root=ROOT):
 contract=json.loads((root/'locales/en/home-bindings.json').read_text())
 raw=(root/'index.html').read_bytes(); soup=BeautifulSoup(raw,'html.parser')
 section=soup.select_one('#saint-of-the-day')
 if section is None:raise ValueError('Saint unit absent')
 # Existing selectors describe the pre-insertion tree. Resolve them without
 # the new sibling, then restore it before calculating current selectors.
 following=section.next_sibling; parent=section.parent
 already=any(b["key"].startswith("home.saintDay.") for b in contract["bindings"])
 if not already:section.extract()
 preserved=[]
 for old in contract['bindings']:
  if old['key'].startswith('home.saintDay.'):continue
  nodes=soup.select(old['selector'])
  if len(nodes)!=1:raise ValueError('Old binding ambiguous '+old['key'])
  n=nodes[0];value=n.get(old['attribute']) if old['kind']=='attribute' else ' '.join(str(n.contents[old['nodeIndex']]).split())
  if value!=old['source']:raise ValueError('Unrelated home source changed '+old['key'])
  preserved.append((dict(old),n))
 if not already:
  if following:following.insert_before(section)
  else:parent.append(section)
 bindings=[]
 for b,n in preserved:b['selector']=selector(n);bindings.append(b)
 copy=json.loads((root/'locales/en/home-copy.json').read_text())
 for k in list(copy):
  if k.startswith('home.saintDay.'):del copy[k]
 messages=json.loads((root/'locales/en/saint-of-day.json').read_text())
 from datetime import date
 manifest=json.loads((root/'locales/saint-of-day.json').read_text())
 messages['dateLabel']=date.fromisoformat(manifest['activeDate']).strftime('%d.%m.%Y')
 for n in section.select('[data-saint-key],[data-saint-alt],[data-saint-generated-date]'):
  attr='alt' if n.has_attr('data-saint-alt') else None
  name=n.get('data-saint-alt') or n.get('data-saint-key') or n['data-saint-generated-date'];key='home.saintDay.'+name
  value=n[attr] if attr else n.get_text()
  if value!=messages[name]:raise ValueError('Saint source mismatch '+name)
  b={'key':key,'selector':selector(n),'source':value,'kind':'attribute' if attr else 'text'}
  if attr:b['attribute']=attr
  else:b['nodeIndex']=0
  bindings.append(b);copy[key]=value
 result={root/'locales/en/home-copy.json':copy}
 for lang in json.loads((root/'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
  local=json.loads((root/f'locales/{lang}/home-copy.json').read_text());pack=json.loads((root/f'locales/{lang}/saint-of-day.json').read_text());pack['dateLabel']=messages['dateLabel']
  for key in messages:local['home.saintDay.'+key]=pack[key]
  if set(local)!=set(copy):raise ValueError('Locale home keys differ '+lang)
  result[root/f'locales/{lang}/home-copy.json']=local
 contract.update(bindings=bindings,messages=copy,masterSha256=hashlib.sha256(raw).hexdigest())
 result[root/'locales/en/home-bindings.json']=contract
 result[root/'locales/en/saint-of-day-copy.json']={'values':{'index.html':dict(Counter(messages.values()))}}
 return {p:json.dumps(j,ensure_ascii=False,indent=2)+'\n' for p,j in result.items()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for path,text in outputs().items():
  if a.check:
   if path.read_text()!=text:raise SystemExit('Saint home bindings stale')
  else:path.write_text(text)
 print('Saint home bindings checked' if a.check else 'Saint home bindings refreshed')
