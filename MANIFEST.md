# PR-A2 RECONSTRUCTION - durable source packet v1 (GATE CLOSED, not for merge)

Reconstructed 2026-10-23 00:35-00:45 EDT from the exact recorded source-write
commands (recovery zip sha256 e62f97be1de27b9a38a6621a3011e9754905f4124c8fbcd6e58a8da3d2adbade,
25 command records + initial cert-test heredoc) after the 23:54 sandbox rebuild
destroyed the unpushed head 1608e346. Lost-run evidence is history only.

Base: b77f2f16 (remote stage #876 squash; commit message records it applied
exactly the ce476a22 + 7f45c212 A1 packet diff on 3763e61a). Verified zero file
overlap with the A1 test follow-up and #877. Scrum must independently verify
this base mapping before treating reconstruction fidelity as proven.

## Unique source files (7, complete list from replayed commands)
- locales/travel-authored-mirror-equivalence.json (02 evidence writer, values
  RECOMPUTED on this base; 07 family-into-group). gateStatus is
  'pending-final-qa' - CLOSED. The historical flip (11) was NOT replayed per
  Main 00:31 ruling: regenerated computed evidence requires independent new
  validation, not the inherited approved flag.
- scripts/i18n/reviewed_travel_authored_mirror.py (03 initial, 15 anchor-IDs
  fix, strict raise per 24 with 17 interim noop skipped per Main's supersede
  ruling - adapted single replacement, documented)
- scripts/i18n/same_page_injection.py (04 chain)
- scripts/qa/test_travel_authored_mirror_certification.py (05 heredoc, 06/08/09/10 edits)
- scripts/qa/probe_partial_build.py (12 pins 154/142, 20+21 split mirror
  proof-class blocks, 22 englishSources block, 24 explicit synthetic marker)
- scripts/i18n/manifest_policy.py (13 chain import, 14 strip predicate, 16 scopes)
- scripts/qa/test_travel_generated_availability.py (01 re-pin, reviewable
  acceptance scope - flagged for Scrum independent authorized-scope review)

## Closed-gate design (Main 00:31)
The producer returns the manifest unchanged while gateStatus != 'approved', so
this tree builds byte-identical output to base: build --check GREEN, and
probe/cert/availability tests (which assert the merged end-state) are RED until
Scrum flips the gate as their independent-verification act. same-page-manifest.js
is deliberately NOT in this packet; the generated candidate (produced with a
temporary local flip) is preserved separately as unaccepted verification
material. Scrum's gate path: flip gateStatus to 'approved', run
python3 scripts/build-international.py, compare the regenerated manifest against
the candidate, re-run the battery.

## Fresh verification at this exact tree (local flip only for the run, reverted)
All at b77f2f16 + these 7 files, 2026-10-23 00:38-00:45 EDT:
- python3 scripts/build-international.py: EXIT 0; regenerated manifest carries
  the 5 variants (es/fr/it/pl/pt) inside travel-travel-master-equivalence with
  proof type travel-authored-mirror; 0 standalone pending travel rows
- scripts/qa/test_travel_authored_mirror_certification.py: 3/3 OK
- scripts/qa/test_travel_generated_availability.py: 2/2 OK
- scripts/qa/check_i18n_policy.py: passed
- scripts/qa/probe_partial_build.py: PROBE-EXIT-0, SPLIT PARTIAL PROBE PASS,
  marker line present, MASK COUNTS manifest-travel-mirror: 5 + sources: 5

## Still outstanding (next checkpoints)
Full battery (i18n:check, 4x i18n chunks, prepush) and fresh negative controls
(missing evidence family -> production build must exit 1 at the producer raise;
missing variant -> policy ValueError; content drift -> cert FAIL; explicit
synthetic absence -> probe PASS) in a second worktree.
