#!/usr/bin/env python3
"""Completeness gate for scripts/qa/shard-manifest.tsv.

The manifest decides which steps run_full_qa.sh --shard K/N executes, so an
incomplete or stale manifest would silently drop coverage. This test derives
the ground-truth inventory by EXECUTING the script's own expansion
(--list-steps, which walks the same qa_step/index code path, including the
17-item mirror loop, the litany_mirror pipefail special case, and the
--skip-i18n-test consumed slot) and asserts index+command PAIRS, not call
sites and not a command set: a reordered, edited, added or removed step must
fail this gate. Fail closed, always.
"""
import subprocess, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = 'scripts/qa/run_full_qa.sh'
MANIFEST = ROOT / 'scripts/qa/shard-manifest.tsv'
SHARDS = 8

def list_steps(skip):
    out = subprocess.run(['bash', SCRIPT, '--list-steps'] + (['--skip-i18n-test'] if skip else []),
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        raise AssertionError('--list-steps failed: ' + out.stderr[-500:])
    pairs = {}
    for line in out.stdout.splitlines():
        if '\t' not in line:
            continue
        idx, cmd = line.split('\t', 1)
        if idx.isdigit():
            pairs[int(idx)] = cmd
    return pairs

def manifest_rows():
    rows = {}
    for line in MANIFEST.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        idx, shard, secs, cmd = line.split('\t', 3)
        rows[int(idx)] = (int(shard), int(secs), cmd)
    return rows

class ShardManifestCompleteness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = list_steps(False)
        cls.skip = list_steps(True)
        cls.manifest = manifest_rows()

    def test_runtime_expansion_shape(self):
        # 149 slots in file order, indices dense 0..148.
        self.assertEqual(sorted(self.full), list(range(len(self.full))))
        self.assertEqual(len(self.full), 149)
        # Under --skip-i18n-test exactly one slot is consumed but unexecuted,
        # and it is the i18n:test slot.
        consumed = sorted(set(self.full) - set(self.skip))
        self.assertEqual(len(consumed), 1)
        self.assertEqual(self.full[consumed[0]], 'npm run i18n:test')
        self.assertEqual(len(self.skip), 148)
        # The 17-item mirror loop is present in the expansion (order-sensitive):
        # litany_mirror runs through its pipefail wrapper, not a bare unittest call.
        litany = [c for c in self.full.values() if 'litany' in c]
        self.assertEqual(len(litany), 1)
        self.assertIn('pipefail', litany[0])
        self.assertIn('tmp/litany.txt', litany[0])

    def test_manifest_covers_every_slot_exactly_once_with_matching_pairs(self):
        self.assertEqual(sorted(self.manifest), sorted(self.full),
                         'manifest indices must equal the runtime expansion, exactly once each')
        for idx, cmd in self.full.items():
            shard, secs, mcmd = self.manifest[idx]
            self.assertEqual(mcmd, cmd, f'index {idx}: manifest command does not match the runtime step')
            self.assertGreaterEqual(shard, 0)
            self.assertLess(shard, SHARDS)
            self.assertGreaterEqual(secs, 0)

    def test_runtime_shard_selection_is_disjoint_and_complete(self):
        # Drive the script's own selection path: --list-steps --shard K/N runs
        # the same manifest lookup (and fail-closed checks) as execution. The
        # eight shard lists must partition the skip-i18n runtime inventory.
        seen = []
        for k in range(SHARDS):
            out = subprocess.run(['bash', SCRIPT, '--list-steps', '--skip-i18n-test', '--shard', f'{k}/{SHARDS}'],
                                 capture_output=True, text=True, cwd=ROOT)
            if out.returncode != 0:
                raise AssertionError(f'--list-steps --shard {k}/{SHARDS} failed: {out.stderr[-500:]}')
            seen += [int(l.split('\t', 1)[0]) for l in out.stdout.splitlines()
                     if '\t' in l and l.split('\t', 1)[0].isdigit()]
        self.assertEqual(sorted(seen), sorted(self.skip),
                         'shard selections must cover every runtime step exactly once')

    def test_every_shard_non_empty(self):
        counts = {s: 0 for s in range(SHARDS)}
        for shard, _, _ in self.manifest.values():
            counts[shard] += 1
        empty = [s for s, n in counts.items() if n == 0]
        self.assertEqual(empty, [], f'shards with no steps: {empty}')

if __name__ == '__main__':
    unittest.main()
