#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/manual-narration/elevenlabs-session"

keys=(
  joyful_1 joyful_2 joyful_3 joyful_4 joyful_5
  luminous_1 luminous_2 luminous_3 luminous_4 luminous_5
  sorrowful_1 sorrowful_2 sorrowful_3 sorrowful_4 sorrowful_5
  glorious_1 glorious_2 glorious_3 glorious_4 glorious_5
)

missing=0
bad=0

for key in "${keys[@]}"; do
  file="$DIR/${key}-full-session-script.md"
  if [ ! -f "$file" ]; then
    echo "MISSING: $file"
    missing=1
    continue
  fi

  steps=$(grep -c '^## STEP ' "$file" || true)
  if [ "$steps" -ne 13 ]; then
    echo "BAD STEP COUNT ($steps): $file"
    bad=1
  fi
done

if [ "$missing" -ne 0 ] || [ "$bad" -ne 0 ]; then
  echo "Verification failed."
  exit 1
fi

echo "Verification passed: all 20 session files exist with 13 steps each."
