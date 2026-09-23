# Live setup status — 2026-09-22

Project: Saint Charbel Testimonies (`alxccoizzksyitxvqhpv`), jnrahme's Org, free plan, us-east-1.
Public project URL: https://alxccoizzksyitxvqhpv.supabase.co

Completed and verified:
- Applied 202609220001_protected_testimonies.sql to the initially empty database using the authenticated dashboard.
- SQL verification: all six testimony tables have RLS; intake, publication and screening switches are false; anon cannot read submissions or execute intake; anon can read publications.
- Live HTTPS read-only test passed: public publication reads succeed and all five private tables return permission denied to anonymous clients. No stories were created.
- Site URL: https://marsharbel.com/account.html. Exact redirect allowlist: /account and /account.html on https://marsharbel.com.
- Confirm email enabled; anonymous sign-in and new signups disabled, verified after reload and via Auth settings API.
- Frontend public project URL, publishable key and Turnstile site key connected. Local moderation sign-in enabled; account creation and submissions remain off.
- Fixed worker CAPTCHA compatibility locally: trusted server Auth bootstrap obtains a worker session; role/email checked; all database calls use a separate public-key client with the restricted JWT. Privileged server code remains trusted. Security tests cover denial if bootstrap returns a moderator and forbid privileged-client database calls. Live worker integration remains untested.

Pending user steps:
- Owner account created by user: jnrahme@gmail.com, UUID c613c676-84a9-4256-8016-6011966a3888. Moderator role assigned after explicit confirmation and verified in the live SQL result. Live password sign-in and CAPTCHA verification succeeded; the page reached authenticator enrollment. Owner subsequently requested and explicitly confirmed removal of the MFA requirement. Applied 202609220002_moderator_password_access.sql via dashboard; verified the live function still requires an authenticated server-issued moderator role. Local frontend moderatorMfaRequired=false. Real owner session successfully loaded the private admin panel without MFA; all three publishing controls remain off.
- Cloudflare signed in. Created managed Turnstile widget "Saint Charbel testimonies" for marsharbel.com, localhost and 127.0.0.1 (local hosts for setup testing; remove before launch). Pre-clearance remains off. Public site key connected locally. After explicit confirmation, saved the secret in Supabase Auth CAPTCHA settings. Reload verified Turnstile protection enabled; real login accepted the challenge. No secret was saved in repository files.

Remaining setup:
- Production SMTP, restricted worker credentials, AI key/model, screening function deployment, scheduling and retention, backups/restore and live end-to-end checks. Intake function deployment is now completed; its gateway authentication configuration still needs resolution.
- No public submissions or publishing enabled; password/CAPTCHA moderator access works, but the full publication flow is not yet live-tested.

Run live read-only checks with: node scripts/tests/testimony_live_readonly.mjs

Latest verification: live anonymous privacy checks passed; mocked testimony UI flow checks passed at 375 and 1366 pixels; paused-state quality suite passed 55 tests. Real owner login reached MFA enrollment; no testimony was published.

Current admin mode: password + CAPTCHA, no MFA required. Remember-browser storage is opt-in. Latest tests passed: SQL/edge security, browser session storage, live anonymous privacy checks, and mocked browser flows. Public deployment of this frontend remains pending.

Submission UI simplified: one Submit testimony button below human verification; mandatory preview and View Published action removed. Mocked direct submission/CAPTCHA, double-submit prevention and failure-preserves-text tests passed on desktop/mobile; 60 layout/accessibility checks passed. The intake endpoint is deployed; public account delivery, gateway authentication and feature flags still require setup before visitors can submit.

## Deployment progress at 22:18 UTC
- Deployed `submit-testimony` through the authenticated Supabase editor, with its shared validation inlined. No secrets are in the deployed source.
- Saved `TURNSTILE_SECRET_KEY` and `TESTIMONY_ALLOWED_ORIGINS` in encrypted Function secrets. Allowed origins are https://marsharbel.com, http://127.0.0.1:4321 and http://localhost:4321 for controlled setup testing. Remove local origins before launch.
- Live allowed-origin OPTIONS returned HTTP 204 with the expected CORS headers, proving the deployed handler runs.
- Missing and forged credentials returned HTTP 401 at the Supabase gateway. These checks do not prove signed-in submission or database insertion.
- The legacy JWT gate remains enabled. Requested confirmation before changing it; no approval has been received.
- The owner questioned the contributor sign-in requirement. Guest submission is under clarification; no guest-access change has been applied.
- No real story has been submitted or published. Frontend intake remains paused.

## 2026-09-23 hCaptcha connection
- Restored expired hCaptcha and Supabase dashboard sessions using the existing Google/GitHub accounts.
- Generated the hCaptcha server secret and saved it directly in Supabase Function secrets as HCAPTCHA_SECRET_KEY. It was not written to source files. HCAPTCHA_SITE_KEY and TESTIMONY_CAPTCHA_PROVIDER=hcaptcha are also saved.
- Deployed the updated submit-testimony function with provider selection, configured site-key binding, hostname validation and bounded verification requests. Dashboard confirmed the new deployment timestamp.
- Local public configuration now selects hCaptcha with the real site key. Auth continues to use its existing Turnstile configuration.
- Real Chrome visibly renders the I am human checkbox at 127.0.0.1:4321/submit-testimony.html. The embedded browser instead produced a blank CAPTCHA frame. No solved challenge or accepted real submission is claimed.
- Provider-side domain allowlisting was NOT saved: hCaptcha rejected 127.0.0.1 as an invalid domain. Discarded that invalid edit. Server-side exact allowed origins and verification hostname checks remain enforced. Configure provider allowlisting with a supported staging hostname before launch.
- Security tests and the complete mocked UI suite passed, including CAPTCHA failure, retry, expiry, and retained draft text. Tests do not replace live token validation.
- Asked for action-time permission to complete the visible real CAPTCHA; still pending. All intake/publishing flags remain paused. Guest intake, AI worker credentials/scheduling and full publication testing remain unfinished.

## Guest-flow deployment, later on 2026-09-23
- Applied 202609230001_guest_testimonies.sql to the live database and verified dashboard success. Guest submissions have no author account, remain private under existing RLS, and are inserted only by the service role after CAPTCHA verification. Limits: 10 guest attempts per minute and the existing 200 global/day budget; exact duplicate stories rejected.
- Deployed the guest variant of submit-testimony (no contributor login required in the handler). Supabase's legacy JWT gateway remains ON pending action-time confirmation, so guest requests still cannot reach it.
- Added an authenticated moderator-only manual-review RPC with 30-character notes, revision checks and audit logging. This records human screening without claiming AI ran; publication remains a separate capped moderator action. Guest cards do not offer author clarification because guest contact details are not collected.
- Updated form, account, moderation and privacy copy for guests, text-only intake, hCaptcha and manual review. Frontend submissionsEnabled and database intake/publishing switches remain OFF until the gateway setting and live test are completed.
- Database security suite, Edge handler suite and browser-flow suite passed, including guest submission without session and manual review enabling a separate approval action. Provider/database browser responses are mocked.
- Live anonymous requests to both new RPCs returned 401; existing live private-table denial checks passed. No real guest story has been submitted or published.
- hCaptcha onboarding is complete; the generated secret exists only in Supabase server secrets. Provider-side domain allowlisting is OFF because 127.0.0.1 was rejected. The name is Saint Charbel testimony submissions. Server exact origin/hostname checks remain enforced.
- The real hCaptcha checkbox renders in Chrome; the embedded browser frame was blank. Requested explicit action-time approval to disable the legacy login gate for this CAPTCHA-protected guest endpoint and complete the real CAPTCHA. Pending reply; do not report end-to-end success.

## Stage release verification — 2026-09-23
- Fresh security, guest/manual-review UI, browser-session, live anonymous privacy, and deployment-verifier tests passed.
- Combined navigation and testimony quality suite: 305 passed. Shared navigation check: 49 pages, zero drift.
- Full QA passed using the feature worktree server on port 4321. An initial run on the default port 4173 reached a different running server and failed canonical-URL checks; rerun against the correct worktree passed.
- Updated operational documentation for guest CAPTCHA and manual review; corrected the JWT configuration comment.
- Stage points to public marsharbel.com. No stage push was made: live guest submission remains blocked on explicit browser action-time confirmation for the legacy JWT setting and CAPTCHA completion. Intake and publication flags remain off.

## Confirmed live flow — 2026-09-23
- Owner explicitly confirmed legacy JWT setting change and real CAPTCHA testing. Saved gateway OFF; anonymous malformed request reached handler and returned validation 400.
- Enabled database intake/publication, kept screening off; frontend submissionsEnabled=true.
- Chrome real hCaptcha completed; guest form returned accepted reference ddfed3d1-06b0-4531-805e-8fa5f27da7c6. No contributor login.
- Existing moderator session loaded the private queued story. Recorded manual review, approved, verified anonymous public projection, unpublished, then rejected. Admin queue and public list empty afterward. Clearly labeled QA entry contains no personal religious/medical claim.
- Live anonymous private-table denial checks passed after enablement.
- Removed premature automatic-retention promise from public form: retention scheduler and backup restoration are not yet configured. AI screening remains off.
