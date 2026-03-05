#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

for v in v20260302 v20260303 v20260304; do
  cp -f mystery-meditation.js "mystery-meditation.${v}.js"
  cp -f global-audio-player.js "global-audio-player.${v}.js"
done

echo "Synced mystery/global runtime files for v20260302, v20260303, v20260304."
