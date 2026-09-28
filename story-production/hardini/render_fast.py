#!/usr/bin/env python3
"""Resume Kokoro page narration with one model load per bounded batch."""
from pathlib import Path
import json,os,re,sys,subprocess
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
import numpy as np,soundfile as sf
from kokoro import KPipeline
root=Path(__file__).parent;rows=json.loads((root/'page-manifest.json').read_text());out=root/'audio-parts';out.mkdir(exist_ok=True);limit=int(sys.argv[1]) if len(sys.argv)>1 else 8;made=0
pipeline=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',device='cpu')
def pieces(text):
 parts=re.split(r'(?<=[,;:])\s+',text);chunks=[];current=''
 for part in parts:
  if len(current)+len(part)+1<=84:current=(current+' '+part).strip()
  else:
   if current:chunks.append(current)
   current=part
   while len(current)>84:
    split=current.rfind(' ',45,84)
    if split<0:split=83
    chunks.append(current[:split].strip());current=current[split:].strip()
 if current:chunks.append(current)
 return chunks
for row in rows:
 page=row['page']
 if (root/'audio'/f'page-{page:02}.mp3').exists():continue
 for idx,sentence in enumerate(row['sentences']):
  for piece,fragment in enumerate(pieces(sentence)):
   dest=out/f'{page:02}-{idx:02}-{piece:02}.flac'
   if dest.exists() and dest.stat().st_size>15000:continue
   if made>=limit:print('BATCH',made,'NEXT',page,idx,piece,flush=True);sys.exit(0)
   waves=[x[2] for x in pipeline(fragment,voice='am_michael',speed=.94)];assert waves
   sf.write(dest,np.concatenate(waves),24000);made+=1
   print('PART',page,idx,piece,round(sum(len(w) for w in waves)/24000,2),flush=True)
 subprocess.run([sys.executable,str(root/'assemble_audio.py'),str(page)],check=True)
print('BATCH',made,'COMPLETE',flush=True)
