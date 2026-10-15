# Duplicate-QA reduction only: executable review artifact

REVIEW ONLY. No merge request, no release approval, no production proof. Cancellation is unchanged: shared `hostinger-stage`, `cancel-in-progress: true`. This is NOT a fix for cancelled scans. Earlier references to a cancellation fix or cancellation-starvation fix are superseded by this label. The actual change removes duplicate QA computation only.

Refreshed actual post-#817 base: `136de2bd3507066d8f33af564fc49483eacae9fa`, tree `4f5259095bec44f516e24cd09d6ab3d2c865fc0c`. This refresh uses the actual squash and its sources, not provisional or d27 receipts. The implementation branch will still require final-stage refresh, independent source review, exact-head CI, and a separate first-stage execution gate. This review branch adds executable evidence under this directory; production implementation remains a workflow-only delta. No content, locale, test assertion, QA script, infrastructure, access, or cancellation configuration is changed.

## Replay

From repository root, with Python and PyYAML available:

```
python3 docs/ci/duplicate-qa-reduction/test_embedded.py
```

The tests extract the actual Python block from `.github/workflows/deploy-stage.yml`, not the standalone copy. `actual-embedded.py` is a review snapshot of those same bytes. 38 tests pass locally; controls include API deadlines/errors, pagination, strict latest-run/attempt selection, partial-rerun fail-closed, workflow/repo/SHA/tree/blob/job identities, before/after races, and artifact source tampering. This is fixture execution, not a deployed Actions run. `test-results.log` records that distinction. Intentional skips in existing test reports remain skips.

## Post-#817 command equivalence

`current-command-union.json` captures 138 unsharded command argv selections and their existing eight shard selections plus dedicated `npm run i18n:test`. The ordered union is exact. `current-coverage-map.json` maps each command index explicitly to its owning shard or dedicated i18n job and records every separate qa-gates command. No command is removed. This is selection proof, not 137 runtime success receipts.

The verifier unit suite is outside the full QA runner: the old deploy-local qa job and the existing `qa-gates` both run the exact same `python3 -m unittest discover -s scripts/qa -p 'test_verify_deployment.py'`. `qa` requires `qa-gates` success, so removing the duplicate invocation does not remove verifier tests. The current 20-test suite was executed locally and retains #818 controls.

Dedicated i18n: the runner's `--skip-i18n-test` branch consumes the i18n index without executing it; all eight shards use that flag; the separate `i18n-test` job executes the identical `npm run i18n:test` once. The qa aggregate requires both every shard and dedicated i18n success. The coverage map records the exact consumed index and source hashes. The existing Browser quality workflow independently retains eight isolated jobs and strict aggregate; no tests or intentional test skips are changed.

All QA/browser jobs retain separate workspaces and existing command order. No parallel-in-one-checkout transformation is proposed. No old d27 totals or provisional #817 totals certify this current code. Post-#817 refresh is now in post817-command-coverage.json:138commands, exact union, i18nindex62, verifier-unit retained. Full actual-code38tests and verifier20tests rerun. Exact-head PR CI and first real admission remain separate future gates.

## Implementation acceptance conditions (verbatim review ruling)

1. Test the ACTUAL embedded admission logic, not the abstract model: exact job-name multiset/attempt/repo/head repo/SHA/tree/workflow ID+path+blob, wrong same-name workflow, API auth/errors/malformed fields, all pagination and 1000-result truncation, old-success vs newer-pending/failed rerun, dependency races before/after scan. Read attempt-specific jobs. A partial rerun omitting earlier successful jobs must fail closed under strict no-mixed-attempt rule; explain "rerun all jobs" recovery rather than silently borrowing prior jobs.
2. Resolve "latest matching run" vs "reject duplicates" precisely: multiple legitimate records must have deterministic latest selection BEFORE result checks; duplicate/conflicting records within identity/jobs fail. Never success-filter first. SHA alone is not run-attempt identity.
3. Preserve verifier tests already in qa-gates and every other gate; explicit checkout exact SHA/tree. Check before/after dependency run ID AND attempt, not only conclusion. Stage drift recorded as superseded only when a newer SHA is actually confirmed; unreadable state = unverified.
4. Refreshed post-#817 successor inventory/hash evidence required - no provisional/d27 grandfathering. Source-only review separate from later exact-head CI and first real stage execution. Capture raw run/attempt/job IDs, URLs, workflow blob hashes, timestamped scan scope; a cancelled run may have no final artifact - platform record is truth.
5. Bounded GitHub API wait/network timeout; fail closed if the existing read token is insufficient - no permission expansion. Immutable evidence distinct from mutable latest-live view. No fake production pushes for race tests.

## State truth and recovery

Latest matching run is the highest run ID after exact-stage event/branch selection; all matching records must pass identity validation. Latest attempt is read from that run before any conclusion checks. Duplicate record IDs or job-name multisets fail. A partial rerun cannot mix prior attempt jobs: use "rerun all jobs" to obtain a complete new attempt. Old success never covers a newer pending/failed attempt.

Successful test/review evidence remains distinct from per-commit publication observation and mutable latest-live state. The scan only covers the existing verifier file selector. Cancellation can interrupt finalizers and leave no JSON artifact; the platform's cancelled attempt remains unverified. No guarantee of every-commit publication. This workflow neither uploads nor serializes Hostinger's external publisher.

## Reviewer counterexample repair

The fetched current run must have the SAME ID as the latest selected run-list ID before any attempt lookup. A coherent alternate older successful run/attempt/job fixture now rejects on this explicit predicate, not on a missing fixture lookup. Independent review still pending.

## Stage observation-window repair

Closing current-stage reads now occur after dependency snapshots at wait admission, before scan launch, and after scan before awarding a receipt. Actual-helper fixtures advance stage inside all three snapshot windows and reject superseded/unverified. These checks are observations, not atomic external-publication locks.

## Timestamped claims for this checkpoint

Historical source/test claim: at07:24EDT the helper bytes inherited from exact a0b39574 were replayed against actual136de2bd sources:38fixture controls PASS,20current verifier unit tests PASS,actionlint1.7.12 PASS (shellcheck/pyflakes optional integrations disabled). This is source/local-test proof, not exact-head CI or site publication.

Latest-stage reconciliation: at07:25:01EDT GitHub refs/heads/stage was136de2bd; this is a separate ref observation, not a public site-byte verification claim. Existing base-stage QA/browser/deploy run records are attached in post817-live-records.json as historical evidence, not real admission receipts for the new workflow.

Implementation candidate is workflow-only branch ci/duplicate-qa-post817, commit5ba320c (fullidentity in refreshedreceipt). NoPR/merge yet. Independent source review must precede PR. This evidence branch includes documents/tests only for review and must NOT itself be merged as the production workflow change.
