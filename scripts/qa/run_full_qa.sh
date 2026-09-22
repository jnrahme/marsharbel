#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "${1:-}" == "--ci" ]]; then
  export CI=1
fi

cd "${ROOT}"

node scripts/build-home-css.mjs --check

echo "[qa] Checking SEO metadata and sitemap coverage"
python3 scripts/qa/check_seo.py
python3 -m unittest discover -s scripts/qa -p 'test_seo.py'

echo "[qa] Running site smoke tests"
npm run test:site-smoke

echo "[qa] Running rosary regression tests"
npm run test:rosary-all

echo "[qa] QA suite finished"
