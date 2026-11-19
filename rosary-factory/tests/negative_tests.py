#!/usr/bin/env python3
"""Offline negative tests for build_day.py's hard gates. No network: every run passes
--saint-check off and uses a tiny synthetic pack built in a temp dir.

Every case must make the build FAIL with the expected refusal. A passing build is a test
failure. Run from the factory root:  python3 tests/negative_tests.py
"""
import hashlib, json, os, subprocess, sys, tempfile
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

def fingerprint(date, saint, wav_sha, text_sha, pack):
    return hashlib.sha256(json.dumps({
        'date': date, 'lang': 'en', 'mystery': 'joyful', 'saint_name': saint,
        'intro_wav_sha256': wav_sha, 'intro_text_sha256': text_sha,
        'donor_sha256': pack['donor_sha256'], 'art_shas': pack['art_shas'],
        'code_sha256': sha256(BUILD)}, sort_keys=True).encode()).hexdigest()

def run(args, expect, name):
    r = subprocess.run([sys.executable, BUILD] + args, capture_output=True, text=True,
                       cwd=ROOT, timeout=300)
    out = r.stdout + r.stderr
    if r.returncode == 0:
        fails.append(f'{name}: build PASSED, expected refusal'); print(f'FAIL {name}: build passed'); return
    if expect not in out:
        fails.append(f'{name}: refused but without {expect!r}: {out[-300:]}')
        print(f'FAIL {name}: wrong refusal: {out[-200:]}'); return
    print(f'pass {name}')

tmp = tempfile.mkdtemp(prefix='rf-negtest-')
packs = os.path.join(tmp, 'packs'); pd = os.path.join(packs, 'en', 'joyful')
os.makedirs(os.path.join(pd, 'art'))
DONOR = os.path.join(pd, 'donor.mp4')
WAV = os.path.join(tmp, 'intro.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=640x360:r=20:d=3',
                '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '3', '-pix_fmt', 'yuv420p',
                DONOR], check=True)
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
def save_pack(pk): json.dump(pk, open(os.path.join(pd, 'pack.json'), 'w'))
save_pack(pack)
open(os.path.join(pd, 'description-template.txt'), 'w').write('{DATE_LONG} {SAINT} {ASK}\n{CHAPTERS}\n{VN_URL}\n')
json.dump({'artworks': []}, open(os.path.join(pd, 'art-ledger.json'), 'w'))
PRAYERS = ['our_father', 'hail_mary', 'glory_be', 'fatima', 'apostles_creed',
           'hail_holy_queen', 'let_us_pray', 'rosary_concluding_prayer']
def write_map(extra):
    ev = [{'film_start': round(0.10 + i * 0.01, 3), 'kind': 'HM', 'param': [0, i + 1],
           'source_key': k, 'text': 'x'} for i, k in enumerate(PRAYERS)]
    ev.append({'film_start': 0.20, 'kind': 'VR', 'param': None, 'source_key': 'vr', 'text': 'V x'})
    ev += extra
    json.dump({'events': ev}, open(os.path.join(pd, 'film-time-map.json'), 'w'))
write_map([])

BASE = ['--date', '2026-11-21', '--lang', 'en', '--packs-dir', packs,
        '--intro-wav', WAV, '--intro-sha256', wav_sha,
        '--intro-text', TEXT, '--intro-text-sha256', text_sha,
        '--saint-name', 'Saint Test', '--saint-check', 'off',
        '--outdir', os.path.join(tmp, 'out0')]

# 1. locale refusal: AR (or any non-en) must fail closed
run(['ar' if a == 'en' else a for a in BASE], 'NOT BUILT', 'locale-refusal-ar')

# 2. intro-text sha mismatch (text/sha pair inconsistent)
run(BASE[:-5] + ['--saint-name', 'Saint Test', '--saint-check', 'off'] if False else
    [x if x != text_sha else '0' * 64 for x in BASE], 'intro text sha mismatch', 'intro-text-sha-mismatch')

# resume fixture: matching saved fingerprint + phase7.ok + a wrong-length master
outdir = os.path.join(tmp, 'out'); os.makedirs(outdir, exist_ok=True)
fp = fingerprint('2026-11-21', 'Saint Test', wav_sha, text_sha, pack)
json.dump({'fingerprint': fp, 'fmap': [], 'nccs': [], 'overflow': [], 'cr_bottoms': [], 'att': 0.0},
          open(os.path.join(outdir, 'phase7-state.json'), 'w'))
open(os.path.join(outdir, 'phase7.ok'), 'w').write('ok\n')
MASTER = os.path.join(outdir, 'master-en-2026-11-21-joyful.mp4')
def fake_master(secs):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'color=c=black:s=640x360:r=20:d={secs}',
                    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', str(secs), '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', MASTER], check=True)
fake_master(2)

# 3a. resume with changed saint -> refused
run(BASE + ['--outdir', outdir, '--resume', '--saint-name', 'Saint Changed'], 'RESUME REFUSED', 'resume-changed-saint')
# 3b. resume with changed intro (consistent text+sha pair, so only the fingerprint catches it)
r = subprocess.run([sys.executable, BUILD] + BASE + ['--outdir', outdir, '--resume',
        '--intro-text', TEXT2, '--intro-text-sha256', text2_sha],
        capture_output=True, text=True, cwd=ROOT, timeout=300)
out = r.stdout + r.stderr
if r.returncode != 0 and 'RESUME REFUSED' in out: print('pass resume-changed-intro')
else: fails.append(f'resume-changed-intro: {out[-200:]}'); print(f'FAIL resume-changed-intro: {out[-200:]}')
# 3c. resume with changed pack (re-encoded donor, pins re-pointed so only the fingerprint catches it)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=white:s=640x360:r=20:d=3',
                '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '3', '-pix_fmt', 'yuv420p', DONOR], check=True)
pack_changed = dict(pack); pack_changed['donor_sha256'] = sha256(DONOR)
save_pack(pack_changed)
run(BASE + ['--outdir', outdir, '--resume'], 'RESUME REFUSED', 'resume-changed-pack')
save_pack(pack)  # restore (donor file differs now, so restore donor too)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=640x360:r=20:d=3',
                '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '3', '-pix_fmt', 'yuv420p', DONOR], check=True)
pack['donor_sha256'] = sha256(DONOR)
save_pack(pack)
# donor bytes changed under the same logical pack -> fingerprint fixture is stale; rebuild fixture
fp = fingerprint('2026-11-21', 'Saint Test', wav_sha, text_sha, pack)
json.dump({'fingerprint': fp, 'fmap': [], 'nccs': [], 'overflow': [], 'cr_bottoms': [], 'att': 0.0},
          open(os.path.join(outdir, 'phase7-state.json'), 'w'))

# 4. duration mismatch: resume accepted (fingerprint matches), master is 1s vs expected ~4.5s
fake_master(1)
run(BASE + ['--outdir', outdir, '--resume'], 'DURATION MISMATCH', 'duration-mismatch')

# 5. body overflow: a meditation far too long must hard-fail, never ship
write_map([{'film_start': 0.30, 'kind': 'ANN', 'param': 1, 'source_key': 'ann1', 'text': None},
           {'film_start': 0.31, 'kind': 'MED', 'param': ['intro', 1], 'source_key': 'med1',
            'text': 'word ' * 900}])
run(BASE + ['--outdir', os.path.join(tmp, 'out2')], 'BODY OVERFLOW', 'body-overflow')

print()
if fails:
    print('NEGATIVE TESTS FAILED:'); [print(' -', f) for f in fails]; sys.exit(1)
print('ALL NEGATIVE TESTS PASS (every gate refused as designed)')
