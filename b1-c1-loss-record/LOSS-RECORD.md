# B1 C1 packet loss record (closed reference) - 2026-10-25

Status: LOSS RECORD + recovery attempt log. Not content. No integration, route registration, certification, or release authorization is created or implied by this file. Preservation route matches PR #887/#888 (gate closed, never merge).

## What was lost (byte streams), and when
Sandbox resets destroyed the only agent-held copies of the full C1 packets on/after 2026-10-23. Producer branch b1-recovery was local-only (never pushed; no origin ref; GitHub API 404 on its commits).

### Original packet locators + hashes (verified at receipt 2026-10-23)
- b1-c1-amiracle-full-healingv2-v1.zip
  - sha256: 20f93d71657a733e0383501312861b6ca8e8dc1a541d62c70ab5c07e62a3b58f (verified by content lane 2026-10-23 05:06:43 EDT against received bytes)
  - size: 89,106 bytes; 36 files
  - agentmsg: agentmsg-01M5M02EGSXT94M0BVX66JTCDD; blob b953582a67c64c562f8accf936898b70a8579d513863fb355757055268c7e896
  - original Main path: /downloads/b1-c1-amiracle-full-healingv2-v1-b953582a.zip
  - contents: a-miracle full en+7 + healing v2 (supersedes healing v1; adds FAQPage ld+json slots faq.bestLd/faq.dayLd, breadcrumb=hero.heading, inLanguage dropped)
- b1-c1-anxiety-full-v1.zip
  - sha256: f9eb5ff25f82229a5f1537bcd0bc5cfdfcf8f2fb48ace690d462de50fcdd3710 (evidence index 2026-10-23 05:14 EDT)
  - original Main path: /downloads/b1-c1-anxiety-full-v1-e158bd77.zip
  - contents: anxiety full en+7 + AR-clause adjudication note (b1-c1-ar-clause-adjudication.md, commit 85fc5eaa)
- SUPERSEDED, not rebuilt for history: b1-c1-healing-full-v1.zip sha256 b96c27736d1b60f61b087a2a655ea3db060efb3aaf89d2889b29278ac0b695bc (superseded by healing v2 above; loss is documentation-only)

## Already preserved on origin (this branch)
- groundwork packet sha256 8f62b372 (commit a57661e)
- healing checkpoint2 sha256 dab2905f (commit e976518)

## Lost producer commit list (branch b1-recovery, base b77f2f16)
4350ba89 B1 source reconstruction | 2f390eb2 healing template+en | 2b4c1a8b..f342b815 healing 7 locales | 83ea140f healing v2 template+en | 9cacb0ce healing v2 locales | 299a6e81 a-miracle template+en | 91f15cd2 a-miracle fidelity fixes | bf9a644b a-miracle 7 locales | 85fc5eaa AR-clause adjudication record | 837e6dbc anxiety template+en | c351e3e3 anxiety 7 locales

## Recovery attempts (2026-10-25 ~06:45 EDT, all exact, none guessed)
- agent_message: no fetch-attachment/blob action exists (send only).
- observations.attachments: zero rows for blob b953582a... / %b1-c1% (email-only table).
- observations fetch: requires /observations/ path; none exists for these blobs.
- git fetch by SHA from origin (85fc5eaa, 837e6dbc, 83ea140f, 299a6e81): "couldn't find remote ref".
- GitHub API GET git/commits/85fc5eaa...: 404. Branch b1-recovery: no origin ref.
- Locale lane (also routed copies 2026-10-23 05:04:48): confirmed no copies.
- Content lane /downloads + /tmp/b1-wt/packets: wiped by sandbox reset. Main local paths: absent.

## Ruling (Main, 2026-10-25 06:46 EDT)
Producer (locale lane) reconstructs: adjudication first from actual transcript/attested values, then C1 packets from recorded recipes + groundwork. Fresh hashes, explicit NEW RECONSTRUCTION label, NO byte-identity claim. Content lane (this branch's owner) verifies fresh packets against the recorded recipes/hashes above before preserving here. No integration gate waiver. Superseded v1 not rebuilt.

## Verification gate for incoming reconstructed packets
1. Explicit NEW RECONSTRUCTION label present.
2. Contents reproduce the recorded structure (36-file amiracle+healingV2 set; anxiety set + adjudication note) per the 2026-10-23 05:14 evidence index.
3. No claim of byte identity to the lost originals; fresh sha256 recorded alongside original hashes above.
4. Closed-reference preservation only; gate stays closed; never merge.

## Reconstruction intake log
- 2026-10-25 06:48 EDT: b1-c1-ar-clause-adjudication-RECONSTRUCTION-20261025.md received via Main (producer locale lane). Fresh sha256 8abbecc6aa73e9fb793ddf7880adc40afd94df01794a16718a6982846314115d verified against received bytes by content lane. NEW RECONSTRUCTION label present; no byte-identity claim. EN/AR petition-after values independently cross-checked byte-equal against stage f2d9cd0d catalogs (locales/en + locales/ar saint-charbel-novena-master-copy.json). Adjudication remains OPEN; Main review pending; no clause ruling or R3 gate change. Superseding zips (amiracle+healingV2, anxiety) still rebuilding at producer.
