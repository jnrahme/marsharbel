# Testimony intake activation checklist
The QA UI is intentionally fail-closed. `submissionsEnabled` and the database kill switch default to `false`.
1. Create a Supabase project and run `supabase-testimonies.sql`.
2. Deploy `supabase/functions/submit-testimony/index.ts`.
3. Set secrets: `TURNSTILE_SECRET_KEY`, `TESTIMONY_IP_HMAC_SECRET` (32+ random bytes), `TESTIMONY_ALLOWED_ORIGINS`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.
4. Configure the exact production and QA origins. Never commit service-role or Turnstile secret keys.
5. Add only public Supabase URL/anon key and Turnstile site key to `testimony-config.js`.
6. Create a dedicated moderator account, require MFA, set `app_metadata.role=moderator`, and test RLS with an unprivileged account.
7. Enable the database kill switch, then set `submissionsEnabled:true` in a reviewed deployment.
Layers: fail-closed flags, origin allowlist, request-size/field limits, honeypot, minimum completion time, Turnstile action validation, HMAC-hashed IP rate limiting, RLS, moderator-only writes, output escaping, private-by-default status, and a database kill switch. These reduce risk but do not make a public system "unhackable." Add monitoring, alerts, log retention limits, backups, and periodic access reviews before production.
