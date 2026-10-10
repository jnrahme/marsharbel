#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

SHARD_K=""; SHARD_N=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ci) export CI=1 ;;
    --shard) SHARD_K="${2%%/*}"; SHARD_N="${2##*/}"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

cd "${ROOT}"

# --- sharding + timings (additive: with no flags this script behaves as before) ---
# --shard K/N  run only the steps whose index % N == K (steps are numbered in file order)
# Every step is numbered exactly once, so the shards together cover every step.
STEP_INDEX=0
QA_TIMES="$(mktemp)"
qa_step() {
  local idx=${STEP_INDEX}
  STEP_INDEX=$((STEP_INDEX + 1))
  if [[ -n "${SHARD_N}" && $((idx % SHARD_N)) -ne ${SHARD_K} ]]; then
    return 0
  fi
  local start end
  start=$(date +%s)
  "$@"
  end=$(date +%s)
  printf '%s\t%s\n' "$((end - start))" "[$idx] $*" >> "${QA_TIMES}"
}
qa_report() {
  echo "[qa] step timings (seconds, slowest first):"
  sort -rn "${QA_TIMES}" | sed 's/^/  /'
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    { echo "### QA step timings (s)${SHARD_N:+ - shard ${SHARD_K}/${SHARD_N}}"; echo '```'; sort -rn "${QA_TIMES}"; echo '```'; } >> "${GITHUB_STEP_SUMMARY}"
  fi
}
trap qa_report EXIT

qa_step python3 -m unittest discover -s scripts/qa -p 'test_new_page_locales.py'
qa_step python3 -m unittest discover -s scripts/qa -p 'test_partial_locale.py'
qa_step python3 scripts/qa/probe_partial_build.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_metadata.py
qa_step python3 scripts/qa/test_travel_release.py
qa_step python3 -m unittest discover -s scripts/qa -p test_media_nav_repin.py
qa_step python3 -m unittest discover -s scripts/qa -p test_history_nav_repin.py
qa_step python3 -m unittest discover -s scripts/qa -p test_ru_travel_repin.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_scoped_delta.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_parallel_repin.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_metadata_attribute_order.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_metadata_splice.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_authored_final_hashes.py
qa_step python3 -m unittest discover -s scripts/qa -p test_page_mirror_ru_whitespace.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_variant_evidence.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_generated_availability.py
qa_step python3 -m unittest discover -s scripts/qa -p test_generated_sitemap_dates.py
qa_step node scripts/tests/scoped_travel_resolver.cjs
qa_step python3 -m unittest discover -s scripts/qa -p test_ru_nav_alignment_repin.py
qa_step python3 -m unittest discover -s scripts/qa -p test_ru_travel_chrome.py
qa_step python3 -m unittest discover -s scripts/qa -p test_travel_media_bindings_prepare.py
qa_step python3 -m unittest discover -s scripts/qa -p test_retired_novena_nav_repin.py

qa_step npx playwright test tests/element-collision.spec.js --project=laptop --workers=2
qa_step python3 scripts/qa/test_travel_equivalence.py
qa_step node scripts/tests/travel_equivalence.cjs
qa_step node scripts/tests/travel_release_proof.cjs
qa_step npx playwright test tests/travel-equivalence.spec.js --project=phone --project=laptop --workers=2
qa_step npx playwright test tests/miracles-english-escape.spec.js --project=phone --project=laptop --workers=2
qa_step python3 scripts/qa/test_prayer_keyed_masters.py
qa_step python3 scripts/qa/test_prayer_equivalence.py
qa_step npx playwright test tests/prayer-equivalence.spec.js --project=phone --project=laptop --workers=2
qa_step npx playwright test tests/prayer-share-runtime.spec.js --project=phone --project=laptop --workers=2
qa_step npx playwright test tests/prayer-keyed-masters.spec.js --project=laptop --workers=2
qa_step python3 -m unittest discover -s scripts/qa -p test_source_safeguards.py
qa_step python3 scripts/qa/test_new_master_english_escape.py
qa_step python3 scripts/qa/test_exact_source_inputs.py
qa_step python3 scripts/qa/test_limited_launch.py
qa_step npx playwright test tests/limited-launch.spec.js tests/hindi-travel-hub.spec.js --project=phone --project=laptop --workers=2
qa_step python3 scripts/qa/test_source_copy_keys.py
qa_step python3 scripts/qa/check_travel_routes.py
qa_step python3 scripts/qa/test_travel.py
qa_step npx playwright test tests/travel-routing.spec.js tests/travel-hub.spec.js --project=phone --project=laptop --workers=4
qa_step node scripts/tests/video-fallback.mjs
qa_step npx playwright test tests/video-playback.spec.js --project=phone --project=laptop --workers=2
qa_step node scripts/qa/test_analytics_hostname.cjs
qa_step python3 -m unittest discover -s scripts/qa -p 'test_security_headers.py'

qa_step node scripts/build-home-css.mjs --check
qa_step npm run i18n:check
qa_step python3 scripts/build-eucharistic-miracles.py --check
qa_step npm run i18n:test
qa_step npx playwright test tests/language-persistence.spec.js tests/locale-preference-routing.spec.js --project=phone --project=laptop --workers=2

echo "[qa] Refactor, mirror and locale contract tests"
for t in chaplet_mirror de_exact_catalogs encyclopedia_trail error_document exact_master exact_wiring feast_mirror footer_navigation head_fragments jsonld_serializer litany_mirror locale_foundation locale_home_navigation prayer_mirror saint_pillars tour_nav; do
  qa_step python3 "scripts/qa/test_${t}.py"
done

echo "[qa] Checking specs for absolute machine paths"
qa_step python3 scripts/qa/check_spec_paths.py
qa_step python3 -m unittest discover -s scripts/qa -p 'test_spec_paths.py'

echo "[qa] Checking SEO metadata and sitemap coverage"
qa_step python3 scripts/qa/check_seo.py
qa_step python3 -m unittest discover -s scripts/qa -p 'test_seo.py'
qa_step python3 -m unittest discover -s scripts/qa -p 'test_answer_faq_parity.py'

echo "[qa] Checking RSS feeds against their source pages"
qa_step python3 scripts/build_news_desk.py --check
qa_step python3 -m unittest discover -s scripts/qa -p test_news_desk.py
qa_step python3 scripts/build_feeds.py --check
qa_step python3 scripts/build_news_thumbs.py --check
qa_step python3 -m unittest discover -s scripts/qa -p 'test_feeds.py'

echo "[qa] Checking indexable testimony baseline"
qa_step node scripts/build-testimony-baseline.mjs --check
qa_step node scripts/tests/testimony_static.mjs

echo "[qa] Running testimony security tests"
qa_step npm run test:testimony-security

echo "[qa] Running site smoke tests"
qa_step npm run test:site-smoke
echo "[qa] Eucharistic collection browser checks"
qa_step env PORT=4189 bash scripts/tests/run_eucharistic_collection.sh

qa_step python3 -m unittest discover -s scripts/qa -p 'test_rosary_bead_copy.py'
qa_step npx playwright test tests/rosary-bead-teacher.spec.js --project=small-phone --project=phone --project=laptop --workers=2

echo "[qa] Running rosary regression tests"
qa_step npm run test:rosary-smoke
qa_step npm run test:rosary-menu
qa_step npm run test:rosary-end-rules
qa_step npm run test:rosary-prayer-behavior
qa_step npm run test:rosary-intro-cta
qa_step npm run test:rosary-ui-regression
qa_step npm run test:story-floating-player
qa_step npm run test:checklist

echo "[qa] Eucharistic authored locale mirrors"
qa_step python3 -m unittest discover -s scripts/qa -p 'test_eucharistic_locale.py'
qa_step python3 -m unittest discover -s scripts/qa -p 'test_home_mirror.py'
qa_step python3 -m unittest discover -s scripts/qa -p 'test_mirror_structure.py'
qa_step python3 -m unittest discover -s scripts/qa -p 'test_locale_mirror_policy.py'
qa_step python3 -m unittest discover -s scripts/qa -p 'test_history_master_mirror.py'
qa_step python3 -m unittest discover -s scripts/qa -p 'test_travel_page_mirrors.py'
qa_step node scripts/tests/history_equivalence.cjs
qa_step npx playwright test tests/history-master.spec.js --project=phone --project=laptop --workers=2
qa_step npx playwright test tests/travel-master.spec.js --project=phone --project=laptop --workers=2
qa_step env PORT=4197 bash scripts/tests/run_eucharistic_locales.sh

echo "[qa] Books content API: feed, shelf parity and round trip"
qa_step npm run books:check

echo "[qa] QA suite finished"
