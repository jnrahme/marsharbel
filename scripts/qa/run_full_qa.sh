#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "${1:-}" == "--ci" ]]; then
  export CI=1
fi

cd "${ROOT}"

node scripts/build-home-css.mjs --check
npm run i18n:check
npm run i18n:test

echo "[qa] Checking SEO metadata and sitemap coverage"
python3 scripts/qa/check_seo.py
python3 -m unittest discover -s scripts/qa -p 'test_seo.py'

echo "[qa] Checking RSS feeds against their source pages"
python3 scripts/build_feeds.py --check
python3 scripts/build_news_thumbs.py --check
python3 -m unittest discover -s scripts/qa -p 'test_feeds.py'

echo "[qa] Checking indexable testimony baseline"
node scripts/build-testimony-baseline.mjs --check
node scripts/tests/testimony_static.mjs

echo "[qa] Running testimony security tests"
npm run test:testimony-security

echo "[qa] Running site smoke tests"
npm run test:site-smoke

echo "[qa] Running rosary regression tests"
npm run test:rosary-all

echo "[qa] QA suite finished"
