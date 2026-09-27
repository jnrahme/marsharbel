#!/usr/bin/env python3
"""Resumable sentence-wise Kokoro rendering; one bounded model load per sentence."""
import json,re,sys,subprocess
from pathlib import Path
import numpy as np,soundfile as sf
root=Path(__file__).parent;rows=json.loads((root/'page-manifest.json').read_text());out=root/'audio-parts';out.mkdir(exist_ok=True)
page=int(sys.argv[1]);idx=int(sys.argv[2]);text=rows[page-1]['sentences'][idx]
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
piece_index=int(sys.argv[3]) if len(sys.argv)>3 else None
for piece,fragment in enumerate(chunks):
 if piece_index is not None and piece != piece_index:continue
 dest=out/f'{page:02}-{idx:02}-{piece:02}.flac'
 if dest.exists() and dest.stat().st_size>15000:continue
 from kokoro import KPipeline
 pipeline=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',device='cpu')
 audio=list(pipeline(fragment,voice='am_michael',speed=.94));assert audio
 waves=[x[2] for x in audio];sf.write(dest,np.concatenate(waves),24000)
 print('PART',page,idx,piece,round(sum(len(w) for w in waves)/24000,2),flush=True)
