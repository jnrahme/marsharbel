#!/usr/bin/env bash
set -euo pipefail

VOICE_ID="${1:-wWWn96OtTHu1sn8SRGEr}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

keys=(
  joyful_1 joyful_2 joyful_3 joyful_4 joyful_5
  luminous_1 luminous_2 luminous_3 luminous_4 luminous_5
  sorrowful_1 sorrowful_2 sorrowful_3 sorrowful_4 sorrowful_5
  glorious_1 glorious_2 glorious_3 glorious_4 glorious_5
)

for key in "${keys[@]}"; do
  "$ROOT/scripts/build_elevenlabs_mystery_session.sh" "$key" "$VOICE_ID"
done

echo "Built ${#keys[@]} mystery session files."
