import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { verifySubscriberToken } from '../_shared/subscriber-token.ts';

// The Supabase gateway forces content-type: text/plain on edge-function responses,
// so result pages live on marsharbel.com. GET redirects to the confirm page; POST
// (RFC 8058 one-click and the site form) does the unsubscribe and returns JSON.
const RESULT_BASE = 'https://marsharbel.com/daily-prayer-result';

function redirect(state: string, params?: Record<string, string>): Response {
  const url = new URL(RESULT_BASE);
  url.searchParams.set('r', state);
  for (const [name, value] of Object.entries(params || {})) url.searchParams.set(name, value);
  return new Response(null, { status: 303, headers: { location: url.toString(), 'cache-control': 'no-store' } });
}

Deno.serve(async request => {
  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL'); const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if (!supabaseUrl || !key) return redirect('paused');
    const db = createClient(supabaseUrl, key, { auth: { persistSession: false } });
    const requestUrl = new URL(request.url);

    if (request.method === 'GET') {
      const token = requestUrl.searchParams.get('token') || '';
      if (!token || token.length > 200) return redirect('invalid');
      const subscriberId = await verifySubscriberToken(token);
      if (!subscriberId) return redirect('invalid');
      const { data, error } = await db.rpc('prayer_manage_peek', { p_id: subscriberId });
      if (error) throw error;
      if (!data?.found) return redirect('invalid');
      if (data.status === 'unsubscribed') return redirect('already-unsubscribed');
      return redirect('confirm-unsub', { token });
    }

    if (request.method === 'POST') {
      // RFC 8058 one-click: POST to the List-Unsubscribe URI (token stays in the query string).
      let token = requestUrl.searchParams.get('token') || '';
      if (!token) {
        const contentType = request.headers.get('content-type') || '';
        if (contentType.includes('application/x-www-form-urlencoded')) {
          const form = new URLSearchParams(await request.text());
          token = form.get('token') || '';
        } else {
          const body = await request.json().catch(() => ({}));
          token = typeof body?.token === 'string' ? body.token : '';
        }
      }
      if (!token || token.length > 200) return Response.json({ error: 'invalid' }, { status: 400 });
      const subscriberId = await verifySubscriberToken(token);
      if (!subscriberId) return Response.json({ error: 'invalid' }, { status: 400 });
      const { data, error } = await db.rpc('prayer_unsubscribe', { p_id: subscriberId });
      if (error) throw error;
      if (data?.ok) return Response.json({ ok: true });
      if (data?.already) return Response.json({ ok: true, already: true });
      return Response.json({ error: 'invalid' }, { status: 400 });
    }

    return new Response('Method not allowed', { status: 405 });
  } catch {
    return redirect('error');
  }
});
