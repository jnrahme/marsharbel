#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PORT="${PORT:-4198}"
node "$ROOT/scripts/dev-server.mjs" --port="$PORT" >/tmp/marsharbel-hero-crop-qa.log 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT
sleep 1
status=0
BASE_URL="http://127.0.0.1:$PORT" node "$ROOT/scripts/tests/hero_figure_crop.mjs" || status=$?
if (( status != 0 )); then
  echo "Hero-figure crop gate failed (exit $status)" >&2
fi
exit "$status"
