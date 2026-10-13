-- Safety rollback after independently approved migration, NOT automatic execution.
-- First disable client accounts/Facebook feature flags; if signup was opened,
-- set disable_signup=true in Auth configuration (not SQL). Leave Site URL and testimony OTP settings unchanged.
-- Preserve tables, rows, the non-raising signup trigger and existing testimony/prayer/feedback access.
begin;
revoke all on public.game_profiles from public, anon, authenticated;
revoke all on public.game_progress from public, anon, authenticated;
revoke all on public.subscriptions from public, anon, authenticated;
-- Never restore the registration-abort trigger or unsafe whole-account deletion RPC.
commit;
-- Read back grants and safe trigger after commit. Existing-user game-account reads/writes
-- will fail explicitly; guest game remains usable. service_role is not changed.
