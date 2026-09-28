#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PORT="${PORT:-4189}"
node "$ROOT/scripts/dev-server.mjs" --port="$PORT" >/tmp/marsharbel-eucharistic-qa.log 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT
sleep 1
BASE_URL="http://127.0.0.1:$PORT" node "$ROOT/scripts/tests/eucharistic_collection.mjs"
