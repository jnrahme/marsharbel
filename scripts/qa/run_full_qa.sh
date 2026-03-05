#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "${1:-}" == "--ci" ]]; then
  export CI=1
fi

cd "${ROOT}"

echo "[qa] Running site smoke tests"
npm run test:site-smoke

echo "[qa] Running rosary regression tests"
npm run test:rosary-all

echo "[qa] QA suite finished"
