import json,re,sys,gc
from pathlib import Path
import numpy as np,soundfile as sf,torch
torch.set_num_threads(2)
root=Path(__file__).parent;rows=json.loads((root/'page-manifest.json').read_text());out=Path('/tmp/augustine-parts');out.mkdir(exist_ok=True)
from kokoro import KPipeline
pipe=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',device='cpu')
def chunks(text):
 parts=re.split(r'(?<=[,;:])\s+',text);cs=[];cur=''
 for part in parts:
  if len(cur)+len(part)+1<=84:cur=(cur+' '+part).strip()
  else:
   if cur:cs.append(cur)
   cur=part
   while len(cur)>84:
    sp=cur.rfind(' ',45,84)
    if sp<0:sp=83
    cs.append(cur[:sp].strip());cur=cur[sp:].strip()
 if cur:cs.append(cur)
 return cs
N=0
for r in rows:
 for i,s in enumerate(r['sentences']):
  for j,c in enumerate(chunks(s)):
   d=out/f"{r['page']:02}-{i:02}-{j:02}.flac"
   if d.exists():continue
   N+=1
   if N>4:sys.exit(0)
   with torch.inference_mode():
    a=[x[2] for x in pipe(c.replace('Possidius','Po-sid-ee-us'),voice='am_michael',speed=.94)]
   sf.write(d,np.concatenate([np.asarray(w) for w in a]),24000);del a;gc.collect()
  print('S',r['page'],i,flush=True)
print('DONE')
