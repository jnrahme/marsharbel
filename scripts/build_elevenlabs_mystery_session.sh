#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <mystery_key> [voice_id]"
  echo "Example: $0 joyful_2"
  echo "Example: $0 joyful_2 wWWn96OtTHu1sn8SRGEr"
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
  exit 1
fi

KEY="$1"
VOICE_ID="${2:-wWWn96OtTHu1sn8SRGEr}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$ROOT/manual-narration/full-audio-pack/rosary-en"
OUT_DIR="$ROOT/manual-narration/elevenlabs-session"

mkdir -p "$OUT_DIR"

FILES=("$SRC_DIR/${KEY}-step-"*.txt)
if [ ! -e "${FILES[0]}" ]; then
  echo "No files found for key: $KEY"
  exit 1
fi

if [ "${#FILES[@]}" -ne 13 ]; then
  echo "Expected 13 step files for ${KEY}, found ${#FILES[@]}."
  exit 1
fi

OUT_FILE="$OUT_DIR/${KEY}-full-session-script.md"
{
  echo "# ${KEY} Full Recording Script"
  echo
  echo "Voice: ${VOICE_ID}"
  echo "Use one stage per exported mp3, keeping step mapping exactly."
  echo
  echo "Target files: media/rosary/${KEY}/step-01.mp3 ... step-13.mp3"
  echo
  for f in $(printf '%s\n' "$SRC_DIR/${KEY}-step-"*.txt | sort); do
    step="$(basename "$f" .txt | sed "s/${KEY}-step-//")"
    echo "## STEP ${step} -> media/rosary/${KEY}/step-${step}.mp3"
    echo
    cat "$f"
    echo
    echo "---"
    echo
  done
} > "$OUT_FILE"

echo "Wrote: $OUT_FILE"
