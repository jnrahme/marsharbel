#!/usr/bin/env python3
"""Join all sentence parts for a page and add deliberate rests."""
import json,re,subprocess,sys
from pathlib import Path
import numpy as np,soundfile as sf
root=Path(__file__).parent;rows=json.loads((root/'page-manifest.json').read_text());page=int(sys.argv[1]);row=rows[page-1];parts=root/'audio-parts';out=root/'audio';out.mkdir(exist_ok=True)
audio=[]
for idx,sentence in enumerate(row['sentences']):
 files=sorted(parts.glob(f'{page:02}-{idx:02}-*.flac'))
 if not files:raise ValueError(f'Missing sentence {page}-{idx}')
 for i,file in enumerate(files):
  clip,rate=sf.read(file);assert rate==24000;audio.append(clip)
  if i<len(files)-1:audio.append(np.zeros(round(.11*rate),dtype=np.float32))
 audio.append(np.zeros(round(.27*24000),dtype=np.float32))
wave=np.concatenate(audio);wav=out/f'page-{page:02}.wav';sf.write(wav,wave,24000)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-codec:a','libmp3lame','-qscale:a','3',str(out/f'page-{page:02}.mp3')],check=True)
wav.unlink();print('DONE',page,round(len(wave)/24000,2),flush=True)
