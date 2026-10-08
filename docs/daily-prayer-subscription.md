# Daily prayer subscription - architecture and operations

Sign-up at `/daily-prayer`, double opt-in, 6 AM ET daily issue (rosary mystery of the day,
link to the Maronite prayers of the day, daily Saint Charbel prayer), subscriber list in
Supabase, delivery through a provider adapter (Resend first), sender domain
`mail.marsharbel.com`. Design target: 1-2 million subscribers.

## Boundaries (mirror testimony/feedback pipelines)
- All subscriber data behind RLS; only service-role RPCs touch it.
- Guest signup only after Turnstile verification (`subscribe_prayer` action) + IP rate limits.
- Confirm/unsubscribe links are stateless HMAC URLs (`subscriber-token.ts`); no token
  material is stored. Links are bearer links, standard for mailing lists.
- Unsubscribe: footer link -> branded "are you sure?" page -> confirm. No logins.
  RFC 8058 one-click POSTs from mail clients hit the same endpoint.
- First real send is gated: `prayer_controls.send_enabled` ships `false`; bulk send is an
  ask-first decision tier item. `daily_send_cap` (default 90) keeps the Resend free tier safe.

## Data model (migration 202610080001)
- `prayer_controls` - signup/send switches, daily caps.
- `prayer_subscribers` - email (unique, lower-cased), status pending/confirmed/unsubscribed
  /bounced/complained, locale, source, timestamps.
- `prayer_issues` - one row per issue date; claim is idempotent; counters.
- `prayer_send_log` - per-recipient result with provider message id.
- `prayer_intake_rates` - 10 signups per IP hash per 5-minute window.
- Moderator reads (`prayer_subscriber_stats`, `prayer_subscriber_list`) reuse
  `testimony_require_moderator()`.

## Edge functions
- `subscribe-prayer` - POST from the site; validates, rate-limits, Turnstile-verifies,
  inserts pending, sends the double opt-in confirm email.
- `confirm-subscription` - GET link target; verifies HMAC, marks confirmed, branded result page.
- `unsubscribe-prayer` - GET are-you-sure page, POST confirm, RFC 8058 POST support.
- `send-daily-prayer` - POST with `Authorization: Bearer DAILY_PRAYER_CRON_SECRET`; claims the
  issue, keyset-paginates confirmed subscribers, sends via adapter with List-Unsubscribe
  headers, records per-recipient results, honors the daily cap (overflow defers, issue stays
  open for resume).
- `_shared/email-adapter.ts` - provider seam (`EMAIL_PROVIDER=resend`); swap without touching callers.
- `_shared/prayer-email-templates.ts` - branded shell; prayer text verbatim from the published
  saint-charbel-prayers page; the postal line lives here and nowhere else.

## Secrets (Supabase project env, dashboard)
`RESEND_API_KEY` (vault), `EMAIL_PROVIDER=resend`, `DAILY_PRAYER_FROM_EMAIL` (mail.marsharbel.com
sender), `DAILY_PRAYER_FROM_NAME`, `DAILY_PRAYER_TOKEN_SECRET` (random 32+ bytes),
`DAILY_PRAYER_CRON_SECRET` (random). Turnstile + allowed origins reuse TESTIMONY_* project secrets.

## DNS (Hostinger hPanel)
Verify `mail.marsharbel.com` in the Resend dashboard, add the DKIM/SPF/MX records it issues.
Send stays disabled until domain verification is green.

## Schedule
6 AM ET send: Supabase cron (pg_cron -> net.http_post) or external caller hitting
`send-daily-prayer` with the cron secret. Wire after first-send approval.

## Scale notes (1-2M target)
- Sends: keyset pagination already; at volume switch to Resend batch API (100/call) and a
  worker queue; the adapter absorbs the change.
- Lists: stats are aggregate counts; subscriber list is paginated (500/page).
- Free tier is launch-only; paid plan is a money decision for Joey.
