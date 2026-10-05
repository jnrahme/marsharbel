#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "${1:-}" == "--ci" ]]; then
  export CI=1
fi

cd "${ROOT}"

python3 scripts/qa/check_travel_routes.py
python3 scripts/qa/test_travel.py
npx playwright test tests/travel-routing.spec.js tests/travel-hub.spec.js --project=phone --project=laptop --workers=4
node scripts/tests/video-fallback.mjs
npx playwright test tests/video-playback.spec.js --project=phone --project=laptop --workers=2
node scripts/qa/test_analytics_hostname.cjs
python3 -m unittest discover -s scripts/qa -p 'test_security_headers.py'

node scripts/build-home-css.mjs --check
npm run i18n:check
python3 scripts/build-eucharistic-miracles.py --check
npm run i18n:test

echo "[qa] Refactor, mirror and locale contract tests"
for t in chaplet_mirror de_exact_catalogs encyclopedia_trail error_document exact_master exact_wiring feast_mirror footer_navigation head_fragments jsonld_serializer litany_mirror locale_foundation locale_home_navigation prayer_mirror saint_pillars tour_nav; do
  python3 "scripts/qa/test_${t}.py"
done

echo "[qa] Checking specs for absolute machine paths"
python3 scripts/qa/check_spec_paths.py
python3 -m unittest discover -s scripts/qa -p 'test_spec_paths.py'

echo "[qa] Checking SEO metadata and sitemap coverage"
python3 scripts/qa/check_seo.py
python3 -m unittest discover -s scripts/qa -p 'test_seo.py'
python3 -m unittest discover -s scripts/qa -p 'test_answer_faq_parity.py'

echo "[qa] Checking RSS feeds against their source pages"
python3 scripts/build_news_desk.py --check
python3 -m unittest discover -s scripts/qa -p test_news_desk.py
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
echo "[qa] Eucharistic collection browser checks"
PORT=4189 bash scripts/tests/run_eucharistic_collection.sh

python3 -m unittest discover -s scripts/qa -p 'test_rosary_bead_copy.py'
npx playwright test tests/rosary-bead-teacher.spec.js --project=small-phone --project=phone --project=laptop --workers=2

echo "[qa] Running rosary regression tests"
npm run test:rosary-all

echo "[qa] Eucharistic authored locale mirrors"
python3 -m unittest discover -s scripts/qa -p 'test_eucharistic_locale.py'
python3 -m unittest discover -s scripts/qa -p 'test_home_mirror.py'
python3 -m unittest discover -s scripts/qa -p 'test_mirror_structure.py'
python3 -m unittest discover -s scripts/qa -p 'test_locale_mirror_policy.py'
PORT=4197 bash scripts/tests/run_eucharistic_locales.sh

echo "[qa] Books content API: feed, shelf parity and round trip"
npm run books:check

echo "[qa] QA suite finished"
