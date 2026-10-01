#!/usr/bin/env python3
"""Render each page with Kokoro am_michael at .94; resumable WAV->MP3 work."""
import json,re,subprocess,sys
from pathlib import Path
import numpy as np,soundfile as sf
root=Path(__file__).parent
pages=json.loads((root/'page-manifest.json').read_text());out=root/'audio';out.mkdir(exist_ok=True)
start=int(sys.argv[1]) if len(sys.argv)>1 else 1
stop=int(sys.argv[2]) if len(sys.argv)>2 else len(pages)+1
# Per-phrase subprocesses bound peak memory and preserve work after a killed render.
for page in pages[start-1:stop-1]:
 i=page['page'];target=out/f'page-{i:02}.mp3'
 if target.exists() and target.stat().st_size>10000:print('SKIP',i,flush=True);continue
 for idx,sentence in enumerate(page['sentences']):
  subprocess.run([sys.executable,str(root/'generate_sentence_audio.py'),str(i),str(idx)],check=True)
 subprocess.run([sys.executable,str(root/'assemble_audio.py'),str(i)],check=True)
