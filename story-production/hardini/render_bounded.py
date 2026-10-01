#!/usr/bin/env python3
"""Small resumable Kokoro batch, one model load per fragment, then assemble complete pages."""
import json,os,re,subprocess,sys
from pathlib import Path
r=Path(__file__).parent;rows=json.loads((r/'page-manifest.json').read_text());limit=int(sys.argv[1]) if len(sys.argv)>1 else 6;made=0

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
 if (r/'audio'/f'page-{page:02}.mp3').exists():continue
 complete=True
 for idx,sentence in enumerate(row['sentences']):
  for piece,_ in enumerate(pieces(sentence)):
   dest=r/'audio-parts'/f'{page:02}-{idx:02}-{piece:02}.flac'
   if dest.exists() and dest.stat().st_size>15000:continue
   if made>=limit:print('BATCH',made,'NEXT',page,idx,piece,flush=True);sys.exit(0)
   env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
   subprocess.run([sys.executable,str(r/'generate_sentence_audio.py'),str(page),str(idx),str(piece)],check=True,env=env)
   made+=1
 if all(all((r/'audio-parts'/f'{page:02}-{idx:02}-{p:02}.flac').exists() for p in range(len(pieces(s)))) for idx,s in enumerate(row['sentences'])):
  subprocess.run([sys.executable,str(r/'assemble_audio.py'),str(page)],check=True)
print('BATCH',made,'COMPLETE',flush=True)
