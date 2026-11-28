# Decisions and owner preferences

Source column: WhatsApp = Joey's own messages (author user), verified in the message store when recorded.
"Ruling" = scrum/train owner ruling, relayed through the main agent, not an owner line.

| Date (EDT) | Decision | Source |
|---|---|---|
| 2026-10-08 11:50 | Ship target: at least 100 PRs merged per day. REPLACED 2026-10-13 15:50 (next row) | WhatsApp |
| 2026-10-13 15:50 | The 100 PRs/day target is replaced by verified, high-impact delivery metrics. Scoreboard = verified completions (deployed and live-checked), not PR volume. PR and merge counts stay in reports as context only. Message wamid.HBgLMTQwNDQzNzUzNzMVAgASGBQzQjJCQ0Q1MEM1Q0Y3OTgwMjNDOQA= (Paperclip optimization directive, Phase 8) | WhatsApp |
| 2026-10-11 13:21 | Decide and move; carve-outs still go to Joey: money or paid tiers, agreements, significant deletion, risky irreversible infra, reputation risk, credential creation | WhatsApp (voice) |
| 2026-10-10 22:25 | A page ships only when EVERY active locale is ready, all languages in one release, no locale-orphan pages. Arabic backfill of existing English pages is the standing second priority | WhatsApp via main |
| 2026-10-13 | Rights: no permission requests to third parties, re-source instead. No more rosary video publishes with RosaryCenter art. Same-name image swaps on CDN-cached paths get a rename | Owner via main |
| 2026-10-13 15:09 | All full-international-translation work is committed and a huge PR is worked continually until merged | WhatsApp |
| 2026-10-13 15:29 | Autonomous Execution and Memory Protocol (persistent task registry, parallel agents, verified DONE) | WhatsApp |
| 2026-10-13 | Ruling: the translation PR is one long-lived branch intl/full-translation, commit by commit, merged at each green consistent state; gate-code edits stay small separate PRs; already gate-true PRs merge first | Scrum ruling |
| 2026-10-13 | Ruling: private preview pages may skip the keyed-mirror requirement only if noindex AND listed in locales/private-preview-pages.json, with isolation asserted every run | Scrum ruling (PR #785) |
| standing | Never hurt Google: moved or removed page needs a 301 and sitemap update in the same PR; hreflang reciprocal; real lastmod. One feature one PR (translation excepted above). Free tier only. Rendered review before done (AGENTS.md) | Owner via main / AGENTS.md |


## Backlog-health rules (scrum, from the 2026-10-13 15:50 Paperclip directive, Phases 3, 5, 7)

Context: the Paperclip board is display-only (no execution adapters, heartbeats off), so the real execution layer is the lanes. These rules are enforced by scrum over the real lanes, not inside Paperclip. Board desk keeps the mirror truthful.

Enforceable today (scrum owns, checked hourly and in the daily sweep):
1. One accountable owner per active task, with acceptance criteria and a next action. A task with no owner is flagged to main the same hour.
2. WIP limit: one primary execution task per specialist lane. Leads may coordinate several but name the critical-path task. Scrum flags any lane carrying more than one primary task and says which to queue. Existing work is queued, not dropped.
3. Self-unblocking order for any BLOCKED task before it goes to Joey: inspect the blocker, search authorized sources (message store, repo, memory), check the dependency is still valid, try a safe alternative, delegate troubleshooting, retry after a real change, record the resolution. Only founder-level decisions or unavailable external dependencies escalate. Evidence this works: 15 of 21 audit blockers were closed from the message store alone (tasks/BLOCKED_RECLASSIFICATION.md).
4. Delivery pipeline statuses map onto the registry: REQUESTED=BACKLOG, READY, CLAIMED=IN PROGRESS, REVIEW=IN REVIEW, VERIFIED, DELIVERED=DONE (merged and live-checked). Code: implement, test, PR, review, authorized merge, deploy, verify. Content: research, source check, editorial review, publish, live check. Media: produce, editorial review, asset QA, authorized publish, public playback check.
5. No self-certification: DONE needs evidence a second party can open (merge SHA, CI 22/22 on the exact head, live URL check, or a rendered review). An agent statement alone moves a task to IN REVIEW at most. Lesson from board card MAR-101 (description stale, native history supported done): a done card is verified from its native history and delivery evidence, never from the list description.
6. Stalled-work check: any PR or task with no state change in 4 hours while executable work remains gets a kick request to main with the hours lost.
7. Handoffs are recorded in the registry with the dependent task id, responsible lane and the deliverable. Departments own delivery and do not forward messages.

Needs a mechanism (not enforceable today, noted so it is not claimed):
- Native Paperclip locks, checkout and dependencies: the board has no execution adapters. Mirror only.
- Heartbeat and event-trigger audit, cost per verified deliverable, per-agent cycle time and rework rate: needs run and cost data per lane. Scrum can compute cycle time for PRs from GitHub; cost data is not available to scrum.
- Budget changes: any significant increase goes to Joey for approval.
