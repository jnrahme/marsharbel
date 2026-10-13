# Decisions and owner preferences

Source column: WhatsApp = Joey's own messages (author user), verified in the message store when recorded.
"Ruling" = scrum/train owner ruling, relayed through the main agent, not an owner line.

| Date (EDT) | Decision | Source |
|---|---|---|
| 2026-10-08 11:50 | Ship target: at least 100 PRs merged per day | WhatsApp |
| 2026-10-11 13:21 | Decide and move; carve-outs still go to Joey: money or paid tiers, agreements, significant deletion, risky irreversible infra, reputation risk, credential creation | WhatsApp (voice) |
| 2026-10-10 22:25 | A page ships only when EVERY active locale is ready, all languages in one release, no locale-orphan pages. Arabic backfill of existing English pages is the standing second priority | WhatsApp via main |
| 2026-10-13 | Rights: no permission requests to third parties, re-source instead. No more rosary video publishes with RosaryCenter art. Same-name image swaps on CDN-cached paths get a rename | Owner via main |
| 2026-10-13 15:09 | All full-international-translation work is committed and a huge PR is worked continually until merged | WhatsApp |
| 2026-10-13 15:29 | Autonomous Execution and Memory Protocol (persistent task registry, parallel agents, verified DONE) | WhatsApp |
| 2026-10-13 | Ruling: the translation PR is one long-lived branch intl/full-translation, commit by commit, merged at each green consistent state; gate-code edits stay small separate PRs; already gate-true PRs merge first | Scrum ruling |
| 2026-10-13 | Ruling: private preview pages may skip the keyed-mirror requirement only if noindex AND listed in locales/private-preview-pages.json, with isolation asserted every run | Scrum ruling (PR #785) |
| standing | Never hurt Google: moved or removed page needs a 301 and sitemap update in the same PR; hreflang reciprocal; real lastmod. One feature one PR (translation excepted above). Free tier only. Rendered review before done (AGENTS.md) | Owner via main / AGENTS.md |
