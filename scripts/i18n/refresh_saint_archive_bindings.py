"""Extend the archive keyed contract, preserving every prior keyed value."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.make_bindings import build
FAMILY='saint-of-the-day-master'
def refresh(root):
 import i18n.make_bindings as mb
 mb.ROOT=root
 path=root/f'locales/en/{FAMILY}-bindings.json';old=json.loads(path.read_text());new,_=build('saint-of-the-day.html',FAMILY,'saintDay')
 catalogs={p.parent.name:json.loads(p.read_text()) for p in root.glob(f'locales/*/{FAMILY}-copy.json')}
 result={l:dict(c) for l,c in catalogs.items()};history=json.loads((root/'locales/saint-day-archive.json').read_text());items={e['date']:e for e in history['entries']}
 def sig(b):return tuple(b.get(k) for k in ['selector','source','kind','nodeIndex','attribute'])
 existing={sig(b):b for b in old['bindings']}
 import re
 for b in new['bindings']:
  if sig(b) in existing:b['key']=existing[sig(b)]['key'];continue
  match=re.match(r'#saint-day-(\d{4}-\d{2}-\d{2}) > (.*)',b['selector'])
  if not match:raise ValueError('Unreviewed archive chrome changed: '+b['selector'])
  date,selector=match.groups();item=items[date]
  if 'copy' not in item:raise ValueError('Historical archive binding changed: '+date)
  if '> time:' in selector:field='date'
  elif '> span:' in selector:field='calendar'
  elif selector.startswith('h3:'):field='name'
  elif selector.startswith('p:nth-of-type(2)'):field='story'
  elif selector.startswith('p:nth-of-type(3)'):field='provenance'
  elif selector.startswith('a:'):field='infoCta'
  else:raise ValueError('Unknown dated archive binding: '+selector)
  key='saintDay.archive.'+date+'.'+field;b['key']=key
  for lang in catalogs:
   if field=='date':value='.'.join(reversed(date.split('-')))
   else:value=item['copy'][lang][field]
   if key in result[lang] and result[lang][key]!=value:raise ValueError('Archive reviewed value changed: '+key)
   result[lang][key]=value
 # Every historical message stays present, including shared chrome keys.
 new['messages']=result['en'];path.write_text(json.dumps(new,ensure_ascii=False,indent=1)+'\n')
 for lang,c in result.items():(root/f'locales/{lang}/{FAMILY}-copy.json').write_text(json.dumps(c,ensure_ascii=False,indent=1)+'\n')
 return new
if __name__=='__main__':refresh(Path(__file__).resolve().parents[2])
