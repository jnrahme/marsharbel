-- Restore moderator MFA at the database layer.
-- Supersedes 202609220002_moderator_password_access.sql, which dropped the aal2 check.
-- Moderation RPCs (via testimony_require_moderator) and the moderator RLS policies
-- all call this function, so requiring aal2 here enforces MFA server-side.
-- Roll out AFTER the client ships moderatorMfaRequired:true (see docs/MODERATOR-MFA.md).
create or replace function public.testimony_is_moderator() returns boolean
language sql stable set search_path = '' as $$
  select auth.uid() is not null
    and coalesce(auth.jwt()->'app_metadata'->>'role','') = 'moderator'
    and coalesce(auth.jwt()->>'aal','') = 'aal2'
$$;
