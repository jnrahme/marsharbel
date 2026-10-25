from PIL import Image, ImageDraw, ImageFont
import json

BG='#111217'; MUTE='#c0b8ac'; IVORY='#f3eee6'; LINE='#38383b'; GOLD='#d3c5aa'
def f(n,serif=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVu'+('Serif' if serif else 'Sans')+'.ttf',n)
def wrap(s,font,width,d):
    out=[];cur=''
    for w in s.split():
        t=(cur+' '+w).strip()
        if cur and d.textlength(t,font=font)>width: out.append(cur);cur=w
        else: cur=t
    if cur: out.append(cur)
    return out
def base():
    im=Image.new('RGB',(1280,720),BG); return im,ImageDraw.Draw(im)
def label(d,text):
    d.text((48,30),text,font=f(20),fill=MUTE)
    d.line((48,116,1232,116),fill=LINE)
def tag(d):
    d.text((860,692),'LAYOUT PREVIEW - NOT FOR RELEASE',font=f(16),fill='#6b675f')
def phone(im,name):
    im.resize((390,219),Image.Resampling.LANCZOS).save(name.replace('.jpg','-phone.jpg'),quality=95)

DL='/downloads/'
# ---------- INTRO CARD ----------
im,d=base()
d.text((48,22),'MONDAY, OCTOBER 26',font=f(20),fill=MUTE)
d.text((48,54),'Saint Demetrius of Thessalonica',font=f(38,True),fill=IVORY)
d.line((48,116,1232,116),fill=LINE)
a=Image.open(DL+'demetrius-kyiv-mosaic-gap-c5acd367.jpg').convert('RGB')
a.thumbnail((360,496))
im.paste(a,(48+(418-a.width)//2,140+(500-a.height)//2))
text='Today, October twenty-sixth, we remember Saint Demetrius of Thessalonica, a martyr. Saint Demetrius of Thessalonica, pray for us.'
y=160
for ln in wrap(text,f(29),710,d): d.text((518,y),ln,font=f(29),fill=IVORY); y+=38
d.text((518,560),'Mosaic: Saint Demetrius, 1108-1113',font=f(22),fill=GOLD)
cred='Mosaic of Saint Demetrius of Thessaloniki, 1108-1113, Saint Michael\'s Golden-Domed Monastery, Kyiv; now Tretyakov Gallery, Moscow. Image: Google Arts & Culture, via Wikimedia Commons (public domain).'
y=596
for ln in wrap(cred,f(20),710,d): d.text((518,y),ln,font=f(20),fill=MUTE); y+=27
tag(d)
im.save('preview-intro-card.jpg',quality=96); phone(im,'preview-intro-card.jpg')

# ---------- MYSTERY CARDS ----------
keys=json.load(open('/home/sandbox/repo/story-production/daily-rosary/scripts/en/joyful-body-unique-texts.json'))
if isinstance(keys,dict): keys=[{'key':k,'text':v} for k,v in keys.items()]
kmap={(k.get('key') or k.get('chunk_key')):k['text'] for k in keys}
arts={1:'annunciation-virgin-WGA09191-60325264.jpg',2:'giotto-visitation-43ee27d2.jpg',3:'giotto-nativity-0ae3de20.jpg',4:'giotto-presentation-2603e60b.jpg',5:'giotto-doctors-6ecd8562.jpg'}
titles={1:'The Annunciation',2:'The Visitation',3:'The Nativity',4:'The Presentation',5:'Finding Jesus in the Temple'}
for dnum in range(1,6):
    im,d=base()
    d.text((48,30),'JOYFUL MYSTERIES',font=f(20),fill=MUTE)
    d.text((48,60),titles[dnum],font=f(38,True),fill=IVORY)
    d.line((48,116,1232,116),fill=LINE)
    a=Image.open(DL+arts[dnum]).convert('RGB'); a.thumbnail((418,520))
    im.paste(a,(48+(418-a.width)//2,140+(520-a.height)//2))
    y=160
    for ln in wrap(kmap[f'joyful_{dnum}-intro'],f(29),710,d): d.text((518,y),ln,font=f(29),fill=IVORY); y+=38
    tag(d)
    im.save(f'preview-mystery-{dnum}.jpg',quality=96); phone(im,f'preview-mystery-{dnum}.jpg')

# ---------- CREDITS SLATE ----------
im,d=base()
d.text((48,30),'ART CREDITS',font=f(20),fill=MUTE)
d.line((48,70,1232,70),fill=LINE)
creds=[
 ('Intro','Mosaic of Saint Demetrius of Thessaloniki, 1108-1113, Saint Michael\'s Golden-Domed Monastery, Kyiv; now Tretyakov Gallery, Moscow. Image: Google Arts & Culture, via Wikimedia Commons (public domain).'),
 ('The Annunciation','Giotto, The Virgin Receiving the Message, Scrovegni Chapel, Padua (c. 1305). Image: Web Gallery of Art (WGA09191), via Wikimedia Commons (public domain).'),
 ('The Visitation','Giotto, Visitation, Scrovegni Chapel, Padua (c. 1305). Image: Web Gallery of Art (WGA09192), via Wikimedia Commons (public domain).'),
 ('The Nativity','Giotto, Nativity, Scrovegni Chapel, Padua (c. 1305). Image: Web Gallery of Art (WGA09193), via Wikimedia Commons (public domain).'),
 ('The Presentation','Giotto, Presentation of Christ at the Temple, Scrovegni Chapel, Padua (c. 1305). Image: Web Gallery of Art (WGA09197), via Wikimedia Commons (public domain).'),
 ('Finding Jesus in the Temple','Giotto, Christ among the Doctors, Scrovegni Chapel, Padua (c. 1305). Image: Web Gallery of Art (WGA09200), via Wikimedia Commons (public domain).'),
]
y=100
for name,c in creds:
    d.text((48,y),name,font=f(22,True),fill=GOLD); y+=32
    for ln in wrap(c,f(20),1160,d): d.text((72,y),ln,font=f(20),fill=MUTE); y+=27
    y+=14
tag(d)
im.save('preview-credits-slate.jpg',quality=96); phone(im,'preview-credits-slate.jpg')
print('done')
