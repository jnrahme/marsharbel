# ElevenLabs Session Kit

This folder is the recording-facing layer for your Rosary voice production.

## Source of truth
- Rosary narration source text: `manual-narration/full-audio-pack/rosary-en/`
- Output mapping: `manual-narration/full-audio-pack/master-file-map.csv`

## Files in this folder
- `VOICE-STYLE.md`: recommended voice direction + settings
- `joyful-1-stage-02-sample.txt`: approved sample style for first-part mystery prompt
- `ROSARY-MYSTERY-TEMPLATE.md`: reusable structure reference
- `<mystery_key>-full-session-script.md`: full 13-stage recording script for each mystery key

## Standard mystery keys
- `joyful_1` to `joyful_5`
- `luminous_1` to `luminous_5`
- `sorrowful_1` to `sorrowful_5`
- `glorious_1` to `glorious_5`

## Build commands
- Build one mystery session script:
  - `./scripts/build_elevenlabs_mystery_session.sh joyful_1`
- Build all 20 session scripts:
  - `./scripts/build_all_elevenlabs_mystery_sessions.sh`
- Verify kit integrity:
  - `./scripts/verify_elevenlabs_session_kit.sh`

## Output rule
Export each stage as MP3 to its exact target path under `media/rosary/<mystery_key>/step-XX.mp3`.
