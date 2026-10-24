# MASTER_TASKS

Named cross-PR follow-ups owned by the merge train. Each entry names what is
deferred, why, and the tooling that unblocks it.

## face-crop: ratio classes on byte-locked masters (opened 2026-10-13)

The hero-figure face-crop PR (fix/hero-figure-face-crop) adds build-time
`is-portrait` / `is-square-ish` ratio classes everywhere the build owns page
bytes. Three masters are byte-locked by reviewed contracts, so this PR ships them
with NO byte change (even a head-only cache-bust trips the twin-evidence and
mirror-capability gates) and they get their classes in a follow-up. The fleet
styles.css change still reaches them on cache expiry / CDN flush: qadisha's
mar-lichaa gains the max-height cap and the sepia gains the no-upscale rule,
both without any markup change.

- `qadisha-valley.html` - mar-lichaa monastery img (640x960, ratio 0.67) needs
  `is-portrait`. Locked by travel twin evidence (`travel-equivalence.json`
  families `qadisha-valley-travel-master` + zh twin) AND the keyed mirror
  capability check; both gates verifiably go red on any master byte drift
  (body class AND head-only cache-bust). The 3/4 portrait frame waits for the
  twin re-pin; the max-height cap reaches it with the fleet CSS.
- `our-lady-of-lebanon-harissa.html` - basilica img (1100x982, ratio 1.12)
  needs `is-square-ish` (semantic only; rendering unchanged). Locked by travel
  twin evidence (`our-lady-of-lebanon-harissa-travel-master` + zh twin).
- `saint-charbel-prayers.html` - historic sepia portrait (419x595, ratio 0.70)
  needs `is-portrait`. Body frozen by `locales/prayer-metadata-contract.json`
  (`mainSha256`). The no-upscale CSS rule already fixes its softness via the
  head cache-bust; the 3/4 portrait frame waits for the class.

Unblock path: scrum's twin/contract re-pin tooling (same family as the #789
twin cache-bust re-pin). `scripts/tests/hero_figure_crop.mjs` and the
build-pages classifier skip these masters via the same contract files
(`locales/travel-equivalence.json`, `locales/prayer-metadata-contract.json`);
remove the skips in the same PR that lands the re-pins.
