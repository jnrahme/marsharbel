#!/usr/bin/env bash
# Prints a timings TSV (first column = seconds) slowest-first and mirrors it to
# GITHUB_STEP_SUMMARY when available. Read-only; never fails the job.
set -uo pipefail
title="${1:-CI step timings}"
file="${2:-${CI_TIMINGS_FILE:-tmp/ci-timings.tsv}}"
if [[ ! -s "${file}" ]]; then
  echo "[timings] nothing recorded at ${file}"
  exit 0
fi
echo "[timings] ${title} (seconds<TAB>exit<TAB>label, slowest first):"
sort -rn "${file}" | sed 's/^/  /'
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  { echo "### ${title} (s)"; echo '```'; sort -rn "${file}"; echo '```'; } >> "${GITHUB_STEP_SUMMARY}"
fi
