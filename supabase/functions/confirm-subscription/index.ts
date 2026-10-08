import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { verifySubscriberToken } from '../_shared/subscriber-token.ts';

// The Supabase gateway forces content-type: text/plain on edge-function responses,
// so result pages live on marsharbel.com; this endpoint only redirects to them.
const RESULT_BASE = 'https://marsharbel.com/daily-prayer-result';

function redirect(state: string, params?: Record<string, string>): Response {
  const url = new URL(RESULT_BASE);
  url.searchParams.set('r', state);
  for (const [name, value] of Object.entries(params || {})) url.searchParams.set(name, value);
  return new Response(null, { status: 303, headers: { location: url.toString(), 'cache-control': 'no-store' } });
}

Deno.serve(async request => {
  if (request.method !== 'GET') return new Response('Method not allowed', { status: 405 });
  try {
    const url = Deno.env.get('SUPABASE_URL'); const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if (!url || !key) return redirect('paused');
    const token = new URL(request.url).searchParams.get('token') || '';
    if (!token || token.length > 200) return redirect('invalid');
    const subscriberId = await verifySubscriberToken(token);
    if (!subscriberId) return redirect('invalid');
    const db = createClient(url, key, { auth: { persistSession: false } });
    const { data, error } = await db.rpc('prayer_confirm', { p_id: subscriberId });
    if (error) throw error;
    if (data?.ok || data?.already) return redirect('confirmed');
    if (data?.error === 'unsubscribed') return redirect('ended');
    return redirect('invalid');
  } catch {
    return redirect('error');
  }
});
