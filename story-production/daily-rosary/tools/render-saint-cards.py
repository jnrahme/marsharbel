from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,textwrap
p=Path('/downloads/rosary-factory-intros');art=Path('/downloads/rosary-factory-art');scripts=Path('/home/sandbox/rosary-recovery-repo/story-production/daily-rosary/scripts/en')
names={14:'Saint Callistus I',15:'Saint Teresa of Jesus',16:'Saint Hedwig',17:'Saint Ignatius of Antioch',18:'Saint Luke the Evangelist',19:'Saints John de Brébeuf, Isaac Jogues, and their companions'}
headers={14:'WEDNESDAY, OCTOBER 14',15:'THURSDAY, OCTOBER 15',16:'FRIDAY, OCTOBER 16',17:'SATURDAY, OCTOBER 17',18:'SUNDAY, OCTOBER 18',19:'MONDAY, OCTOBER 19'}
credits={14:'Saint Callistus I, nineteenth-century papal mosaic, Basilica of Saint Paul Outside the Walls; via Wikimedia Commons.',15:'Teresa of Jesus, Juan de la Miseria, 1576 (detail); via Wikimedia Commons.',16:'Saint Hedwig and the New Convent, court workshop of Duke Ludwig I, 1353; Getty, via Wikimedia Commons.',18:'Saint Luke Painting the Virgin, El Greco, 1560-67; devotional tradition; Benaki Museum, via Wikimedia Commons.',19:'Saint Isaac Jogues, J. Boyes, 1907 portrait; via Wikimedia Commons.',17:'Saint Ignatius of Antioch, anonymous Byzantine fresco, Hosios Loukas Monastery; via Wikimedia Commons.'}
f=lambda n,serif=False:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVu'+('Serif' if serif else 'Sans')+'.ttf',n)
def lines(s,font,width):
 d=ImageDraw.Draw(Image.new('RGB',(1,1)));out=[];cur=''
 for w in s.split():
  t=(cur+' '+w).strip()
  if cur and d.textlength(t,font=font)>width:out.append(cur);cur=w
  else:cur=t
 if cur:out.append(cur)
 return out
for day in [14,15,16,17,18,19]:
 im=Image.new('RGB',(1280,720),'#111217');d=ImageDraw.Draw(im);d.text((48,22),headers[day],font=f(20),fill='#c0b8ac')
 h=lines(names[day],f(38,True),1184)
 for i,t in enumerate(h):d.text((48,54+i*45),t,font=f(38,True),fill='#f3eee6')
 top=116+(len(h)-1)*45;d.line((48,top,1232,top),fill='#38383b');a=Image.open(art/('17-new.jpg' if day==17 else f'{day}.jpg')).convert('RGB');maxsize=(300,300) if day==14 else (418,496);a.thumbnail(maxsize);im.paste(a,(48+(418-a.width)//2,top+24+(500-a.height)//2))
 script=(scripts/f'2026-10-{day}.txt').read_text().strip();text=script.removeprefix('Today we remember '+names[day]+'. ')
 if text==script:text=script
 font=f(29);y=top+42
 for line in lines(text,font,710):d.text((518,y),line,font=font,fill='#f3eee6');y+=38
 assert y<top+330,(day,y)
 y=max(548,top+360)
 if day==19:d.text((518,y-34),'Portrait: Saint Isaac Jogues',font=f(22),fill='#d3c5aa')
 for line in lines(credits[day],f(20),710):d.text((518,y),line,font=f(20),fill='#c0b8ac');y+=27
 assert y<=706,(day,y)
 im.save(p/f'2026-10-{day}-card.jpg',quality=96)
 im.resize((390,219),Image.Resampling.LANCZOS).save(p/f'2026-10-{day}-phone.jpg',quality=95)
print('Rendered6cards1280x720plus390pxphoneframes;nativeCallistus300pxmax')
