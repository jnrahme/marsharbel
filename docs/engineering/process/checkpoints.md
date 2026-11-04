# Resume checkpoints

Long builds survive restarts, workspace wipes and lane handoffs through one plain markdown file per build.

## When
Any build that is LARGE, or any storybook/video/batch job expected to span more than one session.

## Where
`checkpoints/<build-name>.md` in the repo, on the build's own branch. Push to origin at every milestone and whenever the state section changes. Delete the file when the build ships (merge PR removes it).

## Format
```
# <build name>
Owner lane: <lane>      Branch: <branch>      PR: <link or "none yet">
Updated: <date time>

## State
Done so far, in a few bullets. Facts only.

## Next step
The single next action, specific enough to start without asking.

## Resume instructions
Commands to get back to a working state (branch, install, env needs, where scratch files live), and what must NOT be redone.

## Open questions / blockers
Who is needed (e.g. Joey for approval, 6-digit code), and since when.

## Decisions log
Date, decision, reason. One line each.
```

## Rules
- Update before stopping, not after. A stale checkpoint is worse than none.
- No secrets, tokens or personal data in it. The repo is public.
- Scratch outputs that cannot be committed (large media) get a path/location line in "Resume instructions" and a note on how to regenerate.
