# Independent reviewer for big features

The reviewer is never the builder and never the lane that wrote the spec.

## Triggers
Required when a PR is LARGE (see spec-first.md), or ships a new public page type, a new interactive feature, or anything Joey will judge visually. Optional for routine content.

## Flow
1. Builder marks the PR ready and posts "Ready for review" with the QA preview link.
2. Integrator assigns a reviewer lane. Reviewer comments "Reviewing" on the PR.
3. Reviewer works from the PR's acceptance criteria, opens the thing the way Joey would (clicks, taps, watches), then posts the checklist below as a PR comment.
4. Any failed item goes back to the builder. The reviewer re-checks after the fix. Merge only after a comment with all items passed or explicitly waived with a reason.

## Proof checklist (copy into the PR comment)
```
Reviewer: <lane>   Builder: <lane>   Commit reviewed: <sha>
- [ ] Each acceptance criterion tested, one line of evidence each
- [ ] Opened on desktop and phone, real viewport confirmed (innerWidth)
- [ ] Screenshots attached (desktop + phone) of key states, including empty/error
- [ ] Interactions exercised: click, tap, keyboard, navigation, language switch
- [ ] Full QA gate from AGENTS.md green on this commit
- [ ] Regression pass: home page and two unrelated pages still fine
- [ ] Security/data: no secrets, no new personal data, inputs validated
- [ ] SEO: metadata, canonical, hreflang, sitemap where relevant
- [ ] Rollback step from the spec read and plausible
- [ ] Not verified / known gaps: <list, or "none">
Verdict: pass / fail
```

## Rules
- "Tests pass" is not evidence. Evidence is something the reviewer saw.
- Reviewer states honestly what they did not check.
- After merge, the reviewer verifies live once and posts the link.
