#!/usr/bin/env python3
"""Rosary factory - single-trigger daily assembly from fixed parts.

Usage:
  python3 build_day.py --date 2026-11-22 --lang en --intro-wav intro.wav --intro-sha256 <sha>
      --saint-name "Saint ..." --ask her|his|their [--saint-check auto] --outdir out/<date>

Per-day inputs: date (-> weekday -> mystery set, locked rotation), saint of the day
(fetched LIVE from Vatican News; --saint-name is the confirmed spoken form after the
minting checkpoint), and the per-day intro WAV (the only generated piece).
Everything else (body program, art, credits, texts) comes from the language+mystery pack:
donor video/audio spans + film-time-map texts + art ledger pins. No rebuild from scratch.

QA battery: sha pins (donor, art, WAV), overflow scan, per-class NCC vs donor frames,
-xerror decode, levels gate (encoded true peak <= -2 dBTP; constant attenuation at the
single AAC encode when the mix peaks hot), duration check, QA frames.
"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont

ROT = {0: 'joyful', 1: 'sorrowful', 2: 'glorious', 3: 'luminous', 4: 'sorrowful', 5: 'joyful', 6: 'glorious'}
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
ORD = {1:'first',2:'second',3:'third',4:'fourth',5:'fifth',6:'sixth',7:'seventh',8:'eighth',9:'ninth',10:'tenth',
 11:'eleventh',12:'twelfth',13:'thirteenth',14:'fourteenth',15:'fifteenth',16:'sixteenth',17:'seventeenth',
 18:'eighteenth',19:'nineteenth',20:'twentieth',21:'twenty-first',22:'twenty-second',23:'twenty-third',
 24:'twenty-fourth',25:'twenty-fifth',26:'twenty-sixth',27:'twenty-seventh',28:'twenty-eighth',29:'twenty-ninth',
 30:'thirtieth',31:'thirty-first'}

def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)

def sha256(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def ffprobe_duration(p):
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',p],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())

VN_BASE = os.environ.get('RF_VN_BASE', 'https://www.vaticannews.va').rstrip('/')

def fetch_saint(mm, dd):
    url = f'{VN_BASE}/en/saints/{mm}/{dd}.html'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8','ignore')
    details = []
    t = re.sub(r'<script.*?</script>','',html,flags=re.S); t = re.sub(r'<style.*?</style>','',t,flags=re.S)
    t = re.sub(r'<[^>]+>',' ',t); import html as H; t = H.unescape(t); t = re.sub(r'\s+',' ',t)
    m = re.search(r'journey of faith\. (.+?)(?: Born| When| In \d| He | She | Died| became | History | her | his | are | were | A [A-Z]| Your contribution| St\.? \w+ (?:was|is))', t)
    headline = m.group(1).strip() if m else None
    if headline:
        headline = re.sub(r'\s+(History|Tradition|Legend)\b.*$', '', headline).strip()
        headline = re.sub(r'[\s,]+St\.?$', '', headline).strip().rstrip(',:;')
    # dated entries ONLY for the requested month/day: a valid-looking link to another
    # date's saint page never qualifies for this build's date
    anchors = [(m.start(), m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()) for m in
               re.finditer(rf'<a[^>]+href="(/en/saints/{mm}/{dd}/[^"#?]+\.html)"[^>]*>(.*?)</a>', html, re.S)]
    # older index pages put the saint's name in the section <h2> and leave the anchor text
    # generic ('Read all...'): bind the nearest preceding heading instead (parser repair
    # 2026-11-19, EN43 proof build on the live 11/12 page)
    GENERIC = {'', 'read all...', 'read all', 'read more...', 'read more'}
    if any(t.lower() in GENERIC for _, _, t in anchors):
        h2s = [(m.start(), re.sub(r'<[^>]+>', '', m.group(1)).strip()) for m in
               re.finditer(r'<h2[^>]*>(.*?)</h2>', html, re.S)]
        entries = []
        for pos, h, t in anchors:
            if t.lower() in GENERIC:
                prior = [x for x in h2s if x[0] < pos]
                t = prior[-1][1] if prior else t
            entries.append((h, t))
    else:
        entries = [(h, t) for _, h, t in anchors]
    return url, headline, entries, t

# Reviewed name-variant equivalences (e.g. VN 'Elisabeth' = spoken 'Elizabeth').
# Entries are added ONLY at the minting checkpoint after a review of the specific date's
# pages. Never auto-derive variants. Each entry is a dated lock with its evidence:
#   REVIEWED_VARIANTS = {'elisabeth': {'as': 'elizabeth', 'locked': '2026-11-19',
#                                      'evidence': 'VN 11/19 index headline vs article body H1'}}
REVIEWED_VARIANTS = {}
SAINT_TITLES = {'saint','st','blessed','bl','b','v','of','the','and','virgin','martyr','martyrs',
                'pope','abbot','abbess','bishop','confessor','apostle','evangelist','founder',
                'foundress','priest','monk','nun','hermit','doctor','widow','queen','king'}

def saint_tokens(name):
    toks = []
    for w in re.findall(r'[a-z]+', name.lower()):
        v = REVIEWED_VARIANTS.get(w)
        if v: w = v['as']
        if w not in SAINT_TITLES and len(w) >= 2:
            toks.append(w)
    return toks

def h1_matches(h1, saint_name):
    want = set(saint_tokens(saint_name))
    if not want:
        return False
    got = set(saint_tokens(h1))
    return want.issubset(got)

ap = argparse.ArgumentParser()
ap.add_argument('--date', required=True)
ap.add_argument('--lang', default='en')
ap.add_argument('--intro-wav', required=True)
ap.add_argument('--intro-sha256', required=True)
ap.add_argument('--saint-name', required=True, help='confirmed spoken short form, e.g. "Saint Elizabeth of Hungary"')
ap.add_argument('--intro-text', required=True, help='EXACT minted intro text from the voice minter (checkpoint-owned); rendered on the intro card and recorded in the manifest')
ap.add_argument('--intro-text-sha256', required=True, help='sha256 of the exact intro text string (no trailing newline)')
ap.add_argument('--ask', default='their', choices=['her','his','their'])
ap.add_argument('--packs-dir', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packs'))
ap.add_argument('--outdir', required=True)
ap.add_argument('--attenuate-db', type=float, default=None, help='override; default auto from measured mix peak')
ap.add_argument('--resume', action='store_true', help='skip phases 4-7 when the phase-7 marker exists AND the saved input fingerprint matches (sandbox-timeout recovery)')
ap.add_argument('--saint-check', default='auto', choices=['auto','off'], help='auto: verify the locked saint LIVE against Vatican News (production). off: offline/test only, recorded in the manifest')
a = ap.parse_args()

for _k, _v in REVIEWED_VARIANTS.items():
    if not (isinstance(_v, dict) and _v.get('as') and _v.get('locked') and _v.get('evidence')):
        raise SystemExit(f'REVIEWED_VARIANTS[{_k!r}] must be a dated lock with evidence: '
          '{"as": <spoken token>, "locked": "YYYY-MM-DD", "evidence": <what was compared>}')
    datetime.date.fromisoformat(_v['locked'])

if a.lang != 'en':
    raise SystemExit(f'locale {a.lang!r} is NOT BUILT: the factory currently builds English only. '
      'The AR lane has no RTL card renderer and no Arabic texts yet (see RULE.md, "Staging a new pack" item 6). '
      'Failing closed instead of producing a wrong-language build.')

d = datetime.date.fromisoformat(a.date)
mystery = ROT[d.weekday()]
packdir = os.path.join(a.packs_dir, a.lang, mystery)
pack = json.load(open(os.path.join(packdir, 'pack.json')))
os.makedirs(a.outdir, exist_ok=True); os.makedirs(os.path.join(a.outdir,'cards'), exist_ok=True)
os.chdir(a.outdir)
print(f'== rosary-factory build_day: {a.date} ({d.strftime("%A")}) {a.lang}/{mystery} ==')

# 1. pin checks
donor = os.path.join(packdir, pack['donor_file'])
ds = sha256(donor); assert ds == pack['donor_sha256'], f'donor sha mismatch {ds}'
print('donor sha OK', ds[:12])
def art_path(n):
    for ext in ('.jpg', '.png'):
        p = os.path.join(packdir, 'art', f'{n}{ext}')
        if os.path.exists(p): return p
    return os.path.join(packdir, 'art', f'{n}.jpg')  # missing: let sha256() raise
for n, expect in pack['art_shas'].items():
    s = sha256(art_path(n))
    assert s == expect, f'art {n} sha mismatch {s}'
print('art shas OK 5/5')
ws = sha256(a.intro_wav); assert ws == a.intro_sha256, f'intro wav sha mismatch {ws}'
OFF = ffprobe_duration(a.intro_wav)
print(f'intro wav OK {ws[:12]} duration {OFF:.3f}')

# build fingerprint: binds every per-day input + pack pins + this code. --resume reuses a
# saved master ONLY when the fingerprint matches exactly.
CODE_SHA = sha256(os.path.abspath(__file__))
# every byte that can change the film: per-day inputs, ALL pack config/map/ledger/template
# files (not just the binary pins), the rendering options, and this code.
FINGERPRINT = hashlib.sha256(json.dumps({
  'date': a.date, 'lang': a.lang, 'mystery': mystery, 'saint_name': a.saint_name,
  'ask': a.ask, 'attenuate_db': a.attenuate_db, 'saint_check': a.saint_check,
  'intro_wav_sha256': ws, 'intro_text_sha256': a.intro_text_sha256,
  'donor_sha256': pack['donor_sha256'], 'art_shas': pack['art_shas'],
  'pack_json_sha256': sha256(os.path.join(packdir, 'pack.json')),
  'map_sha256': sha256(os.path.join(packdir, 'film-time-map.json')),
  'ledger_sha256': sha256(os.path.join(packdir, 'art-ledger.json')),
  'desc_template_sha256': sha256(os.path.join(packdir, pack.get('description_template', 'description-template.txt'))),
  'code_sha256': CODE_SHA}, sort_keys=True).encode('utf-8')).hexdigest()
print('fingerprint', FINGERPRINT[:16])

# 2. saint live check: the locked saint MUST verify against the live Vatican News index for
# this date. A mismatch refuses the build - never fall back silently. When the saint is
# verified on the index but has no detail page, the description links the index.
mm = f'{d.month:02d}'; dd = f'{d.day:02d}'
vn_entry = None
if a.saint_check == 'off':
    vn_index = headline = vn_url = None
    print('saint-check OFF: live Vatican News verification skipped (offline/test mode; recorded in manifest)')
else:
    vn_index, headline, vn_entries, vn_index_text = fetch_saint(mm, dd)
    want = set(saint_tokens(a.saint_name))
    if vn_entries:
        # bind ONE dated entry: the saint's distinctive tokens must all live in a single
        # index entry - never assembled across entries (a cross-entry mixture is a wrong saint).
        matches = [(h, t) for h, t in vn_entries if want and want.issubset(set(saint_tokens(t)))]
        if not matches:
            raise SystemExit(f'SAINT MISMATCH: {a.saint_name!r} matches no single dated entry on the '
              f'Vatican News saint index for {mm}/{dd} ({vn_index}). Entries present: '
              f'{[t for _, t in vn_entries][:8]}. Refusing to build - re-lock the saint at the minting checkpoint.')
        matches.sort(key=lambda m: len(set(saint_tokens(m[1]))))  # tightest entry wins
        href, entry_text = matches[0]
        vn_entry = {'text': entry_text, 'href': href}
        vn_url = f'{VN_BASE}{href}'
        # identity re-check: the entry page's own H1 must match the locked saint
        try:
            _req = urllib.request.Request(vn_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'})
            _body = urllib.request.urlopen(_req, timeout=15).read().decode('utf-8', 'ignore')
            _m1 = re.search(r'<h1[^>]*>(.*?)</h1>', _body, re.S)
            _h1 = re.sub(r'<[^>]+>', '', _m1.group(1)).strip() if _m1 else ''
            if not h1_matches(_h1, a.saint_name):
                raise SystemExit(f'SAINT MISMATCH: the dated entry page H1 {_h1!r} does not match '
                  f'{a.saint_name!r} ({vn_url}). Wrong-but-real page - refusing to build.')
        except SystemExit:
            raise
        except Exception:
            pass  # detail page unreachable: the dated-entry binding stands on its own
    else:
        # NO whole-page token fallback: a page-wide token-subset test can assemble a saint
        # from unrelated words. With no parseable dated entry, fail closed.
        raise SystemExit(f'SAINT CHECK FAILED: no parseable dated entries on the Vatican News saint index '
          f'for {mm}/{dd} ({vn_index}). The index markup changed or the fetch was intercepted. '
          'Refusing to build: repair the dated-entry parser (fetch_saint) or re-lock the saint '
          'with a separately reviewed dated lock at the minting checkpoint.')
print('Vatican News:', vn_url, '| index:', vn_index, '| entry:', vn_entry); print('headline:', headline)

# 3. load pack map, rebase
m = json.load(open(os.path.join(packdir, 'film-time-map.json')))
EV = m['events']
for e in EV:
    if isinstance(e.get('param'), list): e['param'] = tuple(e['param'])
REBASE = OFF - pack['map_intro_s']
donor_start, donor_speech_end = pack['donor_audio_interval']
speech_end_map = donor_speech_end + (pack['map_intro_s'] - donor_start)
SPEECH_END = speech_end_map + REBASE
CREDITS_S = pack['credits_s']; CCS = pack['credit_card_s']
BODY_END = SPEECH_END + CREDITS_S
DONOR_TOTAL_END = donor_speech_end + CREDITS_S
print(f'REBASE {REBASE:+.3f} SPEECH_END {SPEECH_END:.3f} FILM_TOTAL {BODY_END:.3f}')

textmap = {e['source_key']: e['text'] for e in EV if e.get('source_key') and e.get('text') is not None}
PR = {k: textmap[k] for k in ('our_father','hail_mary','glory_be','fatima','apostles_creed','hail_holy_queen','let_us_pray','rosary_concluding_prayer')}
VR_V = [e['text'] for e in EV if e['kind'] == 'VR'][0]
VR_R = ([e['text'] for e in EV if e['kind'] == 'VRR'] or [None])[0] or pack.get('vr_r_fallback')
THANKS_T = pack['thanks_text'] if pack.get('thanks_text') else [e['text'] for e in EV if e['kind']=='THANKS'][0]
medintro, medbead = {}, {}
for e in EV:
    if e['kind'] == 'MED':
        p = e['param']
        if p[0] == 'intro': medintro[p[1]] = e['text']
        else: medbead[(p[1], p[2])] = e['text']
titles = {int(k): v for k, v in pack['titles'].items()}
LBL = pack['label']

BG='#111217'; MUTE='#c0b8ac'; IVORY='#f3eee6'; LINE='#38383b'; GOLD='#d3c5aa'; DIM='#d8d2c8'; DOTOFF='#6b675f'
def f(n, serif=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVu'+('Serif' if serif else 'Sans')+'.ttf', n)
def wrap(s, font, width, dr, hard=False):
    out=[]; cur=''
    for w0 in s.split():
        parts=[w0]
        if hard:
            while dr.textlength(parts[-1],font=font)>width:
                p=parts[-1]; k=len(p)
                while k>1 and dr.textlength(p[:k],font=font)>width: k-=1
                parts[-1]=p[:k]; parts.append(p[k:])
        for w in parts:
            t=(cur+' '+w).strip() if cur else w
            if cur and dr.textlength(t,font=font)>width: out.append(cur); cur=w
            else: cur=t
    if cur: out.append(cur)
    return out
ART = {n: Image.open(art_path(f'g{n}')).convert('RGB') for n in (1,2,3,4,5)}
overflow = []
def card(label, title, decade, meditation, prayer_label, prayer_text, dots, cid='?'):
    im=Image.new('RGB',(1280,720),BG); dr=ImageDraw.Draw(im)
    dr.text((48,26),label,font=f(20),fill=MUTE)
    if title:
        if dr.textlength(title,font=f(38,True)) > 1184:
            raise SystemExit(f'TITLE OVERFLOW on card {cid}: {title!r} is wider than 1184px at the title font. '
              'Fix the pack title - never ship an overflowing card.')
        dr.text((48,56),title,font=f(38,True),fill=IVORY)
    dr.line((48,112,1232,112),fill=LINE)
    if decade:
        ar=ART[decade].copy(); ar.thumbnail((418,540)); im.paste(ar,(48+(418-ar.width)//2,132+(540-ar.height)//2))
    x=518 if decade else 120; w=700 if decade else 1040
    scale=1.0
    while True:
        mf=max(18,round(29*scale)); ml=max(26,round(38*scale))
        pf=max(16,round(25*scale)); pl=max(22,round(33*scale))
        ll=max(24,round(36*scale)); gap=max(8,round(14*scale))
        yfit=150
        if meditation: yfit+=len(wrap(meditation,f(mf),w,dr))*ml+gap
        if prayer_label: yfit+=ll
        if prayer_text: yfit+=len(wrap(prayer_text,f(pf),w,dr))*pl
        if yfit<=640 or scale<=0.76: break
        scale-=0.04
    y=150
    if meditation:
        for ln in wrap(meditation,f(mf),w,dr): dr.text((x,y),ln,font=f(mf),fill=IVORY); y+=ml
        y+=gap
    if prayer_label:
        dr.text((x,y),prayer_label,font=f(22),fill=GOLD); y+=ll
    if prayer_text:
        for ln in wrap(prayer_text,f(pf),w,dr): dr.text((x,y),ln,font=f(pf),fill=DIM); y+=pl
    if y>646:
        raise SystemExit(f'BODY OVERFLOW on card {cid} ({label} / {title}): text bottom {y}px > 646px '
          f'(scale {scale:.2f}, floor 0.76). Shorten the pack text - never ship an overflowing card.')
    if dots is not None:
        for i in range(10):
            cx=x+i*30; cy=664
            if i<dots: dr.ellipse((cx-7,cy-7,cx+7,cy+7),fill=IVORY)
            else: dr.ellipse((cx-7,cy-7,cx+7,cy+7),outline=DOTOFF,width=2)
    return im

date_line = f'{d.strftime("%A").upper()}, {MONTHS[d.month-1].upper()} {d.day}'
_tsha = hashlib.sha256(a.intro_text.encode('utf-8')).hexdigest()
assert _tsha == a.intro_text_sha256, f'intro text sha mismatch: {_tsha}'
spoken = a.intro_text
def intro_card():
    im=Image.new('RGB',(1280,720),BG); dr=ImageDraw.Draw(im)
    dr.text((48,26),date_line,font=f(20),fill=MUTE)
    if dr.textlength(a.saint_name,font=f(38,True)) > 1184:
        raise SystemExit(f'SAINT-TITLE OVERFLOW on the intro card: {a.saint_name!r} is wider than 1184px. '
          'Use the confirmed SHORT spoken form.')
    dr.text((48,56),a.saint_name,font=f(38,True),fill=IVORY)
    dr.line((48,112,1232,112),fill=LINE)
    y=150
    for ln in wrap(spoken,f(29),1140,dr): dr.text((48,y),ln,font=f(29),fill=IVORY); y+=38
    if y > 646:
        raise SystemExit(f'INTRO OVERFLOW: the minted intro text bottoms at {y}px > 646px. '
          'Re-mint a shorter intro - never ship an overflowing card.')
    return im

import glob
master = f'master-{a.lang}-{a.date}-{mystery}.mp4'
PHASE7_DONE = False
if a.resume and os.path.exists('phase7.ok') and os.path.exists(master) and os.path.exists('phase7-state.json'):
    _saved = json.load(open('phase7-state.json'))
    if _saved.get('fingerprint') != FINGERPRINT:
        raise SystemExit('RESUME REFUSED: the saved phase-7 state was built from different inputs '
          f'(saved fingerprint {_saved.get("fingerprint","<none>")[:12]} != current {FINGERPRINT[:12]}; '
          'intro WAV/text, any pack file, options, saint, date or code changed). Delete phase7.ok '
          'and the saved master to rebuild from scratch.')
    _msha = _saved.get('master_sha256')
    if not _msha or sha256(master) != _msha:
        raise SystemExit('RESUME REFUSED: the saved master bytes do not match the master hash recorded '
          'at build time (replaced, truncated or tampered master). Delete phase7.ok and the saved '
          'master to rebuild from scratch.')
    PHASE7_DONE = True
if not PHASE7_DONE:
    # 4. events -> cards
    ev=[]
    for e in EV:
        k=e['kind']
        if k in ('intro','CREDIT'): continue
        t=e['film_start']+REBASE
        if k=='VR_R': k='VRR'
        ev.append((t,k,e['param'],e))
    ev.sort(key=lambda z:z[0])
    bad=[(ev[i-1][1:3],ev[i][1:3]) for i in range(1,len(ev)) if ev[i][0]<=ev[i-1][0]]
    assert not bad, f'non-monotonic {bad[:3]}'
    prayers={'OF':('Our Father',PR['our_father']),'GB':('Glory Be',PR['glory_be']),'FATIMA':('Fatima Prayer',PR['fatima']),
     'CREED':("The Apostles' Creed",PR['apostles_creed']),'HHQ':('Hail, Holy Queen',PR['hail_holy_queen']),
     'LETPRAY':('Let Us Pray',PR['let_us_pray']),'CONCL':('Concluding Prayer',PR['rosary_concluding_prayer']),
     'SOC':('Sign of the Cross','In the name of the Father, and of the Son, and of the Holy Spirit. Amen.')}
    entries=[]; fmap=[]; cur_med={}
    intro_card().save('cards/intro.png')
    entries.append(('cards/intro.png',0.0,OFF))
    fmap.append({'card':'intro.png','film_start':0.0,'film_end':round(OFF,3),'kind':'intro','source':'rosary-factory build_day (text-only, fresh)'})
    for idx,(t,kind,p,src) in enumerate(ev):
        end=ev[idx+1][0] if idx+1<len(ev) else SPEECH_END
        cid=f'c{idx:03d}'
        if kind=='FAM': c=card('DAILY ROSARY',pack['fam_title'],None,None,None,None,None,cid)
        elif kind=='ANN':
            cur_med[p]=medintro[p]; c=card(LBL,titles[p],p,cur_med[p],None,None,0,cid)
        elif kind=='MED':
            if p[0]=='intro': c=card(LBL,titles[p[1]],p[1],medintro[p[1]],None,None,0,cid)
            else: cur_med[p[1]]=medbead[(p[1],p[2])]; c=card(LBL,titles[p[1]],p[1],cur_med[p[1]],None,None,p[2],cid)
        elif kind=='VR':
            if pack['vr_style']=='combined': c=card('THE '+pack['fam_title'][4:].upper() if False else 'THE '+LBL,None,None,None,'V. '+VR_V,'R. '+VR_R,None,cid)
            else: c=card('THE '+LBL,None,None,None,'V.',VR_V,None,cid)
        elif kind=='VRR': c=card('THE '+LBL,None,None,None,'R.',VR_R,None,cid)
        elif kind=='HM':
            sec,b=p; dn=sec if sec else 0
            c=card(LBL if dn else 'THE '+LBL,titles.get(dn) if dn else None,dn or None,cur_med.get(dn) if dn else None,'Hail Mary',PR['hail_mary'],b if dn else None,cid)
        elif kind in prayers:
            lb,tx=prayers[kind]; dn=p if isinstance(p,int) and p else None
            c=card(LBL if dn else 'THE '+LBL,titles.get(dn) if dn else None,dn,cur_med.get(dn) if dn else None,lb,tx,(10 if (dn and kind in('GB','FATIMA')) else (0 if dn else None)),cid)
        elif kind=='INTENT': c=card('THE '+LBL,None,None,None,'Intention',src.get('text'),None,cid)
        elif kind=='THANKS': c=card('THE '+LBL,None,None,None,None,THANKS_T,None,cid)
        else: raise SystemExit(f'unhandled kind {kind}')
        path=f'cards/{cid}.png'; c.save(path)
        entries.append((path,t,end))
        fmap.append({'card':f'{cid}.png','film_start':round(t,3),'film_end':round(end,3),'kind':kind,
                     'param':list(p) if isinstance(p,tuple) else p,'source_key':src.get('source_key'),
                     'source_sha256':src.get('source_sha256'),'text':src.get('text')})
    print('body cards rendered:', len(entries), '| overflow:', overflow if overflow else 'none')

    # 5. credits (per pack mode, URLs hard-wrapped)
    led = json.load(open(os.path.join(packdir,'art-ledger.json')))
    artworks = [x for x in led['artworks'] if x['slot'].split('_')[0] == mystery] or led['artworks']
    artworks = sorted(artworks, key=lambda x: x['slot'])
    CC = led.get('credit_copy', {}).get('cards', {})
    cr_bottoms = []
    for i, aw in enumerate(artworks[:5]):
        n = aw['slot'].split('_')[1]
        if pack['credits_mode'] == 'ledger_credit_copy':
            assert aw['slot'] in CC, f'missing credit_copy for {aw["slot"]}'
            body = CC[aw['slot']]
            clines = None
        elif pack['credits_mode'] == 'commons_lines':
            clines = [f"Work: {aw['artist']}, {aw['work']}.",
                      "Source marks this artwork reproduction public domain.",
                      "Source: Wikimedia Commons.",
                      f"Commons page: {aw['source_url']}"]
            if aw.get('caveat'):
                clines.append(f"Note: {aw['caveat']}")
            body = None
        else:  # giotto_template
            body = (f"{aw['artist']}. {aw['work']}. Source marks this artwork reproduction public domain. "
                    f"Source: Web Gallery of Art, via Wikimedia Commons. Commons page: {aw['source_url']} "
                    f"Note: Italian law may restrict some commercial uses of Italian heritage imagery within Italy; applicability to this scan is unverified.")
            clines = None
        im = Image.new('RGB',(1280,720),BG); dr = ImageDraw.Draw(im)
        dr.text((48,26),'ART CREDIT',font=f(20),fill=MUTE)
        dr.text((48,56),aw['title'],font=f(38,True),fill=IVORY)
        dr.line((48,112,1232,112),fill=LINE)
        ar = ART[int(n)].copy(); ar.thumbnail((418,540)); im.paste(ar,(48+(418-ar.width)//2,132+(540-ar.height)//2))
        y = 150
        if clines is not None:
            for para in clines:
                for ln in wrap(para, f(20), 700, dr, hard=True):
                    dr.text((518,y),ln,font=f(20),fill=DIM); y += 28
                y += 10
        else:
            for ln in wrap(body, f(20), 700, dr, hard=True):
                dr.text((518,y),ln,font=f(20),fill=DIM); y += 28
        assert y <= 700, f'credit overflow {aw["slot"]} bottom={y}'
        cr_bottoms.append(y)
        im.save(f'cards/cr{i}.png')
        entries.append((f'cards/cr{i}.png', SPEECH_END + i*CCS, SPEECH_END + (i+1)*CCS))
        fmap.append({'card':f'cr{i}.png','film_start':round(SPEECH_END+i*CCS,3),'film_end':round(SPEECH_END+(i+1)*CCS,3),
                     'kind':'CREDIT','param':i,'source':f'rosary-factory credits ({pack["credits_mode"]})'})
    print('credits rendered: 5 | bottoms', cr_bottoms)

    # 6. NCC proof: rendered cards vs donor frames at equal content timestamps
    import numpy as np
    def donor_frame(t):
        sh(['ffmpeg','-y','-v','error','-ss',f'{t:.3f}','-i',donor,'-frames:v','1','/tmp/rf_df.png'])
        return np.asarray(Image.open('/tmp/rf_df.png').convert('L'), dtype=np.float64)
    def ncc(aa, bb):
        aa=aa-aa.mean(); bb=bb-bb.mean(); return float((aa*bb).sum()/np.sqrt((aa*aa).sum()*(bb*bb).sum()))
    sample_idx = [1, 2, len(ev)//4, len(ev)//2, 3*len(ev)//4, len(ev)-3, len(ev)-2, len(ev)-1]
    sample_idx = sorted(set(max(1, min(i, len(ev)-1)) for i in sample_idx))
    nccs = []
    for i in sample_idx:
        t, kind, p, src = ev[i]
        end = ev[i+1][0] if i+1 < len(ev) else SPEECH_END
        t_mid = (t + end) / 2
        donor_t = t_mid - REBASE - (pack['map_intro_s'] - donor_start)
        card_img = np.asarray(Image.open(f'cards/c{i:03d}.png').convert('L').resize((640,360)), dtype=np.float64)
        v = ncc(card_img, donor_frame(donor_t))
        nccs.append((kind, f'c{i:03d}', round(v,4)))
    print('NCC samples:', nccs)
    if pack.get('donor_layout') == 'legacy':
        # the donor predates the factory card layout: its frames are not a visual reference
        # (audio-only donor). Samples are printed for the record, not asserted.
        print('NCC vs donor NOT asserted: pack donor_layout=legacy (donor predates the factory card layout)')
    else:
        assert all(v >= 0.99 for _,_,v in nccs), 'NCC below 0.99 - card content mismatch vs donor'

    # 7. assemble: fresh intro segment + donor body span + audio (single AAC encode w/ attenuation)
    sh(['ffmpeg','-y','-v','error','-loop','1','-framerate','20','-t',f'{OFF:.3f}','-i','cards/intro.png',
        '-vf','scale=640:360','-r','20','-c:v','libx264','-preset','fast','-b:v','250k','-maxrate','350k','-bufsize','700k',
        '-pix_fmt','yuv420p','-an','vintro.mp4'])
    if pack.get('donor_layout') == 'legacy':
        # audio-only donor: assemble the body from THIS build's rendered cards - donor frames are
        # never used, so the fresh INTENT/art/credit cards are what the viewer actually sees.
        # chunked concat-filter assembly: ~24 cards per chunk (memory-bounded: each -loop 1
        # input holds a decoder queue, so 140+ inputs in one graph OOMs). Chunk encodes are
        # lossless (qp 0); the final pass joins chunks with the concat filter (frame-exact)
        # at the body bitrate. Frame counts are cumulative-boundary exact (boundary k =
        # round((t_k-OFF)*20)), so quantization never accumulates and audio stays in sync.
        cumf = lambda t: int(round((t - OFF) * 20))
        CH = 24
        chunks = []
        for ci in range(0, len(ev), CH):
            grp = list(range(ci, min(ci + CH, len(ev))))
            args = ['ffmpeg','-y','-v','error']
            parts = []; labels = []
            for j, i in enumerate(grp):
                end = ev[i+1][0] if i+1 < len(ev) else SPEECH_END
                nf = max(1, cumf(end) - cumf(ev[i][0]))
                args += ['-loop','1','-framerate','20','-i',f'cards/c{i:03d}.png']
                parts.append(f'[{j}:v]scale=640:360,trim=end_frame={nf},setpts=PTS-STARTPTS[s{j}]')
                labels.append(f'[s{j}]')
            fc = ';'.join(parts) + ';' + ''.join(labels) + f'concat=n={len(labels)}:v=1:a=0[v]'
            sh(args + ['-filter_complex', fc, '-map','[v]','-r','20','-c:v','libx264','-preset','fast',
                       '-qp','0','-pix_fmt','yuv420p','-an', f'vchunk{ci//CH:02d}.mp4'])
            chunks.append(f'vchunk{ci//CH:02d}.mp4')
        args = ['ffmpeg','-y','-v','error']
        for cn in chunks: args += ['-i', cn]
        fc = ''.join(f'[{k}:v]' for k in range(len(chunks))) + f'concat=n={len(chunks)}:v=1:a=0[v]'
        sh(args + ['-filter_complex', fc, '-map','[v]','-r','20','-c:v','libx264','-preset','fast',
                   '-b:v','24k','-maxrate','30k','-bufsize','60k','-pix_fmt','yuv420p','-an','vbody.mp4'])
        vb = ffprobe_duration('vbody.mp4')
        assert abs(vb - (SPEECH_END - OFF)) < 0.3, f'legacy vbody {vb:.3f}s != body span {SPEECH_END - OFF:.3f}s'
        print(f'legacy donor_layout: vbody assembled from {len(ev)} fresh cards ({vb:.3f}s) - donor frames unused')
        VBODY_SRC = 'fresh cards (legacy donor_layout)'
    else:
        sh(['ffmpeg','-y','-v','error','-ss',f'{donor_start:.3f}','-to',f'{donor_speech_end:.3f}','-i',donor,'-map','0:v',
            '-r','20','-c:v','libx264','-preset','fast','-b:v','24k','-maxrate','30k','-bufsize','60k','-pix_fmt','yuv420p','-an','vbody.mp4'])
        VBODY_SRC = 'donor video span'
    # credits are ALWAYS fresh-encoded from this build's rendered cards (donor credit pixels may predate the current ledger)
    for i in range(5):
        sh(['ffmpeg','-y','-v','error','-loop','1','-framerate','20','-t',f'{CCS:.3f}','-i',f'cards/cr{i}.png',
            '-vf','scale=640:360','-r','20','-c:v','libx264','-preset','fast','-b:v','250k','-maxrate','350k','-bufsize','700k',
            '-pix_fmt','yuv420p','-an',f'vcr{i}.mp4'])
    open('crcat.txt','w').write(''.join(f"file 'vcr{i}.mp4'\n" for i in range(5)))
    sh(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','crcat.txt','-c','copy','vcredits.mp4'])
    vd = ffprobe_duration('vcredits.mp4')
    assert abs(vd - CREDITS_S) < 0.3, f'credits segment {vd} != {CREDITS_S}'
    open('vcat.txt','w').write("file 'vintro.mp4'\nfile 'vbody.mp4'\nfile 'vcredits.mp4'\n")
    sh(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','vcat.txt','-c','copy','video-final.mp4'])
    # measure mix peak pre-encode to choose attenuation
    mix = (f"[0:a]aformat=sample_rates=44100:channel_layouts=mono[a0];"
           f"[1:a]aformat=sample_rates=44100:channel_layouts=mono[a1];"
           f"[a0][a1][2:a]concat=n=3:v=0:a=1[mix]")
    r = subprocess.run(['ffmpeg','-i',a.intro_wav,'-ss',f'{donor_start:.3f}','-to',f'{donor_speech_end:.3f}','-i',donor,
        '-f','lavfi','-t',f'{CREDITS_S:.3f}','-i','anullsrc=r=44100:cl=mono','-filter_complex',mix + ',[mix]ebur128=peak=true[m]',
        '-map','[m]','-f','null','-'],capture_output=True,text=True)
    pk = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    raw_peak = float(pk[-1])
    att = a.attenuate_db if a.attenuate_db is not None else (0.0 if raw_peak <= -2.5 else round(-3.0 - raw_peak, 1))
    print(f'mix raw peak {raw_peak} dBFS -> attenuation {att} dB')
    sh(['ffmpeg','-y','-v','error','-i',a.intro_wav,'-ss',f'{donor_start:.3f}','-to',f'{donor_speech_end:.3f}','-i',donor,
        '-f','lavfi','-t',f'{CREDITS_S:.3f}','-i','anullsrc=r=44100:cl=mono','-filter_complex',mix + f',[mix]volume={att}dB[a]',
        '-map','[a]','-c:a','aac','-b:a','52k','-ar','44100','-ac','1','audio-final.m4a'])
    master = f'master-{a.lang}-{a.date}-{mystery}.mp4'
    sh(['ffmpeg','-y','-v','error','-i','video-final.mp4','-i','audio-final.m4a','-map','0:v','-map','1:a',
        '-c:v','copy','-c:a','copy','-movflags','+faststart',master])


    json.dump({'fingerprint': FINGERPRINT, 'master_sha256': sha256(master), 'fmap': fmap, 'nccs': nccs,
               'overflow': overflow, 'cr_bottoms': cr_bottoms, 'att': att, 'vbody_source': VBODY_SRC},
              open('phase7-state.json','w'))
    open('phase7.ok','w').write('ok\n')
else:
    _st = json.load(open('phase7-state.json'))
    fmap, nccs, overflow, cr_bottoms, att = _st['fmap'], _st['nccs'], _st['overflow'], _st['cr_bottoms'], _st['att']
    VBODY_SRC = _st.get('vbody_source', 'donor video span')
    print('RESUME: phases 4-7 skipped (phase7.ok + master present)')
# 8. QA battery
r = subprocess.run(['ffmpeg','-v','error','-xerror','-i',master,'-f','null','-'],capture_output=True,text=True)
assert r.returncode == 0, 'decode errors: '+r.stderr[:400]
dur = ffprobe_duration(master)
EXPECTED_DUR = BODY_END
assert abs(dur - EXPECTED_DUR) < 0.5, f'DURATION MISMATCH: master {dur:.3f}s vs expected {EXPECTED_DUR:.3f}s (intro {OFF:.3f}s + body span + credits {CREDITS_S:.3f}s)'
r = subprocess.run(['ffmpeg','-i',master,'-map','0:a','-af','volumedetect,ebur128=peak=true','-f','null','-'],capture_output=True,text=True)
mean = float(re.findall(r'mean_volume: (-?[\d.]+) dB', r.stderr)[-1])
mx = float(re.findall(r'max_volume: (-?[\d.]+) dB', r.stderr)[-1])
tp = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)[-1])
assert tp <= -2.0, f'levels gate FAIL tp={tp}'
msha = sha256(master); msize = os.path.getsize(master)
for nm, t in (('qa-intro.png', OFF/2), ('qa-med.png', 300.0), ('qa-credit.png', SPEECH_END + 2*CCS + 1)):
    sh(['ffmpeg','-y','-v','error','-ss',str(t),'-i',master,'-frames:v','1',nm])
print(f'MASTER {master} {msize} B {dur:.3f}s sha {msha}')
print(f'LEVELS mean {mean} max {mx} TP {tp} dBFS (gate <= -2 PASS)')

# 9. description
def ts(s):
    s=int(s); return f'{s//60:02d}:{s%60:02d}'
chap=[]
for sel, lab in pack['chapters']:
    if sel=='intro': chap.append(('00:00', a.saint_name + ('' if any(s2=='SOC' for s2,_ in pack['chapters']) else ' / opening prayers')))
    elif sel=='ANN': chap.append((ts([e for e in fmap if e['kind']=='ANN' and e['param']==lab][0]['film_start']), titles[lab]))
    elif sel=='SOC': chap.append((ts([e for e in fmap if e['kind']=='SOC'][0]['film_start']), lab))
    elif sel=='HHQ': chap.append((ts([e for e in fmap if e['kind']=='HHQ'][0]['film_start']), lab))
    elif sel=='CREDIT': chap.append((ts([e for e in fmap if e['kind']=='CREDIT'][0]['film_start']), lab))
tpl = open(os.path.join(packdir, pack['description_template'])).read()
desc = tpl.replace('{DATE_LONG}', d.strftime('%A, ') + f'{MONTHS[d.month-1]} {d.day}, {d.year}') \
          .replace('{SAINT}', a.saint_name).replace('{ASK}', a.ask) \
          .replace('{CHAPTERS}', '\n'.join(f'{t} {l}' for t,l in chap)) \
          .replace('{VN_URL}', vn_index or vn_url or '(saint source not verified - saint-check off)')  # description links the stable day index (EN43/EN52-54 convention); the exact bound entry page is recorded in the manifest
# normalize to exactly one trailing newline so generated bytes equal the published artifact
# (YouTube stores the description with a single trailing \n; the template emits \n\n).
open(f'description-{a.date}.txt','w').write(desc.rstrip('\n') + '\n')

# 10. time map + ledger note + manifest
json.dump({'film': master[:-4], 'offset_intro_s': round(OFF,3), 'donor_sha256': pack['donor_sha256'],
  'donor_audio_interval_film': list(pack['donor_audio_interval']), 'speech_end_body_s': round(SPEECH_END-OFF,3),
  'credits_s': CREDITS_S, 'body_end_s': round(BODY_END-OFF,3), 'film_total_s': round(BODY_END,3),
  'built_by': 'rosary-factory build_day.py', 'vbody_source': VBODY_SRC, 'events': fmap}, open(f'film-time-map-{a.date}.json','w'), indent=1)
manifest = {'date': a.date, 'weekday': d.strftime('%A'), 'lang': a.lang, 'mystery': mystery,
  'fingerprint': FINGERPRINT, 'saint_check': a.saint_check,
  'saint': a.saint_name, 'vatican_news': vn_url, 'vn_entry': vn_entry, 'vn_headline': headline,
  'intro_wav_sha256': ws, 'intro_text': spoken, 'intro_dur_s': round(OFF,3),
  'donor_sha256': pack['donor_sha256'], 'art_shas': pack['art_shas'],
  'master': master, 'master_sha256': msha, 'master_bytes': msize, 'duration_s': round(dur,3),
  'levels': {'mean_db': mean, 'max_db': mx, 'true_peak_dbfs': tp, 'attenuation_db': att},
  'ncc_samples': nccs, 'overflow': overflow, 'credit_bottoms': cr_bottoms}
json.dump(manifest, open(f'manifest-{a.date}.json','w'), indent=1)
print('WROTE', master, f'description-{a.date}.txt', f'film-time-map-{a.date}.json', f'manifest-{a.date}.json')
print('== BUILD OK ==')
