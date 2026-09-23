-- Temporary owner-requested password-only moderator access.
-- Server-issued moderator role remains mandatory; public access is unchanged.
create or replace function public.testimony_is_moderator() returns boolean
language sql stable set search_path = '' as $$
  select auth.uid() is not null
    and coalesce(auth.jwt()->'app_metadata'->>'role','') = 'moderator'
$$;
