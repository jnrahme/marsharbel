# Shared game accounts migration: draft review, not application

Project alxccoizzksyitxvqhpv is shared with testimonies. Migration is NOT approved for application. No merge/apply/deploy automation permitted. Owner migration go-ahead and independent security review required. The first applied draft has unsafe signup trigger and callable account deletion RPC; this corrective draft narrows privileges/policies, makes signup best-effort, revokes direct trigger-function execution and removes unsafe deletion RPC. No billing, Stripe activation, subscription purchase or account deletion client ships.

## Preflight and apply gate

Security must take fresh catalog/schema snapshots including exact constraints, policies, grants, trigger/function definitions+ACL, auth FKs, testimony dependencies and signup settings; compare to Oct12 evidence before reviewing. Current public auth/settings at2026-10-13 reports Facebook and Google enabled, disable_signup=true. Do not flip signup to false without a separately reviewed shared-project decision. Existing Meta app credentials are already vaulted, never pasted into this PR.

Check existing game rows satisfy new constraints; abort on incompatibility, never delete/repair user data silently. Review trigger exception path, schema-qualified objects and search_path. Ensure whole-account deletion RPC is removed and client never calls it; testimony/report author FKs currently CASCADE, so account deletion erases unrelated testimony data. Test migration and failure cases on an isolated disposable schema/database, not the production project.

After owner approval, security applies the one transaction. Check catalog readback, owner/other-user/anon access, profile fallback, game-only checkpoint schema, no prayer/reflection payload, signup failure isolation and unchanged testimony policies/grants. New-user signup must remain disabled unless approved. Release flag remains OFF. Real Facebook OAuth verification is separate from public provider-enabled metadata; no claim of successful token exchange yet.

## Rollback plan

Before COMMIT: any constraint/privilege/statement failure aborts the transaction; ROLLBACK, confirm original catalog unchanged. Do not split the transaction.

After COMMIT: disable client accounts/Facebook flags; if signup was opened set disable_signup=true. Run independently reviewed safe-disable rollback SQL to revoke all public/anon/authenticated privileges on only game_profiles, game_progress and subscriptions. Preserve all tables/rows and the safe non-raising trigger; do not restore the unsafe delete RPC or registration-abort trigger. Do not touch testimony/prayer/feedback objects or service_role. Confirm grant readback and trigger after commit. Reverting a git file does not roll back live DB. Any further change needs fresh catalog and review.

## PR handling

Draft PR against latest stage. Review-only SQL and docs excluded from web deploy. No ready/auto-merge label. Must not apply from CI or introduce a deployment hook. Parent batches owner migration go-ahead only after security prepares final diff, rollback and consequences. Content/integrator remains single remote push door.
