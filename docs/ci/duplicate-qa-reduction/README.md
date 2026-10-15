# Duplicate-QA reduction only: executable review artifact

REVIEW ONLY. No merge request, no release approval, no production proof. Cancellation is unchanged: shared `hostinger-stage`, `cancel-in-progress: true`. This is NOT a fix for cancelled scans. Earlier references to a cancellation fix or cancellation-starvation fix are superseded by this label. The actual change removes duplicate QA computation only.

Base stage: `6cf7e5b75049f6e2003211b09698d5acfe4305a6`. #817 has not merged at this checkpoint. Therefore this artifact is NOT final post-#817 evidence. The implementation branch will still require final-stage refresh, independent source review, exact-head CI, and a separate first-stage execution gate. This review branch adds executable evidence under this directory; production implementation remains a workflow-only delta. No content, locale, test assertion, QA script, infrastructure, access, or cancellation configuration is changed.

## Replay

From repository root, with Python and PyYAML available:

```
python3 docs/ci/duplicate-qa-reduction/test_embedded.py
```

The tests extract the actual Python block from `.github/workflows/deploy-stage.yml`, not the standalone copy. `actual-embedded.py` is a review snapshot of those same bytes. 34 tests pass locally; controls include API deadlines/errors, pagination, strict latest-run/attempt selection, partial-rerun fail-closed, workflow/repo/SHA/tree/blob/job identities, before/after races, and artifact source tampering. This is fixture execution, not a deployed Actions run. `test-results.log` records that distinction. Intentional skips in existing test reports remain skips.

## Current-base command equivalence

`current-command-union.json` captures 137 unsharded command argv selections and their existing eight shard selections plus dedicated `npm run i18n:test`. The ordered union is exact. `current-coverage-map.json` maps each command index explicitly to its owning shard or dedicated i18n job and records every separate qa-gates command. No command is removed. This is selection proof, not 137 runtime success receipts.

The verifier unit suite is outside the full QA runner: the old deploy-local qa job and the existing `qa-gates` both run the exact same `python3 -m unittest discover -s scripts/qa -p 'test_verify_deployment.py'`. `qa` requires `qa-gates` success, so removing the duplicate invocation does not remove verifier tests. The current 20-test suite was executed locally and retains #818 controls.

Dedicated i18n: the runner's `--skip-i18n-test` branch consumes the i18n index without executing it; all eight shards use that flag; the separate `i18n-test` job executes the identical `npm run i18n:test` once. The qa aggregate requires both every shard and dedicated i18n success. The coverage map records the exact consumed index and source hashes. The existing Browser quality workflow independently retains eight isolated jobs and strict aggregate; no tests or intentional test skips are changed.

All QA/browser jobs retain separate workspaces and existing command order. No parallel-in-one-checkout transformation is proposed. No old d27 totals or provisional #817 totals certify this current code. After #817 merges, regenerate the final-stage selection/source artifact and run the actual-code tests again.

## Implementation acceptance conditions (verbatim review ruling)

1. Test the ACTUAL embedded admission logic, not the abstract model: exact job-name multiset/attempt/repo/head repo/SHA/tree/workflow ID+path+blob, wrong same-name workflow, API auth/errors/malformed fields, all pagination and 1000-result truncation, old-success vs newer-pending/failed rerun, dependency races before/after scan. Read attempt-specific jobs. A partial rerun omitting earlier successful jobs must fail closed under strict no-mixed-attempt rule; explain "rerun all jobs" recovery rather than silently borrowing prior jobs.
2. Resolve "latest matching run" vs "reject duplicates" precisely: multiple legitimate records must have deterministic latest selection BEFORE result checks; duplicate/conflicting records within identity/jobs fail. Never success-filter first. SHA alone is not run-attempt identity.
3. Preserve verifier tests already in qa-gates and every other gate; explicit checkout exact SHA/tree. Check before/after dependency run ID AND attempt, not only conclusion. Stage drift recorded as superseded only when a newer SHA is actually confirmed; unreadable state = unverified.
4. Refreshed post-#817 successor inventory/hash evidence required - no provisional/d27 grandfathering. Source-only review separate from later exact-head CI and first real stage execution. Capture raw run/attempt/job IDs, URLs, workflow blob hashes, timestamped scan scope; a cancelled run may have no final artifact - platform record is truth.
5. Bounded GitHub API wait/network timeout; fail closed if the existing read token is insufficient - no permission expansion. Immutable evidence distinct from mutable latest-live view. No fake production pushes for race tests.

## State truth and recovery

Latest matching run is the highest run ID after exact-stage event/branch selection; all matching records must pass identity validation. Latest attempt is read from that run before any conclusion checks. Duplicate record IDs or job-name multisets fail. A partial rerun cannot mix prior attempt jobs: use "rerun all jobs" to obtain a complete new attempt. Old success never covers a newer pending/failed attempt.

Successful test/review evidence remains distinct from per-commit publication observation and mutable latest-live state. The scan only covers the existing verifier file selector. Cancellation can interrupt finalizers and leave no JSON artifact; the platform's cancelled attempt remains unverified. No guarantee of every-commit publication. This workflow neither uploads nor serializes Hostinger's external publisher.
