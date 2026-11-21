"""Re-point C-0016 provenance pins orphaned by the squash merge of #676.

The squash (stage 19845304) dropped the PR branch's ancestry, leaving
locales/travel-equivalence.json pinning preparedRevision/sourceRevision
fdcd070f688af4c400008f4bac94ed038478b1bb, which is no longer an ancestor
of stage HEAD. The evidence gate (travel_variant_evidence.blob) then fails
closed with 'Missing/nonancestor evidence provenance' on every stage build.

Zero-drift re-point: every pinned file's blob at fdcd070f is byte-identical
to its blob at 19845304893719bcdee5864fb31fd3c3e043e386 and matches the
recorded candidateFileSha256, so the pin can name the stage-reachable
commit with no content change. Surgical splice of the one sha string only;
json validated before write; trailing newline preserved.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / 'locales/travel-equivalence.json'
OLD = 'fdcd070f688af4c400008f4bac94ed038478b1bb'
NEW = '19845304893719bcdee5864fb31fd3c3e043e386'
EXPECTED_PINS = 49
EXPECTED_VARIANTS = 37


def blob_sha(ref, path):
    raw = subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT, stderr=subprocess.DEVNULL)
    return hashlib.sha256(raw).hexdigest()


def main():
    # Gate: new ref must be stage-reachable, old must be gone from ancestry.
    subprocess.run(['git', 'merge-base', '--is-ancestor', NEW, 'HEAD'], cwd=ROOT, check=True)
    raw = RECORD.read_text()
    pins = raw.count(OLD)
    if pins != EXPECTED_PINS:
        raise ValueError(f'expected {EXPECTED_PINS} pins of {OLD[:8]}, found {pins}')
    record = json.loads(raw)
    variants = [(v['file'], v.get('reviewEvidence', {}).get('candidateFileSha256', ''))
                for g in record['groups'].values() for v in g.get('variants', {}).values()
                if v.get('reviewEvidence', {}).get('preparedRevision') == OLD]
    if len(variants) != EXPECTED_VARIANTS:
        raise ValueError(f'expected {EXPECTED_VARIANTS} scoped variants pinned at {OLD[:8]}, found {len(variants)}')
    # Zero-drift proof BEFORE writing: old blob == new blob == candidate pin.
    mismatches = [(f, blob_sha(OLD, f)[:12], blob_sha(NEW, f)[:12], c[:12])
                  for f, c in variants
                  if not (blob_sha(OLD, f) == blob_sha(NEW, f) == c)]
    if mismatches:
        raise ValueError(f'non-zero-drift variants: {mismatches[:3]}')
    out = raw.replace(OLD, NEW)
    if out.count(NEW) != pins or OLD in out:
        raise ValueError('splice drift')
    json.loads(out)  # validate before write
    RECORD.write_text(out if out.endswith('\n') else out + '\n')
    print(f're-pointed {pins} pins ({len(variants)} scoped variants): {OLD[:8]} -> {NEW[:8]}; zero-drift verified {len(variants)}/{len(variants)}')


if __name__ == '__main__':
    main()
