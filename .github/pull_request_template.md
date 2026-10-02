<!--
Routine PRs (content, storybooks, copy, small fixes): fill "Summary" and "Verification" only, delete the rest.
LARGE builds: fill every section. See docs/engineering/process/spec-first.md for what counts as large.
-->

## Summary
What changed and why, in two or three lines.

## Verification
Live link or QA preview, desktop and phone screenshots, gate results, what is NOT verified yet.

---
## Spec (LARGE builds only)

**Large?** yes / no (see spec-first.md)

### Goal
One paragraph: the outcome and who it is for.

### Acceptance criteria
- [ ] Observable, testable statement 1
- [ ] Observable, testable statement 2

### Risks
Data, security, SEO, cost, performance, anything that touches production state. Name the worst case.

### Rollback
Exact steps to undo (revert PR, disable flag, restore data) and who runs them.

### Reviewer (independent, not the builder)
Name of the lane that will post the proof checklist (see independent-review.md).

### Checkpoint file
`checkpoints/<build-name>.md` (see checkpoints.md)
