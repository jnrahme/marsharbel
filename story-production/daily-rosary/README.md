# Daily rosary factory

First milestone: October 13-19, 2026, English then Arabic, followed by other languages that pass the Catholic prayer and narration gates. This directory is a production registry, not an assertion that every day is rendered or scheduled.

## Reuse model

Store saint intros separately by date and language. Store four immutable mystery body masters per language, exposed through seven weekday mappings. Monday/Saturday share Joyful; Tuesday/Friday share Sorrowful; Wednesday/Sunday share Glorious; Thursday uses Luminous. Spoken announcements name the mysteries, not a stale weekday/date.

Calendars are year- and region-scoped. A saint-of-day lookup is not a liturgical rank. For example, October 18, 2026 is Sunday in Ordinary Time; Luke's fixed date does not turn that Sunday into his liturgical feast. October 19 is a memorial of the North American martyrs in the US, while Paul's date differs in the US calendar. Use devotional "we remember" without making a false feast claim.

## Directories

- `calendars/`: researched saint/date/rank/mystery/source mappings.
- `scripts/<locale>/`: exact reviewed prayer and intro scripts.
- `manifests/`: source, artwork, immutable body and episode registries.
- `tools/`: glue and validation. No automatic uploads or publishing.
- `tests/`: fixture-driven safety checks.

Binary masters, WAVs and large art files use immutable external storage, recorded with exact URLs, byte counts and SHA256. Do not overwrite released assets. Public repo records contain no secrets, private review credentials, unrelated exports or private conversation archives.

## Gates

Research -> text/art review -> main-generated Achird WAV -> pronunciation/words check -> rendered intro -> body hash check -> glue -> full decode/splice inspection -> independent Quality -> provider queue -> exact public-destination verification. Ready/rendered is not scheduled, a queue receipt is not live, and a bridge monthly allowance is not yearly capacity.

Keep V6's saint name, short sourced context, invocation and real picture. No Instagram hook/question/reveal mechanics. Never abbreviate prayers or bunch visualization prompts. Show each prompt while its full Hail Mary is prayed. Retain inherited Rosary Center art uncertainty: owner-directed reuse with credit, not a license claim.

## Present inventory

One approved English Sorrowful body and October 13 Edward intro. Remaining first-week texts are drafts, with artwork and narration gates pending. Arabic is not produced. Year-wide calendar not complete. This honest register must be updated from actual assets and receipts, never predicted completion.

## Glue proof
`tools/glue.py` was run on the approved Edward intro plus approved English Sorrowful body. It reproduced the exact approved V6 master SHA256, preserved all 4,349 video and 50,967 audio body packet payloads and decoded the whole 36:28 without timestamp reversal. Regression proof is in `manifests/glue-v6-regression-proof.json`. Negative tests cover existing-output protection and hash mismatch. Installed PyAV17.1.0 documentation checked: https://pyav.basswood.io/docs/17.1/api/container.html . Context7 did not offer a version-specific17.1 library ID; upstream versioned documentation was used instead.
