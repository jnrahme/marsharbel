# Protected testimony launch

The feature is implemented but remains off until services are configured. Static pages are served by Hostinger. Supabase Auth, PostgreSQL and Edge Functions handle private data and intake; no Netlify function route is used. Text only: uploads are not accepted.

## 1. Provision an isolated backend

Create a Supabase project in an appropriate region. Configure production site URL and an exact redirect allowlist for `https://marsharbel.com/account` and `/account.html`. Enable verified email, production SMTP, email rate limits, and Turnstile protection in Supabase Auth. Keep development redirect URLs out of production. Test delivery and sign-in before enabling accounts.

Apply `supabase/migrations/202609220001_protected_testimonies.sql`. It creates private submissions, a safe public publication table, reports, daily budgets and audit history. It revokes old browser access without deleting legacy records. Do not run the old root SQL file. Review any existing custom grants and policies separately: local tests cannot inspect an already-configured production database.

Create the owner Auth account and set its **app_metadata** role to `moderator` through the trusted dashboard/Admin API. Never use editable user metadata. Do not assign this role to ordinary users. The moderator page supports password login and TOTP enrollment/verification. Protect the Supabase and hosting accounts themselves with MFA as well.

Create a separate confirmed Auth user with app_metadata role `testimony_worker`. Its login credentials are server-side secrets. It must never have the moderator role. It cannot read other users' submissions through tables or call the publishing function; it can only claim one review and record notes for that claim.

## 2. Server-only configuration

Set these in Supabase Function secrets, not in source control or chat:

- `TESTIMONY_ALLOWED_ORIGINS=https://marsharbel.com` (comma-separated, exact origins)
- `TURNSTILE_SECRET_KEY` for a widget restricted to the production hostname
- `TESTIMONY_WORKER_EMAIL`, `TESTIMONY_WORKER_PASSWORD`
- `TESTIMONY_SCHEDULER_SECRET`: at least 32 random characters
- `OPENAI_API_KEY`: a dedicated project key with usage alerts and the smallest needed access
- `TESTIMONY_REVIEW_MODEL`: an explicitly selected model supporting Responses API structured outputs; validate it with representative English, Arabic and French samples

Supabase provides `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`. Intake alone uses the service role; the screening worker deliberately uses the public key plus its restricted user account.

Optionally set `TESTIMONY_TRUSTED_IP_HEADER` and a random `TESTIMONY_IP_HMAC_SECRET` (32+ characters) **only** behind a gateway that overwrites that header and rejects requests bypassing the gateway. Arbitrary forwarding headers are spoofable. Without this configuration, database account and global limits still apply; the application does not claim IP enforcement.

Deploy:

```sh
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
supabase functions deploy submit-testimony
supabase functions deploy screen-testimonies
```

The function configuration disables the platform JWT gate to support preflight/scheduler calls. Intake explicitly verifies the user JWT with Auth; the worker requires the scheduler secret, then signs in as the restricted worker. Origin checking is an additional browser control, not authentication.

## 3. Scheduling and recovery

Schedule an authenticated POST to `/functions/v1/screen-testimonies` once a minute using Supabase Cron plus Vault/pg_net or an equivalent trusted scheduler. The Authorization value is `Bearer <TESTIMONY_SCHEDULER_SECRET>`. Store the secret in Vault or scheduler secrets, never in a public SQL file or URL. Each invocation handles at most one job, reserves a daily slot before contacting AI, uses a fixed output cap and a 40-second provider timeout. Defaults allow at most 50 reserved AI jobs per UTC day, including failures. Requests have no tools and cannot execute publication actions. Budget exhaustion leaves stories queued. Expired processing claims become failed after five minutes on the next worker run. A moderator can retry failed reviews.

Enable pg_cron and schedule deletion nightly:

```sql
select cron.schedule('testimony-retention', '15 3 * * *',
  $$select public.testimony_purge();$$);
```

This deletes rejected/withdrawn stories after 30 days, old counters after seven days and resolved reports after 30 days. Audit history retains action metadata; do not place contact details in decision reasons. Configure a deliberate audit-retention policy if needed. Backups may retain older data for their configured retention period; disclose that accurately and restrict backup access.

Enable project database backups and verify a restoration into a separate project before launch. Record the backup schedule and retention supported by your plan; they are not provisioned by this repository. Recovery must not restore obsolete permissive policies. Keep an owner-access recovery procedure for MFA and the emergency database switches.

## 4. Edge protection and launch limits

Before public launch configure WAF/rate rules on **both** the static-site origin and Supabase/Auth endpoints (or their trusted gateway). A WAF protecting only marsharbel.com does not cover requests directly to the Supabase domain. Use provider protections and/or a gateway appropriate to the backend; do not trust a browser-only throttle.

Starting application limits, enforced transactionally:

- Two submission attempts reaching the database per verified account per UTC day.
- Three pending/needs-clarification stories per account.
- 200 database intake attempts globally per UTC day.
- Ten per IP/day when trusted IP configuration is enabled.
- Five author edits/day; edits immediately remove the publication and reset screening.
- Five publications/day; only a moderator with MFA can override, with a recorded reason.
- Fifty AI job reservations/day. Fixed 7,000-character story and 1,800-output-token bounds. This is a request/token cap, not an exact dollar cap; model pricing and provider costs remain external.
- Three reports per account/day and 200 globally/day.

The existing public pages remain readable if the testimony backend fails. Failed screening never publishes. AI summarizes and flags issues; it does not verify truth, medical causation or Church recognition. Review privacy and consent wording for your actual processing arrangements before collecting sensitive stories. Contact details and unnecessary identifiers are not requested; basic email/phone/URL redaction is best-effort, not complete anonymization.

## 5. Connect the frontend without opening intake

Set public values in `testimony-config.js`: project HTTPS URL, public anon/publishable key and Turnstile site key. Do not put service-role, scheduler, worker or AI secrets there. Set `accountsEnabled` and `moderationEnabled` only after testing Auth and the owner MFA flow. Leave `submissionsEnabled` false until the end-to-end checks below pass.

Sign in at `/testimony-review`. The database switches start off. Test them with controlled accounts in a separate test project. At launch, enable the database switches for intake, screening and publication, then set `submissionsEnabled:true` in the frontend through the normal reviewed release process. The frontend flag alone cannot open the backend.

The dashboard contains Pause intake, AI, and publishing. Pausing does not remove existing published stories; use Unpublish for individual entries. Authors can withdraw while intake is paused. To halt a compromised frontend, database controls can be set directly by the project owner:

```sql
update public.testimony_controls
set intake_enabled=false, publishing_enabled=false, screening_enabled=false
where id=true;
```

## 6. Acceptance checks

Run `npm run test:testimony-security`, `BASE_URL=http://127.0.0.1:4321 npm run test:testimony-ui` with the dev server running, and normal browser-quality/QA checks. SQL tests use embedded PostgreSQL (PGlite) with representative Auth claims; browser service interactions and provider requests are mocked. These do not replace live service validation.

In the test project verify: email delivery; expired/reused/wrong-host CAPTCHA rejection; unauthorized REST writes; one author's inability to read another's private story; MFA enrollment/recovery; real structured AI responses; wrong worker role denial; concurrent cap enforcement; stale approve after edit; author withdrawal; public fields only; report/unpublish flow; scheduler outages and retries; paused intake; backup restore; and the 30-day purge schedule. Verify direct database grants as well as the UI.

Publish only after these checks succeed. Do not mark the integration live merely because the static deployment passes.

## References

- https://supabase.com/docs/guides/database/postgres/row-level-security
- https://supabase.com/docs/guides/auth/auth-mfa
- https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
