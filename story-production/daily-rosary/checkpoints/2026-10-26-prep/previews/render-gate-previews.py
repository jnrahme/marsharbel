from PIL import Image, ImageDraw, ImageFont
import json
BG='#111217'; MUTE='#c0b8ac'; IVORY='#f3eee6'; LINE='#38383b'; GOLD='#d3c5aa'; DIM='#d8d2c8'; DOTOFF='#6b675f'
def f(n,serif=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVu'+('Serif' if serif else 'Sans')+'.ttf',n)
def wrap(s,font,width,d):
    out=[];cur=''
    toks=[]
    for w in s.split():
        while d.textlength(w,font=font)>width:
            k=len(w)
            while k>1 and d.textlength(w[:k],font=font)>width: k-=1
            toks.append(w[:k]); w=w[k:]
        toks.append(w)
    for w in toks:
        t=(cur+' '+w).strip()
        if cur and d.textlength(t,font=font)>width: out.append(cur);cur=w
        else: cur=t
    if cur: out.append(cur)
    return out
def tag(d): d.text((860,692),'LAYOUT PREVIEW - NOT FOR RELEASE',font=f(16),fill=DOTOFF)
def phone(im,n): im.resize((390,219),Image.Resampling.LANCZOS).save(n.replace('.jpg','-phone.jpg'),quality=95)
DL='/downloads/'
keys=json.load(open('/home/sandbox/repo/story-production/daily-rosary/scripts/en/joyful-body-unique-texts.json'))
if isinstance(keys,dict): keys=[{'key':k,'text':v} for k,v in keys.items()]
kmap={(k.get('key') or k.get('chunk_key')):k['text'] for k in keys}
HAIL=json.load(open('/home/sandbox/repo/story-production/daily-rosary/scripts/en/prayers.json'))['hail_mary']
arts={1:'annunciation-virgin-WGA09191-60325264.jpg',2:'giotto-visitation-43ee27d2.jpg',3:'giotto-nativity-0ae3de20.jpg',4:'giotto-presentation-2603e60b.jpg',5:'giotto-doctors-6ecd8562.jpg'}
titles={1:'The Annunciation',2:'The Visitation',3:'The Nativity',4:'The Presentation',5:'Finding Jesus in the Temple'}
# ---- 5 prayer-along pages (bead position = decade number, to demonstrate progress) ----
for dn in range(1,6):
    im=Image.new('RGB',(1280,720),BG); d=ImageDraw.Draw(im)
    d.text((48,26),'JOYFUL MYSTERIES',font=f(20),fill=MUTE)
    d.text((48,56),titles[dn],font=f(38,True),fill=IVORY)
    d.line((48,112,1232,112),fill=LINE)
    a=Image.open(DL+arts[dn]).convert('RGB'); a.thumbnail((418,540))
    im.paste(a,(48+(418-a.width)//2,132+(540-a.height)//2))
    y=150
    for ln in wrap(kmap[f'joyful_{dn}-intro'],f(29),700,d): d.text((518,y),ln,font=f(29),fill=IVORY); y+=38
    y+=14
    d.text((518,y),'Hail Mary',font=f(22),fill=GOLD); y+=36
    for ln in wrap(HAIL,f(25),700,d): d.text((518,y),ln,font=f(25),fill=DIM); y+=33
    for i in range(10):
        cx=518+i*30; cy=664
        if i<dn: d.ellipse((cx-7,cy-7,cx+7,cy+7),fill=IVORY)
        else: d.ellipse((cx-7,cy-7,cx+7,cy+7),outline=DOTOFF,width=2)
    tag(d)
    im.save(f'preview-prayalong-{dn}.jpg',quality=96); phone(im,f'preview-prayalong-{dn}.jpg')

# ---- 6 per-art final credit cards (exact source/licence URLs) ----
J='Italian jurisdiction note (preserved uncertainty, not a legal conclusion): Italian domestic cultural-heritage law (D.Lgs 42/2004) may restrict some commercial uses of Italian heritage imagery within Italy; applicability to this scan unverified; no Commons restriction template present.'
cards=[
 ('demetrius-kyiv-mosaic-gap-c5acd367.jpg','Intro - Saint Demetrius of Thessalonica',
  ['Work: Mosaic of Saint Demetrius of Thessaloniki, 1108-1113, Saint Michael\'s Golden-Domed Monastery, Kyiv; now Tretyakov Gallery, Moscow.',
   'Licence: Public domain (faithful reproduction of 2D public-domain mosaic).',
   'Source: Google Arts & Culture, via Wikimedia Commons.',
   'Commons page: https://commons.wikimedia.org/wiki/File:%D0%A1%D0%B2._%D0%94%D0%BC%D0%B8%D1%82%D1%80%D0%B8%D0%B9_%D0%A1%D0%BE%D0%BB%D1%83%D0%BD%D1%81%D0%BA%D0%B8%D0%B9_-_Google_Art_Project.jpg',
   'Known states: minor plaster loss along bottom edge; Commons description notes non-natural colours on this scan (preserved, no correction).'],None),
 ('annunciation-virgin-WGA09191-60325264.jpg','The Annunciation (Virgin panel)',
  ['Giotto di Bondone, No. 15 Annunciation - The Virgin Receiving the Message, Scrovegni Chapel, Padua (c. 1305).',
   'Licence basis: PD-Art + PD-old-auto-expired (deathyear 1337).',
   'Source: Web Gallery of Art (WGA09191), via Wikimedia Commons.',
   'Commons page: https://commons.wikimedia.org/wiki/File:Giotto_di_Bondone_-_No._15_Annunciation_-_The_Virgin_Receiving_the_Message_-_WGA09191.jpg',
   'Known state: plaster loss visible lower-left (authentic state).'],J),
 ('giotto-visitation-43ee27d2.jpg','The Visitation',
  ['Giotto di Bondone, No. 16 Scenes from the Life of the Virgin - 7. Visitation, Scrovegni Chapel, Padua (c. 1305).',
   'Licence basis: PD-Art + PD-old-auto-expired (deathyear 1337).',
   'Source: Web Gallery of Art (WGA09192), via Wikimedia Commons.',
   'Commons page: https://commons.wikimedia.org/wiki/File:Giotto_di_Bondone_-_No._16_Scenes_from_the_Life_of_the_Virgin_-_7._Visitation_-_WGA09192.jpg'],J),
 ('giotto-nativity-0ae3de20.jpg','The Nativity',
  ['Giotto di Bondone, No. 17 Scenes from the Life of Christ - 1. Nativity, Scrovegni Chapel, Padua (c. 1305).',
   'Licence basis: PD-Art + PD-old-100-1923 (per Scrum refinement; equivalent asserted PD basis to other panels).',
   'Source: Web Gallery of Art (WGA09193), via Wikimedia Commons.',
   'Commons page: https://commons.wikimedia.org/wiki/File:Giotto_di_Bondone_-_No._17_Scenes_from_the_Life_of_Christ_-_1._Nativity_-_Birth_of_Jesus_-_WGA09193.jpg'],J),
 ('giotto-presentation-2603e60b.jpg','The Presentation',
  ['Giotto di Bondone, No. 19 Scenes from the Life of Christ - 3. Presentation of Christ at the Temple, Scrovegni Chapel, Padua (c. 1305).',
   'Licence basis: PD-Art + PD-old-auto-expired (deathyear 1337).',
   'Source: Web Gallery of Art (WGA09197), via Wikimedia Commons.',
   'Commons page: https://commons.wikimedia.org/wiki/File:Giotto_di_Bondone_-_No._19_Scenes_from_the_Life_of_Christ_-_3._Presentation_of_Christ_at_the_Temple_-_WGA09197.jpg'],J),
 ('giotto-doctors-6ecd8562.jpg','Finding Jesus in the Temple',
  ['Giotto di Bondone, No. 22 Scenes from the Life of Christ - 6. Christ among the Doctors, Scrovegni Chapel, Padua (c. 1305).',
   'Licence basis: PD-Art + PD-old-auto-expired (deathyear 1337).',
   'Source: Web Gallery of Art (WGA09200), via Wikimedia Commons.',
   'Commons page: https://commons.wikimedia.org/wiki/File:Giotto_di_Bondone_-_No._22_Scenes_from_the_Life_of_Christ_-_6._Christ_among_the_Doctors_-_WGA09200.jpg',
   'Known state: darkest/most abraded panel of the set (authentic state, disclosed; no restoration).'],J),
]
for idx,(file,title,lines,jnote) in enumerate(cards):
    im=Image.new('RGB',(1280,720),BG); d=ImageDraw.Draw(im)
    d.text((48,26),'ART CREDIT',font=f(20),fill=MUTE)
    d.text((48,56),title,font=f(34,True),fill=IVORY)
    d.line((48,108,1232,108),fill=LINE)
    a=Image.open(DL+file).convert('RGB'); a.thumbnail((330,540))
    im.paste(a,(48+(330-a.width)//2,128+(540-a.height)//2))
    y=140
    for para in lines:
        for ln in wrap(para,f(19),800,d): d.text((430,y),ln,font=f(19),fill=DIM); y+=26
        y+=10
    if jnote:
        for ln in wrap(jnote,f(16),800,d): d.text((430,y),ln,font=f(16),fill=MUTE); y+=22
    tag(d)
    im.save(f'preview-credit-{idx}.jpg',quality=96); phone(im,f'preview-credit-{idx}.jpg')
print('done')
