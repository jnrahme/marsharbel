#!/usr/bin/env python3
"""Prepare exact-WAV interleaved EN rosary body. No approval or publishing."""
import argparse,json,hashlib,re,wave
from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw,ImageFont

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wrap(draw,text,font,width):
 lines=[];line=''
 for word in text.split():
  test=(line+' '+word).strip()
  if line and draw.textlength(test,font=font)>width:lines.append(line);line=word
  else:line=test
 if line:lines.append(line)
 return lines

def prepare(family,template,scripts,wavdir,artdir,out):
 out=Path(out)
 if out.exists():raise ValueError('Output directory exists; immutable build')
 template=json.loads(Path(template).read_text());texts=json.loads(Path(scripts).read_text());textmap={r['key']:r for r in texts}
 if len(textmap)!=61:raise ValueError('Expected61unique new takes')
 for r in texts:
  if hashlib.sha256(r['text'].encode()).hexdigest()!=r['text_sha256']:raise ValueError('Script hash mismatch:'+r['key'])
 timeline=[];pos=0;chunks=[];frames=[];pages=[];last=None;last_prompt={};out.mkdir();f=lambda n,serif=False:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVu'+('Serif'if serif else'Sans')+'.ttf',n)
 names=[textmap[f'{family}_{n}-announcement']['text'].split('. ',1)[1].rstrip('.') for n in range(1,6)]
 for index,original in enumerate(template):
  r={**original};r['start']=pos
  if 'key' not in r:
   chunks.append(bytes(round(r['duration']*24000)*2));frames.append((last,r['duration']));timeline.append(r);pos+=r['duration'];continue
  old=r['key'];new=None
  if old=='opening-announcement':new=f'{family}-announcement'
  elif old.startswith('announce'):new=f'{family}_{r["section"]}-announcement'
  elif old.startswith('sorrowful_'):
   step=int(old[-2:]);new=f'{family}_{r["section"]}-intro'if step==1 else f'{family}_{r["section"]}-bead-{step-2}'
  if new:
   x=textmap[new];r.update(key=new,text=x['text'],text_sha256=x['text_sha256'],file=str(Path(wavdir)/f'{new}.wav'))
  path=Path(r['file'])
  with wave.open(str(path)) as w:
   if (w.getnchannels(),w.getsampwidth(),w.getframerate())!=(1,2,24000):raise ValueError('WAV format:'+str(path))
   r['duration']=w.getnframes()/w.getframerate();chunks.append(w.readframes(w.getnframes()))
  if not new and digest(path)!=r['sha256']:raise ValueError('Shared approved WAV changed:'+old)
  r['sha256']=digest(path);r['text_sha256']=hashlib.sha256(r['text'].encode()).hexdigest()
  sec=r['section'];n=min(5,max(1,sec));im=Image.new('RGB',(1280,720),'#111217');draw=ImageDraw.Draw(im)
  head=f'{family.upper()} MYSTERIES';title=names[n-1]if sec in range(1,6)else family.title()+' Mysteries'
  draw.text((48,22),head,font=f(20),fill='#c0b8ac');draw.text((48,54),title,font=f(38,True),fill='#f3eee6');draw.line((48,116,1232,116),fill='#38383b')
  art=Image.open(Path(artdir)/f'{family}-{n}.jpg').convert('RGB');art.thumbnail((418,544));im.paste(art,(48+(418-art.width)//2,140+(544-art.height)//2))
  txt=r['text'];slices=[txt];bounds=[0,r['duration']]
  if r['kind']=='apostles_creed':cut=txt.index('he ascended');slices=[txt[:cut].strip(),txt[cut:].strip()];bounds=[0,24.14,r['duration']]
  if r['kind']=='meditation':last_prompt[sec]=txt
  for part,s in enumerate(slices):
   page=im.copy();d=ImageDraw.Draw(page);y=148
   if r['kind']=='hail_mary'and sec in range(1,6):
    if sec not in last_prompt:raise ValueError('Hail Mary missing preceding prompt')
    for line in wrap(d,last_prompt[sec],f(32),680):d.text((518,y),line,font=f(32),fill='#d3c5aa');y+=38
    y+=17;d.text((518,y),'Hail Mary',font=f(23),fill='#c0b8ac');y+=35
   for line in wrap(d,s,f(32),680):d.text((518,y),line,font=f(32),fill='#f3eee6');y+=38
   if y>=638:raise ValueError('Text overflow:'+r['key'])
   if r['kind']=='hail_mary':
    total=10 if sec in range(1,6) else 3
    for i in range(total):d.ellipse((518+i*30,650,528+i*30,660),fill='#f3eee6'if i<r['bead']else'#4d4a46')
   dest=out/f'{index:03}-{r["key"]}-p{part+1}.jpg';page.save(dest,quality=95);last=str(dest);dur=bounds[part+1]-bounds[part];frames.append((last,dur));pages.append({'key':r['key'],'start':pos+bounds[part],'duration':dur,'file':last,'display_text':s,'visualization_text':last_prompt.get(sec)if r['kind']=='hail_mary'else None})
  timeline.append(r);pos+=r['duration']
 counts=Counter(r['kind']for r in timeline)
 for k,n in {'hail_mary':53,'our_father':6,'glory_be':6,'fatima':5,'meditation':55}.items():
  if counts[k]!=n:raise ValueError('Wrong prayer count:'+k)
 with wave.open(str(out/'raw.wav'),'wb')as w:w.setparams((1,2,24000,0,'NONE','not compressed'));w.writeframes(b''.join(chunks))
 (out/'timeline.json').write_text(json.dumps(timeline,indent=2));(out/'pages.json').write_text(json.dumps(pages,indent=2));(out/'images.txt').write_text('\n'.join(f"file '{file}'\nduration {dur:.6f}"for file,dur in frames)+f"\nfile '{last}'\n")
 (out/'build-proof.json').write_text(json.dumps({'family':family,'duration_without_endcredits':pos,'counts':dict(counts),'status':'prepared;credits+encode+actualartifactQA+ownerreviewpending'},indent=2))
 return pos
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in['family','template','scripts','wavdir','artdir','output']:p.add_argument('--'+k,required=True)
 a=p.parse_args();print(prepare(a.family,a.template,a.scripts,a.wavdir,a.artdir,a.output))
