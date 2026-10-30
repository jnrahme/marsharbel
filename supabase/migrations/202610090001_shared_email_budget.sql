-- Shared daily email-send budget across workers (Resend account cap is account-wide) plus
-- worker heartbeat tracking for staleness alerts. Service-role only, like the prayer pipeline.
-- Safe to rerun this migration.
begin;
create table if not exists public.email_send_budget (
 day date primary key,
 subscription_claimed integer not null default 0 check(subscription_claimed >= 0),
 request_claimed integer not null default 0 check(request_claimed >= 0)
);
create table if not exists public.email_worker_heartbeat (
 worker text primary key check(char_length(worker) <= 60),
 last_run_at timestamptz not null default now()
);
alter table public.email_send_budget enable row level security;
alter table public.email_worker_heartbeat enable row level security;
revoke all on public.email_send_budget from public,anon,authenticated;
revoke all on public.email_worker_heartbeat from public,anon,authenticated;
-- Atomic daily budget claim. One account-wide cap (prayer_controls.daily_send_cap) shared by
-- every sending worker; the 'request' flow always yields to the subscription flow by reserving
-- the day's not-yet-claimed confirmed subscribers. Day anchors to America/New_York like the
-- daily issue date.
create or replace function public.claim_email_send_budget(p_flow text,p_count integer) returns integer
language plpgsql security definer set search_path='' as $$
declare b public.email_send_budget; cap integer; reserve integer; grant_count integer; today date; begin
 if p_count is null or p_count < 1 then return 0; end if;
 today := (now() at time zone 'America/New_York')::date;
 select c.daily_send_cap into cap from public.prayer_controls c where c.id;
 cap := greatest(1,coalesce(cap,90));
 insert into public.email_send_budget(day) values(today) on conflict(day) do nothing;
 select * into b from public.email_send_budget where day=today for update;
 if p_flow='subscription' then
   grant_count := least(p_count,greatest(0,cap - b.subscription_claimed - b.request_claimed));
   update public.email_send_budget set subscription_claimed=subscription_claimed+grant_count where day=today;
 elsif p_flow='request' then
   select count(*) into reserve from public.prayer_subscribers where status='confirmed';
   reserve := greatest(0,reserve - b.subscription_claimed);
   grant_count := least(p_count,greatest(0,cap - b.subscription_claimed - b.request_claimed - reserve));
   update public.email_send_budget set request_claimed=request_claimed+grant_count where day=today;
   grant_count := greatest(0,grant_count);
 else
   raise exception 'unknown_flow';
 end if;
 return grant_count;
end $$;
revoke all on function public.claim_email_send_budget(text,integer) from public,anon,authenticated;
grant execute on function public.claim_email_send_budget(text,integer) to service_role;
-- Deploy-time cron wiring for the staleness alerter (pg_cron + pg_net). Kept as a parameterized
-- function so no URL or secret lives in the repo; run once per project after deploy:
--   select public.email_worker_alerter_schedule('https://<project>.supabase.co','<cron-secret>');
-- Idempotent: re-running replaces the schedule.
create or replace function public.email_worker_alerter_schedule(p_url text,p_secret text) returns text
language plpgsql security definer set search_path='' as $$
begin
 if not exists (select 1 from pg_extension where extname='pg_cron')
 or not exists (select 1 from pg_extension where extname='pg_net') then
   return 'skipped: pg_cron/pg_net not installed';
 end if;
 begin perform cron.unschedule('check-worker-heartbeats'); exception when others then null; end;
 perform cron.schedule('check-worker-heartbeats','*/30 * * * *',
   format($job$select net.http_post(url:='%s/functions/v1/check-worker-heartbeats',headers:=jsonb_build_object('content-type','application/json','authorization','Bearer %s'),body:='{}'::jsonb)$job$,rtrim(p_url,'/'),p_secret));
 return 'scheduled every 30 min';
end $$;
revoke all on function public.email_worker_alerter_schedule(text,text) from public,anon,authenticated;
grant execute on function public.email_worker_alerter_schedule(text,text) to service_role;
commit;
