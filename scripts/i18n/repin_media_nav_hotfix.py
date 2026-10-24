"""Non-author +3 prayer nav placeholder and DE exact header-only repin.
Only catalogSha256/masterSha256 change; all checks finish before writing.
"""
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.exact_master import render_exact
from i18n.reviewed_history import digest
CODES={'ar','de','fr','ru','pt','it','pl','es'}
FAMILIES={'saint-charbel-prayers-master','saint-charbel-novena-master'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(base,path):return subprocess.check_output(['git','show',base+':'+path],cwd=ROOT)
def outside_header(raw):
 s=BeautifulSoup(raw,'html.parser')
 if not s.header:raise ValueError('Missing header')
 s.header.decompose();return str(s)
def placeholder_delta(old,new,prefix):
 expected={prefix+'.header.'+s:s.title()for s in ('media','music','video')}
 return set(new)-set(old)==set(expected) and not set(old)-set(new) and all(old[k]==new[k]for k in old) and all(new[k]==v for k,v in expected.items())
def prepare(base):
 path='locales/prayer-equivalence.json';old=json.loads(blob(base,path));record=json.loads((ROOT/path).read_text());baseline=copy.deepcopy(record);rows=[]
 if record['gateStatus']!='approved' or old['gateStatus']!='approved' or set(record['groups'])!=FAMILIES:raise ValueError('Approved family set changed')
 for family,g in record['groups'].items():
  if set(g['variants'])!={'en'}|CODES:raise ValueError('Unexpected locale set')
  for code,v in g['variants'].items():
   raw=blob('HEAD',v['file']);prior=blob(base,v['file'])
   if digest(raw.decode())!=v['bodySha256'] or digest(prior.decode())!=v['bodySha256']:raise ValueError('Main pin drift')
   if outside_header(raw)!=outside_header(prior):raise ValueError('Non-header drift')
   if code=='en':continue
   cp=v['catalog'];before=blob(base,cp);after=(ROOT/cp).read_bytes()
   if not placeholder_delta(json.loads(before),json.loads(after),family.removesuffix('-master')):raise ValueError('Placeholder class differs: '+cp)
   if old['groups'][family]['variants'][code]['catalogSha256']!=sha(before) or v['catalogSha256']not in (sha(before),sha(after)):raise ValueError('Pin provenance differs')
   rows.append({'family':family,'locale':code,'oldSha256':sha(before),'newSha256':sha(after),'added':3,'removed':0,'changed':0});v['catalogSha256']=sha(after);baseline['groups'][family]['variants'][code]['catalogSha256']=old['groups'][family]['variants'][code]['catalogSha256']
 if baseline!=old:raise ValueError('Other review fields changed')
 updates={path:record};registry=json.loads((ROOT/'locales/registry.json').read_text())
 for name in ('biography','miracles'):
  p='locales/de/'+name+'-exact.json';prior=json.loads(blob(base,p));cat=json.loads((ROOT/p).read_text());master=cat['master'];before=blob(base,master);after=(ROOT/master).read_bytes()
  if prior['masterSha256']!=sha(before) or cat['masterSha256']not in (sha(before),sha(after)):raise ValueError('Exact base pin differs')
  check=copy.deepcopy(cat);check['masterSha256']=prior['masterSha256']
  if check!=prior or outside_header(before)!=outside_header(after):raise ValueError('Exact non-header drift')
  cat['masterSha256']=sha(after)
  for label,value in {'Media':'Medien','Music':'Musik','Video':'Video','Gallery':'Galerie'}.items():
   if cat['chrome'].get(label)!=value:raise ValueError('Reviewed chrome missing')
  render_exact(ROOT,registry,'de',name,registry['exactMirrors'][name]['routes']['de'],cat);updates[p]=cat;rows.append({'exact':name,'oldMasterSha256':sha(before),'newMasterSha256':sha(after)})
 return updates,rows
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--check',action='store_true');a=ap.parse_args();updates,rows=prepare(a.base)
 if not a.check:
  for p,data in updates.items():(ROOT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'mode':'check'if a.check else 'write','pins':rows},indent=2))
