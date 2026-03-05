#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_URL="${BASE_URL:-http://127.0.0.1:4173}"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx is required for agentic smoke checks. Install Node.js/npm first."
  exit 1
fi

export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
PWCLI="${CODEX_HOME}/skills/playwright/scripts/playwright_cli.sh"

if [[ ! -x "${PWCLI}" ]]; then
  echo "Playwright CLI wrapper not found at ${PWCLI}."
  echo "Install the playwright skill or run deterministic tests with: npm run qa"
  exit 1
fi

mkdir -p "${ROOT}/output/playwright"
cd "${ROOT}"

"${PWCLI}" open "${BASE_URL}" --headed
"${PWCLI}" snapshot
"${PWCLI}" screenshot --output "output/playwright/home-smoke.png"

echo "Agentic smoke capture completed: output/playwright/home-smoke.png"
