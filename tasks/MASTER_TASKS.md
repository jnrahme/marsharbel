# MASTER TASKS

Reconciled against GitHub and stage d5b67353 on 2026-10-13 3:30 PM EDT. See README.md for statuses.

Task: one block per task.

## T-001 [READY] Joey 2026-10-13 15:09: all international translation work in one huge PR, worked until merged

- Description: Branch intl/full-translation with one draft PR to stage; commits per logical change; stage merged in regularly
- Priority: P0
- Assigned: content (push door) + AR/intl lane
- Dependencies: T-002..T-009
- Acceptance: PR exists and is open; each commit passes build twice + i18n:check; verdict table in PR body kept current; each green consistent state merged; CI 22/22 on the exact head
- Branch/PR: branch intl/full-translation (not yet pushed)
- Evidence/notes: -

## T-002 [IN REVIEW] Joey 2026-10-10 22:25 rule (j) + Oct 13 translation scope: fr nav marking + twin reroute

- Description: Land fr header nav marking and reroute; repin frozen authored hashes by script
- Priority: P0
- Assigned: content, review scrum
- Dependencies: T-010
- Acceptance: 12 stage-twin hrefs routed; marking strip inverse tested; repin_authored_final_hashes.py --write run on the final head; CI 22/22; live check
- Branch/PR: PR #783 head 67eee959 (draft)
- Evidence/notes: Gate approved with conditions; CI red on test_travel_authored_final_hashes until repin applied

## T-003 [IN REVIEW] Translation scope: de pinned travel twin marking (12 pages)

- Description: Pinned de travel twins get header marking; gates strip exact marking before comparing to candidates
- Priority: P0
- Assigned: content, scrum gate patches
- Dependencies: T-010
- Acceptance: pinned_marking_gate.patch + fix2 applied; rebuild twice; 12 de pages + manifest + lastmod committed; rendered review; CI 22/22
- Branch/PR: PR #782 head 8723ea64 (draft)
- Evidence/notes: Waiting on content rebuild (pass 1 started 3:24 PM)

## T-004 [READY] Translation scope: es nav marking + reroute (24 pages)

- Description: One locale per PR after fr
- Priority: P1
- Assigned: AR/intl lane
- Dependencies: T-002
- Acceptance: rebased on fr merge, re-diffed, repin run, rendered check, CI 22/22
- Branch/PR: patch 7b48d889 reviewed, no PR yet
- Evidence/notes: Waits for fr merge

## T-005 [BACKLOG] Translation scope: it, pl, pt nav marking

- Description: One PR per locale in order it, pl, pt
- Priority: P1
- Assigned: AR/intl lane
- Dependencies: T-004
- Acceptance: same as T-004
- Branch/PR: -
- Evidence/notes: -

## T-006 [BACKLOG] Translation scope: hi, th nav marking (limited launch)

- Description: Ship as mark-as-English; PR body states rendered review pending
- Priority: P2
- Assigned: AR/intl lane
- Dependencies: T-005
- Acceptance: same as T-004 plus honest not-reviewed wording
- Branch/PR: -
- Evidence/notes: -

## T-007 [BACKLOG] Translation scope: de finish_nav (13 pages) and ru pinned travel twins

- Description: FINISH_MARK_LOCALES after the ar leftover PR; ru roundtrip check once source commit exists
- Priority: P1
- Assigned: content, scrum review
- Dependencies: T-003
- Acceptance: strip roundtrip proven; CI 22/22
- Branch/PR: -
- Evidence/notes: -

## T-008 [BACKLOG] Translation scope: ar leftover 23 pages

- Description: Arabic pages left after the parity rebuild; manifest line non-author reviewed; 390px RTL dropdown render
- Priority: P1
- Assigned: content + AR lane, scrum review
- Dependencies: T-003
- Acceptance: contentSha256 manifest line reviewed; RTL render at 390px; CI 22/22
- Branch/PR: -
- Evidence/notes: Queued after de/ru

## T-009 [BACKLOG] Translation scope: /news in 9 locales, Arabic backfill of EN pages, locale-link worklists

- Description: Plan from scrum after es and fr PRs open
- Priority: P1
- Assigned: AR/intl lane, scrum plan
- Dependencies: T-004
- Acceptance: plan accepted; all active locales ready per page (rule j)
- Branch/PR: -
- Evidence/notes: Worklists: locale-links-worklist (87 rows), deep ar/de/ru (2172 rows)

## T-010 [IN REVIEW] Joey 2026-10-13 15:29 protocol: this registry

- Description: tasks/ files plus I18N_STATUS.md; reconcile weekly vs GitHub and board
- Priority: P0
- Assigned: scrum
- Dependencies: -
- Acceptance: files merged to stage via docs PR; reconciliation timestamp in PROGRESS.md
- Branch/PR: branch docs-registry (unpushed)
- Evidence/notes: Needs content lane to push

## T-011 [IN PROGRESS] Rights audit (Joey standing rule: real photos, rights recorded)

- Description: Registry for 328 unregistered files (about 320 need per-image source records); AI storybook sets marked as AI-generated, no third-party source
- Priority: P1
- Assigned: scrum, content
- Dependencies: -
- Acceptance: each file registered or removed; 410 live (done); registry diff docs-only PR
- Branch/PR: P1 #780 merged; registry diff owed
- Evidence/notes: Hash-match: 8 of 328 derivatives

## T-012 [READY] Portrait follow-up (credit line, rename, polish, .enc-language gap)

- Description: Visible Commons credit line, rename saint-charbel-portrait-photo.webp, design-director polish, CSS gap fix
- Priority: P1
- Assigned: content, design director
- Dependencies: T-011
- Acceptance: one keyed PR; rendered review; live check; CDN rename rule
- Branch/PR: #781 merged
- Evidence/notes: -

## T-013 [IN REVIEW] Saint of the Day homepage unit (news desk)

- Description: Daily unit, hidden by default, shows on its New York date; catalog admission via saint-of-day-copy tuple
- Priority: P1
- Assigned: news desk, content applies, scrum review
- Dependencies: -
- Acceptance: non-author catalog and mutation review; rollover mechanics; CI 22/22; deployed current-date test
- Branch/PR: patch df42a873 (3 commits on f7eb455e), not yet a PR
- Evidence/notes: No-JS absence accepted, to be stated in PR body

## T-014 [VERIFIED] Joyful Mysteries private preview reader

- Description: Noindex allowlisted preview for Joey review; narration audio swap to follow
- Priority: P1
- Assigned: content, studio
- Dependencies: -
- Acceptance: CI 22/22 on 5850b80b; stage isolation check; live check 20 min after merge
- Branch/PR: PR #785 head 5850b80b (draft)
- Evidence/notes: Scrum approved gate code and registry block

## T-015 [BLOCKED] Games hub (EN-only game, all-locale hub PR)

- Description: Hub with first-card English qualifier, plain-text 'In development' cards; nav item after
- Priority: P2
- Assigned: game dept, scrum review
- Dependencies: fun verdict
- Acceptance: Joey fun verdict; sitemap and release-text fixtures first
- Branch/PR: -
- Evidence/notes: Blocked on Joey's fun verdict on the game

## T-016 [BACKLOG] CSP externalization (mystery-meditation first)

- Description: Move inline scripts for CSP enforcement
- Priority: P2
- Assigned: security lane
- Dependencies: -
- Acceptance: one PR per page family; CSP report-only clean
- Branch/PR: PR #579 held
- Evidence/notes: Merge only when parent says

## T-017 [BLOCKED] Moderator MFA restore

- Description: aal2 server and client
- Priority: P1
- Assigned: security lane
- Dependencies: Joey
- Acceptance: Joey go; MFA enrolment
- Branch/PR: PR #578 (do not merge)
- Evidence/notes: Needs Joey's go

## T-018 [READY] Daily Saint of the Day social card via Buffer

- Description: Dispatch through content lane (only gh-authenticated box)
- Priority: P2
- Assigned: opportunity desk, content dispatches
- Dependencies: T-013
- Acceptance: preflight (dedupe, asset bind, 8 AM EDT floor); rights note for card art
- Branch/PR: -
- Evidence/notes: Scrum cannot dispatch (no gh auth)

## T-019 [IN PROGRESS] Rosary language videos

- Description: EN video unlisted and re-cut with cleared art; no RosaryCenter art
- Priority: P1
- Assigned: studio, main holds publish go
- Dependencies: -
- Acceptance: cleared-art source record; main go
- Branch/PR: -
- Evidence/notes: rosary-videos.json empty, nothing breaks

## T-020 [BACKLOG] C-0070 QA hollow-step audit

- Description: Audit QA steps that pass without testing
- Priority: P2
- Assigned: scrum
- Dependencies: -
- Acceptance: list of hollow steps with fixes
- Branch/PR: todo-01M4HE8P73K1B2NZ2GV97QM3XK
- Evidence/notes: -

## T-021 [BACKLOG] Noindex same-page control coverage decision

- Description: Decide coverage for noindex pages
- Priority: P3
- Assigned: scrum
- Dependencies: -
- Acceptance: ruling recorded in DECISIONS.md
- Branch/PR: todo-01M4R14M4SBH49AFECW3MEW5H9
- Evidence/notes: -

## T-022 [BACKLOG] Hold queue: #765 motion spec, #757 nav gap, #559 promote, #504 preview, #502 lane process pack

- Description: Review or close each
- Priority: P3
- Assigned: scrum train
- Dependencies: -
- Acceptance: each merged, closed or re-owned
- Branch/PR: #765 #757 #559 #504 #502
- Evidence/notes: -
