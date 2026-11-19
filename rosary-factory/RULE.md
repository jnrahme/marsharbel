# Rosary Factory - the daily rosary assembly rule

**A day is created from fixed parts. Never rebuild from scratch.**

Owner directive (Joey, 2026-11-16, via Main): the daily rosary is assembled by script from
already-created parts - fixed recordings and card programs per language per mystery set -
and the only per-day inputs are (1) the saint of the day, locked from the LIVE Vatican News
saint page, and (2) the day's intro narration audio. Tokens do not go into rebuilds.

## Creating a day (the instant path)

```
python3 new_day.py 2026-11-22            # resolves mystery + live saint, prints the intake form
# -> hand the intake form to the voice minter (Main: tools speak, Achird, approved direction)
# -> receive intro WAV + sha256 + text_sha256
python3 build_day.py --date 2026-11-22 --lang en --intro-wav <wav> --intro-sha256 <sha> \
    --saint-name "<confirmed spoken saint name>" --ask her|his|their --outdir out/2026-11-22
```

Output: `master-<lang>-<date>-<mystery>.mp4`, `description-<date>.txt`,
`film-time-map-<date>.json`, `manifest-<date>.json`, QA frames - ready for the review gate
and the desk publish route. Then archive the whole outdir to a Drive release folder
(`en-<date>-release`, anyone-reader) the same day.

## Rotation (locked)

Mon=Joyful, Tue=Sorrowful, Wed=Glorious, Thu=Luminous, Fri=Sorrowful, Sat=Joyful, Sun=Glorious.

## Folder structure

```
rosary-factory/
  RULE.md                this file - the written rule
  new_day.py             daily trigger (prep): mystery + live saint + intake form
  build_day.py           assembly: fixed parts + intro WAV -> gated master
  bootstrap_packs.py     fetches+verifies pack binaries from Drive (sha-pinned)
  packs/
    registry.json        per-pack status, Drive IDs, sha256 pins
    <lang>/<mystery>/
      pack.json          donor pins, card structure config, VR style, credits mode
      film-time-map.json canonical card texts/timings (donor coords)
      art-ledger.json    artwork provenance + credit copy (rights record)
      description-template.txt
      art/ g1..g5.jpg    (binary, Drive-fetched by bootstrap, sha-pinned)
      donor.mp4          (binary, Drive-fetched by bootstrap, sha-pinned)
```

## Hard gates (build_day.py enforces all of them; a failure stops the build)

- Donor, art (5/5) and intro WAV sha256 pins verified before any rendering.
- Card overflow scan (all text bottoms <= 646px; credits <= 700px).
- NCC >= 0.99 of re-rendered body cards vs donor frames at equal content timestamps
  (the byte/frame-equivalence proof; texts are machine-copied from the pack map, never retyped).
- Decode-clean (-xerror).
- Levels gate: encoded true peak <= -2 dBTP. The mix peak is measured first; if hotter than
  -2.5 dBFS, constant attenuation is applied at the single AAC encode and the measure is reported.
- Credit cards are ALWAYS rendered fresh from the pack ledger (never reused from donor pixels:
  a donor's credit section may predate the current ledger). Art credit wording is verbatim
  ledger copy, URLs hard-wrapped, jurisdiction caveats retained. No worldwide-clearance claims.
- Saint lock: new_day.py fetches the Vatican News index live. The spoken form is confirmed at
  the minting checkpoint (source typos fixed there, e.g. VN 11/21 headline "Sheperd" -> spoken
  "the Good Shepherd" per the article body). The description links the index; never invent
  detail-page slugs.
- The intro WAV is the only generated media per day. No new paid services, ever.
- Publication stays on the existing route: review gate -> desk upload (no API writes to
  YouTube from this tooling) -> signed-out oembed verification -> FB-only promo packet.

## Staging a new pack (glorious, luminous, ar/*)

1. Pick the published-generation donor master from its Drive release folder; record sha256.
2. Copy its film-time-map (canonical texts), art ledger, and art bytes (sha-match to the
   standing ledger pins) into `packs/<lang>/<mystery>/`.
3. Write `pack.json` (copy an existing one; set label/fam_title/titles/vr_style/credits_mode/
   donor_audio_interval/map_intro_s from the donor's map header).
4. Derive `description-template.txt` from the donor episode's shipped description, replacing
   date/saint/chapters/URL with {DATE_LONG} {SAINT} {ASK} {CHAPTERS} {VN_URL}.
5. Update `packs/registry.json`, run `bootstrap_packs.py`, then prove the pack: build a past
   date with its original intro WAV and compare frames + description against the published
   master (NCC >= 0.99 body, description byte-identical), like the EN48/EN52 proofs.
6. AR packs additionally need the RTL card renderer (Noto Sans Arabic, right-aligned text;
   reference: the ar-prayalong-release card style). AR daily production stays on owner hold
   (MAR-65) until the owner opens that lane.

7. v4 amendments (2026-11-17): --intro-text/--intro-text-sha256 are mandatory (the minted words
   own the intro card, hash-verified). Intro/credit segments encode at 250k (24k is proven
   unreadable on art+text cards). Long builds run as build + --resume against phase7.ok.
   Always eyeball qa-credit.png and qa-intro.png before reporting a build done - NCC does not
   prove readability.

8. Playbook reference (provenance corrected 2026-11-19): Joey's own asks (WhatsApp 2026-11-18
   21:22-21:28, verified in observations) were "can you make better videos? maybe we can start
   an animated series of saint charbel", "start researching what make a viral video and store
   the information somewhere where we can retrieve it", and that the store be tool-agnostic.
   He did NOT issue a standing build rule for the rosary lane. The playbook (Drive
   1yK2TBK90K6vJA96inaz5PMUpNexBZFph) and lessons-log.md (Drive 1dtv3xDiTU-J9Wi3kQlTa1I8e-QxrZlgM)
   are the research store answering that ask. Applying playbook ideas to this lane is MAIN's
   reversible creative ruling (2026-11-18 21:27), not owner instruction: (a) promo reels get a
   Ken Burns pan and the follow-ask as the FINAL caption line, from the next promo; (b) rosary
   body stays slow and locked - no 2-3s cuts, no ending restructure; (c) intro card may be
   tightened toward a short hook ONLY if the donor body stays untouched; (d) existing hard
   rules stand (candle+portrait template, end splash, subscribe ask). Lessons skeletons get
   filed per release with numbers n/a until an insights route exists. Any of (a)-(c) reverts
   on Main's word.
