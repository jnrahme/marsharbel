#!/usr/bin/env python3
"""Install and sha-verify pack binaries (donor video + artwork) for packs/<lang>/<mystery>/.

Two documented input routes, no internal tooling:

  python3 bootstrap_packs.py en joyful --from-dir /path/to/downloads
      PROVEN route. The operator downloads the pinned files however they like (browser,
      any download tool) into a directory holding donor.mp4 (or donor parts) and g1..g5.jpg;
      this script verifies every sha256 against packs/registry.json and installs them.

  python3 bootstrap_packs.py en joyful
      Plain-HTTPS download of the anyone-reader Drive IDs pinned in registry.json
      (https://drive.google.com/uc?export=download&id=<id>). NOT execution-proven from a
      clean environment: Drive can answer a confirm interstitial instead of bytes for large
      files. The sha pins catch that (the install fails verification); fall back to
      --from-dir. Never relax a pin to make a download pass.
"""
import hashlib, json, os, shutil, sys, urllib.request

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def main():
    lang, mystery = sys.argv[1], sys.argv[2]
    from_dir = None
    if '--from-dir' in sys.argv:
        from_dir = sys.argv[sys.argv.index('--from-dir') + 1]
    here = os.path.dirname(os.path.abspath(__file__))
    reg = json.load(open(os.path.join(here, 'packs', 'registry.json')))['packs'][f'{lang}/{mystery}']
    dest = os.path.join(here, 'packs', lang, mystery)
    os.makedirs(os.path.join(dest, 'art'), exist_ok=True)
    tmp = os.path.join(dest, '.bootstrap-tmp'); os.makedirs(tmp, exist_ok=True)

    def obtain(file_id, name):
        if from_dir:
            src = os.path.join(from_dir, name)
            if not os.path.exists(src):
                raise SystemExit(f'missing {src} in --from-dir')
            return src
        out = os.path.join(tmp, name)
        url = f'https://drive.google.com/uc?export=download&id={file_id}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=300) as r, open(out, 'wb') as f:
            shutil.copyfileobj(r, f)
        return out

    d = reg['donor']
    if d.get('concat'):
        parts = [obtain(fid, f'donor-part{i}.mp4') for i, fid in enumerate(d['drive_ids'])]
        with open(os.path.join(dest, 'donor.mp4'), 'wb') as out:
            for p in parts:
                with open(p, 'rb') as f: shutil.copyfileobj(f, out)
    else:
        shutil.copy(obtain(d['drive_id'], 'donor.mp4'), os.path.join(dest, 'donor.mp4'))
    got = sha256(os.path.join(dest, 'donor.mp4'))
    if got != d['sha256']:
        os.remove(os.path.join(dest, 'donor.mp4'))
        raise SystemExit(f'donor sha mismatch: got {got}, want {d["sha256"]}. '
                         'If you used the plain-HTTPS route, Drive likely served an interstitial; use --from-dir.')
    print('donor OK', got[:16], d.get('name', ''))
    for n, a in reg['art'].items():
        p = os.path.join(dest, 'art', f'{n}.jpg')
        shutil.copy(obtain(a['drive_id'], f'{n}.jpg'), p)
        got = sha256(p)
        if got != a['sha256']:
            os.remove(p)
            raise SystemExit(f'art {n} sha mismatch: got {got}, want {a["sha256"]}')
        print('art OK', n, got[:12])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'pack {lang}/{mystery} installed and verified')

if __name__ == '__main__':
    main()
