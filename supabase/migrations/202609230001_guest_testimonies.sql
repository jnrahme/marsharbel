begin;
-- Guest intake is only callable by the server after CAPTCHA verification.
alter table public.testimony_submissions alter column author_id drop not null;
create or replace function public.testimony_submit_guest(p_payload jsonb) returns jsonb
language plpgsql security definer set search_path='' as $$
declare c public.testimony_controls; sid uuid; begin
 select * into c from public.testimony_controls where id for update;
 if not c.intake_enabled then return jsonb_build_object('error','intake_paused'); end if;
 if not public.testimony_budget('intake:global',c.daily_intake_limit)
 or not public.testimony_budget('intake:guest-minute:'||to_char(now() at time zone 'UTC','YYYYMMDDHH24MI'),10)
 then return jsonb_build_object('error','rate_limited'); end if;
 if exists(select 1 from public.testimony_submissions where story=p_payload->>'story' and status not in ('withdrawn','rejected')) then return jsonb_build_object('error','duplicate'); end if;
 insert into public.testimony_submissions(author_id,display_name,story,language,country,event_date,age_attested,consent_publish,ai_consent)
 values(null,p_payload->>'display_name',p_payload->>'story',p_payload->>'language',coalesce(p_payload->>'country',''),nullif(p_payload->>'event_date','')::date,(p_payload->>'age_attested')::boolean,(p_payload->>'consent_publish')::boolean,(p_payload->>'ai_consent')::boolean) returning id into sid;
 insert into public.testimony_audit(submission_id,action) values(sid,'guest_submitted');
 return jsonb_build_object('id',sid);
end $$;
revoke all on function public.testimony_submit_guest(jsonb) from public,anon,authenticated;
grant execute on function public.testimony_submit_guest(jsonb) to service_role;
-- A moderator may explicitly perform the screening personally. This neither
-- publishes nor claims AI ran, and invalidates outstanding worker claims.
create or replace function public.testimony_manual_review(p_id uuid,p_revision integer,p_reason text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare s public.testimony_submissions; begin
 perform public.testimony_require_moderator();
 select * into s from public.testimony_submissions where id=p_id for update;
 if not found then raise exception 'not_found'; end if;
 if s.revision is distinct from p_revision then raise exception 'stale_revision'; end if;
 if s.status<>'pending' then raise exception 'closed_submission'; end if;
 if char_length(trim(p_reason))<30 or char_length(p_reason)>1000 then raise exception 'review_reason_required'; end if;
 update public.testimony_submissions set review_state='complete',review_claim=null,revision=revision+1,updated_at=now(),
 review_notes=jsonb_build_object('source','human','summary',p_reason,'recommendation','review','flags',jsonb_build_array(),'questions',jsonb_build_array(),'disclaimer','Screened manually by the moderator; no AI verification or truth certification.') where id=p_id;
 insert into public.testimony_audit(submission_id,actor_id,action,reason) values(p_id,auth.uid(),'manual_review',p_reason);
 return jsonb_build_object('ok',true);
end $$;
revoke all on function public.testimony_manual_review(uuid,integer,text) from public,anon;
grant execute on function public.testimony_manual_review(uuid,integer,text) to authenticated;
commit;
