# Corrections-to-rules loop

Every correction from Joey becomes a rule, so it is never re-learned. A correction is any message that says something was wrong, ugly, broken, unwanted, or "do it this way from now on".

## Capture (same day, by the lane that got corrected)
1. Quote Joey's words and the date. Do not paraphrase away the meaning.
2. Add one entry to `docs/engineering/corrections-log.md` (newest first):
   ```
   ## 2026-10-02 - short title
   - Lane: <lane>
   - Joey said: "<exact quote>"
   - What went wrong: <one line, honest>
   - Rule: <imperative sentence, checkable>
   - Promoted to AGENTS.md: no / yes (section)
   ```
3. If the rule is general (applies beyond this one task), also add it to the right section of `AGENTS.md` in the same PR and mark "Promoted: yes". Task-only fixes stay in the log.
4. Ship it in a docs-only PR, or inside the fix PR if one exists. Do not wait for a batch.

## Review (weekly, plus after any incident)
The integrator lane reads the log's new entries and:
- merges duplicates into one rule,
- removes rules that are obsolete or contradicted by a newer Joey instruction (keep the log entry, mark "superseded by"),
- checks every promoted rule is stated once in AGENTS.md, short and testable,
- reports to Joey the count of new rules and any repeat offenses (same mistake logged twice = escalate, fix the process).

## Skills handoff
The skill librarian lane owns `/skills`. When a promoted rule is really a reusable workflow or quality standard, the integrator posts the log entry link to the librarian, who decides whether a skill is created or updated. The repo log stays the source of truth for rules; skills reference it, not copy it.
