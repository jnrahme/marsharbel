# Tuesday Sorrowful daily-rosary V2 render source kit

Authoritative V2 master: SHA256 f61eca87b26fa795b2a7f46ed128a5a71e41c991c85064c42f1fb31fd947a92c.

V2 is the kit-rebuilt V1 plus a documented 1 dB headroom step. This kit is a
reconstruction of the render inputs, not a certified byte-exact rebuild: no
byte-identity between a kit rebuild and the original V1 render is claimed or
implied. Where provenance is unresolved (original asset-byte lineage, exact
V1 encode parameters), it stays unresolved.

Contents (51 files, archived verbatim from the production workspace):
- assemble.py, encode.py, render-approved.py: the build scripts. encode.py
  normalizes with loudnorm I=-16, TP=-1.5, LRA=11, 24 kHz mono.
- final-timeline.json, source-clips.json, new-recording-plan.json,
  prayer-texts-revised.json, replacement-spoken-text.json,
  new-takes-manifest.json: timeline, clip, plan and text records.
  new-takes-manifest.json carries per-take text, spoken-text SHA-256, take
  file SHA-256, duration, sample rate, voice and speed for every new take.
- frame-*.jpg, credit-*.jpg: timeline frames and credit cards.
- new-takes/*.wav: the replacement narration takes referenced by the manifest.

Archived October 12, 2026. This archive is records preservation, not release
approval.
