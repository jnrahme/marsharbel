-- Optional YouTube IDs remain private until a moderator approves the whole submission.
begin;
alter table public.testimony_submissions add column if not exists youtube_video_id text
  check (youtube_video_id is null or youtube_video_id ~ '^[A-Za-z0-9_-]{11}$');
alter table public.testimony_publications add column if not exists youtube_video_id text
  check (youtube_video_id is null or youtube_video_id ~ '^[A-Za-z0-9_-]{11}$');

-- Do not broaden table grants or direct-write policies. The public projection
-- remains readable only under its existing RLS policy.
-- Existing guest intake is server-only and remains under the same rate limits.
create or replace function public.testimony_submit_guest(p_payload jsonb) returns jsonb
language plpgsql security definer set search_path='' as $$
declare c public.testimony_controls; sid uuid; begin
 select * into c from public.testimony_controls where id for update;
 if not c.intake_enabled then return jsonb_build_object('error','intake_paused'); end if;
 if not public.testimony_budget('intake:global',c.daily_intake_limit)
 or not public.testimony_budget('intake:guest-minute:'||to_char(now() at time zone 'UTC','YYYYMMDDHH24MI'),10)
 then return jsonb_build_object('error','rate_limited'); end if;
 if exists(select 1 from public.testimony_submissions where story=p_payload->>'story' and status not in ('withdrawn','rejected')) then return jsonb_build_object('error','duplicate'); end if;
 insert into public.testimony_submissions(author_id,display_name,story,language,country,event_date,age_attested,consent_publish,ai_consent,youtube_video_id)
 values(null,p_payload->>'display_name',p_payload->>'story',p_payload->>'language',coalesce(p_payload->>'country',''),nullif(p_payload->>'event_date','')::date,(p_payload->>'age_attested')::boolean,(p_payload->>'consent_publish')::boolean,(p_payload->>'ai_consent')::boolean,nullif(p_payload->>'youtube_video_id','')) returning id into sid;
 insert into public.testimony_audit(submission_id,action) values(sid,'guest_submitted');
 return jsonb_build_object('id',sid);
end $$;
revoke all on function public.testimony_submit_guest(jsonb) from public,anon,authenticated;
grant execute on function public.testimony_submit_guest(jsonb) to service_role;

-- Preserve account-based submissions and edits if that legacy flow is in use.
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
 insert into public.testimony_submissions(author_id,display_name,story,language,country,event_date,age_attested,consent_publish,ai_consent,youtube_video_id)
 values(p_author,p_payload->>'display_name',p_payload->>'story',p_payload->>'language',coalesce(p_payload->>'country',''),nullif(p_payload->>'event_date','')::date,(p_payload->>'age_attested')::boolean,(p_payload->>'consent_publish')::boolean,(p_payload->>'ai_consent')::boolean,nullif(p_payload->>'youtube_video_id','')) returning id into sid;
 insert into public.testimony_audit(submission_id,actor_id,action) values(sid,p_author,'submitted');
 return jsonb_build_object('id',sid);
end $$;
revoke all on function public.testimony_submit(uuid,jsonb,text) from public,anon,authenticated;
grant execute on function public.testimony_submit(uuid,jsonb,text) to service_role;

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
  update public.testimony_submissions set display_name=p_payload->>'display_name',story=p_payload->>'story',youtube_video_id=nullif(p_payload->>'youtube_video_id',''),status='pending',revision=revision+1,
   review_state='queued',review_notes=null,review_claim=null,updated_at=now(),author_message='' where id=p_id;
 else raise exception 'invalid_action'; end if;
 insert into public.testimony_audit(submission_id,actor_id,action) values(p_id,auth.uid(),p_action);
 return jsonb_build_object('ok',true);
end $$;
revoke all on function public.testimony_author_action(uuid,text,integer,jsonb) from public,anon;
grant execute on function public.testimony_author_action(uuid,text,integer,jsonb) to authenticated;

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
  insert into public.testimony_publications(id,display_name,story,language,country,event_date,youtube_video_id) values(s.id,s.display_name,s.story,s.language,s.country,s.event_date,s.youtube_video_id);
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
revoke all on function public.testimony_moderate(uuid,integer,text,text,boolean) from public,anon;
grant execute on function public.testimony_moderate(uuid,integer,text,text,boolean) to authenticated;
commit;
