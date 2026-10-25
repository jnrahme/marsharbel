# 2026-10-26 prep checkpoint (Monday, Joyful, Saint Demetrius of Thessalonica)

Status: PREP EVIDENCE ONLY. No render, no mint, no upload, no release PASS. All gates with Scrum/main.

## Donor (EN body audio)
- Source: published episode 6VTvjDk6x-k "Daily Rosary | Monday, October 19, 2026 | Joyful Mysteries | Saints John de Brebeuf & Isaac Jogues" (oembed-verified public 2026-10-24 23:05 ET).
- Body splice: 17.935s (joyful-announcement exact unit match, NCC 0.9963). Body duration 2027.162s.
- Body master (44.1k stereo) sha256 prefix: bacae24f5c44b6857c349691079b0984 ; 16k mono working copy: 322e0f0d5601504f45ee46cbf4e4ecf5. WAVs NOT committed (357MB); re-derive: download episode audio, cut at 17.935s.
- Donor WAVs live in agent factory storage only; original public video is the recovery source.
- Findings: see donor-evidence/. Key ones: repo audio/en/joyful units are meditation-only snippets, NOT sample-identical to the published body (different generation; wording matches the 61 keys); donor body reuse is the only provenance-true path. Tail 1948.81->2027.16s measured digital silence; spoken tail includes thank-you + subscribe lines (1942.86-1948.82). No trim proposed.
- Quality: unresolved spoken-word differences with recognizer evidence only (enunciation/simian/bead-9) - see caveats in oct19-key-verification-global.json. Full donor quality unverified.

## Art (Scrum 23:10 candidate gate; final layout/film gates pending)
- Selected: Kyiv Demetrius mosaic (intro) + Giotto Scrovegni cycle (5 mysteries, Virgin Annunciation panel). Gabriel panel NOT selected; no composite.
- Ledger: joyful-art-ledger-oct26-aec3e3cc.md (exact sources/hashes/URLs). All 6 received files hash-match.
- Licence facts preserved incl. CC vs PD distinction, Nativity PD-old-100-1923 refinement, Italy jurisdiction uncertainty. No licence clearance claim for the whole film.
- Previews: previews/ (intro card, 5 mystery intro cards, 5 prayer-along pages with full Hail Mary + progress dots, 6 per-art credit cards with exact URLs, overview slate; each with 390px phone-proof). All carry "LAYOUT PREVIEW - NOT FOR RELEASE". Full compositions preserved; no crop/colour/restoration; no upscaling.

## Words
- EN intro (main-selected): "Today, October twenty-sixth, we remember Saint Demetrius of Thessalonica, a martyr. Saint Demetrius of Thessalonica, pray for us."
- AR intro (main-selected): اليوم السادس والعشرون من تشرين الأوّل. نذكر القدّيس ديمتريوس التسالونيكي، شهيداً. يا قدّيس ديمتريوس التسالونيكي، صلِّ لأجلنا.
- AR joyful key candidates: ar-joyful-keys-oct26-36bc4597.json (61/61 units, SHA-verified mechanically; Scrum 23:07 words PASS at candidate strength; exact-keys/independent-source gate before any mint; NO mints yet).

## Next gated steps
Morning voice-production (EN+AR intro), art final decision, exact audio/film gates. Oct 25 EN+AR holds unchanged.
