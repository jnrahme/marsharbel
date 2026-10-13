import json,sys,pathlib,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
p=pathlib.Path(sys.argv[1]);family=sys.argv[2];ledger=json.load(open('/downloads/rosary-factory-body-art/ledger.json'));t=json.load(open(p/'timeline.json'));duration=sum(r['duration'] for r in t)+75
lines=(p/'images.txt').read_text().splitlines()[:-1]
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
for n in range(1,6):
 r=next(x for x in ledger if x['key']==f'{family}_{n}');im=Image.new('RGB',(1280,720),'#111217');d=ImageDraw.Draw(im)
 for y,text,size in [(80,'Image source',30),(145,r['title'],29),(230,'Rosary Center',38),(310,'Artwork from the rosary images on marsharbel.com.',27),(370,'Artist and video-reuse rights not verified.',26),(425,'Credit is not a license. Private review only.',26)]:d.text((60,y),text,font=font(size),fill='#f3eee6')
 url=r['url'];d.text((60,520),url[:75],font=font(19),fill='#c0b8ac');d.text((60,640),'MARSHARBEL.COM',font=font(28),fill='#f3eee6');dest=p/f'credit-{n}.jpg';im.save(dest,quality=95);lines.extend([f"file '{dest}'",'duration 15'])
lines.append(f"file '{dest}'");(p/'images-with-credits.txt').write_text('\n'.join(lines))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(p/'images-with-credits.txt'),'-i',str(p/'raw.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=75','-t',str(duration),'-r','2','-c:v','libx264','-profile:v','high','-level:v','3.1','-preset','fast','-crf','26','-pix_fmt','yuv420p','-c:a','aac','-ar','24000','-ac','1','-b:a','64k','-movflags','+faststart','-y',str(p/f'{family}-en-body-private.mp4')],check=True)
f=p/f'{family}-en-body-private.mp4';(p/'encode-proof.json').write_text(json.dumps({'duration':duration,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'status':'private-only;rights/audio/ownergatespending'},indent=2))
print((p/'encode-proof.json').read_text())
