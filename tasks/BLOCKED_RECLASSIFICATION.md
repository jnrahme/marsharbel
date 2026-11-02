# Blocked-task reclassification (2026-10-13, 3:50 PM EDT)

Source: the weekly audit (98 units, 21 marked Blocked). Rule: documentation does not replace execution, so every row has a recovery owner and the next executable step. Transcripts of voice notes are not stored in this public repo; they stay in the private message store and are referenced by message time.

Result: 17 self-recoverable, 2 externally dependent, 2 approval-required. 15 of the 21 were blocked only on missing context, and that context was recovered today from the message store (voice-note transcripts held in the main chat, reply-to ids, adjacent turns).

| Audit # | Request (short) | Class | Recovery owner | Next executable step |
|---|---|---|---|---|
| 11 | More movement and aliveness (PR #765) | approval-required | Design director | Finish reduced-motion, mobile and performance QA and rendered preview now; then one clear ask to Joey: approve the motion look (visual approval is the only missing gate) |
| 16 | Google/Facebook sign-in, subscriptions | split: approval-required (shared Supabase migration sign-off), self-recoverable (build) | Gaming/accounts lead + security | Build the Facebook provider behind a flag using the Meta app Joey said already exists (check vault first, no new credential asks); write the migration as a draft PR with rollback; ask Joey only for the migration go (risky infra carve-out) |
| 45 | Dedicate today's rosary "for him" | self-recoverable (resolved) | Main + rosary lane | Referent recovered: Pope Leo XIV, Gemelli surgery news of 8:07 AM; main answered at 8:16-8:19 AM. Verify the dedication is in the published video title or description, then mark DONE |
| 58 | Authentic Catholic prayers, full Mawrid intake | externally dependent (same-edition full copy) | Mawrid lane | Run the acquisition ladder in order, time-boxed 48h: library catalogs (WorldCat, HathiTrust), Gallica/BnF, Internet Archive, Google Books, publisher and Maronite sources; log each result. Do not ask Joey to photograph 620 pages. Only if all fail, ask Joey for one photo of the title and copyright page |
| 60 | "What prayer is this one?" (photo) | self-recoverable | Mawrid lane | Image bytes are not in the message store, but the lane received them. Recover from the lane's files or chat, verify against the printed text, and confirm the answer given at 6:03 PM Oct 12 |
| 62 | Digital copy without 620 photographs | externally dependent | Mawrid lane | Same ladder as #58 (merge the two); track as one item |
| 64 | Today's Prayers timezone-aware card | self-recoverable | SEO content + prayer lane + design | The basis question is answered: the Maronite calendar, as used by the Saint of the Day unit (PR #788). Spec the card from the Oct 12 6:13 PM voice note; build after #788 merges, reusing its date-gate mechanism |
| 72 | "What happened to this?" | self-recoverable (resolved) | Main | Reply target recovered: Joey's 3:09 PM line on the single big translation PR. Main answered at 3:25 PM. Mark DONE when intl/full-translation PR is open |
| 84 | Voice 12:45 PM Oct 12 | self-recoverable (resolved) | Main | Transcript recovered: stop sending bugs; build a self-driving flag-and-fix lane. Done: bug pipeline skill and hunter lane exist. Verify the loop runs |
| 85 | Voice 6:06 PM Oct 12 | self-recoverable (resolved) | Mawrid lane | Recovered: make sure all the prayers are added and searchable site-wide. Fold into #58 acceptance |
| 86 | Voice 8:26 PM Oct 12 | self-recoverable (resolved) | Rosary lane | Recovered: a daily rosary rotation, one post per supported language, English approved first then the rest. Tracked under rosary language videos (T-019) |
| 87 | Voice 8:35 AM Oct 13 | self-recoverable (resolved) | Rosary lane | Recovered: pronunciation of the Lebanese Hail Mary; Joey confirmed it was right at 8:43 AM. Close |
| 88 | Voice 8:54 AM Oct 13 | self-recoverable (resolved) | Rosary lane | Recovered: all languages, correct Catholic version per country, post on YouTube. ES and FR Sorrowful assembled at 3:04 PM; others queued. Next: publish go from main per rights hold |
| 89 | Voice 9:03 AM Oct 13 | self-recoverable (resolved) | Main | Recovered: complaint that the daily all-language work was not ready. Action: the daily production cadence below |
| 90 | Voice 9:04 AM Oct 13 | self-recoverable (resolved) | Main | Recovered: the standing north star is every day, every supported language, the Maronite version. Add to DECISIONS.md (done) |
| 91 | Voice 9:06 AM Oct 13 | self-recoverable (resolved) | Rosary lane + news desk | Recovered: build seven days per language and the saint of the day per language, then glue and post. Track as T-019 sub-tasks |
| 92 | Voice 9:11 AM Oct 13 | self-recoverable (resolved) | Rosary lane | Recovered: "keep trying until done". No separate work |
| 93 | Voice 9:52 AM Oct 13 | self-recoverable (resolved) | Main + scrum | Recovered: asks for status on SEO and translations. Answered by the intl PR and I18N_STATUS.md |
| 94 | Voice 12:38 PM Oct 13 | self-recoverable (resolved) | Rosary lane | Recovered: finish the Arabic video and post on YouTube. Studio said the AR body encode starts after ES; main holds the publish go |
| 95 | Image 3:45 PM Oct 12 | self-recoverable (resolved) | Main | Context recovered: Google sign-in verification screenshot. No task. Close |
| 96 | Image 11:31 PM Oct 12 | self-recoverable (resolved) | Main | Context recovered: screenshot of a Gmail verification code email. The code is consumed. No task. Close |

Process fix: every inbound voice note or image gets its transcript or description written into the audit record at receipt, so "transcript pending" never becomes a blocker again.
