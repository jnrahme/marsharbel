# Reviewed PR opening convention

Keep the existing authenticated GitHub workspace alive. Verify `gh auth status` before attempting login. Restart device login only if authentication is actually unavailable; no new login is needed for each merge.

After local checks and rendered phone/desktop review, open routine stage PRs with:

```sh
scripts/github/open-reviewed-pr.sh --qa-reviewed --head <branch> --title <title> --body-file <review-notes>
```

The opener creates the PR, then arms squash auto-merge immediately. GitHub's existing stage branch protection waits for required checks. Arming is not a merge and does not bypass CI. Check the PR result and live deploy afterward; auto-merge is not completion proof.

For a site-wide redesign, story film, explicit owner hold, or any other work requiring owner review, use `--qa-reviewed --hold` instead. Those PRs remain open without auto-merge. Do not retroactively arm every open PR: #410 is explicitly held. Draft PRs use the ordinary `gh pr create --draft` path.

The wrapper is deliberately a convention, not a privileged workflow. It grants no new workflow token access and cannot re-enable auto-merge on held PRs. Its QA-reviewed flag records the human/operator gate; it does not claim to perform visual review itself.
