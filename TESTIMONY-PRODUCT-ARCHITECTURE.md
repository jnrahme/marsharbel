# Testimony product architecture

## Launch policy (decided 2026-09-19)
- **Accounts required to submit.** No anonymous submissions; the Edge Function rejects requests without a valid Supabase Auth session, and each story is stored with its `submitter_id`. Anonymous visitors can still read approved testimonies.
- **Adults only.** Submitters attest they are 18 or older; the attestation is required in the form, enforced by the Edge Function, and stored on the row (`age_attested`, database-checked).
- **30-day rejected retention.** Rejected stories are deleted 30 days after moderation (`purge_rejected_testimonies`, scheduled nightly). Private photos for rejected submissions are deleted with the same job before uploads are activated.
- **Sole initial moderator.** Joey is the only account granted `app_metadata.role='moderator'` at launch. Adding another moderator is a new owner decision.
- **Mandatory moderator MFA.** Moderator row-level policies require `aal2`, so moderation fails closed until the MFA step-up is complete.
- **Supabase stack.** Supabase Auth for identity, Postgres with RLS for data, and private Supabase Storage for photos (signed upload URLs).

## Coherent journeys
- Read an approved testimony -> share a story -> sign in/create an account -> confirm 18+ -> save a draft -> add up to five images -> submit -> track pending/approved/rejected status from the account page.
- Moderator signs in with MFA -> reviews story and images separately -> requests clarification or approves/rejects -> approval publishes only intentionally selected fields -> rejected entries purge after 30 days.
- Public navigation keeps Testimonies, Rosary, and Souvenirs as distinct but consistent journeys. Checkout remains Shopify-hosted; prayer state remains local to the prayer flow.

## Image pipeline before activation
Use private object storage with signed upload URLs. Enforce JPEG/PNG/WebP, 10 MB/file pre-upload and lower post-processing limits, MIME and magic-byte agreement, max pixel count, virus/malware scan, metadata removal, server-side decode/re-encode, random object keys, no SVG/HTML, no public bucket, and separate moderator approval. Add alt text and consent/rights attestations. Wire rejected-image deletion into the 30-day purge job before uploads go live.

## Remaining owner inputs before activation
- Create the Supabase project (free tier is enough to start) and provide its public URL/anon key for `testimony-config.js`; service-role and Turnstile secrets are set as function secrets, never committed.
- Create a Cloudflare Turnstile site key/secret pair for the QA and production origins.
- Choose the transactional email sender/domain Supabase Auth should use for account confirmation and recovery (default Supabase email works to start; a custom domain is a later improvement).
- Review the privacy policy page so it states the adults-only rule and the 30-day rejected-retention rule before intake opens.

## Test plan
Unit: normalization, limits, escaping, rate windows, permission checks, status transitions, age attestation, auth-required rejection. Integration: Turnstile verification, authenticated draft ownership, signed image upload, scan/re-encode, RLS (author reads own only, moderator requires aal2), moderator actions, publish/unpublish, rejected-purge job, kill switch. E2E: visitor/account/moderator journeys. Accessibility: labels, errors, focus, keyboard, contrast, reduced motion, screen readers. Responsive: 390/768/1280/1440 widths with overflow and image-crop checks. Security: dependency audit, secret scan, RLS negative tests, CSP, origin checks, upload polyglots, stored-XSS payloads, replay, enumeration, CSRF, abuse spikes, backup/restore and incident drill.
