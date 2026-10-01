#!/usr/bin/env bash
# Open a reviewed PR and arm its protected-branch merge, unless held for the owner.
set -euo pipefail
hold=false
if [[ "${1:-}" != "--qa-reviewed" ]]; then
  echo 'Usage: open-reviewed-pr.sh --qa-reviewed [--hold] <gh pr create options>' >&2
  echo 'Confirm local checks and rendered review first. --hold is required for owner-approval work.' >&2
  exit 2
fi
shift
if [[ "${1:-}" == "--hold" ]]; then hold=true; shift; fi
for arg in "$@"; do
  case "$arg" in
    --base|--base=*|--repo|--repo=*|-R|-R=*|--draft|-d)
      echo "Unsupported option: $arg. This opener targets non-draft stage PRs in jnrahme/marsharbel." >&2
      exit 2;;
  esac
done
url=$(gh pr create --repo jnrahme/marsharbel --base stage "$@")
printf '%s\n' "$url"
if [[ "$hold" == false ]]; then
  gh pr merge "$url" --repo jnrahme/marsharbel --auto --squash
  echo 'Auto-merge armed. Required branch checks still gate publication.'
else
  echo 'Held for owner review. Auto-merge was not enabled.'
fi
