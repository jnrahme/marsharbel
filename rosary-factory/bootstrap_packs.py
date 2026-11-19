#!/usr/bin/env python3
"""Fetch and sha-verify pack binaries (donor videos + artwork) from the marsharbel Drive
into packs/<lang>/<mystery>/. Downloads go through the operator's connected Drive tooling.

  python3 bootstrap_packs.py en joyful
  python3 bootstrap_packs.py en sorrowful
"""
import hashlib, json, os, subprocess, sys

lang, mystery = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
reg = json.load(open(os.path.join(here, 'packs', 'registry.json')))['packs'][f'{lang}/{mystery}']
dest = os.path.join(here, 'packs', lang, mystery)
os.makedirs(os.path.join(dest, 'art'), exist_ok=True)

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def dl(file_id):
    r = subprocess.run(['tools', 'google-drive', 'download', '--file-id', file_id, '--json'],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)['file_path']

d = reg['donor']
if d.get('concat'):
    parts = [dl(i) for i in d['drive_ids']]
    with open(os.path.join(dest, 'donor.mp4'), 'wb') as out:
        for p in parts:
            out.write(open(p, 'rb').read())
else:
    import shutil; shutil.copy(dl(d['drive_id']), os.path.join(dest, 'donor.mp4'))
got = sha256(os.path.join(dest, 'donor.mp4'))
assert got == d['sha256'], f'donor sha mismatch: {got}'
print('donor OK', got[:16], d['name'])
for n, a in reg['art'].items():
    import shutil
    p = os.path.join(dest, 'art', f'{n}.jpg'); shutil.copy(dl(a['drive_id']), p)
    got = sha256(p); assert got == a['sha256'], f'art {n} sha mismatch: {got}'
print('art OK 5/5')
print(f'{lang}/{mystery} pack READY')
