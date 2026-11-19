# Rosary Factory - the daily rosary assembly rule

**A day is created from fixed parts. Never rebuild from scratch.**

Standing rule for this lane (set by the owner on 2026-11-16): the daily rosary is assembled
by script from already-created parts - fixed recordings and card programs per language per
mystery set - and the only per-day inputs are (1) the saint of the day, locked from the LIVE
Vatican News saint page, and (2) the day's intro narration audio. No rebuilds from scratch.

## Creating a day (the instant path)

```
python3 new_day.py 2026-11-22            # resolves mystery + live saint, prints the intake form
# -> hand the intake form to the voice-minting checkpoint
# -> receive intro WAV + its sha256 + the exact minted text + the text's sha256
python3 build_day.py --date 2026-11-22 --lang en --intro-wav <wav> --intro-sha256 <sha> \
    --intro-text "<exact minted intro text>" --intro-text-sha256 <text sha> \
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
- Overflow hard-fail: a card whose body text bottoms past 646px, whose title/saint-name is
  wider than 1184px, or whose credit block bottoms past 700px STOPS the build (no append, no
  ship). The minted intro text overflowing the intro card also stops the build.
- NCC >= 0.99 of re-rendered body cards vs donor frames at equal content timestamps
  (the byte/frame-equivalence proof; texts are machine-copied from the pack map, never retyped).
- Decode-clean (-xerror).
- Duration gate: the master duration must equal the expected film length (intro + body span +
  credits) within 0.5s; a mismatch stops the build.
- Resume binding: --resume reuses a saved master ONLY when the saved phase-7 fingerprint
  (date, saint, intro WAV+text shas, pack donor+art pins, code sha) matches the current inputs
  exactly; any change refuses the resume.
- Levels gate: encoded true peak <= -2 dBTP. The mix peak is measured first; if hotter than
  -2.5 dBFS, constant attenuation is applied at the single AAC encode and the measure is reported.
- Credit cards are ALWAYS rendered fresh from the pack ledger (never reused from donor pixels:
  a donor's credit section may predate the current ledger). Wording per pack credits_mode:
  ledger_credit_copy = verbatim ledger copy; commons_lines = fixed lines built from ledger
  fields (artist, work, source URL, caveat); giotto_template = the standing Giotto attribution
  template filled from ledger fields. URLs hard-wrapped, jurisdiction caveats retained. No
  worldwide-clearance claims.
- Saint lock: new_day.py fetches the Vatican News index live. The spoken form is confirmed at
  the minting checkpoint (source typos fixed there, e.g. VN 11/21 headline "Sheperd" -> spoken
  "the Good Shepherd" per the article body). build_day.py RE-VERIFIES the locked saint against
  the live index and REFUSES the build on a mismatch - there is no silent fallback. When the
  saint verifies on the index but has no detail page, the description links the index; never
  invent detail-page slugs. Name-variant overrides (REVIEWED_VARIANTS) are dated locks with an
  evidence note, added only at the minting checkpoint.
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
6. AR IS NOT BUILT. The factory has no RTL card renderer and no Arabic labels/dates/prayers,
   and build_day.py fails closed on any --lang other than en. Opening the AR lane is new work:
   Arabic texts, RTL rendering (Noto Sans Arabic, right-aligned; reference: the
   ar-prayalong-release card style), and ar/* packs staged per this section. The MAR-65 hold
   covers exactly ONE artifact: the Nov 16 2026 AR Joyful release (archive folder
   13lHJffVCSyWxkL1zGj0wQm480J7OF_BC) - never release that artifact. MAR-65 does NOT hold the
   AR lane itself; the lane is simply unbuilt.

7. v4 amendments (2026-11-17): --intro-text/--intro-text-sha256 are mandatory (the minted words
   own the intro card, hash-verified). Intro/credit segments encode at 250k (24k is proven
   unreadable on art+text cards). Long builds run as build + --resume against phase7.ok.
   Always eyeball qa-credit.png and qa-intro.png before reporting a build done - NCC does not
   prove readability.

8. Playbook reference (provenance corrected 2026-11-19): the owner's asks on 2026-11-18 were
   about better videos, a possible animated series, and a retrievable viral-video research
   store - not a standing build rule for this lane. The playbook (Drive
   1yK2TBK90K6vJA96inaz5PMUpNexBZFph) and lessons-log.md (Drive 1dtv3xDiTU-J9Wi3kQlTa1I8e-QxrZlgM)
   are that research store. Applying playbook ideas to this lane is the lane coordinator's
   reversible creative ruling (2026-11-18), not owner instruction: (a) promo reels get a Ken
   Burns pan and the follow-ask as the FINAL caption line, from the next promo; (b) the rosary
   body stays slow and locked - no 2-3s cuts, no ending restructure; (c) the intro card may be
   tightened toward a short hook ONLY if the donor body stays untouched; (d) existing hard
   rules stand (candle+portrait template, end splash, subscribe ask). Lessons skeletons get
   filed per release with numbers n/a until an insights route exists. Any of (a)-(c) reverts
   on the coordinator's word.

9. v5 amendments (2026-11-19, independent review of the repo push): overflow/title/intro
   overflow hard-fail (was: collect-and-report); saint mismatch refuses the build (was: silent
   index fallback); duration gate added; --resume bound to an input fingerprint (was: marker
   file only); non-en locales fail closed; REVIEWED_VARIANTS entries are dated locks with
   evidence; offline negative tests in tests/negative_tests.py.

10. v7 amendments (2026-11-19, luminous staging): new card kind INTENT (opening intentions:
    'For an increase in faith/hope/charity.'); art files may be .jpg or .png (sha-pinned either
    way); pack field donor_layout=legacy marks an audio-only donor whose frames predate the
    factory card layout - frame NCC vs donor is printed for the record, not asserted, and the
    pack note must say why. Saint-index parser repair: older VN index pages carry the saint's
    name in the section <h2> with a generic 'Read all...' anchor - the dated entry binds the
    nearest preceding heading; mocked tests cover the repair and its refusal side.
    Description {VN_URL} fills with the stable saints DAY-INDEX page (EN43 and EN48-54
    convention); the exact bound entry page is recorded in the manifest instead.
11. v8 amendments (2026-11-19, review round 1 on PR #932): in legacy donor_layout the body
    video assembles from THIS build's rendered cards - chunked concat-filter, cumulative
    frame-boundary exact, lossless chunks joined at body bitrate; donor frames are never
    used and the manifest records vbody_source. The luminous pack credits_mode is
    ledger_credit_copy: every artwork's card copy is exact per-art text held in the ledger
    (source_url verbatim inside it, reproduction source and PD-Art/jurisdiction note
    included - the Cana card credits Google Arts & Culture / Louvre-RMN, never a Commons
    boilerplate). Tests: legacy-fresh-body (red-donor pixel proof), luminous-credit-copy
    statics, credit-copy-missing refusal.

10. v6 amendments (2026-11-19, re-review): the fingerprint binds ALL build-affecting bytes -
    pack.json, film-time-map.json, art-ledger.json, description-template.txt, donor/art pins,
    ask/attenuate/saint-check options, intro WAV+text, date, saint, and the code - and the
    saved master must match the master hash recorded at build time (a replaced master refuses
    resume). The saint gate binds ONE dated index entry (no cross-entry token mixtures) and
    re-checks the entry page's H1; the matched entry is recorded in the manifest.
    bootstrap_packs.py uses a documented --from-dir adapter boundary (proven) or plain-HTTPS
    Drive fetches (not execution-proven; the sha pins catch interstitials).
