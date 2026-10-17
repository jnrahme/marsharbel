-- Visitor feedback intake: private by default, service-role-only writes, human moderation.
-- Mirrors the testimony pipeline boundaries. Safe to rerun this migration.
begin;
create table if not exists public.feedback_controls (
 id boolean primary key default true check(id),
 intake_enabled boolean not null default true,
 daily_intake_limit integer not null default 100 check(daily_intake_limit between 1 and 1000)
);
insert into public.feedback_controls(id) values(true) on conflict do nothing;
create table if not exists public.feedback_submissions (
 id uuid primary key default gen_random_uuid(),
 display_name text not null default '' check(char_length(display_name) <= 80),
 email text not null default '' check(char_length(email) <= 254),
 category text not null default 'suggestion' check(category in ('suggestion','bug','praise','question','other')),
 message text not null check(char_length(message) between 10 and 2000),
 page_url text not null default '' check(char_length(page_url) <= 300),
 status text not null default 'pending' check(status in ('pending','approved','rejected')),
 board_card_ref text not null default '' check(char_length(board_card_ref) <= 120),
 revision integer not null default 1,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 moderated_at timestamptz
);
create index if not exists feedback_queue on public.feedback_submissions(status,created_at);
create table if not exists public.feedback_audit (
 id bigint generated always as identity primary key,
 submission_id uuid references public.feedback_submissions(id) on delete set null,
 actor_id uuid, action text not null, reason text not null default '',
 created_at timestamptz not null default now()
);
create table if not exists public.feedback_intake_rates (
 ip_hash text not null check(ip_hash ~ '^[0-9a-f]{64}$'),
 window_start bigint not null,
 used integer not null default 1 check(used > 0),
 primary key(ip_hash,window_start)
);
create index if not exists feedback_intake_rates_expiry on public.feedback_intake_rates(window_start);
alter table public.feedback_submissions enable row level security;
alter table public.feedback_controls enable row level security;
alter table public.feedback_audit enable row level security;
alter table public.feedback_intake_rates enable row level security;
revoke all on public.feedback_submissions from public,anon,authenticated;
revoke all on public.feedback_controls from public,anon,authenticated;
revoke all on public.feedback_audit from public,anon,authenticated;
revoke all on public.feedback_intake_rates from public,anon,authenticated;
create or replace function public.feedback_budget(p_bucket text,p_limit integer) returns boolean
language plpgsql security definer set search_path='' as $$
declare n integer; begin
 insert into public.testimony_budgets(bucket,period,used) values(p_bucket,(now() at time zone 'UTC')::date,1)
 on conflict(bucket,period) do update set used=public.testimony_budgets.used+1 returning used into n;
 return n<=p_limit;
end $$;
create or replace function public.feedback_check_intake_rate(p_ip_hash text) returns boolean
language plpgsql security definer set search_path='' as $$
declare current_window bigint; n integer; begin
 if p_ip_hash is null or p_ip_hash !~ '^[0-9a-f]{64}$' then raise exception 'invalid_hash'; end if;
 current_window := floor(extract(epoch from statement_timestamp()) / 300)::bigint;
 delete from public.feedback_intake_rates where window_start < current_window - 1;
 insert into public.feedback_intake_rates(ip_hash,window_start,used) values(p_ip_hash,current_window,1)
 on conflict(ip_hash,window_start) do update set used=least(public.feedback_intake_rates.used+1,11)
 returning used into n;
 return n <= 10;
end $$;
-- Guest intake is only callable by the server after CAPTCHA verification.
create or replace function public.feedback_submit_guest(p_payload jsonb) returns jsonb
language plpgsql security definer set search_path='' as $$
declare c public.feedback_controls; sid uuid; begin
 select * into c from public.feedback_controls where id for update;
 if not c.intake_enabled then return jsonb_build_object('error','intake_paused'); end if;
 if not public.feedback_budget('intake:feedback-global',c.daily_intake_limit)
 or not public.feedback_budget('intake:feedback-minute:'||to_char(now() at time zone 'UTC','YYYYMMDDHH24MI'),5)
 then return jsonb_build_object('error','rate_limited'); end if;
 if exists(select 1 from public.feedback_submissions where message=p_payload->>'message' and status<>'rejected') then return jsonb_build_object('error','duplicate'); end if;
 insert into public.feedback_submissions(display_name,email,category,message,page_url)
 values(coalesce(p_payload->>'display_name',''),coalesce(p_payload->>'email',''),coalesce(p_payload->>'category','suggestion'),p_payload->>'message',coalesce(p_payload->>'page_url','')) returning id into sid;
 insert into public.feedback_audit(submission_id,action) values(sid,'guest_submitted');
 return jsonb_build_object('id',sid);
end $$;
-- Moderator approve/reject; reuses the testimony moderator role check.
create or replace function public.feedback_moderate(p_id uuid,p_revision integer,p_action text,p_reason text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare s public.feedback_submissions; begin
 perform public.testimony_require_moderator();
 select * into s from public.feedback_submissions where id=p_id for update;
 if not found then raise exception 'not_found'; end if;
 if s.revision is distinct from p_revision then raise exception 'stale_revision'; end if;
 if s.status<>'pending' then raise exception 'closed_submission'; end if;
 if p_action not in ('approved','rejected') then raise exception 'invalid_action'; end if;
 if p_action='rejected' and char_length(trim(p_reason))<5 then raise exception 'reason_required'; end if;
 update public.feedback_submissions set status=p_action,revision=revision+1,updated_at=now(),moderated_at=now() where id=p_id;
 insert into public.feedback_audit(submission_id,actor_id,action,reason) values(p_id,auth.uid(),p_action,coalesce(p_reason,''));
 return jsonb_build_object('ok',true);
end $$;
-- Moderator queue read; returns nothing without the moderator role.
create or replace function public.feedback_queue(p_status text default 'pending') returns setof public.feedback_submissions
language plpgsql security definer set search_path='' as $$ begin
 perform public.testimony_require_moderator();
 return query select * from public.feedback_submissions where status=p_status order by created_at asc limit 200;
end $$;
-- Records the board card reference after the edge function creates the card.
create or replace function public.feedback_set_board_ref(p_id uuid,p_revision integer,p_ref text) returns jsonb
language plpgsql security definer set search_path='' as $$ begin
 perform public.testimony_require_moderator();
 if p_ref is null or char_length(p_ref)<2 or char_length(p_ref)>120 then raise exception 'invalid_ref'; end if;
 update public.feedback_submissions set board_card_ref=p_ref,revision=revision+1,updated_at=now()
 where id=p_id and revision=p_revision and status='approved';
 if not found then raise exception 'stale_revision'; end if;
 insert into public.feedback_audit(submission_id,actor_id,action,reason) values(p_id,auth.uid(),'board_card_created',p_ref);
 return jsonb_build_object('ok',true);
end $$;
revoke all on function public.feedback_budget(text,integer) from public,anon,authenticated;
revoke all on function public.feedback_check_intake_rate(text) from public,anon,authenticated;
revoke all on function public.feedback_submit_guest(jsonb) from public,anon,authenticated;
revoke all on function public.feedback_moderate(uuid,integer,text,text) from public,anon,authenticated;
revoke all on function public.feedback_queue(text) from public,anon,authenticated;
revoke all on function public.feedback_set_board_ref(uuid,integer,text) from public,anon,authenticated;
grant execute on function public.feedback_budget(text,integer) to service_role;
grant execute on function public.feedback_check_intake_rate(text) to service_role;
grant execute on function public.feedback_submit_guest(jsonb) to service_role;
grant execute on function public.feedback_moderate(uuid,integer,text,text) to authenticated;
grant execute on function public.feedback_queue(text) to authenticated;
grant execute on function public.feedback_set_board_ref(uuid,integer,text) to authenticated;
commit;
