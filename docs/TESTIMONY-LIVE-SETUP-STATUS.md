# Live setup status — 2026-09-22

Project: Saint Charbel Testimonies (`alxccoizzksyitxvqhpv`), jnrahme's Org, free plan, us-east-1.
Public project URL: https://alxccoizzksyitxvqhpv.supabase.co

Completed and verified:
- Applied 202609220001_protected_testimonies.sql to the initially empty database using the authenticated dashboard.
- SQL verification: all six testimony tables have RLS; intake, publication and screening switches are false; anon cannot read submissions or execute intake; anon can read publications.
- Live HTTPS read-only test passed: public publication reads succeed and all five private tables return permission denied to anonymous clients. No stories were created.
- Site URL: https://marsharbel.com/account.html. Exact redirect allowlist: /account and /account.html on https://marsharbel.com.
- Confirm email enabled; anonymous sign-in and new signups disabled, verified after reload and via Auth settings API.
- Frontend public project URL and publishable key connected; feature flags remain off.
- Fixed worker CAPTCHA compatibility locally: trusted server Auth bootstrap obtains a worker session; role/email checked; all database calls use a separate public-key client with the restricted JWT. Privileged server code remains trusted. Security tests cover denial if bootstrap returns a moderator and forbid privileged-client database calls. Live worker integration remains untested.

Pending user steps:
- Supabase account form prepared for jnrahme@gmail.com. User must enter a fresh password and click Create user; the browser tool requires a credential-creation handoff. No moderator role assigned yet.
- Cloudflare GitHub login asks for read-only email access; browser authorization confirmation requested, not yet granted.

Remaining setup:
- Owner role/MFA, Turnstile widget and Auth CAPTCHA, production SMTP, restricted worker credentials, AI key/model, Edge Function deployments, scheduling and retention, backups/restore and live end-to-end checks.
- No public submissions or publishing enabled; do not represent the admin login or full flow as ready.

Run live read-only checks with: node scripts/tests/testimony_live_readonly.mjs
