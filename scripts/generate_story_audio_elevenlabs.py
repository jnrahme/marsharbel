#!/usr/bin/env python3
"""
Generate Saint Charbel story narration clips with ElevenLabs.

Requirements:
  - ELEVENLABS_API_KEY in environment
Usage:
  python3 scripts/generate_story_audio_elevenlabs.py \
    --voice-id L1aJrPa7pLJEyYlh3Ilq
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORYBOOK_JS = ROOT / "storybook.js"
OUT_DIR_DEFAULT = ROOT / "media" / "storybook" / "en-elevenlabs"


def extract_en_slides(js_text: str) -> list[dict[str, str]]:
    block_match = re.search(r"en:\s*\[(.*?)\],\s*ar:", js_text, re.S)
    if not block_match:
        raise ValueError("Could not locate English story block in storybook.js")
    en_block = block_match.group(1)

    raw_objs: list[str] = []
    depth = 0
    start = -1
    in_str = False
    prev = ""
    for i, ch in enumerate(en_block):
        if ch == "'" and prev != "\\":
            in_str = not in_str
        if in_str:
            prev = ch
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    raw_objs.append(en_block[start + 1 : i])
                    start = -1
        prev = ch
    slides: list[dict[str, str]] = []

    def pick(field: str, src: str) -> str:
        m = re.search(rf"{field}:\s*'([^']*)'", src, re.S)
        return m.group(1).strip() if m else ""

    for obj in raw_objs:
        title = pick("title", obj)
        body = pick("body", obj)
        prayer = pick("prayer", obj)
        heart = pick("heart", obj)
        audio = pick("audio", obj)
        if not title:
            continue
        slides.append(
            {
                "title": title,
                "body": body,
                "prayer": prayer,
                "heart": heart,
                "audio": audio,
            }
        )
    return slides


def build_text(slide: dict[str, str]) -> str:
    title = (slide.get("title") or "").strip()
    body = (slide.get("body") or "").strip()
    prayer = (slide.get("prayer") or "").strip()
    heart = (slide.get("heart") or "").strip()

    if prayer.lower().startswith("little prayer:"):
        prayer = "Let us pray. " + prayer.split(":", 1)[1].strip()
    if heart.lower().startswith("heart moment:"):
        heart = "Remember this. " + heart.split(":", 1)[1].strip()

    parts = [title, body, prayer, heart]
    text = ". ".join(p.strip().rstrip(".") for p in parts if p)
    return re.sub(r"\s+", " ", text).strip()


def tts_elevenlabs(api_key: str, voice_id: str, text: str, model_id: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128&optimize_streaming_latency=0"
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.62,
            "similarity_boost": 0.92,
            "style": 0.08,
            "use_speaker_boost": True,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "xi-api-key": api_key,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice-id", required=True, help="ElevenLabs voice ID")
    parser.add_argument("--model-id", default="eleven_multilingual_v2")
    parser.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT))
    parser.add_argument("--pause-ms", type=int, default=250)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    js_text = STORYBOOK_JS.read_text(encoding="utf-8")
    slides = extract_en_slides(js_text)
    missing_audio = [i + 1 for i, s in enumerate(slides) if not s.get("audio")]
    if missing_audio:
        raise ValueError(f"Slides missing audio mapping: {missing_audio}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Slides detected: {len(slides)}")
    for idx, slide in enumerate(slides, start=1):
        out_file = out_dir / slide["audio"]
        text = build_text(slide)
        if not text:
            print(f"[skip] Slide {idx}: empty text")
            continue
        if out_file.exists() and not args.overwrite:
            print(f"[keep] {out_file.name}")
            continue
        if args.dry_run:
            print(f"[dry] {out_file.name}: {text[:90]}...")
            continue

        api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
        if not api_key:
            raise EnvironmentError("ELEVENLABS_API_KEY is not set.")

        try:
            audio = tts_elevenlabs(api_key, args.voice_id, text, args.model_id)
        except urllib.error.HTTPError as e:
            details = e.read().decode("utf-8", errors="ignore")
            print(f"[error] {out_file.name}: HTTP {e.code} {details}", file=sys.stderr)
            return 1
        except Exception as e:  # noqa: BLE001
            print(f"[error] {out_file.name}: {e}", file=sys.stderr)
            return 1

        out_file.write_bytes(audio)
        print(f"[ok] {out_file.name} ({len(audio)} bytes)")
        time.sleep(max(args.pause_ms, 0) / 1000.0)

    print(f"Done. Output dir: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
