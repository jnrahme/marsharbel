# Testimony setup

The old anonymous-insert and unrestricted authenticated-user policies have been retired. **Do not reuse them.** The current migration revokes browser access to the old `testimonies` table and its old intake RPC, preserving its data for manual review.

Follow [the protected testimony deployment guide](../docs/PROTECTED-TESTIMONIES-SETUP.md). The sole schema source is `supabase/migrations/202609220001_protected_testimonies.sql`.
