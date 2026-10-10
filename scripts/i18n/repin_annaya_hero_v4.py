"""Annaya hero v4 bounded re-pin (Main delegation 2026-10-10 15:11 EDT).

Updates ONLY masterSha256 + sourceRevision on the two Annaya keyed
contracts after the hero content commits. Never edits bindings, copy,
messages, or masters. Non-author runner: executor-applied, one-shot.
"""
import hashlib, json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ['annaya-tour-travel-master', 'annaya-tour-zh-travel-master']
def repin(root=ROOT):
    raw = (root / 'annaya-tour.html').read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    rev = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    out = {}
    for family in FAMILIES:
        path = root / f'locales/en/{family}-bindings.json'
        contract = json.loads(path.read_text())
        assert contract['master'] == 'annaya-tour.html', family
        old = (contract['masterSha256'], contract['sourceRevision'])
        contract.update(masterSha256=sha, sourceRevision=rev)
        out[path] = contract
        print(f'{family}: {old[0][:12]}/{old[1][:8]} -> {sha[:12]}/{rev[:8]}')
    return out
if __name__ == '__main__':
    updates = repin()
    for p, data in updates.items():
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
