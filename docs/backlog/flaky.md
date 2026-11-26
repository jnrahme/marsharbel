# Flaky test ledger

Every red run that is not a real product or test bug lands here, one row per
observation. The ledger is the input to hardening work: a test that flakes
twice gets a fix PR, not a third rerun.

Rules:

- Log the flake the day it is seen, with the run URL and the failing shard or job.
- "Resolved" rows keep their fix PR so the pattern is searchable.
- Never delete a row; close it out by moving it to Resolved.
- A rerun that goes green does not clear the flake. Only a merged fix does.

## Open

| Date | Test / shard | Symptom | Run | Suspected cause |
| --- | --- | --- | --- | --- |
| 2026-10-15 | qa-shard 5/8 | Shard timed out mid-run; green on rerun with no code change | [run 38824388383](https://github.com/jnrahme/marsharbel/actions/runs/38824388383) | Shard workload near the timeout ceiling; needs per-file timing data |

## Resolved

| Date | Test / shard | Symptom | Runs | Root cause | Fix |
| --- | --- | --- | --- | --- | --- |
| 2026-11-24 - 2026-11-25 | check_seo.py sitemap lastmod (qa-shard 5/8, PR and stage runs) | 84 stale-lastmod errors after every squash merge; each rerun red until dates were re-stamped by hand | [45556119584](https://github.com/jnrahme/marsharbel/actions/runs/45556119584), [45604310991](https://github.com/jnrahme/marsharbel/actions/runs/45604310991) | Squash merges rewrite commit dates to merge-day, so page history no longer matched the committed lastmod values | [#952](https://github.com/jnrahme/marsharbel/pull/952) (squash-aware lastmod check), [#953](https://github.com/jnrahme/marsharbel/pull/953) (post-merge regen) |
| 2026-11-25 | test_film_freshness_nov11.py (qa-shard 6/8) | KeyError 'homeDek' for zh-Hans locale | [45544400585](https://github.com/jnrahme/marsharbel/actions/runs/45544400585) | Missing locale key after the zh-Hans home rollout; content bug, fixed in the #941/#950 era. Harder assertions tracked as Q-004 | assertion hardening PR pending |
