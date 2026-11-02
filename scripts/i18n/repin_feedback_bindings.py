#!/usr/bin/env python3
"""Re-pin the held feedback mirror family after master drift (#741 changed
feedback.html without updating locales/en/feedback-bindings.json).

Provenance (verified before write): the current pin 7de07f4faa37... equals
sha256(feedback.html) at 12853cef (#664), the commit that last touched the
bindings file, so the pin was correct when written and the drift came later.

Usage:
  python3 scripts/i18n/repin_feedback_bindings.py          # report only
  python3 scripts/i18n/repin_feedback_bindings.py --write  # rewrite the pin (targeted value replace, formatting preserved)
"""
import argparse, json, re, subprocess
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL = 'locales/en/feedback-bindings.json'
ALLOWLIST = {REL}  # the only file this script may rewrite
PIN_AT = '12853cef'  # commit whose feedback.html bytes the current pin matches

def sha(b): return sha256(b).hexdigest()

def prepare():
    path = ROOT / REL
    contract = json.loads(path.read_text())
    master, pinned = contract['master'], contract['masterSha256']
    current = sha((ROOT / master).read_bytes())
    if current == pinned:
        return None, {'binding': REL, 'status': 'already current', 'masterSha256': current}
    base_bytes = subprocess.check_output(['git', 'show', f'{PIN_AT}:{master}'], cwd=ROOT)
    if sha(base_bytes) != pinned:
        raise ValueError(f'{REL}: pin {pinned[:12]} does not match {PIN_AT} bytes {sha(base_bytes)[:12]} - provenance broken, stop')
    updated = json.loads(path.read_text())
    updated['masterSha256'] = current
    check = json.loads(path.read_text()); check['masterSha256'] = pinned
    if check != contract:
        raise ValueError(f'{REL}: re-pin would change fields beyond masterSha256')
    return (path, pinned, current), {'binding': REL, 'master': master, 'oldMasterSha256': pinned, 'newMasterSha256': current}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    write, row = prepare()
    if a.write and write:
        path, old_sha, new_sha = write
        text = path.read_text()
        new_text, n = re.subn(r'("masterSha256":\s*")' + re.escape(old_sha) + r'(")',
                              lambda m: m.group(1) + new_sha + m.group(2), text, count=1)
        if n != 1:
            raise ValueError(f'{REL}: targeted re-pin matched {n} times (expected 1)')
        path.write_text(new_text)
    print(json.dumps({'mode': 'write' if a.write else 'report', 'result': row}, indent=2))
