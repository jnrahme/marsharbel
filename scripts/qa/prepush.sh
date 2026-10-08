#!/usr/bin/env bash
# Fast static gates that CI would otherwise discover 5-25 minutes after the push.
# Same commands as CI, same order, no network, no browser. About 1-2 minutes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

step() { printf '\n[prepush] %s\n' "$1"; }

step "generated pages are in sync with src/pages"
node scripts/build-pages.mjs --check
step "navigation and home.css are in sync"
node scripts/sync-navigation.mjs --check
node scripts/build-home-css.mjs --check
step "international build, i18n policy, same-page control"
python3 scripts/build-international.py --check
python3 scripts/qa/check_i18n_policy.py
python3 scripts/build-same-page-control.py --check
python3 scripts/qa/check_runtime_labels.py
step "SEO, sitemap lastmod, specs"
python3 scripts/qa/check_seo.py
python3 scripts/sitemap_lastmod.py --check
python3 scripts/qa/check_spec_paths.py
step "fast unit tests (everything except the slow i18n suite)"
for t in scripts/qa/test_*.py; do
  case "$t" in *test_i18n.py) continue ;; esac
  (cd scripts/qa && python3 "$(basename "$t")" >/dev/null) || { echo "FAILED: $t"; exit 1; }
done
step "dead code"
bash scripts/qa/dead_code_check.sh >/dev/null
printf '\n[prepush] all static gates passed\n'
