import json,subprocess,numpy as np,soundfile as sf,sys
from kokoro import KPipeline
p=KPipeline(lang_code='a')
man=json.load(open('page-manifest.json'))
want=[int(a) for a in sys.argv[1:]]
for m in man:
    if m['page'] not in want: continue
    out=[];sil=np.zeros(int(24000*0.45))
    for s in m['sentences']:
        for g,ps,a in p(s.replace('Qalamoun','Kalamoon'),voice='am_michael',speed=0.94):
            out.append(a)
        out.append(sil)
    f=f"/tmp/marina-{m['page']:02d}.wav"
    sf.write(f,np.concatenate(out),24000)
    d=f"/home/sandbox/marsharbel/media/storybook-marina/en/page-{m['page']:02d}.mp3"
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f,'-codec:a','libmp3lame','-b:a','96k',d],check=True)
    print(m['page'],len(np.concatenate(out))/24000,flush=True)
