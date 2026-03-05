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
    node "${ROOT}/scripts/dev-server.mjs" --port="${PORT}" >"${LOG_FILE}" 2>&1 &
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
node scripts/tests/site_smoke.mjs "--base-url=${BASE_URL}"
