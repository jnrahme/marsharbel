#!/usr/bin/env python3
"""Rosary factory - daily trigger (prep phase).

  python3 new_day.py 2026-11-22

Resolves the day's mystery set from the locked rotation, fetches the saint of the day
LIVE from Vatican News, checks the pack is staged, and prints the exact intro spec to
hand to the voice-minting checkpoint (the owner's approved voice and direction).
After the WAV arrives:

  python3 build_day.py --date 2026-11-22 --lang en --intro-wav <wav> --intro-sha256 <sha> \
      --intro-text "<exact minted text>" --intro-text-sha256 <sha> \
      --saint-name "<confirmed spoken form>" --ask her|his|their --outdir out/2026-11-22

The intro WAV is the ONLY generated piece per day. Everything else is fixed parts.
"""
import datetime, json, os, re, sys, urllib.request

ROT = {0:'joyful',1:'sorrowful',2:'glorious',3:'luminous',4:'sorrowful',5:'joyful',6:'glorious'}
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
ORD = {1:'first',2:'second',3:'third',4:'fourth',5:'fifth',6:'sixth',7:'seventh',8:'eighth',9:'ninth',10:'tenth',
 11:'eleventh',12:'twelfth',13:'thirteenth',14:'fourteenth',15:'fifteenth',16:'sixteenth',17:'seventeenth',
 18:'eighteenth',19:'nineteenth',20:'twentieth',21:'twenty-first',22:'twenty-second',23:'twenty-third',
 24:'twenty-fourth',25:'twenty-fifth',26:'twenty-sixth',27:'twenty-seventh',28:'twenty-eighth',29:'twenty-ninth',
 30:'thirtieth',31:'thirty-first'}

date = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else 'en'
d = datetime.date.fromisoformat(date)
mystery = ROT[d.weekday()]
here = os.path.dirname(os.path.abspath(__file__))
packdir = os.path.join(here, 'packs', lang, mystery)
reg = json.load(open(os.path.join(here, 'packs', 'registry.json')))
status = reg['packs'].get(f'{lang}/{mystery}', {}).get('status', 'UNKNOWN')

mm, dd = f'{d.month:02d}', f'{d.day:02d}'
url = f'https://www.vaticannews.va/en/saints/{mm}/{dd}.html'
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'})
t = urllib.request.urlopen(req, timeout=30).read().decode('utf-8','ignore')
t = re.sub(r'<script.*?</script>','',t,flags=re.S); t = re.sub(r'<style.*?</style>','',t,flags=re.S)
t = re.sub(r'<[^>]+>',' ',t); import html as H; t = H.unescape(t); t = re.sub(r'\s+',' ',t)
m = re.search(r'journey of faith\. (.+?)(?: Born| When| In \d| He | She | Died| became | History | her | his | are | were | A [A-Z]| Your contribution| St\.? \w+ (?:was|is))', t)
headline = m.group(1).strip() if m else '(parse manually from the page)'
headline = re.sub(r'\s+(History|Tradition|Legend)\b.*$', '', headline).strip()
headline = re.sub(r'[\s,]+St\.?$', '', headline).strip().rstrip(',:;')
def _norm(w): return re.sub(r'[^A-Za-z]', '', w).lower()
_t = headline.split()
for _k in range(1, len(_t)):
    if len(_t) - _k <= _k and [_norm(w) for w in _t[_k:]] == [_norm(w) for w in _t[:len(_t)-_k]]:
        headline = ' '.join(_t[:_k]); break

print(f'DATE      {date} ({d.strftime("%A")})')
print(f'MYSTERY   {mystery}  (locked rotation Mon=Joyful Tue=Sorrowful Wed=Glorious Thu=Luminous Fri=Sorrowful Sat=Joyful Sun=Glorious)')
print(f'PACK      {packdir}  [{"staged" if os.path.exists(os.path.join(packdir,"pack.json")) else "NOT STAGED - run bootstrap_packs.py / see RULE.md"}]')
print(f'REGISTRY  {status}')
print(f'SAINT URL {url}')
print(f'HEADLINE  {headline}')
print()
print('INTAKE FORM for the voice-minting checkpoint:')
print('  voice: the standing approved voice for this lane')
print('  direction: "Natural conversational pace - the same voice, speed and warmth as when speaking with a friend. Expressive and heartfelt in the prayer with gentle emotion, but normal speaking speed. Not slow, not theatrical."')
print(f'  text template: "Today, {MONTHS[d.month-1]} {ORD[d.day]}, we remember <SAINT>. <SAINT>, pray for us."')
print('  <SAINT> = confirmed short spoken form of the headline (fix source typos; this confirmation is the minting checkpoint).')
print('  reply with the WAV + its sha256 + text_sha256, then run build_day.py as shown in the header of this script.')
