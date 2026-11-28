import pathlib,json,subprocess,hashlib
p=pathlib.Path('/downloads/daily-rosary-tuesday');t=json.load(open(p/'final-timeline.json'));total=max(r['start']+r['duration'] for r in t);starts=[next(r['start'] for r in t if r.get('key')==f'announce{i}') for i in range(1,6)];cuts=[0,*starts[1:],total];frames=['frame-1.jpg','frame-2-crop.jpg','frame-3.jpg','frame-4.jpg','frame-5.jpg'];v=[]
for i in range(5):v.extend([f"file '{p/frames[i]}'",f'duration {cuts[i+1]-cuts[i]:.6f}'])
for i in range(1,6):v.extend([f"file '{p/f'credit-{i}.jpg'}'",'duration 15'])
v.append(f"file '{p/'credit-5.jpg'}'");(p/'video-images.txt').write_text('\n'.join(v))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(p/'assembled-raw.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar','24000','-ac','1','-y',str(p/'assembled-normalized.wav')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(p/'video-images.txt'),'-i',str(p/'assembled-normalized.wav'),'-af','apad=pad_dur=75','-t',str(total+75),'-r','2','-c:v','libx264','-preset','fast','-crf','26','-pix_fmt','yuv420p','-c:a','aac','-b:a','64k','-movflags','+faststart','-y',str(p/'tuesday-sorrowful-private-preview.mp4')],check=True)
print('PREVIEW',total+75,hashlib.sha256((p/'tuesday-sorrowful-private-preview.mp4').read_bytes()).hexdigest(),(p/'tuesday-sorrowful-private-preview.mp4').stat().st_size)
