# Security hardening, October 2, 2026

Status: proposed PR, not deployed. Baseline: stage d51b0ea.

## Baseline verified against production

At 20:51-20:53 UTC, HTTPS homepage and moderation page returned only
`Content-Security-Policy: upgrade-insecure-requests`, without the other headers.
Netlify headers do not configure Hostinger production.
Source directories, .git/config and TOML files return 403. package.json is public;
this is build metadata, not a secret. Production uses Hostinger hcdn.

Anonymous Supabase reads: public publication IDs readable; all five private
submission/control/audit/budget/report tables deny access (401/403, code 42501).
Email auto-confirm is disabled. These checks did not create users or submissions.
Local testimony SQL, validation and Edge tests pass. They test CAPTCHA hostname
and site-key binding, limited JSON, fail-closed secrets, private intake, quotas,
server-issued moderator role, stale edits and publish/unpublish boundaries.
This is not a claim that every migration/function is deployed identically.
Both production-only and full npm dependency audits found zero advisories.
Third-party scripts loaded from jsDelivr, Google Tag Manager, CAPTCHA providers
and optional Shopify remain supply-chain dependencies. Inline analytics bootstrap
scripts currently prevent strict script-src enforcement without hashes/nonces.

## PR 1 implementation

- Production .htaccess: nosniff, DENY framing plus frame-ancestors none,
  strict-origin referrers and disabled camera/mic/geolocation/payment/USB.
- Enforced lightweight CSP: no objects, no foreign base URL, HTTPS upgrades.
- Dependency-aware report-only CSP without allowing inline scripts. This is a
  compatibility step, not protection against script injection yet. Violations
  currently appear in browser DevTools, not a remote reporting service.
- One-day HTTPS-only HSTS, no subdomain/preload commitment. Raise duration only
  after production header/TLS verification. Do not enable includeSubDomains
  until every subdomain is checked.
- No-store on account, submission and moderation HTML. Admin robots noindex and
  no-referrer. The admin HTML is a public shell, not a private-data boundary.
- Five production-config regression tests wired into the full QA gate.

Browser proof: emulated these headers over actual live resources for 7 routes
(home, Arabic home, Annaya tour, rosary guide, submission, moderation, videos) at
390 and 1280px. All 14 cases had no JS exceptions, overflow, broken images or
enforced CSP violations. Report-only violations were inline scripts only.
Inspected actual desktop/phone homepage and phone submission screenshots.
This emulation does NOT verify Apache/LiteSpeed parsing or post-deploy headers.

Deployment gate: independent review, full CI, Hostinger response-header checks
on clean URLs, .html redirects, JS/CSS, error responses and sensitive-page cache
headers, then desktop/phone rendered checks. Confirm exactly one CSP baseline
is effective; host-injected policies intersect, not replace each other.
Verify audio, YouTube, hCaptcha, languages and service worker. HSTS on HTTPS only.

## Open security findings

Moderator MFA is not required in the current config/server migration. Complete
git history places the change in 1c651bb0d53a3e97dc4a5e4a30310ecb6fe5b173,
September 23, 2026 11:07:44 EDT, "Enable CAPTCHA-protected guest testimony review
and consistent navigation". Migration 202609220002 removes the aal2 condition.
The comments claim temporary owner approval; those comments are not permission.
No matching September 22-23 user-channel approval was found in the bounded
observation search. Original conversation recovery and owner decision remain
necessary before changing login behavior. Anonymous denial does not prove MFA.

## Crawl/copy limits and next stages

Public pages can be copied through browsers, screenshots, direct requests and
this public source repository. Neither noai metadata, ai.txt nor robots.txt can
make them copy-proof. robots.txt is voluntary. Do not disable selection or
right-click: they do not stop extraction and hurt accessibility.
AI training opt-outs and AI search/citation opt-outs are separate choices. Keep
Googlebot/Bing access unless the owner deliberately changes search strategy.
Crawler changes wait on that choice. ai.txt/noai are not universal standards and
must never be presented as enforced security controls.

## Cloudflare Free rollout, awaiting DNS approval

Free has Bot Fight Mode, the limited Free Managed Ruleset and one rate-limit
rule. It is not the paid OWASP/full Managed Ruleset or enterprise bot scoring.
Bot Fight Mode applies across the domain and cannot be skipped through WAF
custom rules, so test monitoring and real readers before broad activation.

1. Inventory/export existing DNS (A/AAAA/CNAME/MX/TXT/CAA), mail routing, DNSSEC,
   origin IP, host TLS and custom records. Do not change nameservers from a guess.
2. Add domain to an owner-controlled Cloudflare Free account, compare imported
   records and choose Full (strict) TLS after verifying origin certificate.
3. Proxy only intended web records, leave mail records DNS-only. Get explicit
   owner approval for the exact nameserver change and handle DNSSEC safely.
4. After activation, verify pages, mail records, redirects, SSL, forms, CAPTCHA,
   all locales and deployment access. Cloudflare Free Managed Ruleset is enabled
   by default; verify actual state. Stage rate limiting against observed request
   volume, exclude verified bots where the available rule permits it.
5. Enable bot protection/AI category blocking only after crawler choice and
   compatibility checks. Record rules, rollback and security event monitoring.
6. Prevent origin bypass only after checking Hostinger support; Cloudflare alone
   does not hide/block an already known origin or protect direct Supabase APIs.
   Test origin restrictions without blocking Hostinger CDN/deploy integrations.

No account, DNS, paid service, rule or production backend was changed here.

Sources (read October 2, 2026):
- https://developers.cloudflare.com/bots/plans/free/
- https://developers.cloudflare.com/bots/get-started/bot-fight-mode/
- https://developers.cloudflare.com/waf/managed-rules/
- https://developers.cloudflare.com/waf/rate-limiting-rules/
