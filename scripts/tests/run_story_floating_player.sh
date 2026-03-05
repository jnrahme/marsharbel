#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PORT="${PORT:-4173}"
BASE_URL="${BASE_URL:-http://127.0.0.1:${PORT}}"
LOG_FILE="${ROOT}/tmp/$(basename "$0" .sh)-server-${PORT}.log"
PID_FILE="${ROOT}/tmp/$(basename "$0" .sh)-server-${PORT}.pid"

mkdir -p "${ROOT}/tmp"

SERVER_STARTED_BY_SCRIPT=0
if ! lsof -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  (
    cd "${ROOT}"
    python3 -m http.server "${PORT}" >"${LOG_FILE}" 2>&1 &
    echo $! > "${PID_FILE}"
  )
  SERVER_STARTED_BY_SCRIPT=1
  sleep 1
fi

cleanup() {
  if [[ "${SERVER_STARTED_BY_SCRIPT}" -eq 1 ]] && [[ -f "${PID_FILE}" ]]; then
    PID="$(cat "${PID_FILE}" || true)"
    if [[ -n "${PID}" ]] && kill -0 "${PID}" >/dev/null 2>&1; then
      kill "${PID}" >/dev/null 2>&1 || true
      wait "${PID}" 2>/dev/null || true
    fi
    rm -f "${PID_FILE}"
  fi
}
trap cleanup EXIT

cd "${ROOT}"
case "$(basename "$0")" in
  run_rosary_smoke.sh) node scripts/tests/rosary_smoke.mjs "--base-url=${BASE_URL}" ;;
  run_rosary_menu_behaviors.sh) node scripts/tests/rosary_menu_behaviors.mjs "--base-url=${BASE_URL}" ;;
  run_rosary_end_stage_rules.sh) node scripts/tests/rosary_end_stage_rules.mjs "--base-url=${BASE_URL}" ;;
  run_rosary_prayer_behavior.sh) node scripts/tests/rosary_prayer_behavior.mjs "--base-url=${BASE_URL}" ;;
  run_rosary_intro_cta_behavior.sh) node scripts/tests/rosary_intro_cta_behavior.mjs "--base-url=${BASE_URL}" ;;
  run_rosary_ui_regression.sh) node scripts/tests/rosary_ui_regression.mjs "--base-url=${BASE_URL}" ;;
  run_story_floating_player.sh) node scripts/tests/story_floating_player.mjs "--base-url=${BASE_URL}" ;;
  run_checklist_improvements.sh) node scripts/tests/checklist_improvements.mjs "--base-url=${BASE_URL}" ;;
  *) echo "Unknown runner: $0"; exit 1 ;;
esac
