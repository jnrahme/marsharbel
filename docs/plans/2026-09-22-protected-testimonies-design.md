# Protected testimony publishing

Approved flow: verified account → text-only submission preview and consent → private queue → advisory AI screening → moderator MFA approval → public, revocable publication.

Use Supabase Auth, PostgreSQL/RLS and Edge Functions, independently of the Hostinger static frontend. The browser holds only a public project key. Intake verifies the session, email and Turnstile server-side. No direct browser inserts or updates. Database transactions enforce account/global budgets, pending limits, revision checks and publication caps. Published snapshots contain only approved public fields. Edits immediately unpublish and restart review. Authors can withdraw. Reports and clarification messages stay private.

AI gets text after basic redaction, no tools or publishing permissions. A dedicated worker account can only claim bounded jobs and record structured review notes. Never equate plausibility with truth. Processing failures stay private. Daily reserved job budgets and fixed token/output bounds limit cost; a separate provider project budget remains required.

Defaults: two submissions per account/day, three pending per account, 200 submission attempts/day globally, five publications/day, 50 AI jobs/day. Moderator overrides require explicit reason and are audited. All switches default off. Moderator identity is assigned only in trusted app metadata; MFA is enforced in RPCs and RLS. Text-only launch; no uploads.

Deployment requires Supabase, Turnstile, an AI provider key/model, verified-email delivery, scheduled worker/purge calls, edge abuse controls and backup/restore validation. Keep the public site safe when any configuration is missing. Test SQL authorization and budgets, edge validation and frontend flows with isolated fixtures before enabling services.
