#!/usr/bin/env bash
# CI step timer (instrumentation only). Runs the given command, appends one
# "elapsed_seconds<TAB>exit_code<TAB>label" line to ${CI_TIMINGS_FILE:-tmp/ci-timings.tsv},
# then exits with the command's own status. Output is labels and durations only -
# never secrets - so the timings file is safe to upload as a run artifact.
set -uo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: timed.sh <label> <command...>" >&2
  exit 2
fi
label="$1"; shift
file="${CI_TIMINGS_FILE:-tmp/ci-timings.tsv}"
mkdir -p "$(dirname "${file}")"

start=$(date +%s)
"$@"
rc=$?
end=$(date +%s)
printf '%s\t%s\t%s\n' "$((end - start))" "${rc}" "${label}" >> "${file}"
exit "${rc}"
