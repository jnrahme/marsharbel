-- New tables intentionally quarantine legacy submissions. Do not copy private
-- legacy fields into the public projection. Safe to rerun this migration.
begin;
create table if not exists public.testimony_controls (
 id boolean primary key default true check(id), intake_enabled boolean not null default false,
 publishing_enabled boolean not null default false, screening_enabled boolean not null default false,
 daily_intake_limit integer not null default 200 check(daily_intake_limit between 1 and 1000),
 daily_ai_limit integer not null default 50 check(daily_ai_limit between 1 and 500),
 daily_publish_limit integer not null default 5 check(daily_publish_limit between 1 and 50)
);
insert into public.testimony_controls(id) values(true) on conflict do nothing;
create table if not exists public.testimony_submissions (
 id uuid primary key default gen_random_uuid(), author_id uuid not null references auth.users(id) on delete cascade,
 display_name text not null check(char_length(display_name) between 2 and 80),
 story text not null check(char_length(story) between 60 and 7000),
 language text not null default 'en' check(language in ('en','ar','fr')),
 country text not null default '' check(char_length(country)<=100), event_date date,
 status text not null default 'pending' check(status in ('pending','needs_clarification','approved','rejected','withdrawn')),
 revision integer not null default 1, consent_version text not null default '2026-09-22',
 age_attested boolean not null check(age_attested), consent_publish boolean not null check(consent_publish), ai_consent boolean not null check(ai_consent),
 review_state text not null default 'queued' check(review_state in ('queued','processing','complete','failed')),
 review_notes jsonb, review_started_at timestamptz, review_claim uuid,
 author_message text not null default '', created_at timestamptz not null default now(), updated_at timestamptz not null default now(), moderated_at timestamptz
);
create index if not exists testimony_author on public.testimony_submissions(author_id,created_at);
create index if not exists testimony_queue on public.testimony_submissions(review_state,created_at);
create table if not exists public.testimony_publications (
 id uuid primary key references public.testimony_submissions(id) on delete cascade,
 display_name text not null, story text not null, language text not null, country text not null,
 event_date date, published_at timestamptz not null default now(),
 label text not null default 'Reader-submitted testimony — reviewed for publication'
);
create table if not exists public.testimony_audit (
 id bigint generated always as identity primary key, submission_id uuid references public.testimony_submissions(id) on delete set null,
 actor_id uuid, action text not null, reason text not null default '', created_at timestamptz not null default now()
);
create table if not exists public.testimony_budgets (
 bucket text not null, period date not null default (now() at time zone 'UTC')::date,
 used integer not null default 0, primary key(bucket,period)
);
create table if not exists public.testimony_reports (
 id uuid primary key default gen_random_uuid(), publication_id uuid references public.testimony_publications(id) on delete set null,
 reporter_id uuid not null references auth.users(id) on delete cascade,
 reason text not null check(char_length(reason) between 10 and 1000), resolved boolean not null default false, created_at timestamptz not null default now()
);
create or replace function public.testimony_is_moderator() returns boolean language sql stable
set search_path='' as $$ select coalesce(auth.jwt()->'app_metadata'->>'role','')='moderator' and coalesce(auth.jwt()->>'aal','')='aal2' $$;
create or replace function public.testimony_require_moderator() returns void language plpgsql set search_path='' as $$
begin if not public.testimony_is_moderator() then raise exception 'moderator_mfa_required'; end if; end $$;
-- Atomic counters; every caller locks controls first to serialize reservations.
create or replace function public.testimony_budget(p_bucket text,p_max integer) returns boolean language plpgsql security definer set search_path='' as $$
declare n integer; begin
 insert into public.testimony_budgets(bucket,used) values(p_bucket,1)
 on conflict(bucket,period) do update set used=public.testimony_budgets.used+1 returning used into n;
 return n<=p_max;
end $$;

alter table public.testimony_controls enable row level security;
alter table public.testimony_submissions enable row level security;
alter table public.testimony_publications enable row level security;
alter table public.testimony_audit enable row level security;
alter table public.testimony_budgets enable row level security;
alter table public.testimony_reports enable row level security;
revoke all on public.testimony_controls,public.testimony_submissions,public.testimony_publications,public.testimony_audit,public.testimony_budgets,public.testimony_reports from public,anon,authenticated;
grant select on public.testimony_publications to anon,authenticated;
grant select on public.testimony_controls,public.testimony_submissions,public.testimony_audit,public.testimony_reports to authenticated;
drop policy if exists published_read on public.testimony_publications;
create policy published_read on public.testimony_publications for select to anon,authenticated using(true);
drop policy if exists own_or_moderator on public.testimony_submissions;
create policy own_or_moderator on public.testimony_submissions for select to authenticated using(author_id=auth.uid() or public.testimony_is_moderator());
drop policy if exists moderator_controls on public.testimony_controls;
create policy moderator_controls on public.testimony_controls for select to authenticated using(public.testimony_is_moderator());
drop policy if exists moderator_audit on public.testimony_audit;
create policy moderator_audit on public.testimony_audit for select to authenticated using(public.testimony_is_moderator());
drop policy if exists moderator_reports on public.testimony_reports;
create policy moderator_reports on public.testimony_reports for select to authenticated using(public.testimony_is_moderator());

-- Intake RPC is service-only, called after verified authentication and CAPTCHA.
create or replace function public.testimony_submit(p_author uuid,p_payload jsonb,p_ip_hash text default null) returns jsonb
language plpgsql security definer set search_path='' as $$
declare c public.testimony_controls; n integer; sid uuid; begin
 select * into c from public.testimony_controls where id for update;
 if not c.intake_enabled then return jsonb_build_object('error','intake_paused'); end if;
 if not exists(select 1 from auth.users where id=p_author and email_confirmed_at is not null) then return jsonb_build_object('error','verified_account_required'); end if;
 if not public.testimony_budget('intake:global',c.daily_intake_limit) or not public.testimony_budget('intake:user:'||p_author,2) then return jsonb_build_object('error','rate_limited'); end if;
 if p_ip_hash is not null and not public.testimony_budget('intake:ip:'||p_ip_hash,10) then return jsonb_build_object('error','rate_limited'); end if;
 select count(*) into n from public.testimony_submissions where author_id=p_author and status in ('pending','needs_clarification');
 if n>=3 then return jsonb_build_object('error','pending_limit'); end if;
 if exists(select 1 from public.testimony_submissions where author_id=p_author and story=p_payload->>'story' and status not in ('withdrawn','rejected')) then return jsonb_build_object('error','duplicate'); end if;
 insert into public.testimony_submissions(author_id,display_name,story,language,country,event_date,age_attested,consent_publish,ai_consent)
 values(p_author,p_payload->>'display_name',p_payload->>'story',p_payload->>'language',coalesce(p_payload->>'country',''),nullif(p_payload->>'event_date','')::date,(p_payload->>'age_attested')::boolean,(p_payload->>'consent_publish')::boolean,(p_payload->>'ai_consent')::boolean) returning id into sid;
 insert into public.testimony_audit(submission_id,actor_id,action) values(sid,p_author,'submitted');
 return jsonb_build_object('id',sid);
end $$;

create or replace function public.testimony_author_action(p_id uuid,p_action text,p_revision integer,p_payload jsonb default '{}') returns jsonb
language plpgsql security definer set search_path='' as $$
declare s public.testimony_submissions; c public.testimony_controls; begin
 if auth.uid() is null then raise exception 'sign_in_required'; end if;
 select * into c from public.testimony_controls where id for update;
 select * into s from public.testimony_submissions where id=p_id and author_id=auth.uid() for update;
 if not found then raise exception 'not_found'; end if;
 if s.revision is distinct from p_revision then raise exception 'stale_revision'; end if;
 if p_action='withdraw' then
  if s.status='withdrawn' then return jsonb_build_object('ok',true); end if;
  delete from public.testimony_publications where id=p_id;
  update public.testimony_submissions set status='withdrawn',moderated_at=now(),updated_at=now(),revision=revision+1,review_claim=null where id=p_id;
 elsif p_action='edit' then
  if not c.intake_enabled then raise exception 'intake_paused'; end if;
  if s.status in ('rejected','withdrawn') then raise exception 'closed_submission'; end if;
  if not public.testimony_budget('edit:'||auth.uid(),5) then return jsonb_build_object('error','rate_limited'); end if;
  if s.status='approved' and (select count(*) from public.testimony_submissions where author_id=auth.uid() and status in ('pending','needs_clarification'))>=3 then raise exception 'pending_limit'; end if;
  delete from public.testimony_publications where id=p_id;
  update public.testimony_submissions set display_name=p_payload->>'display_name',story=p_payload->>'story',status='pending',revision=revision+1,
   review_state='queued',review_notes=null,review_claim=null,updated_at=now(),author_message='' where id=p_id;
 else raise exception 'invalid_action'; end if;
 insert into public.testimony_audit(submission_id,actor_id,action) values(p_id,auth.uid(),p_action);
 return jsonb_build_object('ok',true);
end $$;

create or replace function public.testimony_moderate(p_id uuid,p_revision integer,p_action text,p_reason text default '',p_override boolean default false) returns jsonb
language plpgsql security definer set search_path='' as $$
declare s public.testimony_submissions; c public.testimony_controls; n integer; begin
 perform public.testimony_require_moderator();
 select * into c from public.testimony_controls where id for update;
 select * into s from public.testimony_submissions where id=p_id for update;
 if not found then raise exception 'not_found'; end if;
 if s.revision is distinct from p_revision then raise exception 'stale_revision'; end if;
 if char_length(p_reason)>1000 then raise exception 'reason_too_long'; end if;
 if p_action='approve' then
  if not c.publishing_enabled then raise exception 'publishing_paused'; end if;
  if s.status<>'pending' or s.review_state<>'complete' then raise exception 'screening_required'; end if;
  select count(*) into n from public.testimony_audit where action='approve' and created_at >= date_trunc('day',now() at time zone 'UTC') at time zone 'UTC';
  if n>=c.daily_publish_limit and not (p_override and char_length(trim(p_reason))>=10) then raise exception 'publication_limit'; end if;
  if p_override and char_length(trim(p_reason))<10 then raise exception 'override_reason_required'; end if;
  insert into public.testimony_publications(id,display_name,story,language,country,event_date) values(s.id,s.display_name,s.story,s.language,s.country,s.event_date);
  update public.testimony_submissions set status='approved',moderated_at=now(),updated_at=now(),revision=revision+1,author_message='Your testimony was approved for publication.' where id=p_id;
 elsif p_action in ('reject','clarify','unpublish') then
  if s.status='withdrawn' then raise exception 'closed_submission'; end if;
  if char_length(trim(p_reason))<10 then raise exception 'reason_required'; end if;
  delete from public.testimony_publications where id=p_id;
  update public.testimony_submissions set status=case p_action when 'reject' then 'rejected' when 'clarify' then 'needs_clarification' else 'pending' end,
   author_message=p_reason,moderated_at=now(),updated_at=now(),revision=revision+1,review_claim=null,
   review_state=case when review_state='processing' then 'queued' else review_state end where id=p_id;
 else raise exception 'invalid_action'; end if;
 insert into public.testimony_audit(submission_id,actor_id,action,reason) values(p_id,auth.uid(),p_action,case when p_override then '[CAP OVERRIDE] ' else '' end||p_reason);
 return jsonb_build_object('ok',true);
end $$;

create or replace function public.testimony_set_controls(p_intake boolean,p_publishing boolean,p_screening boolean) returns void language plpgsql security definer set search_path='' as $$
begin perform public.testimony_require_moderator();
 update public.testimony_controls set intake_enabled=p_intake,publishing_enabled=p_publishing,screening_enabled=p_screening where id;
 insert into public.testimony_audit(actor_id,action,reason) values(auth.uid(),'controls_changed',jsonb_build_object('intake',p_intake,'publishing',p_publishing,'screening',p_screening)::text);
end $$;
create or replace function public.testimony_report(p_id uuid,p_reason text) returns jsonb language plpgsql security definer set search_path='' as $$
begin
 if auth.uid() is null or not exists(select 1 from auth.users where id=auth.uid() and email_confirmed_at is not null) then raise exception 'verified_account_required'; end if;
 perform 1 from public.testimony_controls where id for update;
 if not public.testimony_budget('reports:global',200) or not public.testimony_budget('reports:'||auth.uid(),3) then return jsonb_build_object('error','rate_limited'); end if;
 if not exists(select 1 from public.testimony_publications where id=p_id) then raise exception 'not_found'; end if;
 insert into public.testimony_reports(publication_id,reporter_id,reason) values(p_id,auth.uid(),p_reason);
 return jsonb_build_object('ok',true);
end $$;
create or replace function public.testimony_resolve_report(p_id uuid) returns void language plpgsql security definer set search_path='' as $$
begin perform public.testimony_require_moderator(); update public.testimony_reports set resolved=true where id=p_id;
 insert into public.testimony_audit(actor_id,action,reason) values(auth.uid(),'report_resolved',p_id::text); end $$;

-- AI worker has only these two RPCs, no raw-table privileges and no publishing RPC.
create or replace function public.testimony_claim_review() returns jsonb language plpgsql security definer set search_path='' as $$
declare s public.testimony_submissions; c public.testimony_controls; claim uuid; begin
 if coalesce(auth.jwt()->'app_metadata'->>'role','')<>'testimony_worker' then raise exception 'worker_required'; end if;
 select * into c from public.testimony_controls where id for update;
 if not c.screening_enabled then return null; end if;
 -- Interrupted jobs fail closed; moderator can retry explicitly.
 update public.testimony_submissions set review_state='failed',review_claim=null where review_state='processing' and review_started_at<now()-interval '5 minutes';
 select * into s from public.testimony_submissions where status='pending' and review_state='queued' order by created_at limit 1 for update skip locked;
 if not found then return null; end if;
 if not public.testimony_budget('ai',c.daily_ai_limit) then return null; end if;
 claim=gen_random_uuid();
 update public.testimony_submissions set review_state='processing',review_started_at=now(),review_claim=claim where id=s.id;
 return jsonb_build_object('id',s.id,'revision',s.revision,'claim',claim,'story',s.story,'language',s.language,
  'duplicate',exists(select 1 from public.testimony_submissions t where t.id<>s.id and lower(trim(t.story))=lower(trim(s.story))));
end $$;
create or replace function public.testimony_complete_review(p_id uuid,p_claim uuid,p_revision integer,p_notes jsonb,p_failed boolean default false) returns void language plpgsql security definer set search_path='' as $$
begin
 if coalesce(auth.jwt()->'app_metadata'->>'role','')<>'testimony_worker' then raise exception 'worker_required'; end if;
 if p_notes is not null and octet_length(p_notes::text)>12000 then raise exception 'review_too_large'; end if;
 update public.testimony_submissions set review_state=case when p_failed then 'failed' else 'complete' end,review_notes=p_notes,review_claim=null
 where id=p_id and review_claim=p_claim and revision=p_revision and status='pending' and review_state='processing';
end $$;
create or replace function public.testimony_retry_review(p_id uuid) returns void language plpgsql security definer set search_path='' as $$
begin perform public.testimony_require_moderator(); update public.testimony_submissions set review_state='queued',review_claim=null where id=p_id and status='pending' and review_state='failed';
 insert into public.testimony_audit(submission_id,actor_id,action) values(p_id,auth.uid(),'review_retry'); end $$;
create or replace function public.testimony_purge() returns integer language plpgsql security definer set search_path='' as $$
declare n integer; begin
 delete from public.testimony_submissions where status in ('rejected','withdrawn') and moderated_at<now()-interval '30 days'; get diagnostics n=row_count;
 delete from public.testimony_budgets where period<(now() at time zone 'UTC')::date-7;
 delete from public.testimony_reports where resolved and created_at<now()-interval '30 days';
 return n;
end $$;

-- Explicit execution allowlist: functions otherwise default to PUBLIC execute.
do $$ declare f record; begin
 for f in select p.oid::regprocedure as sig from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname like 'testimony_%' loop
  execute format('revoke all on function %s from public,anon,authenticated',f.sig);
 end loop;
end $$;
grant execute on function public.testimony_is_moderator() to authenticated;
grant execute on function public.testimony_author_action(uuid,text,integer,jsonb),public.testimony_moderate(uuid,integer,text,text,boolean),public.testimony_set_controls(boolean,boolean,boolean),public.testimony_report(uuid,text),public.testimony_resolve_report(uuid),public.testimony_claim_review(),public.testimony_complete_review(uuid,uuid,integer,jsonb,boolean),public.testimony_retry_review(uuid) to authenticated;
grant execute on function public.testimony_submit(uuid,jsonb,text),public.testimony_purge() to service_role;
-- Disable the obsolete public/author policies without deleting legacy records.
do $$ begin
 if to_regclass('public.testimonies') is not null then revoke all on public.testimonies from public,anon,authenticated; end if;
 if to_regprocedure('public.accept_testimony(text,uuid,jsonb)') is not null then revoke all on function public.accept_testimony(text,uuid,jsonb) from public,anon,authenticated,service_role; end if;
end $$;
commit;
