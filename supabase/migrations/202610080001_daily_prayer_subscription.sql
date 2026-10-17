-- Daily prayer subscription: double opt-in via stateless HMAC links, service-role-only access.
-- Mirrors the testimony/feedback pipeline boundaries. Safe to rerun this migration.
begin;
create table if not exists public.prayer_controls (
 id boolean primary key default true check(id),
 signup_enabled boolean not null default true,
 daily_signup_limit integer not null default 200 check(daily_signup_limit between 1 and 5000),
 send_enabled boolean not null default false,
 daily_send_cap integer not null default 90 check(daily_send_cap between 1 and 100000)
);
insert into public.prayer_controls(id) values(true) on conflict do nothing;
create table if not exists public.prayer_subscribers (
 id uuid primary key default gen_random_uuid(),
 email text not null check(char_length(email) <= 254),
 status text not null default 'pending' check(status in ('pending','confirmed','unsubscribed','bounced','complained')),
 locale text not null default 'en' check(char_length(locale) <= 5),
 source text not null default 'daily-prayer' check(char_length(source) <= 60),
 revision integer not null default 1,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 confirmed_at timestamptz,
 unsubscribed_at timestamptz
);
create unique index if not exists prayer_subscribers_email on public.prayer_subscribers(lower(email));
create index if not exists prayer_subscribers_status_created on public.prayer_subscribers(status,created_at);
create table if not exists public.prayer_issues (
 id uuid primary key default gen_random_uuid(),
 issue_date date not null unique,
 mystery text not null default '' check(char_length(mystery) <= 120),
 prayer_key text not null default '' check(char_length(prayer_key) <= 60),
 send_started_at timestamptz,
 send_completed_at timestamptz,
 attempted integer not null default 0 check(attempted >= 0),
 sent integer not null default 0 check(sent >= 0),
 failed integer not null default 0 check(failed >= 0),
 created_at timestamptz not null default now()
);
create table if not exists public.prayer_send_log (
 id bigint generated always as identity primary key,
 issue_id uuid references public.prayer_issues(id) on delete cascade,
 subscriber_id uuid references public.prayer_subscribers(id) on delete set null,
 status text not null check(status in ('sent','failed','deferred')),
 provider_message_id text not null default '' check(char_length(provider_message_id) <= 120),
 error text not null default '' check(char_length(error) <= 300),
 created_at timestamptz not null default now()
);
create index if not exists prayer_send_log_issue on public.prayer_send_log(issue_id,status);
create table if not exists public.prayer_intake_rates (
 ip_hash text not null check(ip_hash ~ '^[0-9a-f]{64}$'),
 window_start bigint not null,
 used integer not null default 1 check(used > 0),
 primary key(ip_hash,window_start)
);
create index if not exists prayer_intake_rates_expiry on public.prayer_intake_rates(window_start);
alter table public.prayer_subscribers enable row level security;
alter table public.prayer_controls enable row level security;
alter table public.prayer_issues enable row level security;
alter table public.prayer_send_log enable row level security;
alter table public.prayer_intake_rates enable row level security;
revoke all on public.prayer_subscribers from public,anon,authenticated;
revoke all on public.prayer_controls from public,anon,authenticated;
revoke all on public.prayer_issues from public,anon,authenticated;
revoke all on public.prayer_send_log from public,anon,authenticated;
revoke all on public.prayer_intake_rates from public,anon,authenticated;
create or replace function public.prayer_budget(p_bucket text,p_limit integer) returns boolean
language plpgsql security definer set search_path='' as $$
declare n integer; begin
 insert into public.testimony_budgets(bucket,period,used) values(p_bucket,(now() at time zone 'UTC')::date,1)
 on conflict(bucket,period) do update set used=public.testimony_budgets.used+1 returning used into n;
 return n<=p_limit;
end $$;
create or replace function public.prayer_check_intake_rate(p_ip_hash text) returns boolean
language plpgsql security definer set search_path='' as $$
declare current_window bigint; n integer; begin
 if p_ip_hash is null or p_ip_hash !~ '^[0-9a-f]{64}$' then raise exception 'invalid_hash'; end if;
 current_window := floor(extract(epoch from statement_timestamp()) / 300)::bigint;
 delete from public.prayer_intake_rates where window_start < current_window - 1;
 insert into public.prayer_intake_rates(ip_hash,window_start,used) values(p_ip_hash,current_window,1)
 on conflict(ip_hash,window_start) do update set used=least(public.prayer_intake_rates.used+1,11)
 returning used into n;
 return n <= 10;
end $$;
-- Guest signup is only callable by the server after CAPTCHA verification.
-- Confirm/unsubscribe links are stateless HMAC URLs the edge functions mint and verify,
-- so no token material is ever stored here.
create or replace function public.prayer_subscribe_guest(p_email text,p_locale text,p_source text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare c public.prayer_controls; s public.prayer_subscribers; sid uuid; begin
 select * into c from public.prayer_controls where id for update;
 if not c.signup_enabled then return jsonb_build_object('error','signup_paused'); end if;
 if p_email is null or char_length(p_email)>254 or p_email !~ '^[^\s@]+@[^\s@]+\.[^\s@]{2,}$' then return jsonb_build_object('error','invalid_email'); end if;
 select * into s from public.prayer_subscribers where lower(email)=lower(p_email);
 if found then
   if s.status='confirmed' then return jsonb_build_object('error','already_subscribed'); end if;
   if not public.prayer_budget('intake:prayer-resend-global',c.daily_signup_limit) then return jsonb_build_object('error','rate_limited'); end if;
   update public.prayer_subscribers set status='pending',
     locale=coalesce(nullif(p_locale,''),locale),revision=revision+1,updated_at=now(),confirmed_at=null,unsubscribed_at=null where id=s.id;
   return jsonb_build_object('id',s.id,'resent',true);
 end if;
 if not public.prayer_budget('intake:prayer-global',c.daily_signup_limit)
 or not public.prayer_budget('intake:prayer-minute:'||to_char(now() at time zone 'UTC','YYYYMMDDHH24MI'),10)
 then return jsonb_build_object('error','rate_limited'); end if;
 insert into public.prayer_subscribers(email,locale,source)
 values(lower(p_email),coalesce(nullif(p_locale,''),'en'),coalesce(nullif(p_source,''),'daily-prayer')) returning id into sid;
 return jsonb_build_object('id',sid,'resent',false);
end $$;
-- Double opt-in confirm (id is HMAC-verified by the edge function before this runs).
create or replace function public.prayer_confirm(p_id uuid) returns jsonb
language plpgsql security definer set search_path='' as $$
declare s public.prayer_subscribers; begin
 select * into s from public.prayer_subscribers where id=p_id;
 if not found then return jsonb_build_object('error','invalid'); end if;
 if s.status='confirmed' then return jsonb_build_object('already',true); end if;
 if s.status='unsubscribed' then return jsonb_build_object('error','unsubscribed'); end if;
 update public.prayer_subscribers set status='confirmed',confirmed_at=now(),revision=revision+1,updated_at=now() where id=s.id;
 return jsonb_build_object('ok',true);
end $$;
-- Read-only peek so the unsubscribe page can show current state without changing it.
create or replace function public.prayer_manage_peek(p_id uuid) returns jsonb
language plpgsql security definer set search_path='' as $$
declare s public.prayer_subscribers; begin
 select * into s from public.prayer_subscribers where id=p_id;
 if not found then return jsonb_build_object('found',false); end if;
 return jsonb_build_object('found',true,'status',s.status);
end $$;
-- Unsubscribe (id is HMAC-verified by the edge function); idempotent. Serves RFC 8058 one-click too.
create or replace function public.prayer_unsubscribe(p_id uuid) returns jsonb
language plpgsql security definer set search_path='' as $$
declare s public.prayer_subscribers; begin
 select * into s from public.prayer_subscribers where id=p_id;
 if not found then return jsonb_build_object('error','invalid'); end if;
 if s.status='unsubscribed' then return jsonb_build_object('already',true); end if;
 update public.prayer_subscribers set status='unsubscribed',unsubscribed_at=now(),revision=revision+1,updated_at=now() where id=s.id;
 return jsonb_build_object('ok',true);
end $$;
-- Moderator dashboard aggregates; reuses the testimony moderator role check.
create or replace function public.prayer_subscriber_stats() returns jsonb
language plpgsql security definer set search_path='' as $$
declare r jsonb; begin
 perform public.testimony_require_moderator();
 select jsonb_build_object(
   'total',count(*),
   'confirmed',count(*) filter(where status='confirmed'),
   'pending',count(*) filter(where status='pending'),
   'unsubscribed',count(*) filter(where status='unsubscribed'),
   'confirmed_7d',count(*) filter(where status='confirmed' and confirmed_at>now()-interval '7 days'),
   'confirmed_30d',count(*) filter(where status='confirmed' and confirmed_at>now()-interval '30 days'),
   'unsubscribed_30d',count(*) filter(where status='unsubscribed' and unsubscribed_at>now()-interval '30 days')
 ) into r from public.prayer_subscribers;
 return coalesce(r,'{}'::jsonb);
end $$;
create or replace function public.prayer_subscriber_list(p_status text,p_limit integer,p_offset integer) returns setof public.prayer_subscribers
language plpgsql security definer set search_path='' as $$ begin
 perform public.testimony_require_moderator();
 if p_status not in ('pending','confirmed','unsubscribed','bounced','complained','all') then raise exception 'invalid_status'; end if;
 return query select * from public.prayer_subscribers
   where (p_status='all' or status=p_status)
   order by created_at desc limit least(greatest(coalesce(p_limit,100),1),500) offset greatest(coalesce(p_offset,0),0);
end $$;
-- Idempotent issue claim for the daily send job (service role only).
create or replace function public.prayer_issue_claim(p_issue_date date,p_mystery text,p_prayer_key text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare i public.prayer_issues; c public.prayer_controls; begin
 select * into c from public.prayer_controls where id;
 if not c.send_enabled then return jsonb_build_object('error','send_disabled'); end if;
 select * into i from public.prayer_issues where issue_date=p_issue_date;
 if found then
   if i.send_completed_at is not null then return jsonb_build_object('error','already_sent','id',i.id); end if;
   return jsonb_build_object('id',i.id,'resumed',true,'attempted',i.attempted,'sent',i.sent,'failed',i.failed,'cap',c.daily_send_cap);
 end if;
 insert into public.prayer_issues(issue_date,mystery,prayer_key,send_started_at) values(p_issue_date,p_mystery,p_prayer_key,now()) returning id into i.id;
 return jsonb_build_object('id',i.id,'resumed',false,'attempted',0,'sent',0,'failed',0,'cap',c.daily_send_cap);
end $$;
-- Confirmed-recipient page read for the send job, keyset-paginated (service role only).
create or replace function public.prayer_confirmed_batch(p_after_id uuid,p_limit integer) returns setof public.prayer_subscribers
language plpgsql security definer set search_path='' as $$ begin
 return query select * from public.prayer_subscribers
   where status='confirmed' and (p_after_id is null or id>p_after_id)
   order by id asc limit least(greatest(coalesce(p_limit,100),1),1000);
end $$;
-- Per-recipient send result; bumps issue counters (service role only).
create or replace function public.prayer_record_send(p_issue_id uuid,p_subscriber_id uuid,p_status text,p_provider_id text,p_error text) returns jsonb
language plpgsql security definer set search_path='' as $$ begin
 if p_status not in ('sent','failed','deferred') then raise exception 'invalid_status'; end if;
 insert into public.prayer_send_log(issue_id,subscriber_id,status,provider_message_id,error)
 values(p_issue_id,p_subscriber_id,p_status,coalesce(p_provider_id,''),coalesce(p_error,''));
 update public.prayer_issues set attempted=attempted+1,
   sent=sent+(case when p_status='sent' then 1 else 0 end),
   failed=failed+(case when p_status='failed' then 1 else 0 end)
 where id=p_issue_id;
 return jsonb_build_object('ok',true);
end $$;
create or replace function public.prayer_issue_complete(p_issue_id uuid) returns jsonb
language plpgsql security definer set search_path='' as $$ begin
 update public.prayer_issues set send_completed_at=now() where id=p_issue_id and send_completed_at is null;
 return jsonb_build_object('ok',true);
end $$;
revoke all on function public.prayer_budget(text,integer) from public,anon,authenticated;
revoke all on function public.prayer_check_intake_rate(text) from public,anon,authenticated;
revoke all on function public.prayer_subscribe_guest(text,text,text) from public,anon,authenticated;
revoke all on function public.prayer_confirm(uuid) from public,anon,authenticated;
revoke all on function public.prayer_manage_peek(uuid) from public,anon,authenticated;
revoke all on function public.prayer_unsubscribe(uuid) from public,anon,authenticated;
revoke all on function public.prayer_subscriber_stats() from public,anon,authenticated;
revoke all on function public.prayer_subscriber_list(text,integer,integer) from public,anon,authenticated;
revoke all on function public.prayer_issue_claim(date,text,text) from public,anon,authenticated;
revoke all on function public.prayer_confirmed_batch(uuid,integer) from public,anon,authenticated;
revoke all on function public.prayer_record_send(uuid,uuid,text,text,text) from public,anon,authenticated;
revoke all on function public.prayer_issue_complete(uuid) from public,anon,authenticated;
grant execute on function public.prayer_budget(text,integer) to service_role;
grant execute on function public.prayer_check_intake_rate(text) to service_role;
grant execute on function public.prayer_subscribe_guest(text,text,text) to service_role;
grant execute on function public.prayer_confirm(uuid) to service_role;
grant execute on function public.prayer_manage_peek(uuid) to service_role;
grant execute on function public.prayer_unsubscribe(uuid) to service_role;
grant execute on function public.prayer_subscriber_stats() to authenticated;
grant execute on function public.prayer_subscriber_list(text,integer,integer) to authenticated;
grant execute on function public.prayer_issue_claim(date,text,text) to service_role;
grant execute on function public.prayer_confirmed_batch(uuid,integer) to service_role;
grant execute on function public.prayer_record_send(uuid,uuid,text,text,text) to service_role;
grant execute on function public.prayer_issue_complete(uuid) to service_role;
commit;
