# Testimony System Setup (Supabase + Human Moderation)

## 1) Create DB table
Run in Supabase SQL editor:

```sql
create table if not exists public.testimonies (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  published_at timestamptz,
  full_name text not null,
  email text,
  country text,
  parish text,
  language text default 'en',
  event_date date,
  healing_type text,
  testimony_text text not null,
  contact_permission boolean not null default false,
  consent_publish boolean not null default false,
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  verification_note text,
  meta jsonb default '{}'::jsonb
);
```

## 2) Row Level Security

```sql
alter table public.testimonies enable row level security;

-- Anyone can insert new pending testimony
create policy testimonies_insert_public
on public.testimonies
for insert
to anon
with check (status = 'pending');

-- Public can only read approved rows
create policy testimonies_select_public
on public.testimonies
for select
to anon
using (status = 'approved');

-- Authenticated admins can read/update all
create policy testimonies_select_admin
on public.testimonies
for select
to authenticated
using (true);

create policy testimonies_update_admin
on public.testimonies
for update
to authenticated
using (true)
with check (true);
```

## 3) Create admin user
Create one account in Supabase Auth (email/password) for yourself.

## 4) Configure frontend
Edit `/Users/joeyrahme/Github/MarCharbel/testimony-config.js`:
- `supabaseUrl`
- `supabaseAnonKey`
- `turnstileSiteKey`
- `turnstileVerifyEndpoint` (default: `/turnstile-verify.php`)
- `requireTurnstile` (keep `true` for production)

## 5) Turnstile verification (required in production)
This repo now includes `/turnstile-verify.php` to verify tokens server-side.

Setup:
1. Copy `/Users/joeyrahme/Github/MarCharbel/turnstile-secret.php.example` -> `/Users/joeyrahme/Github/MarCharbel/turnstile-secret.php`
2. Put your real secret in `TURNSTILE_SECRET_KEY`
3. Do not commit `turnstile-secret.php`
4. Keep secret key out of frontend files

## 6) Workflow
- Public submits at `/submit-testimony.html`
- Row stored as `pending`
- Admin reviews at `/testimony-review.html`
- Approve -> appears on `/testimonies.html`
