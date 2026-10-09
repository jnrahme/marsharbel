# Moderator MFA (aal2)

Moderation needs three things, all checked on the server:
1. a signed-in user,
2. `app_metadata.role = 'moderator'`,
3. an `aal2` session (password plus authenticator code).

`public.testimony_is_moderator()` checks all three. Every moderation RPC calls it through
`testimony_require_moderator()`, and the moderator RLS policies on `testimony_controls`,
`testimony_audit`, `testimony_reports` and `testimony_submissions` call it directly. The page JS
(`testimony-admin.js`, `moderatorMfaRequired` in `testimony-config.js`) only controls what the UI shows.

History: migration `202609220002_moderator_password_access.sql` (commit 1c651bb0, 2026-09-23)
removed the aal2 check and the config flag was set to false. Migration `202610030001_restore_moderator_aal2.sql`
restores it.

## Rollout order (matters)
1. Merge and deploy the site change (`moderatorMfaRequired: true`). Until the database migration is
   applied, the database still accepts password-only sessions, so nothing breaks.
2. With the moderator present: sign in at /testimony-review. A user with no verified factor sees an
   enrollment QR (scan it with an authenticator app), then enters the code. A user with a verified factor enters a code.
3. Apply `202610030001_restore_moderator_aal2.sql` to production (Supabase SQL editor or CLI).
4. Confirm the moderator can still load the queue and act on one item.

Do not apply the migration before the client change is live: the old client skips the code step,
and its RPC calls would fail with `moderator_mfa_required`.

## Rollback
Re-apply the function body from `202609220002_moderator_password_access.sql`, and set
`moderatorMfaRequired` to false. Use only as a short-term step while fixing access, and re-restore afterwards.

## Break-glass (lost authenticator)
Use the Supabase dashboard or the service role, never the public site:
- Dashboard: Authentication > Users > the moderator user > remove the TOTP factor.
- SQL (service role / SQL editor): `delete from auth.mfa_factors where user_id = '<moderator user id>' and factor_type = 'totp';`

The next sign-in then shows the enrollment QR again. Store recovery steps with the project owner, not in the repo.

## Check enrollment (read-only)
`select id, factor_type, status, friendly_name, created_at from auth.mfa_factors where user_id = (select id from auth.users where raw_app_meta_data->>'role' = 'moderator');`
`status = 'verified'` means an authenticator is enrolled.
