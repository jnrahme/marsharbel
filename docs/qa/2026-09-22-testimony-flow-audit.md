# Testimony flow audit — 2026-09-22

## Scope and status
The local admin/practice workflow is implemented. Public account creation, submission intake, AI screening and publishing remain paused. External SMTP, worker/AI provisioning and Edge Function deployment remain unfinished; mock tests do not establish that this public flow works live.

## Issues corrected
- Rejection validation previously appeared off-screen. Each story now gives reason requirements, inline errors and focus on the field.
- Action outcomes now identify what happened and receive keyboard focus instead of displaying a vague off-screen “Saved”.
- Demo rejections remain visible with their reasons.
- Clarification explains the waiting state; a simulated author reply lets the practice flow continue.
- A reset button restores all three fictional examples and clears demo history.
- Demo notes explicitly identify simulated screening; no database moderation writes occur in demo mode.
- Failed queue loading keeps the panel hidden and offers retry. Removed obsolete MFA instructions from the load error.
- Hidden controls are protected from shared button/grid CSS overriding their hidden state.
- Paused author forms cancel native submission, including Enter/submit events, to prevent form content becoming URL parameters.
- CAPTCHA now displays progress, success, expiry and failure messages. Clicking Login before CAPTCHA completion no longer resets an in-progress check.

## Verification
- Database and Edge Function security suites passed (local PGlite and mocked services).
- Browser-storage tests passed for tab-only sessions, remembered sessions, opt-out, legacy migration and forgetting.
- Live read-only Supabase checks passed: publications readable, all five private tables denied to anonymous requests.
- Mocked author flow: preview, safe text rendering, submission, edit and withdrawal at 375 and 1366 pixels.
- Full demo flow at 375, 768 and 1366 pixels: approve, empty/short/valid rejection, clarification, simulated author reply, unpublish, reset, no database reads or moderation writes.
- Mocked negative cases: expired CAPTCHA, wrong password, server rejection, retry, sign-out, failed queue load and recovery.
- 60 responsive/accessibility/paused-state checks passed across configured viewports.
- Actual in-app browser: approval, rejection, clarification, simulated reply and unpublish visibly verified; actual sign-out cleared the remembered setting and hid the panel.
- Live CAPTCHA comparison: in-app browser encountered Cloudflare error 300030 (widget hung); regular Chrome completed human verification and successfully signed in with the real owner account. No CAPTCHA protection was bypassed.

## Not a production launch certification
Public intake, email delivery, live AI screening, and real publication were not activated or validated end to end. Demo approval never publishes a story. Frontend changes remain local until deployment.
