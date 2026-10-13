# Auth rollout settings and sequencing

Preparation only. Current public /auth/v1/settings read2026-10-13 15:51 EDT: google=true, facebook=true, disable_signup=true. Existing Meta app marsharbel Facebook Login is vaulted; no fresh credential ask. Public settings do not expose current Site URL or redirect allow-list. Those must be read in dashboard before any edit. No new change is authorized by this plan.

Proposed game callback exact allow-list entry: https://games.marsharbel.com/mercy/games/bible-mystery/index.html . Client strips query/hash from redirectTo. Google/Facebook provider callback: https://alxccoizzksyitxvqhpv.supabase.co/auth/v1/callback . Preserve current Site URL byte-for-byte and all existing testimony/email-OTP redirects and settings; do not replace entire allow-list or disable email OTP. Prior Oct12 setup reported games origin /** allow-list; CURRENT live dashboard confirmation remains required before claiming exact current list. Narrowing/removing that wildcard must not break existing clients and requires independent review.

Sequence: owner-approved safe migration while disable_signup=true; security re-dumps catalog/verifies policy, ACL, trigger, unrelated testimony/prayer/feedback unchanged; then separate owner approval for signup+abuse controls; only then enable signup and test throwaway real new-user OAuth. Rollback signup by setting disable_signup=true. Client Facebook flag defaults false and blocks both UI and OAuth method invocation.

Exactly one game signup trigger must be verified after migration; a trigger-count/name conflict is a stop, not permission to remove unrelated triggers. OAuth user must have only ordinary authenticated owner access, never moderator or subscription write role. Facebook may yield absent/unverified email; do not spoof verification or grant testimony-report access on that basis. Existing testimony/report auth FKs CASCADE means whole-account deletion can erase testimony data; deletion stays unavailable. No OAuth signup test is claimed from provider enabled metadata.

Abuse configuration must be verified with security before opening signup: Auth rate limits and supported CAPTCHA. Existing hCaptcha/Turnstile elsewhere is not proof that Supabase Auth's accepted CAPTCHA is wired here. Require actual compatible provider/client token path and isolated verification, not just naming Turnstile. Signup enablement is separate from shared-project SQL go-ahead.

## Fresh dashboard read October 13, 2026 15:54 EDT

Verified Site URL: https://marsharbel.com/account.html . Exact current allow-list: https://marsharbel.com/account ; https://marsharbel.com/account.html ; https://games.marsharbel.com/** . No configuration changed. Preserve all three entries; current wildcard already covers stripped game redirect. Source: https://supabase.com/dashboard/project/alxccoizzksyitxvqhpv/auth/url-configuration .

Fresh protection read: Captcha switch aria-checked=true, provider Turnstile by Cloudflare, masked secret populated. Source https://supabase.com/dashboard/project/alxccoizzksyitxvqhpv/auth/protection . This proves dashboard configuration only, not client token wiring or actual signup acceptance. No setting change.
