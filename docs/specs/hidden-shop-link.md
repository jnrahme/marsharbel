# Hidden shop-link scaffold (not activation-ready for locales)

## Scope and release hold
Default OFF build-time scaffold for the 139 English pages owned by scripts/build-pages.mjs only. No flag-on build, environment setting, store URL, payment, new public page, production deployment or merge is included. Do not activate this feature. Joey must review the QA-ready PR first.

## Contract
- Only SHOP_LINK_ENABLED=1 permits composition. All other values leave output unchanged.
- SHOP_LINK_URL is supplied through the build environment, never committed. Missing, malformed, non-HTTPS or credential-bearing URLs fail before page writes.
- Footer markup lives in partials/fragments/shop-link.html. English wording lives under locales/en/shop-link-copy.json with stable shop.link.label.
- Pure composition adds one link to a page with exactly one composed footer; duplicate links or missing footer/copy fail closed. rel is noopener nofollow.
- Do NOT add noindex to existing pages. A link cannot make its destination noindex. The separate password-protected store's indexing controls must be verified before any later activation.

## Verification
Check no checked-in served HTML bytes change. Hash every existing HTML input around the disabled composition path. Compare complete baseline and candidate ordinary builder output in isolated worktrees; no generated-output changes are part of this PR. Pure synthetic renderer tests cover exactly one link, HTML escaping, unchanged page indexing, and failure cases. No real store URL or enabled build is used. Standard repo CI remains required.

## Multilingual activation follow-up
This is NOT activation-ready for locales. Before activation: translate the label into every published locale; integrate with the normal international postprocessor before same-page manifest hashing; maintain family identity/contracts through normal regeneration; verify one link per in-scope page on desktop/phone and Arabic RTL; verify the private destination/password/indexing and final URL; obtain Joey's explicit activation permission. No locale output changes in this scaffold.

## Rollback
Keep the flag absent/off. Revert this PR if needed. No content or existing served page needs reverting because the committed default-off output is unchanged.
