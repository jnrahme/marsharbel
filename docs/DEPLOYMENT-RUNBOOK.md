# Marsharbel deployment playbook

Owner: Joey Rahme
Updated: 2026-09-22
Review: monthly and after any deployment incident

Pushes to `stage` publish to **https://marsharbel.com**, the public website. Follow this playbook for every release. The hardening items below are a plan, not protections already enabled.

## Definition of done

- [ ] The intended release passed QA before merging into `stage`.
- [ ] Hostinger completed deployment without a checkout error.
- [ ] The **Deploy to Hostinger** workflow for that push passed both `qa` and `verify-deployment`.
- [ ] A normal browser visit shows the expected change; homepage, rosary, and storybook still work.
- [ ] An existing browser session also updates correctly after reload.
- [ ] The previous good revision and recovery instructions are recorded before starting another release.

## Current protections and gaps

| Area | Verified state on 2026-09-22 | Remaining work |
| --- | --- | --- |
| Hostinger checkout | Git metadata restored; repo `jnrahme/marsharbel`, branch `stage`, install path `/` | Preserve `.git`; never replace the live directory through another uploader |
| QA | GitHub Actions runs automated checks | Enforce passing PR checks before `stage` changes |
| Deployment verification | Compares 73 frontend files with the checkout; retries and fails on mismatch | Verify release identity, ordinary cached URLs, and required media |
| Deployment trigger | Hostinger receives pushes independently of GitHub QA | Ensure QA gates publication; a green webhook response alone is insufficient |
| Concurrent pushes | GitHub cancels superseded workflow runs | This does not cancel or lock Hostinger deployments; serialize releases |
| Promotion to `main` | Separate workflow opens a PR immediately on `stage` push | Wait for successful deployment verification and pin the verified commit |
| Branch enforcement | No repository rulesets; `stage` protection not configured | Configure protection if supported by this private repository's GitHub plan |
| Recovery | Two retained copies of the pre-repair site | Create recurring backups of the repaired checkout and test restoration |

The current verifier covers root HTML/JS/CSS/webmanifest files and `mysteries/*.html`. It does not verify every image, audio file, PHP endpoint, or normal browser cache. Identical frontend bytes also do not prove which Git commit is deployed.

## Release procedure with today's setup

Prerequisites: repository write access, GitHub Actions access, and Hostinger hPanel access. Use a clean checkout of the release branch. Do not run checks against an older local `main` and treat them as checks of `stage`.

1. Put changes on a feature branch and open a PR targeting `stage`.
2. Wait for all applicable PR checks to pass on the latest revision. Recheck after updating the branch. Until branch protection is enabled, this is a manual release requirement.
3. Confirm the preceding release finished. Record the previous successful `stage` SHA and its Actions run URL. Do not merge another release while Hostinger is deploying or verification is running.
4. Merge the PR into `stage`. This changes the public site through the Hostinger webhook.
5. Open the **Deploy to Hostinger** run for that exact push in [GitHub Actions](https://github.com/jnrahme/marsharbel/actions). Wait for `verify-deployment` to succeed. A passing QA job or webhook HTTP 200 is not deployment success.
6. Visit the normal website URL in a fresh browser session and an existing session. Check the expected change and exercise homepage navigation, the rosary, and the storybook. For changed audio/images, open those features too.
7. Record the release SHA, successful run URL, and smoke-check result. Only then promote that verified revision to `main` or begin another release. The current auto-created promotion PR is not evidence that deployment passed.

For additional diagnostics, run this from a clean checkout of the exact pushed revision that contains the verifier:

```sh
python3 scripts/qa/verify_deployment.py --base-url https://marsharbel.com
```

Do not use File Manager, FTP, or a ZIP upload to replace `public_html` during normal releases. Preserve server-only configuration and the two retained sitemap files when changing deployment methods. Never commit secrets to Git.

## If a release fails

Stop further merges into `stage` until the current failure is understood. Check the failed Actions job and Hostinger's Git deployment output at Websites → marsharbel.com → Advanced → Git.

| Symptom | Action |
| --- | --- |
| QA fails | Fix the branch and rerun checks. Inspect the live site: the independent Hostinger webhook may already have published this push. |
| “Project directory is not a git repository” | Preserve a copy of the live directory. Recover the Git checkout without deleting server-only files. Do not repeatedly press Deploy or clear cache expecting missing Git metadata to repair itself. |
| Deployment finishes but file verification fails | Confirm configured branch `stage`, latest remote SHA, and deploy log. Compare mismatched files. Once the correct files are on the server, clear Hostinger cache and rerun verification for the current revision. |
| Cache-busted verification passes but browser stays old | Check ordinary asset URLs and service-worker behavior; clear Hostinger cache and repair cache invalidation. Asking every visitor to clear their browser cache is not a completed fix. |
| A newer push superseded this run | Verify the newest intended release. A cancelled older workflow does not prove its Hostinger deployment stopped. |
| Verified files match but a feature breaks | Revert the bad change or fix forward; file equality cannot prove application correctness. |

### Routine rollback

1. Identify the last good SHA using a successful deployment run and the release record.
2. Create a rollback branch from the latest `stage`. Revert the offending change(s) into a **new commit**, review its diff, and open a PR to `stage`. For merge commits, inspect parent history before selecting the revert parent; do not blindly use a generic revert command.
3. Run checks, merge, and follow the same deployment and browser verification steps. Do not force-push or rewrite `stage` history.

### Emergency recovery

Hostinger domain root: `/home/u174996069/domains/marsharbel.com/`.

Retained incident copies:

- `deployment-backup-20260922/public_html`
- `public_html-before-git-repair-20260922`

These are copies of the **old site without functioning Git metadata**. They can recover old content, but simply renaming one to `public_html` will reintroduce the deployment problem. Pause automatic deployment before any emergency folder recovery, preserve the failed state, restore content into a valid checkout, and verify a subsequent Git deployment before closing the incident. Do not delete these backups until a newer backup has passed a restore drill.

## Hardening implementation plan

Implement in this order. Mark each item complete only after its acceptance check passes.

### 1. Enforce the release gate

- Protect `stage`: require PRs, successful required QA checks, and checks against the current base; block force pushes and deletion. Apply restrictions to administrators where supported. Confirm private-repository plan support; do not change visibility or purchase a plan as a workaround.
- Choose the exact required check names from completed runs; avoid ambiguous duplicate job names across workflows.
- Make promotion depend on successful verification of the exact pushed SHA. Reuse an existing matching promotion PR and never substitute a newer unverified branch head.
- Configure the release owner's GitHub failure notifications and test delivery. Notifications are not yet confirmed active.

Acceptance: a PR with deliberately failing QA cannot enter `stage`; a failed deployment cannot produce a success-labelled promotion; the owner receives the test failure notification.

### 2. Verify the complete release

- Add a deployment-generated release marker containing the exact SHA plus a manifest of required public assets. Do not expose secrets or private configuration.
- Compare the marker and frontend through both ordinary URLs and cache-busted URLs. Test a returning browser with the previous service worker installed.
- Validate referenced images/audio with an explicit manifest and suitable content checks; keep expensive full media integrity checks separate where necessary. Include safe checks for required PHP endpoints without submitting real messages.
- Record the deployed SHA, manifest, verification results, and previous good SHA as durable release artifacts.

Acceptance: stale cached JS, an old marker, a missing required image/audio file, and a broken service-worker upgrade each fail verification in a test environment.

### 3. Control deployment and recovery

- Confirm this shared-hosting plan's supported authenticated deployment, locking, and filesystem capabilities. VPS deployment APIs are not evidence of support on this account.
- Where supported, make one workflow own deployment after QA and remove the independent push trigger only after the replacement works. Queue releases and pin the deployed SHA; do not rely on GitHub cancellation to stop server work.
- If supported, upload into a separate versioned release directory, verify it, then atomically switch the live directory. Keep server-only configuration outside release replacement. If this hosting plan cannot do that, document the residual partial-update risk and evaluate a supported hosting option before migration.
- Back up the repaired checkout and server-only files before releases; retain at least the last five good releases plus an off-host copy. Exclude backups and secrets from public access.
- Test rollback on a separate non-public environment. Target recovery within 10 minutes, then record the measured result; this is a target, not a demonstrated guarantee.

Acceptance: two rapid releases finish with the newest approved revision live; an interrupted upload leaves the previous release serving; rollback restores a known good revision and the next deployment still works. Do not inject these failures into the public website.

### 4. Separate staging from production

Create a separate staging site if ongoing preview releases are needed. Validate the complete process there before changing branch-to-site mappings. Until that migration is deliberately implemented, `stage` continues to publish to the public domain and `main` is not the production deployment trigger.

## Evidence and maintenance

- Repair and verifier: [PR #17](https://github.com/jnrahme/marsharbel/pull/17).
- Verified automatic deployment: [run 35747258296](https://github.com/jnrahme/marsharbel/actions/runs/35747258296), revision `a63f80978d39d563c1d9a2bbdbe5e43b5176fce4`; 73 live frontend files matched.
- Hosting reference: [Hostinger Git deployment](https://www.hostinger.com/support/1583302-how-to-deploy-a-git-repository-in-hostinger/). Check actual account capabilities before applying instructions.
- Enforcement reference: [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

Joey owns release decisions and recovery. Review this playbook monthly and after any hosting, branch, cache, or workflow change. Repeat the restore drill after changing the deployment method.
