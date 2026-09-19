-- Saint Charbel testimony intake schema (QA, fail-closed by default)
-- Launch policy decided 2026-09-19:
--   * An account is required to submit (no anonymous submissions).
--   * Adults (18+) only; attestation stored with each submission.
--   * Rejected stories and their private photos are deleted 30 days after rejection.
--   * The site owner is the sole initial moderator; MFA (aal2) is enforced in policy.
--   * Anonymous visitors may keep reading approved testimonies.

create extension if not exists pgcrypto;

create table if not exists public.testimonies (
  id uuid primary key default gen_random_uuid(),
  submitter_id uuid not null references auth.users(id) on delete cascade,
  full_name text not null check(char_length(full_name) between 2 and 120),
  email text,
  language text not null default 'en',
  country text,
  parish text,
  event_date date,
  healing_type text,
  testimony_text text not null check(char_length(testimony_text) between 60 and 7000),
  age_attested boolean not null default false check(age_attested),
  contact_permission boolean not null default false,
  consent_publish boolean not null default false,
  status text not null default 'pending' check(status in ('pending','approved','rejected')),
  created_at timestamptz not null default now(),
  published_at timestamptz,
  moderated_at timestamptz,
  moderated_by uuid references auth.users(id),
  moderation_note text
);

create table if not exists public.testimony_rate_limits (
  ip_hash text primary key,
  window_start timestamptz not null default now(),
  attempts integer not null default 0
);

create table if not exists public.testimony_settings (
  singleton boolean primary key default true check(singleton),
  intake_enabled boolean not null default false
);
insert into public.testimony_settings(singleton,intake_enabled) values(true,false)
  on conflict(singleton) do nothing;

alter table public.testimonies enable row level security;
alter table public.testimony_rate_limits enable row level security;
alter table public.testimony_settings enable row level security;

revoke all on public.testimonies from anon;
revoke all on public.testimony_rate_limits from anon,authenticated;
revoke all on public.testimony_settings from anon,authenticated;

-- Anonymous and signed-in visitors may read approved, published testimonies.
create policy "public reads approved only" on public.testimonies
  for select to anon using(status='approved' and published_at is not null);
create policy "members read approved only" on public.testimonies
  for select to authenticated using(status='approved' and published_at is not null);

-- Authors can read the status of their own submissions, nothing else.
create policy "authors read own testimonies" on public.testimonies
  for select to authenticated using(submitter_id = auth.uid());

-- Moderation requires the moderator role AND a completed MFA step-up (aal2).
-- Joey's account is the only one granted app_metadata.role='moderator' at launch.
create policy "moderators manage testimonies" on public.testimonies
  for all to authenticated
  using((auth.jwt()->'app_metadata'->>'role')='moderator'
        and coalesce(auth.jwt()->>'aal','')='aal2')
  with check((auth.jwt()->'app_metadata'->>'role')='moderator'
        and coalesce(auth.jwt()->>'aal','')='aal2');

-- Server-only intake. Called by the submit-testimony Edge Function with the
-- service role; never granted to browser roles.
create or replace function public.accept_testimony(p_ip_hash text, p_submitter_id uuid, p_payload jsonb)
returns uuid language plpgsql security definer set search_path=public as $$
declare
  v_id uuid;
  v_setting boolean;
  v_limit testimony_rate_limits%rowtype;
begin
  select intake_enabled into v_setting from testimony_settings where singleton=true;
  if coalesce(v_setting,false)=false then
    raise exception 'intake_disabled';
  end if;
  if p_submitter_id is null then
    raise exception 'account_required';
  end if;
  insert into testimony_rate_limits(ip_hash,window_start,attempts) values(p_ip_hash,now(),1)
    on conflict(ip_hash) do update set
      window_start=case when testimony_rate_limits.window_start<now()-interval '1 hour' then now() else testimony_rate_limits.window_start end,
      attempts=case when testimony_rate_limits.window_start<now()-interval '1 hour' then 1 else testimony_rate_limits.attempts+1 end
    returning * into v_limit;
  if v_limit.attempts>3 then
    raise exception 'rate_limited';
  end if;
  insert into testimonies(submitter_id,full_name,email,language,country,parish,event_date,healing_type,testimony_text,age_attested,contact_permission,consent_publish,status)
  values(p_submitter_id,p_payload->>'full_name',nullif(p_payload->>'email',''),coalesce(nullif(p_payload->>'language',''),'en'),nullif(p_payload->>'country',''),nullif(p_payload->>'parish',''),nullif(p_payload->>'event_date','')::date,nullif(p_payload->>'healing_type',''),p_payload->>'testimony_text',true,coalesce((p_payload->>'contact_permission')::boolean,false),true,'pending')
  returning id into v_id;
  return v_id;
end $$;
revoke all on function public.accept_testimony(text,uuid,jsonb) from public,anon,authenticated;

-- 30-day retention: rejected stories are deleted 30 days after moderation.
-- Before photo uploads are activated, this job must also delete the matching
-- private storage objects for purged testimony ids.
create or replace function public.purge_rejected_testimonies()
returns integer language plpgsql security definer set search_path=public as $$
declare
  v_count integer;
begin
  delete from testimonies
  where status='rejected'
    and moderated_at is not null
    and moderated_at < now() - interval '30 days';
  get diagnostics v_count = row_count;
  return v_count;
end $$;
revoke all on function public.purge_rejected_testimonies() from public,anon,authenticated;

-- Nightly purge schedule. Requires the pg_cron extension enabled in the
-- Supabase dashboard (Database -> Extensions) before this statement is run.
-- create extension if not exists pg_cron with schema extensions;
-- select cron.schedule('purge-rejected-testimonies','15 3 * * *',$$select public.purge_rejected_testimonies();$$);
