import json,glob,subprocess,numpy as np,soundfile as sf
rows=json.load(open('page-manifest.json'));sil=np.zeros(int(24000*0.45))
for r in rows:
    out=[]
    for i in range(len(r['sentences'])):
        for f in sorted(glob.glob(f"/tmp/augustine-parts/{r['page']:02}-{i:02}-*.flac")):
            out.append(sf.read(f)[0])
        out.append(sil)
    w=f"/tmp/au{r['page']:02}.wav";sf.write(w,np.concatenate(out),24000)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-codec:a','libmp3lame','-b:a','96k',f"../../media/storybook-augustine/en/page-{r['page']:02d}.mp3"],check=True)
    print(r['page'],round(len(np.concatenate(out))/24000,1))
