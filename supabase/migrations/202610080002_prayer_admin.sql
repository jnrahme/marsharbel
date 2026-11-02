-- Daily prayer admin dashboard: moderator reads (stats, lists, issues, send log), controls toggle,
-- and its audit trail. Reuses the testimony moderator role check. Safe to rerun this migration.
begin;
create table if not exists public.prayer_admin_audit (
 id bigint generated always as identity primary key,
 actor_id uuid,
 action text not null check(char_length(action) <= 60),
 detail text not null default '' check(char_length(detail) <= 300),
 created_at timestamptz not null default now()
);
alter table public.prayer_admin_audit enable row level security;
revoke all on public.prayer_admin_audit from public,anon,authenticated;
-- Recent daily issues with per-issue counters.
create or replace function public.prayer_admin_issues(p_limit integer) returns setof public.prayer_issues
language plpgsql security definer set search_path='' as $$ begin
 perform public.testimony_require_moderator();
 return query select * from public.prayer_issues order by issue_date desc limit least(greatest(coalesce(p_limit,30),1),120);
end $$;
-- Recent send-log rows (newest first).
create or replace function public.prayer_admin_send_log(p_limit integer) returns setof public.prayer_send_log
language plpgsql security definer set search_path='' as $$ begin
 perform public.testimony_require_moderator();
 return query select * from public.prayer_send_log order by id desc limit least(greatest(coalesce(p_limit,50),1),500);
end $$;
-- Current control values.
create or replace function public.prayer_admin_controls() returns jsonb
language plpgsql security definer set search_path='' as $$
declare r jsonb; begin
 perform public.testimony_require_moderator();
 select jsonb_build_object('signup_enabled',c.signup_enabled,'daily_signup_limit',c.daily_signup_limit,'send_enabled',c.send_enabled,'daily_send_cap',c.daily_send_cap)
 into r from public.prayer_controls c where c.id=true;
 return coalesce(r,'{}'::jsonb);
end $$;
-- Toggle the daily send; audited. First bulk send stays an owner decision.
create or replace function public.prayer_admin_set_send_enabled(p_enabled boolean) returns jsonb
language plpgsql security definer set search_path='' as $$ begin
 perform public.testimony_require_moderator();
 update public.prayer_controls set send_enabled=p_enabled where id=true;
 insert into public.prayer_admin_audit(actor_id,action,detail) values(auth.uid(),'set_send_enabled',case when p_enabled then 'enabled' else 'disabled' end);
 return jsonb_build_object('ok',true,'send_enabled',p_enabled);
end $$;
-- Audit trail read.
create or replace function public.prayer_admin_audit_list(p_limit integer) returns setof public.prayer_admin_audit
language plpgsql security definer set search_path='' as $$ begin
 perform public.testimony_require_moderator();
 return query select * from public.prayer_admin_audit order by id desc limit least(greatest(coalesce(p_limit,30),1),200);
end $$;
revoke all on function public.prayer_admin_issues(integer) from public,anon,authenticated;
revoke all on function public.prayer_admin_send_log(integer) from public,anon,authenticated;
revoke all on function public.prayer_admin_controls() from public,anon,authenticated;
revoke all on function public.prayer_admin_set_send_enabled(boolean) from public,anon,authenticated;
revoke all on function public.prayer_admin_audit_list(integer) from public,anon,authenticated;
-- Existing moderator-guarded reads become callable by signed-in moderators.
grant execute on function public.prayer_subscriber_stats() to authenticated;
grant execute on function public.prayer_subscriber_list(text,integer,integer) to authenticated;
grant execute on function public.prayer_admin_issues(integer) to authenticated;
grant execute on function public.prayer_admin_send_log(integer) to authenticated;
grant execute on function public.prayer_admin_controls() to authenticated;
grant execute on function public.prayer_admin_set_send_enabled(boolean) to authenticated;
grant execute on function public.prayer_admin_audit_list(integer) to authenticated;
commit;
