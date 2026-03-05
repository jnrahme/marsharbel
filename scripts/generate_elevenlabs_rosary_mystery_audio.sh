#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <mystery_key> [voice_id]"
  echo "Example: $0 joyful_1"
  echo "Example: $0 joyful_1 wWWn96OtTHu1sn8SRGEr"
  exit 1
fi

KEY="$1"
VOICE_ID="${2:-wWWn96OtTHu1sn8SRGEr}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="${ROSARY_TEXT_DIR:-$ROOT/manual-narration/full-audio-pack/rosary-en-speech-only}"
if [ ! -d "$SRC_DIR" ]; then
  SRC_DIR="$ROOT/manual-narration/full-audio-pack/rosary-en"
fi
DST_DIR="$ROOT/media/rosary/${KEY}"
BACKUP_DIR="$ROOT/manual-narration/elevenlabs-session/_backup-audio/${KEY}"

API_KEY="${ELEVENLABS_API_KEY:-}"
if [ -z "$API_KEY" ] && [ -f "$HOME/.zshrc" ]; then
  API_KEY="$(sed -n 's/^export ELEVENLABS_API_KEY=\"\(.*\)\"/\1/p' "$HOME/.zshrc" | tail -n 1)"
fi

if [ -z "$API_KEY" ]; then
  echo "ELEVENLABS_API_KEY is not set."
  exit 1
fi

mkdir -p "$DST_DIR" "$BACKUP_DIR"

files=("$SRC_DIR/${KEY}-step-"*.txt)
if [ ! -e "${files[0]}" ]; then
  echo "No narration text files found for mystery: $KEY"
  exit 1
fi

if [ "${#files[@]}" -ne 13 ]; then
  echo "Expected 13 stage files for ${KEY}, found ${#files[@]}"
  exit 1
fi

ok=0
for file in $(printf '%s\n' "${files[@]}" | sort); do
  step="$(basename "$file" .txt | sed "s/${KEY}-step-//")"
  dst="$DST_DIR/step-${step}.mp3"
  tmp="$DST_DIR/step-${step}.mp3.tmp"
  err="$ROOT/tmp/elevenlabs-${KEY}-step-${step}.error.json"

  if [ -f "$dst" ]; then
    cp -f "$dst" "$BACKUP_DIR/step-${step}.original.mp3"
  fi

  text="$(cat "$file")"
  payload="$(jq -n --arg text "$text" '{
    text: $text,
    model_id: "eleven_multilingual_v2",
    voice_settings: {
      stability: 0.45,
      similarity_boost: 0.80,
      style: 0.35,
      use_speaker_boost: true
    }
  }')"

  code="$(curl -sS -w "%{http_code}" -o "$tmp" \
    -X POST "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}" \
    -H "xi-api-key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload")"

  if [ "$code" != "200" ]; then
    mv "$tmp" "$err" 2>/dev/null || true
    echo "FAILED ${KEY} step-${step} (HTTP ${code})"
    cat "$err" 2>/dev/null || true
    exit 1
  fi

  mv "$tmp" "$dst"
  echo "WROTE $dst"
  ok=$((ok + 1))
done

echo "Done: ${ok} files replaced for ${KEY}."
