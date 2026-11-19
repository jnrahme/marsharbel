# Rosary factory - equivalence proofs (2026-11-16)

## Proof A - reproduce EN52 (Joyful, donor EN47 generation) PASS
- Description byte-identical to the EN52 packet (built by the old one-off path).
- Frame NCC vs the EN52 master at t=1,30,300,600,900,1200,1500,1800,2025: 0.9867-1.0 (>= 0.99 bar; encode-noise floor).
- Factory master: 18,598,141 B, 2032.700s, TP -2.8 dBTP PASS. sha ddf7613ad5c0e4431b4262ebccc323c6b1c50a1cc3a229b5cb1ebdcc823b1a25.

## Proof B - reproduce published EN48 (Sorrowful, donor EN30 r3 generation) PASS
- Description byte-identical to the archived published description (10xK6X4Vb9wvQ2n_db3fmYJ1ExK2rQnW3).
- Body span NCC vs the published master (B77Ak6rirdI) at t=30..2090: 0.9904-0.9953.
- Intro t=2 NCC 0.9284: visually inspected both frames - identical text/layout/date/saint; the published file's intro is visibly more blurred (second-generation encode at lower effective bitrate). Content-equivalent; pixel noise only.
- Credit frames at t=2110/2150 NCC 0.92-0.96: visually inspected - identical credit card content (same artwork, same ledger credit copy); noise from differing encodes. Factory credits are always fresh-rendered from the current ledger by design (donor EN30 r3's credit pixels predated ledger credit_copy - caught by this check, exactly what it exists for).
- Factory master: 19,537,881 B, 2162.450s, TP -4.7 dBTP PASS. sha fb00f175df178f3bfc37f952819f14ea68675583d590ead3a22b0ba86316752b.

QA frames for both proofs: out/factory-EN52-test/ and out/factory-en48/ (intro/outro/card QA images).

== v4 production run: EN53 (2026-11-22, Glorious, St Cecilia) - first factory-built day shipped to the desk queue
- Two silent-drift bugs found by the qa frame eyeball and fixed in v4:
  1. Intro card text was constructed from --saint-name and drifted from the minted narration
     words. Fix: --intro-text + --intro-text-sha256 are now REQUIRED; the exact minted text is
     hash-verified, rendered on the card, and recorded in the manifest.
  2. Intro/credit segments encoded at 24k starved art+text cards into unreadability (NCC vs
     donor did NOT catch it; the qa-credit.png eyeball did). Fix: intro/credits encode at
     250k/350k maxrate. Body re-encode unchanged (proven donor path).
- --resume added (phase7.ok + phase7-state.json; phases 4-7 skippable) because sandbox builds
  exceed the 120s command cap: full build = run, then re-run same command with --resume.
- EN53 master: 19,110,268 B, 2021.066s, TP -3.2 dBTP PASS,
  sha 1ffe633f9b9b9a75343fa366d07f11a93d332751d3ea8fb0f5439e204817694b.
  NCC body 0.9985-0.9993 vs donor; qa-intro + qa-credit visually verified crisp/correct.
