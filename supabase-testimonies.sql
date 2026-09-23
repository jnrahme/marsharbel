-- Deprecated legacy setup. Do not reuse the old permissive policies.
-- Apply supabase/migrations/202609220001_protected_testimonies.sql instead.
do $$ begin raise exception 'Use the protected-testimonies migration under supabase/migrations. Legacy setup is disabled.'; end $$;
