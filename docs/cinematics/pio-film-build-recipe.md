# Padre Pio v3 film - build recipe (extracted from the production transcript)

Source: animated story video pipeline lane transcript (Sep 28 - Oct 8 2026), the run that
produced the accepted Pio v3 16-scene film (7:33.4, the "7:34 cut" Joey approved:
"this is perfect okay make every thing like this one"). Deployed master:
https://marsharbel.com/media/storybook-pio/pio-film-endcard.mp4
(124,664,121 bytes, sha256 a7dd9a7b7d3db0f5f96dc753500d7d3909d260b66151c7b9c68a6e524b33602a,
h264 1280x720 + aac). Extracted 2026-10-11 for the daily YouTube lane.

## Inputs (per film)
- Storybook pages: 1280x720 WebP stills (repo `media/storybook-<saint>/images/page-NN.webp`).
- Approved story script, one narration line set per scene (see process gates below).

## Narration (Kokoro)
- Package: `kokoro` (pip). Pipeline: `KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M', device='cpu')`.
- Voice: `am_michael`. Speed: `0.94`.
- Chunking: <=84 chars per chunk; 24 kHz FLAC per chunk.
- Assembly: sentence-end rests (0.47 s pauses); WAV master, then WAV->MP3/AAC per scene.
- Note: model weights download from HuggingFace; corporate egress (Zscaler) can block HF - pre-stage weights.

## Video assembly (ffmpeg)
Per scene (duration = its narration duration):
```
ffmpeg -loop 1 -i page-NN.webp -i scene-NN.wav -filter_complex \
  "[0:v]scale=2560:1440,zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=25[v]" \
  -map "[v]" -map 1:a -t <scene_seconds> -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac scene-NN.mp4
```
- Ken Burns only: slow push-in (zoom to max 1.15). No pans over stills, no frame-breaking moves (Joey's rule).
- Scenes joined with xfade dissolves (seam grids reviewed - blends must be proper dissolves).
- Final container: 1280x720, 25 fps, h264 crf 20, AAC audio.

## End card (site-referral tail)
- 3 s freeze on the final outro frame + text overlay: "Read the free storybook at marsharbel.com".
- Pure tail append after the last scene; no narration change.

## Loudness
- Target: -16 LUFS integrated, true peak <= -1.5 dBTP.
- Verify the FINISHED master by measurement (ebur128 print_format), not the loudnorm output row.
- Caveat from production: loudnorm dynamic mode drifts off target (a master read -17.0 LUFS / TP -0.6 after dynamic mode); use linear mode or a second pass until the measured file hits -16/-1.5.

## Process gates (the production standard)
1. Script map BEFORE voicing: full film script per scene, every narration line mapped to the panel that carries it. One review gate. Do not sanitize hard beats (deaths, war, violence stay told) - voice them in language the adjacent art can honestly carry (mood, aftermath, what a person did next).
2. After the nod: Kokoro re-voice + reassemble.
3. Full play-speed WATCHED verification of the new master, including crossfades: per-line verdicts (match/weak/mismatch - Pio's accepted tally was 38 match / 2 weak / 0 mismatch over 40 lines), seam grids per join, audio smoke slices at scene starts. Paper audits alone failed before (JPII stop-ship); the watch is the gate.
4. Deploy via TUS upload to the Hostinger webroot path; verify live with ranged-GET MD5 of first/last bytes + full Content-Length.
5. Durable records per film (NEW standard for the daily lane): script map, scene manifest, voice params, watched-verification verdicts, and a rights ledger entry - committed to the repo, not left in a container.

## Known gaps in the Pio records
- Pio v3 predates the formal watched-verification protocol; its QA of record is Joey's own acceptance.
- The original script-map/scene-manifest files lived in the builder's scratch container and are gone; this recipe is reconstructed from the transcript. New productions must keep these artifacts in-repo from day one (gap 5 above).
