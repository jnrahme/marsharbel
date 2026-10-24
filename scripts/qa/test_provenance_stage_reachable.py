"""Fail closed when C-0016 provenance pins stop being stage-reachable.

Squash merges orphan PR-branch commits. locales/travel-equivalence.json
pins git revisions as review evidence; the evidence gate blobs them, so a
pin naming a commit that is not an ancestor of stage HEAD breaks every
stage build (post-squash deploy red, 2026-10-10). This test asserts every
revision-typed pin in the record stays an ancestor of HEAD.

Known-dormant exception (recorded 2026-10-10, unresolvable until intl
re-derives it): cf50ee5878c2a8a18090311f7c1ca06a2de5438e, the
pilgrimage-master group sourceRevision - a missing object, metadata only,
never blobbed by the gate. Naming it here keeps it visible: removing or
adding an unreachable ref fails this test.
"""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / 'locales/travel-equivalence.json'
KNOWN_DORMANT = {
    'cf50ee5878c2a8a18090311f7c1ca06a2de5438e': 'pilgrimage-master sourceRevision (missing object, metadata-only, dormant)',
}


def revision_pins():
    pins = {}

    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str) and 'evision' in key and len(value) == 40 and all(c in '0123456789abcdef' for c in value):
                    pins.setdefault(value, []).append('.'.join(path + [key]))
                else:
                    walk(value, path + [key])
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, path + [str(i)])

    walk(json.loads(RECORD.read_text()), [])
    return pins


class ProvenanceStageReachable(unittest.TestCase):
    def test_all_revision_pins_are_stage_reachable(self):
        pins = revision_pins()
        unreachable = {}
        for ref, paths in sorted(pins.items()):
            rc = subprocess.run(['git', 'merge-base', '--is-ancestor', ref, 'HEAD'],
                                cwd=ROOT, capture_output=True).returncode
            if rc != 0:
                unreachable[ref] = paths[:2]
        self.assertEqual(set(unreachable), set(KNOWN_DORMANT),
                         f'unreachable provenance pins beyond the named dormant set: {unreachable}')

    def test_dormant_set_is_exact(self):
        pins = revision_pins()
        for ref in KNOWN_DORMANT:
            self.assertIn(ref, pins, f'named dormant pin {ref[:8]} vanished; update the record or this test')


if __name__ == '__main__':
    unittest.main()
