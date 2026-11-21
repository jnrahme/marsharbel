import pathlib,json,subprocess,hashlib
import numpy as np,soundfile as sf
p=pathlib.Path('/downloads/daily-rosary-tuesday');sr=24000;entries=[];pos=0;buf=[];cache={};texts=json.load(open(p/'prayer-texts-revised.json'));new=json.load(open(p/'new-recording-plan.json'));guides=json.load(open(p/'source-clips.json'));repl=json.load(open(p/'replacement-spoken-text.json'))
def silence(d,section):
 global pos
 entries.append({'kind':'quiet','start':pos,'duration':d,'section':section});buf.append(np.zeros(round(d*sr),dtype=np.float32));pos+=d
def add(key,kind,section,text=None,newtake=False,bead=0):
 global pos
 f=p/'new-takes'/(key+'.wav') if newtake else p/(key+'.mp3')
 if str(f) not in cache:
  raw=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(f),'-f','f32le','-ac','1','-ar',str(sr),'-']);cache[str(f)]=np.frombuffer(raw,dtype=np.float32)
 a=cache[str(f)];d=len(a)/sr;entries.append({'key':key,'kind':kind,'section':section,'start':pos,'duration':d,'bead':bead,'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'text':text if text is not None else new.get(key,texts.get(key,''))});buf.append(a);pos+=d
add('opening','preparation',0,newtake=True);silence(6,0)
for i in range(4):
 add('inhale','breath',0,newtake=True);silence(2,0);add('exhale','breath',0,newtake=True);silence(3,0)
add('start','sign_of_cross',0,newtake=True);silence(1,0);add('apostles_creed','apostles_creed',0,newtake=True);silence(1.2,0);add('our_father','our_father',0);silence(1.2,0)
for i,k in enumerate(['faith','hope','charity'],1):add(k,'intention',0,newtake=True);silence(.5,0);add('hail_mary','hail_mary',0,bead=i);silence(1.2,0)
add('glory_be','glory_be',0);silence(2,0)
for n in range(1,6):
 add(f'announce{n}','announcement',n,newtake=True);silence(1.5,n)
 for step in [1,*range(3,13)]:
  key=f'sorrowful_{n}-step-{step:02}';r=next(r for r in guides if r['key']+ '-'+r['step']==key);add(key,'meditation',n,text=repl.get(key,r['script']),newtake=key in repl);silence(2,n)
 silence(5,n);add('our_father','our_father',n);silence(1.2,n)
 for b in range(1,11):add('hail_mary','hail_mary',n,bead=b);silence(1.2,n)
 add('glory_be','glory_be',n);silence(1.2,n);add('fatima','fatima',n,newtake=True);silence(3,n)
add('hail_holy_queen','hail_holy_queen',6,newtake=True);silence(1,6);add('dialogue_v','dialogue_v',6,newtake=True);silence(1,6);add('dialogue_r','dialogue_r',6,newtake=True);silence(1,6);add('let_us_pray','introduction',6,newtake=True);silence(.7,6);add('rosary_concluding_prayer','rosary_concluding_prayer',6,newtake=True);silence(1,6);add('closing','sign_of_cross',6,newtake=True);silence(3,6);add('support','support',6,newtake=True);silence(3,6)
sf.write(p/'assembled-raw.wav',np.concatenate(buf),sr,subtype='PCM_16');(p/'final-timeline.json').write_text(json.dumps(entries,indent=2));print('DURATION',pos)
from collections import Counter
print(Counter(r['kind'] for r in entries));assert sum(r['kind']=='hail_mary' for r in entries)==53;assert sum(r['kind']=='our_father' for r in entries)==6;assert not any('step-02' in r.get('key','') or 'step-13' in r.get('key','') for r in entries)
