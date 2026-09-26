#!/usr/bin/env python3
"""One brief, artifact-only ElevenLabs voice test. Never log credentials."""
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

TEXT = "When Francesco was a boy in Italy, he loved to pray. Years later, as Padre Pio, he listened to people who needed hope."
VOICE = "L1aJrPa7pLJEyYlh3Ilq"  # Existing Saint Charbel narration script's voice ID; test suitability.
OUT = Path("pio-voice-test.mp3")


def main():
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise SystemExit("Missing ELEVENLABS_API_KEY repository secret; no request made")
    # The test must fit the included characters and never enter paid overage.
    usage_req = urllib.request.Request("https://api.elevenlabs.io/v1/user/subscription", headers={"xi-api-key": key})
    try:
        with urllib.request.urlopen(usage_req, timeout=30) as response:
            usage = json.load(response)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Could not verify quota: HTTP {e.code}; no narration attempted") from None
    limit = usage.get("character_limit")
    used = usage.get("character_count")
    if not isinstance(limit, int) or not isinstance(used, int):
        raise SystemExit("Provider did not return a numeric included-character balance; no narration attempted")
    print(f"Tier: {usage.get('tier', 'unknown')}; used: {used}; included limit: {limit}; test text: {len(TEXT)} characters")
    if limit - used < len(TEXT):
        raise SystemExit("Insufficient included characters; no narration attempted")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128"
    payload = json.dumps({"text": TEXT, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.62, "similarity_boost": 0.92, "style": 0.08, "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={"xi-api-key": key, "accept": "audio/mpeg", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
    except urllib.error.HTTPError as e:
        # Provider error bodies can contain sensitive content; do not print them.
        raise SystemExit(f"Narration test failed: HTTP {e.code}") from None
    if not data.startswith(b"ID3") and not data.startswith(b"\xff\xfb") and not data.startswith(b"\xff\xf3") and not data.startswith(b"\xff\xf2"):
        raise SystemExit("Narration response was not recognizable MP3")
    OUT.write_bytes(data)
    print(f"Wrote voice-test audio ({len(data)} bytes)")


if __name__ == "__main__":
    main()
