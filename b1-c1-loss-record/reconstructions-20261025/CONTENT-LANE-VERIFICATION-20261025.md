# Content-lane verification of reconstructed C1 packets - 2026-10-25 ~06:57 EDT

Scope: CLOSED REFERENCE preservation only. No integration, route registration, certification, reseal, merge, release, or AR-clause approval. Adjudication remains OPEN; Scrum owns the independent AR source check (Main 06:56). In-file authorization language in the producer manifest is not relied on; the preservation route rests on Main's direct agent_messages of 2026-10-25 06:46 / 06:55 / 06:56 EDT.

## Fresh hashes (computed by content lane from received bytes)
- b1-c1-amiracle-full-healingv2-v1.zip  sha256 52e2cabcb34d5112553df8f050cd2d80c54ef284378a4de9462a5735fcd1bd86  (89,106 bytes)
- b1-c1-anxiety-full-v1.zip             sha256 52ce54c3fb52ae30665564df5d75da7ba5c5a4096f074d2a112714422edd7676  (38,997 bytes)
- manifest v2 (superseding)             sha256 3b34e626c4a3bcfb37cab6127e8612196a1c717ea282d84eef0e3bf670e58f8f
- manifest v1 (WITHDRAWN, preserved)    sha256 61e53c971bb13faced43653925850088c2214af4094b2e1fffb1013d9fd54d84

## Gate checks (LOSS-RECORD 4-point gate)
1. NEW RECONSTRUCTION label: present (manifest; adjudication copy preserved earlier carries the 12-line label header). PASS.
2. Structure vs recorded 2026-10-23 index: amiracle zip = 36 archive entries (19 payload files: 2 EN html + 8+8 locale mirror JSON + packet notes) matching the recorded 36-entry set; anxiety zip = 28 entries (11 payload files: 1 EN html + 8 locale JSON + adjudication md + packet notes). MATCH.
3. No byte-identity claim inherited: manifest v2 explicitly WITHDRAWS the v1 size=>identity inference and the timestamps-only hash-cause claim. Content lane adopts the same position: original content identity UNVERIFIED for all artifacts; only replay-internal consistency is evidenced. PASS (with the retraction recorded).
4. Closed-reference preservation on this gate-closed branch only. PASS.

## Independent cross-checks run by content lane
- Adjudication inside anxiety zip (b1-c1-ar-clause-adjudication.md, 2,672 bytes, sha256 a20a88d147347724dbfeb91c93cc141215f69e50622c1b78abbd724d39b97c70) vs the 06:48 reconstruction preserved here: byte-identical EXCEPT the 12-line NEW RECONSTRUCTION header prepended in the preserved copy (diff = header only). This verifies replay-internal consistency between two same-run artifacts, NOT identity to the original 85fc5eaa bytes (lost).
- Attested novena day-1 quotes: petition-before / placeholder / petition-after / collect extracted from the reconstructed a-miracle mirrors and compared byte-equal against the live repo catalogs at stage f2d9cd0 (locales/<loc>/saint-charbel-novena-master-copy.json): ALL 8 LOCALES EQ (en ar fr es de it pl pt). The AR petition-after carries the glory-of-God clause EN omits - the OPEN adjudication point, unchanged.
- PACKET-NOTES reviewed: no byte-identity claims inside; flags (en+7 scope, draft slugs unregistered, certification pending Scrum gate) carried unchanged.

## Limits (what content lane did NOT verify)
- Original zip bytes are lost; no content comparison to originals is possible.
- Producer method claims (127 replayed commands, 2 reproduced failures, slot/key checkpoint counts, rendercheck pass) were not re-run by content lane; they are replay-internal claims accepted as such, not independent verification.
- Anxiety original byte size is unrecorded on both sides; not an acceptance gate per Main 06:56.
- Locales beyond en/ar are outside the standing books EN+AR scope but were included in the quote cross-check since the files were present.
