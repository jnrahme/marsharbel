#!/usr/bin/env python3
"""Offline negative tests for build_day.py's hard gates. Two modes, both offline:

A. Gate refusals with --saint-check off and a tiny synthetic pack in a temp dir.
B. Saint-lock tests against a MOCKED Vatican News served by a local HTTP server
   (RF_VN_BASE override): wrong-but-real saints and cross-entry token mixtures must
   refuse; a correctly bound dated entry must pass the saint gate.

Every case must make the build FAIL with the expected refusal (or, for B3, must NOT fail
at the saint gate). A passing build is a test failure.
Run from the factory root:  python3 tests/negative_tests.py
"""
import hashlib, json, os, subprocess, sys, tempfile, threading
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, 'build_day.py')
fails = []

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def run(args, expect, name, env_extra=None):
    env = dict(os.environ); env.update(env_extra or {})
    r = subprocess.run([sys.executable, BUILD] + args, capture_output=True, text=True,
                       cwd=ROOT, timeout=300, env=env)
    out = r.stdout + r.stderr
    if r.returncode == 0:
        fails.append(f'{name}: build PASSED, expected refusal'); print(f'FAIL {name}: build passed'); return None
    if expect and expect not in out:
        fails.append(f'{name}: refused but without {expect!r}: {out[-300:]}')
        print(f'FAIL {name}: wrong refusal: {out[-200:]}'); return None
    print(f'pass {name}'); return out

tmp = tempfile.mkdtemp(prefix='rf-negtest-')
packs = os.path.join(tmp, 'packs'); pd = os.path.join(packs, 'en', 'joyful')
os.makedirs(os.path.join(pd, 'art'))
DONOR = os.path.join(pd, 'donor.mp4')
WAV = os.path.join(tmp, 'intro.wav')
def make_donor(color):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'color=c={color}:s=640x360:r=20:d=3',
                    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '3', '-pix_fmt', 'yuv420p',
                    DONOR], check=True)
make_donor('black')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-t', '1', WAV], check=True)
art_shas = {}
for i in (1, 2, 3, 4, 5):
    p = os.path.join(pd, 'art', f'g{i}.jpg')
    Image.new('RGB', (40, 40), (i * 40, 10, 10)).save(p)
    art_shas[f'g{i}'] = sha256(p)
TEXT = 'Today we remember Saint Test. Saint Test, pray for us.'
TEXT2 = 'Today we remember Somebody Else entirely, changed words.'
text_sha = hashlib.sha256(TEXT.encode()).hexdigest()
text2_sha = hashlib.sha256(TEXT2.encode()).hexdigest()
wav_sha = sha256(WAV)
pack = {'donor_file': 'donor.mp4', 'donor_sha256': sha256(DONOR),
        'donor_audio_interval': [0.0, 3.0], 'map_intro_s': 0.0, 'credits_s': 0.5, 'credit_card_s': 0.1,
        'label': 'JOYFUL MYSTERIES', 'fam_title': 'The Joyful Mysteries',
        'titles': {'1': 'T1', '2': 'T2', '3': 'T3', '4': 'T4', '5': 'T5'},
        'vr_style': 'split', 'vr_r_fallback': 'Amen.', 'thanks_text': 'Thank you.',
        'credits_mode': 'commons_lines', 'art_shas': art_shas, 'chapters': [],
        'description_template': 'description-template.txt'}
PACK_JSON = os.path.join(pd, 'pack.json')
MAP_JSON = os.path.join(pd, 'film-time-map.json')
LEDGER_JSON = os.path.join(pd, 'art-ledger.json')
DESC_TXT = os.path.join(pd, 'description-template.txt')
def save_pack(pk): json.dump(pk, open(PACK_JSON, 'w'))
save_pack(pack)
open(DESC_TXT, 'w').write('{DATE_LONG} {SAINT} {ASK}\n{CHAPTERS}\n{VN_URL}\n')
json.dump({'artworks': []}, open(LEDGER_JSON, 'w'))
PRAYERS = ['our_father', 'hail_mary', 'glory_be', 'fatima', 'apostles_creed',
           'hail_holy_queen', 'let_us_pray', 'rosary_concluding_prayer']
def write_map(extra):
    ev = [{'film_start': round(0.10 + i * 0.01, 3), 'kind': 'HM', 'param': [0, i + 1],
           'source_key': k, 'text': 'x'} for i, k in enumerate(PRAYERS)]
    ev.append({'film_start': 0.20, 'kind': 'VR', 'param': None, 'source_key': 'vr', 'text': 'V x'})
    ev += extra
    json.dump({'events': ev}, open(MAP_JSON, 'w'))
write_map([])

def fingerprint(saint='Saint Test', wsha=wav_sha, tsha=text_sha):
    return hashlib.sha256(json.dumps({
        'date': '2026-11-21', 'lang': 'en', 'mystery': 'joyful', 'saint_name': saint,
        'ask': 'their', 'attenuate_db': None, 'saint_check': 'off',
        'intro_wav_sha256': wsha, 'intro_text_sha256': tsha,
        'donor_sha256': pack['donor_sha256'], 'art_shas': pack['art_shas'],
        'pack_json_sha256': sha256(PACK_JSON), 'map_sha256': sha256(MAP_JSON),
        'ledger_sha256': sha256(LEDGER_JSON), 'desc_template_sha256': sha256(DESC_TXT),
        'code_sha256': sha256(BUILD)}, sort_keys=True).encode()).hexdigest()

BASE = ['--date', '2026-11-21', '--lang', 'en', '--packs-dir', packs,
        '--intro-wav', WAV, '--intro-sha256', wav_sha,
        '--intro-text', TEXT, '--intro-text-sha256', text_sha,
        '--saint-name', 'Saint Test', '--saint-check', 'off',
        '--outdir', os.path.join(tmp, 'out0')]

# A1. locale refusal: AR (or any non-en) must fail closed
run(['ar' if a == 'en' else a for a in BASE], 'NOT BUILT', 'locale-refusal-ar')

# A2. intro-text sha mismatch
run([x if x != text_sha else '0' * 64 for x in BASE], 'intro text sha mismatch', 'intro-text-sha-mismatch')

# resume fixture: matching saved fingerprint + recorded master hash + phase7.ok + master
outdir = os.path.join(tmp, 'out'); os.makedirs(outdir, exist_ok=True)
MASTER = os.path.join(outdir, 'master-en-2026-11-21-joyful.mp4')
def fake_master(secs, color='navy'):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'color=c={color}:s=640x360:r=20:d={secs}',
                    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', str(secs), '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', MASTER], check=True)
def save_state():
    json.dump({'fingerprint': fingerprint(), 'master_sha256': sha256(MASTER),
               'fmap': [], 'nccs': [], 'overflow': [], 'cr_bottoms': [], 'att': 0.0},
              open(os.path.join(outdir, 'phase7-state.json'), 'w'))
    open(os.path.join(outdir, 'phase7.ok'), 'w').write('ok\n')
fake_master(2); save_state()

# A3. resume refusals: changed saint / changed intro / changed donor / map mutation /
#     ledger mutation / config mutation / replaced master
run(BASE + ['--outdir', outdir, '--resume', '--saint-name', 'Saint Changed'], 'RESUME REFUSED', 'resume-changed-saint')
env = dict(os.environ)
r = subprocess.run([sys.executable, BUILD] + BASE + ['--outdir', outdir, '--resume',
        '--intro-text', TEXT2, '--intro-text-sha256', text2_sha], capture_output=True, text=True, cwd=ROOT, timeout=300)
out = r.stdout + r.stderr
if r.returncode != 0 and 'RESUME REFUSED' in out: print('pass resume-changed-intro')
else: fails.append(f'resume-changed-intro: {out[-200:]}'); print(f'FAIL resume-changed-intro: {out[-200:]}')

make_donor('white'); pack['donor_sha256'] = sha256(DONOR); save_pack(pack)
run(BASE + ['--outdir', outdir, '--resume'], 'RESUME REFUSED', 'resume-changed-pack-donor')
make_donor('black'); pack['donor_sha256'] = sha256(DONOR); save_pack(pack); save_state()

_ev = json.load(open(MAP_JSON)); _ev['events'][0]['text'] = 'tampered'
json.dump(_ev, open(MAP_JSON, 'w'))
run(BASE + ['--outdir', outdir, '--resume'], 'RESUME REFUSED', 'resume-changed-map')
write_map([]); save_state()

json.dump({'artworks': [{'tampered': True}]}, open(LEDGER_JSON, 'w'))
run(BASE + ['--outdir', outdir, '--resume'], 'RESUME REFUSED', 'resume-changed-ledger')
json.dump({'artworks': []}, open(LEDGER_JSON, 'w')); save_state()

pack['label'] = 'TAMPERED LABEL'; save_pack(pack)
run(BASE + ['--outdir', outdir, '--resume'], 'RESUME REFUSED', 'resume-changed-config')
pack['label'] = 'JOYFUL MYSTERIES'; save_pack(pack); save_state()

fake_master(2, color='red')  # same length class, different bytes
run(BASE + ['--outdir', outdir, '--resume'], 'RESUME REFUSED', 'resume-replaced-master')

# A4. duration mismatch: resume accepted (fingerprint + master hash match), wrong length
fake_master(1); save_state()
run(BASE + ['--outdir', outdir, '--resume'], 'DURATION MISMATCH', 'duration-mismatch')

# A5. body overflow: a meditation far too long must hard-fail, never ship
write_map([{'film_start': 0.30, 'kind': 'ANN', 'param': 1, 'source_key': 'ann1', 'text': None},
           {'film_start': 0.31, 'kind': 'MED', 'param': ['intro', 1], 'source_key': 'med1',
            'text': 'word ' * 900}])
run(BASE + ['--outdir', os.path.join(tmp, 'out2')], 'BODY OVERFLOW', 'body-overflow')
write_map([])

# B. saint lock against a mocked Vatican News
import http.server, socketserver
INDEX = b'''<html><body>
<a href="/en/saints/11/21/st--other.html">Saint Other</a>
<a href="/en/saints/11/21/b--beta.html">Blessed Beta</a>
<p>journey of faith. Saint Other of Somewhere, hermit</p>
</body></html>'''
H1_OTHER = b'<html><body><h1>Saint Other</h1></body></html>'
H1_BETA = b'<html><body><h1>Blessed Beta</h1></body></html>'
PAGES = {b'/en/saints/11/21.html': INDEX, b'/en/saints/11/21/st--other.html': H1_OTHER,
         b'/en/saints/11/21/b--beta.html': H1_BETA}
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGES.get(self.path.encode())
        if body is None: self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = {'RF_VN_BASE': f'http://127.0.0.1:{srv.server_address[1]}'}
AUTO = [x for x in BASE if x not in ('off', '--saint-check')]  # saint-check auto (default), mocked base

# B1. wrong-but-real: saint not among the dated entries must refuse even though the index loads
run(AUTO + ['--saint-name', 'Saint Test'], 'SAINT MISMATCH', 'saint-wrong-but-real', env_extra=MOCK)
# B2. cross-entry mixture: tokens spread across two different entries must refuse
run(AUTO + ['--saint-name', 'Saint Other Beta'], 'SAINT MISMATCH', 'saint-cross-entry-mixture', env_extra=MOCK)
# B3. correct binding: the dated entry matches; the build must get PAST the saint gate
out = run(AUTO + ['--saint-name', 'Saint Other'], None, 'saint-correct-binding', env_extra=MOCK)
if out is not None and 'SAINT MISMATCH' in out:
    fails.append(f'saint-correct-binding: wrongly refused: {out[-200:]}')
    print('FAIL saint-correct-binding: refused at the saint gate')
elif out is not None:
    print('pass saint-correct-binding (gate passed; build later refused on synthetic-pack grounds as expected)')

# C. round-4 gates: no whole-page fallback, date-filtered entry hrefs
NO_ANCHORS = b'''<html><body>
<p>Saint Other of Somewhere, hermit, is remembered today</p>
</body></html>'''
NO_ANCHORS_MIX = b'''<html><body>
<p>Saint Other of Somewhere</p><p>Blessed Beta of Elsewhere</p>
</body></html>'''
WRONG_DATE = b'''<html><body>
<a href="/en/saints/11/21/b--beta.html">Blessed Beta</a>
<a href="/en/saints/11/20/st--other.html">Saint Other</a>
</body></html>'''
# C1. no parseable dated entry: plain-text words on the page must NOT qualify (old fallback removed)
PAGES[b'/en/saints/11/21.html'] = NO_ANCHORS
run(AUTO + ['--saint-name', 'Saint Other'], 'no parseable dated entries', 'saint-no-entry-fallback-removed', env_extra=MOCK)
# C2. cross-entry token mixture in the no-anchor branch: still refuses closed
PAGES[b'/en/saints/11/21.html'] = NO_ANCHORS_MIX
run(AUTO + ['--saint-name', 'Saint Other Beta'], 'no parseable dated entries', 'saint-no-entry-mixture-refused', env_extra=MOCK)
# C3. wrong-date link: a valid-looking /en/saints/11/20/ link on the 11/21 index never qualifies,
# even when its own page carries a matching H1
PAGES[b'/en/saints/11/21.html'] = WRONG_DATE
PAGES[b'/en/saints/11/20/st--other.html'] = H1_OTHER
run(AUTO + ['--saint-name', 'Saint Other'], 'SAINT MISMATCH', 'saint-wrong-date-link-refused', env_extra=MOCK)
# C4. h2-heading repair: name in the section heading, anchor text generic ('Read all...') -
# the dated entry must still bind (live VN 11/12 page shape)
H2_STYLE = b'''<html><body>
<section><div><h2>Saint Other of Somewhere, Hermit</h2></div>
<div><p>story text</p>
<a href="/en/saints/11/21/st--other.html">Read all...</a></div></section>
</body></html>'''
PAGES[b'/en/saints/11/21.html'] = H2_STYLE
out = run(AUTO + ['--saint-name', 'Saint Other'], None, 'saint-h2-heading-repair', env_extra=MOCK)
if out is not None and 'SAINT MISMATCH' in out:
    fails.append(f'saint-h2-heading-repair: wrongly refused: {out[-200:]}')
    print('FAIL saint-h2-heading-repair: refused at the saint gate')
elif out is not None:
    print('pass saint-h2-heading-repair (gate passed; build later refused on synthetic-pack grounds as expected)')
# C5. h2 repair must not loosen the gate: wrong saint name in the h2 still refuses
H2_WRONG = b'''<html><body>
<section><div><h2>Saint Someone Else</h2></div>
<div><a href="/en/saints/11/21/st--other.html">Read all...</a></div></section>
</body></html>'''
PAGES[b'/en/saints/11/21.html'] = H2_WRONG
run(AUTO + ['--saint-name', 'Saint Other'], 'SAINT MISMATCH', 'saint-h2-wrong-name-refused', env_extra=MOCK)
srv.shutdown()


# C6. legacy donor_layout: the body must assemble from THIS build's fresh cards, never donor
# frames. Red-toned donor + dark factory cards: a mid-body master frame must NOT be donor red.
import glob as _glob
DONOR_RED = os.path.join(pd, 'donor.mp4')
WAV_TONE = os.path.join(tmp, 'intro-tone.wav')
subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=red:s=640x360:r=20:d=3',
                '-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-af','volume=0.06',
                '-t','3','-pix_fmt','yuv420p', DONOR_RED], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','sine=frequency=440:sample_rate=44100',
                '-af','volume=0.06','-t','1', WAV_TONE], check=True)
wav_tone_sha = sha256(WAV_TONE)
pack['donor_layout'] = 'legacy'; pack['donor_sha256'] = sha256(DONOR_RED)
pack['credits_mode'] = 'ledger_credit_copy'
json.dump({'artworks': [{'slot': f'joyful_{i}', 'title': f'T{i}', 'artist': 'A',
                         'work': 'W', 'source_url': f'https://example.test/{i}'} for i in range(1, 6)],
           'credit_copy': {'cards': {f'joyful_{i}': f'A. W. Reproduction: src {i}. https://example.test/{i} Note: rights may differ elsewhere.'
                                     for i in range(1, 6)}}}, open(LEDGER_JSON, 'w'))
json.dump({'events': [{'film_start': 0.0, 'kind': 'intro', 'param': None, 'source_key': 'intro',
                       'text': TEXT}]
           + [{'film_start': round(1.0 + i * 0.3, 3), 'kind': 'HM', 'param': [0, i + 1],
               'source_key': k, 'text': 'x'} for i, k in enumerate(PRAYERS)]
           + [{'film_start': 3.7, 'kind': 'VR', 'param': None, 'source_key': 'vr', 'text': 'V x'}]},
          open(MAP_JSON, 'w'))
save_pack(pack)
leg_out = os.path.join(tmp, 'out-legacy')
r6 = subprocess.run([sys.executable, BUILD, '--date','2026-11-21','--lang','en','--packs-dir',packs,
    '--intro-wav',WAV_TONE,'--intro-sha256',wav_tone_sha,'--intro-text',TEXT,'--intro-text-sha256',text_sha,
    '--saint-name','Saint Test','--saint-check','off','--outdir',leg_out],
    capture_output=True, text=True, cwd=ROOT, timeout=300)
o6 = r6.stdout + r6.stderr
if r6.returncode != 0:
    fails.append(f'legacy-fresh-body: build failed: {o6[-300:]}'); print(f'FAIL legacy-fresh-body: {o6[-200:]}')
elif 'vbody assembled from' not in o6:
    fails.append('legacy-fresh-body: fresh-assembly proof line missing'); print('FAIL legacy-fresh-body: no proof line')
else:
    m6 = _glob.glob(os.path.join(leg_out, 'master-*.mp4'))[0]
    fr6 = os.path.join(tmp, 'legframe.png')
    subprocess.run(['ffmpeg','-y','-v','error','-ss','2.5','-i',m6,'-frames:v','1',fr6], check=True)
    import numpy as _np
    fr = _np.asarray(Image.open(fr6).convert('RGB'), dtype=float)
    rmean = fr[..., 0].mean()
    if rmean > 60 and rmean > 2 * max(fr[..., 1].mean(), fr[..., 2].mean()):
        fails.append('legacy-fresh-body: mid-body frame is donor red - fresh cards not in the output')
        print('FAIL legacy-fresh-body: donor pixels in master')
    else:
        mftm = json.load(open(os.path.join(leg_out, 'film-time-map-2026-11-21.json')))
        if mftm.get('vbody_source') != 'fresh cards (legacy donor_layout)':
            fails.append(f'legacy-fresh-body: manifest vbody_source={mftm.get("vbody_source")!r}')
            print('FAIL legacy-fresh-body: manifest not recorded')
        else:
            print('pass legacy-fresh-body')

# C7. luminous pack statics: exact per-art credit_copy wired, Cana not Commons-mislabeled
_lp = json.load(open(os.path.join(ROOT, 'packs', 'en', 'luminous', 'pack.json')))
_ll = json.load(open(os.path.join(ROOT, 'packs', 'en', 'luminous', 'art-ledger.json')))
_cc = _ll.get('credit_copy', {}).get('cards', {})
_ok = (_lp.get('credits_mode') == 'ledger_credit_copy'
       and all(a['slot'] in _cc and a['source_url'] in _cc[a['slot']] for a in _ll['artworks'])
       and all('rights may differ elsewhere' in _cc[a['slot']] for a in _ll['artworks']))
_cana = _cc.get('luminous_2', '')
_ok = _ok and 'Google Arts & Culture' in _cana and 'RMN-Grand Palais' in _cana and 'Wikimedia Commons' not in _cana
if _ok: print('pass luminous-credit-copy')
else:
    fails.append('luminous-credit-copy: pack mode/credit_copy/cana wiring wrong'); print('FAIL luminous-credit-copy')

# C8. ledger_credit_copy mode refuses when a slot's copy is missing
json.dump({'artworks': [{'slot': 'joyful_1', 'title': 't', 'artist': 'a', 'work': 'w', 'source_url': 'u'}],
           'credit_copy': {'cards': {}}}, open(LEDGER_JSON, 'w'))
run(BASE + ['--outdir', os.path.join(tmp, 'out-cc')], 'missing credit_copy', 'credit-copy-missing-refused')

# C9. description write normalizes to exactly one trailing newline (byte-identity vs the
# published artifact: YouTube keeps a single trailing \n; the template emits \n\n)
_src = open(os.path.join(ROOT, 'build_day.py')).read()
if "write(desc.rstrip('\\n') + '\\n')" in _src:
    print('pass description-single-trailing-newline')
else:
    fails.append('description-single-trailing-newline: writer must emit exactly one trailing newline')
    print('FAIL description-single-trailing-newline')

print()
if fails:
    print('NEGATIVE TESTS FAILED:'); [print(' -', f) for f in fails]; sys.exit(1)
print('ALL NEGATIVE TESTS PASS (every gate refused as designed)')
