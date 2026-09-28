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
 audio.append(np.zeros(round(.47*24000),dtype=np.float32))
# Editorial beat map: a longer breath at emotional turns, questions and reflection transitions.
# Indices are sentence numbers in the approved page manifest; durations in seconds.
beat_map={
 6:{0:.72,1:.75,3:.78,4:.62,7:.77,9:.88},
 7:{2:.68,4:.75,6:.73,8:.78,9:.88},
 8:{3:.83,4:.62,6:.68,7:.78,8:.95},
 9:{0:.65,1:.95,2:.68,5:.78,6:.82,7:.78,9:.9},
 10:{2:1.0,5:1.0,9:.8,12:1.0,13:.7,14:1.0},
}
# Swap each default sentence tail without touching spoken fragments.
if page in beat_map:
 audio=[]
 for idx,sentence in enumerate(row['sentences']):
  files=sorted(parts.glob(f'{page:02}-{idx:02}-*.flac'))
  for i,file in enumerate(files):
   clip,rate=sf.read(file);audio.append(clip)
   if i<len(files)-1:audio.append(np.zeros(round(.11*rate),dtype=np.float32))
  rest=beat_map[page].get(idx,.47)
  audio.append(np.zeros(round(rest*24000),dtype=np.float32))
wave=np.concatenate(audio);wav=out/f'page-{page:02}.wav';sf.write(wav,wave,24000)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-codec:a','libmp3lame','-qscale:a','3',str(out/f'page-{page:02}.mp3')],check=True)
wav.unlink();print('DONE',page,round(len(wave)/24000,2),flush=True)
