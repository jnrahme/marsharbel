# Spec-first for large builds

The template lives in `.github/pull_request_template.md`. Fill the Spec section before writing code, in the first (draft) PR.

## What counts as LARGE
A build is large if ANY of these is true:
- It adds or changes a backend, API, database schema, or stored user data.
- It adds a new system: subscriptions, email sending, auth, payments, analytics pipeline, scheduled bots.
- It touches deploy, Hostinger, CI workflows, or branch protection.
- It changes site-wide navigation, layout, or the design system (not one page).
- It is expected to take more than one working day or more than one lane.
- It handles secrets, personal data, or money.

## What is NOT large (spec skipped)
Articles, miracle accounts, prayers, storybooks, translations, copy fixes, single-page styling, image swaps, bug fixes under about 100 lines.

## Rules
- When unsure, treat it as large. A 10-minute spec is cheaper than a rebuilt feature.
- Under one page. Acceptance criteria must be checkable by someone who did not build it.
- Rollback must be real: a named revert or disable step, not "fix forward".
- If the spec changes mid-build, edit the PR description and note why in the checkpoint file.
