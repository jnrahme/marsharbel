# Task registry (durable in-repo record)

Started 2026-10-13 under the owner's Autonomous Execution and Memory Protocol (WhatsApp, 3:29 PM EDT).

Files here are the durable record. The Paperclip board stays the live mirror: the board is where lanes
claim and move work minute to minute; these files are reconciled from it and from GitHub at least daily and
at every merge-train handoff. If a file and the board disagree, GitHub (merged PRs, open PRs, CI) wins, then
fix both. Existing equivalents are reused, not duplicated:

- Engineering rules stay in `/AGENTS.md` (this directory adds nothing to it except a pointer).
- Rights record stays in `docs/seo/photo-rights-registry.md`.
- Lane process pack (PR #502, docs-only) is the lane charter once merged; `tasks/` only tracks tasks.

| File | Purpose |
|---|---|
| MASTER_TASKS.md | Authoritative task list with the required fields |
| DECISIONS.md | Owner directives and rulings, with source and date |
| PROGRESS.md | Execution history, blockers, next actions |
| COMPLETED.md | Done work with verification evidence |
| SESSION_HANDOFF.md | Exact state to resume |
| I18N_STATUS.md | Per-language audit table (also lives in the intl/full-translation PR body) |

## Statuses
BACKLOG, READY, IN PROGRESS, IN REVIEW, VERIFIED, DONE, BLOCKED, FAILED, CANCELLED.

DONE needs: acceptance criteria verified with evidence AND merged to the target branch (stage), and for a
live-facing change the post-merge live check. VERIFIED means the evidence exists but the PR is not merged yet.
BLOCKED must name the blocker, its owner and the exact ask.

## Task fields
ID, original request (quote and date), description, priority (P0-P3), assigned agent/lane, dependencies,
acceptance criteria, status, branch/PR, verification evidence.
