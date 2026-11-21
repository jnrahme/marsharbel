#!/usr/bin/env bash
# Refactor gate: served files in the working tree must be byte-identical to a base ref.
# Usage: scripts/qa/compare-served.sh <base-ref>   (e.g. origin/stage)
# Ignores source-only paths (src/, partials/fragments/, scripts/, docs/, tests/, *.md, .github/).
set -euo pipefail
base=${1:?base ref required}
ex=':(exclude)src :(exclude)partials/fragments :(exclude)scripts :(exclude)docs :(exclude)tests :(exclude)templates :(exclude).github :(exclude)*.md :(exclude)package.json :(exclude)package-lock.json'
# shellcheck disable=SC2086
changed=$(git diff --name-status "$base" -- . $ex | grep -v '^$' || true)
if [ -n "$changed" ]; then echo "SERVED OUTPUT DIFFERS from $base:"; echo "$changed"; exit 1; fi
echo "Served output byte-identical to $base."
