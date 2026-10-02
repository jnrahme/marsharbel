-- Supplemental pre-CAPTCHA limiter. No raw addresses or user identities stored.
-- Enable function use only after trusted gateway-header and HMAC secret setup.
begin;
create table if not exists public.testimony_intake_rates (
 ip_hash text not null check(ip_hash ~ '^[0-9a-f]{64}$'),
 window_start bigint not null,
 used integer not null default 1 check(used > 0),
 primary key(ip_hash,window_start)
);
create index if not exists testimony_intake_rates_expiry on public.testimony_intake_rates(window_start);
alter table public.testimony_intake_rates enable row level security;
revoke all on public.testimony_intake_rates from public,anon,authenticated;
create or replace function public.testimony_check_intake_rate(p_ip_hash text) returns boolean
language plpgsql security definer set search_path='' as $$
declare current_window bigint; n integer; begin
 if p_ip_hash is null or p_ip_hash !~ '^[0-9a-f]{64}$' then raise exception 'invalid_hash'; end if;
 current_window := floor(extract(epoch from statement_timestamp()) / 300)::bigint;
 -- Fixed 5-minute windows; retain no more than 10 minutes of pseudonymous data.
 delete from public.testimony_intake_rates where window_start < current_window - 1;
 insert into public.testimony_intake_rates(ip_hash,window_start,used) values(p_ip_hash,current_window,1)
 on conflict(ip_hash,window_start) do update set used=least(public.testimony_intake_rates.used+1,31)
 returning used into n;
 return n <= 30;
end $$;
revoke all on function public.testimony_check_intake_rate(text) from public,anon,authenticated;
grant execute on function public.testimony_check_intake_rate(text) to service_role;
commit;
