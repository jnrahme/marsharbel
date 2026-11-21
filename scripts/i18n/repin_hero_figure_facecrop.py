"""Face-crop re-pin: masterSha256 refresh for keyed mirror bindings whose EN
master bytes legitimately changed in the hero-figure face-crop PR (build-added
is-portrait/is-square-ish classes + scoped styles.css cache-bust).

Non-author review still verifies per the merge-train rule; this script is the
deterministic mechanism, not the approval. All checks finish before writing:

  1. The binding's prior pin must equal the master's sha at the PR base
     (origin/stage) - proves the only master drift is this branch's change.
  2. Only masterSha256 changes; every other contract field is byte-preserved.
  3. Bindings already stale at the base (pre-existing drift, not ours) are
     reported and skipped, never silently re-pinned.

Usage: python3 scripts/i18n/repin_hero_figure_facecrop.py          # report only
       python3 scripts/i18n/repin_hero_figure_facecrop.py --write  # rewrite pins
"""
import argparse
import re, copy, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def sha(raw): return hashlib.sha256(raw).hexdigest()

# Exact write allowlist (scrum review): the only files this script may rewrite.
ALLOWLIST = {
    'locales/en/all-saints-and-all-souls-master-bindings.json',
    'locales/en/saints-master-bindings.json',
}

def prepare(base):
    rows, skipped, updates = [], [], {}
    for path in sorted((ROOT / 'locales/en').glob('*-bindings.json')):
        rel = path.relative_to(ROOT).as_posix()
        if rel not in ALLOWLIST:
            continue
        contract = json.loads(path.read_text())
        master, pinned = contract.get('master'), contract.get('masterSha256')
        if not master or not pinned:
            continue
        current = sha((ROOT / master).read_bytes())
        if current == pinned:
            continue
        base_master = subprocess.check_output(['git', 'show', f'{base}:{master}'], cwd=ROOT)
        if sha(base_master) != pinned:
            skipped.append({'binding': rel, 'master': master, 'reason': 'stale at base (pre-existing, not this PR)'})
            continue
        updated = copy.deepcopy(contract)
        updated['masterSha256'] = current
        check = copy.deepcopy(updated)
        check['masterSha256'] = pinned
        if check != contract:
            raise ValueError(f'{rel}: re-pin would change fields beyond masterSha256')
        updates[rel] = updated
        rows.append({'binding': rel, 'master': master, 'oldMasterSha256': pinned, 'newMasterSha256': current})
    return updates, rows, skipped

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='origin/stage')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    updates, rows, skipped = prepare(a.base)
    if a.write:
        old_by_rel = {row['binding']: row['oldMasterSha256'] for row in rows}
        for rel, data in updates.items():
            path = ROOT / rel
            text = path.read_text()
            old_sha, new_sha = old_by_rel[rel], data['masterSha256']
            new_text, n = re.subn(
                r'("masterSha256":\s*")' + re.escape(old_sha) + r'(")',
                lambda m: m.group(1) + new_sha + m.group(2), text, count=1)
            if n != 1:
                raise ValueError(f'{rel}: targeted re-pin matched {n} times (expected 1)')
            path.write_text(new_text)
    print(json.dumps({'mode': 'write' if a.write else 'report', 'repinned': rows, 'skipped': skipped}, indent=2))
