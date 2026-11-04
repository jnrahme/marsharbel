-- Corrected draft based on live catalog inspection 2026-10-12 18:55 EDT.
-- NOT security-cleared and NOT applied. Any incompatible existing row aborts the transaction; no data is deleted.
-- Run in ONE transaction. Touches only new game_* / subscriptions objects plus one auth.users trigger.
begin;

create table if not exists public.game_profiles (
  user_id          uuid primary key references auth.users (id) on delete cascade,
  display_name     text check (display_name is null or char_length(display_name) between 1 and 40),
  avatar_url       text check (avatar_url is null or (avatar_url ~ '^https://' and char_length(avatar_url) <= 500)),
  age_confirmed_at timestamptz,
  created_at       timestamptz not null default now()
);
alter table public.game_profiles enable row level security;
alter table public.game_profiles drop constraint if exists game_profiles_display_name_check;
alter table public.game_profiles add constraint game_profiles_display_name_check
  check (display_name is null or char_length(display_name) between 1 and 40);
alter table public.game_profiles drop constraint if exists game_profiles_avatar_url_check;
alter table public.game_profiles add constraint game_profiles_avatar_url_check
  check (avatar_url is null or (avatar_url ~ '^https://' and char_length(avatar_url) <= 500));
revoke all on public.game_profiles from public, anon, authenticated;
grant select, insert, update on public.game_profiles to authenticated;

drop policy if exists "game_profiles: owner read" on public.game_profiles;
create policy "game_profiles: owner read" on public.game_profiles for select to authenticated
  using ((select auth.uid()) = user_id);
drop policy if exists "game_profiles: owner insert" on public.game_profiles;
create policy "game_profiles: owner insert" on public.game_profiles for insert to authenticated
  with check ((select auth.uid()) = user_id);
drop policy if exists "game_profiles: owner update" on public.game_profiles;
create policy "game_profiles: owner update" on public.game_profiles for update to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

-- MUST NEVER RAISE: this runs inside every auth signup on the shared project.
create or replace function public.handle_new_game_user()
returns trigger language plpgsql security definer set search_path = ''
as $$
declare nm text;
begin
  begin
    nm := left(btrim(coalesce(nullif(btrim(new.raw_user_meta_data ->> 'full_name'), ''),
                              nullif(btrim(new.raw_user_meta_data ->> 'name'), ''),
                              nullif(split_part(coalesce(new.email, ''), '@', 1), ''),
                              'Player')), 40);
    if nm is null or char_length(nm) < 1 then nm := 'Player'; end if;
    insert into public.game_profiles (user_id, display_name)
    values (new.id, nm)
    on conflict (user_id) do nothing;
  exception when others then
    null; -- never block auth signup; client ensureProfile() retries
  end;
  return new;
end;
$$;
revoke all on function public.handle_new_game_user() from public, anon, authenticated;

drop trigger if exists on_auth_user_created_games on auth.users;
create trigger on_auth_user_created_games after insert on auth.users
  for each row execute function public.handle_new_game_user();

create table if not exists public.game_progress (
  user_id    uuid not null references auth.users (id) on delete cascade,
  game_id    text not null check (game_id in ('bible-mystery','card-game')), -- extend per shipped game
  state      jsonb not null default '{}'::jsonb check (octet_length(state::text) <= 65536),
  updated_at timestamptz not null default now(),
  primary key (user_id, game_id)
);
alter table public.game_progress enable row level security;
alter table public.game_progress drop constraint if exists game_progress_game_id_check;
alter table public.game_progress add constraint game_progress_game_id_check
  check (game_id in ('bible-mystery','card-game'));
alter table public.game_progress drop constraint if exists game_progress_state_check;
alter table public.game_progress add constraint game_progress_state_check
  check (octet_length(state::text) <= 65536);
revoke all on public.game_progress from public, anon, authenticated;
grant select, insert, update, delete on public.game_progress to authenticated;
-- The original migration's INSERT policy has this different name.
drop policy if exists "game_progress: owner upsert" on public.game_progress;
drop policy if exists "game_progress: owner read" on public.game_progress;
create policy "game_progress: owner read" on public.game_progress for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists "game_progress: owner insert" on public.game_progress;
create policy "game_progress: owner insert" on public.game_progress for insert to authenticated with check ((select auth.uid()) = user_id);
drop policy if exists "game_progress: owner update" on public.game_progress;
create policy "game_progress: owner update" on public.game_progress for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "game_progress: owner delete" on public.game_progress;
create policy "game_progress: owner delete" on public.game_progress for delete to authenticated using ((select auth.uid()) = user_id);

create table if not exists public.subscriptions (
  user_id uuid primary key references auth.users (id) on delete cascade,
  stripe_customer_id text unique, stripe_subscription_id text unique,
  plan text not null default 'free' check (plan in ('free','supporter')),
  status text not null default 'inactive' check (status in ('active','trialing','past_due','canceled','inactive')),
  current_period_end timestamptz, updated_at timestamptz not null default now()
);
alter table public.subscriptions enable row level security;
alter table public.subscriptions drop constraint if exists subscriptions_plan_check;
alter table public.subscriptions add constraint subscriptions_plan_check
  check (plan in ('free','supporter'));
alter table public.subscriptions drop constraint if exists subscriptions_status_check;
alter table public.subscriptions add constraint subscriptions_status_check
  check (status in ('active','trialing','past_due','canceled','inactive'));
revoke all on public.subscriptions from public, anon, authenticated;
grant select on public.subscriptions to authenticated;   -- read only; writes = service role webhook
drop policy if exists "subscriptions: owner read" on public.subscriptions;
create policy "subscriptions: owner read" on public.subscriptions for select to authenticated using ((select auth.uid()) = user_id);

-- delete_my_game_account() REMOVED: it was callable by any signed-in user via /rpc, wiped data without
-- cancelling Stripe, and the cascades already cover it. Deletion = server-side edge function only (not shipped).
drop function if exists public.delete_my_game_account();

commit;
