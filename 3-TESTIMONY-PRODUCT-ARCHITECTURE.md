# Testimony product architecture

## Coherent journeys
- Read an approved testimony -> share a story -> sign in/create an account -> save a draft -> add up to five images -> submit -> track pending/approved/rejected status.
- Moderator signs in with MFA -> reviews story and images separately -> requests clarification or approves/rejects -> approval publishes only intentionally selected fields.
- Public navigation keeps Testimonies, Rosary, and Souvenirs as distinct but consistent journeys. Checkout remains Shopify-hosted; prayer state remains local to the prayer flow.

## Image pipeline before activation
Use private object storage with signed upload URLs. Enforce JPEG/PNG/WebP, 10 MB/file pre-upload and lower post-processing limits, MIME and magic-byte agreement, max pixel count, virus/malware scan, metadata removal, server-side decode/re-encode, random object keys, no SVG/HTML, no public bucket, and separate moderator approval. Retain originals only if a written policy requires it. Add alt text and consent/rights attestations.

## Account decisions Joey must own
Choose Supabase Auth vs another identity provider, transactional email sender/domain, privacy/retention policy, minimum age/guardian policy, image retention, moderator identities, recovery procedure, and whether anonymous submissions are allowed. The QA build does not invent these choices or activate external services.

## Test plan
Unit: normalization, limits, escaping, rate windows, permission checks, status transitions. Integration: Turnstile verification, authenticated draft ownership, signed image upload, scan/re-encode, RLS, moderator actions, publish/unpublish, kill switch. E2E: visitor/account/moderator journeys. Accessibility: labels, errors, focus, keyboard, contrast, reduced motion, screen readers. Responsive: 390/768/1280/1440 widths with overflow and image-crop checks. Security: dependency audit, secret scan, RLS negative tests, CSP, origin checks, upload polyglots, stored-XSS payloads, replay, enumeration, CSRF, abuse spikes, backup/restore and incident drill.
