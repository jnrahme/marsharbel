# Testimony intake activation checklist
The QA UI is intentionally fail-closed. `submissionsEnabled` and the database kill switch default to `false`. Launch policy: account required to submit, adults 18+ only, rejected stories/photos purged after 30 days, Joey is the sole initial moderator with mandatory MFA, anonymous reading stays open.

1. Create a Supabase project and run `supabase-testimonies.sql`.
2. Enable the pg_cron extension and run the two commented lines at the end of `supabase-testimonies.sql` to schedule the nightly rejected-purge job.
3. Deploy `supabase/functions/submit-testimony/index.ts`.
4. Set secrets: `TURNSTILE_SECRET_KEY`, `TESTIMONY_IP_HMAC_SECRET` (32+ random bytes), `TESTIMONY_ALLOWED_ORIGINS`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
5. Configure the exact production and QA origins. Never commit service-role or Turnstile secret keys.
6. Add only the public Supabase URL/anon key and Turnstile site key to `testimony-config.js`.
7. Create Joey's moderator account in Supabase Auth, enroll MFA (TOTP), and set `app_metadata.role='moderator'`. The database refuses moderator actions until the session reaches `aal2`, so test sign-in with and without the MFA step-up, and test RLS with an unprivileged account. The moderation page is never linked in public navigation, and its client script reveals the panel only after verifying role='moderator' and aal2 in the session token; every other visitor, signed in or not, sees only the generic sign-in form.
8. Keep Joey as the only moderator. Adding another moderator later is a new owner decision and should be recorded in writing first.
9. Confirm the intake rejects: signed-out requests, `age_confirmed:false`, bad origins, oversize bodies, and replayed Turnstile tokens.
10. Enable the database kill switch, then set `submissionsEnabled:true` in a reviewed deployment.
Layers: fail-closed flags, account-required auth, origin allowlist, request-size/field limits, honeypot, minimum completion time, Turnstile action validation, HMAC-hashed IP rate limiting, RLS with author-scoped reads, aal2-enforced moderator-only writes, output escaping, private-by-default status, 30-day rejected purge, and a database kill switch. These reduce risk but do not make a public system "unhackable." Add monitoring, alerts, log retention limits, backups, and periodic access reviews before production.
