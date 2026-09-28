#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PORT="${PORT:-4189}"
node "$ROOT/scripts/dev-server.mjs" --port="$PORT" >/tmp/marsharbel-eucharistic-qa.log 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT
sleep 1
# Capture the browser test exit explicitly so a missing Chromium binary,
# JS import error, assertion failure or crashed process is a CI failure.
status=0
BASE_URL="http://127.0.0.1:$PORT" node "$ROOT/scripts/tests/eucharistic_collection.mjs" || status=$?
if (( status != 0 )); then
  echo "Eucharistic browser regression failed (exit $status)" >&2
fi
exit "$status"
