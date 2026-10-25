# B1 C1 packet RECONSTRUCTION manifest - 2026-10-25
Producer: locale review lane, on Main's closed-reference reconstruction authorization (Oct 25 06:46).
CLOSED REFERENCE ONLY. No routes/certification/reseal/integration/merge/release. Not the original zip bytes.

## Reconstructed artifacts (fresh hashes)
1. b1-c1-amiracle-full-healingv2-v1.zip
   sha256 52e2cabcb34d5112553df8f050cd2d80c54ef284378a4de9462a5735fcd1bd86 - 89,106 bytes
   LOST ORIGINAL REFERENCE: sha256 20f93d71657a733e0383501312861b6ca8e8dc1a541d62c70ab5c07e62a3b58f, 89,106 bytes,
   sent 2026-10-23 05:04:33 EDT, agent_message_id agentmsg-01M5M02EGSXT94M0BVX66JTCDD,
   blob_hash b953582a67c64c562f8accf936898b70a8579d513863fb355757055268c7e896.
   NOTE: reconstruction byte size EQUALS the original's recorded byte size (89,106) - zip size is content-determined;
   consistent with byte-identical contents (zip timestamps differ, so the sha256 differs by construction).
2. b1-c1-anxiety-full-v1.zip
   sha256 52ce54c3fb52ae30665564df5d75da7ba5c5a4096f074d2a112714422edd7676 - 38,997 bytes
   LOST ORIGINAL REFERENCE: sha256 f9eb5ff25f82229a5f1537bcd0bc5cfdfcf8f2fb48ace690d462de50fcdd3710,
   sent 2026-10-23 05:13:06 EDT (blob_hash not persisted in my transcript; Main's inbound record holds it).
   Original byte size was not recorded on my side - Main can compare 38,997 against its record for content confirmation.
3. b1-c1-ar-clause-adjudication-RECONSTRUCTION-20261025.md (sent separately 06:48)
   sha256 8abbecc6aa73e9fb793ddf7880adc40afd94df01794a16718a6982846314115d
   Cross-confirmed: the anxiety zip replay independently regenerated the original md body (2,672 bytes) and it is
   BYTE-IDENTICAL to this reconstruction's body (cmp verified). Original producer commit 85fc5eaa (local-only, lost).

## Method (full replay, no invented values)
- Exact original base restored: git worktree at b77f2f16 (PR #876), the recorded production base.
- Oct 22 src edits replayed from the recorded script: replacement counts 5/3/1/15 match the recorded results exactly.
- EN pages rebuilt via node scripts/build-pages.mjs (4 pages); output matches the recorded "4 pages built, 4 written"
  and the recorded 8-file modified set exactly.
- All 127 production commands (Oct 23 02:0x-05:14) replayed verbatim from the transcript; 125 exited 0; the 2 nonzero
  exits (idx 3224 FileNotFoundError prayers.html; idx 3293 elision assert on ar tail) reproduce the ORIGINAL
  failures byte-identically - the original run hit and fixed the same things (fix at original idx 3296, replayed).
- No network, no external access, no unbounded generation.

## Checkpoint equality (recorded vs replayed)
- healing template v1: 169 slots (112 page + 47 header + 10 locale plumbing) - MATCH. en catalog 159 keys - MATCH.
- healing v2 final: 171 slots / 114 page / 161 keys = v1 + faq.bestLd + faq.dayLd (the recorded v2 delta) - CONSISTENT.
- a-miracle: 144 slots (87 page) / 134 catalog keys - MATCH. anxiety: 134 slots (77 page) / 124 keys - MATCH.
- attested novena quotes: 8 locales x petition-after byte-equal to live repo catalogs (stage f2d9cd0) - MATCH.
- EN input pages: git history proves no stage changes to the 3 pages between the production base and now
  (last touches: healing Oct 15, a-miracle Oct 13, anxiety Oct 8; the Oct 22 recovery edits are replayed on top).

## Fresh strengthened verification (2026-10-25, all 3 pages, EN fill vs live page)
missing-slots: none; title/footer/tag-histogram/link(text+href): all match; deep ld+json: matches except
locale-plumbing placeholder slots (differ by construction, as in the original recorded checks).
Known non-rendering divergences from live EN source, both recorded in the original packet notes and reproduced:
(a) a-miracle live CTA row uses single-quoted attributes; (b) healing live source has one stray space after a <p>.
All 7-locale renderchecks (/tmp/b1-rendercheck.py) pass in replay, exit 0, as originally recorded.

## Superseded intermediates rebuilt too (available on request; not the ask)
b1-c1-groundwork-v1.zip, b1-c1-healing-checkpoint2.zip, b1-c1-healing-full-v1.zip (hashes in intermediate-hashes.txt).

## Gaps (honest)
- Zip sha256s cannot match the originals (zip timestamps). Byte SIZE equality (89,106) supports content equality
  for the a-miracle zip; anxiety size comparison needs Main's inbound record.
- Replayed commit hashes differ from the recorded locals (2f390eb2, 2b4c1a8b, 299a6e81, 91f15cd2, bf9a644b,
  83ea140f, 9cacb0ce, 837e6dbc, c351e3e3, 85fc5eaa) - git timestamps; tree contents are the verified artifact.
