import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { landingPage } from '../_shared/prayer-email-templates.ts';
import { verifySubscriberToken } from '../_shared/subscriber-token.ts';

function html(status: number, page: string): Response {
  return new Response(page, { status, headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' } });
}

const HOME = '<p style="margin:16px 0 0;"><a href="https://marsharbel.com" style="color:#6d3b2a;">Back to marsharbel.com</a></p>';
const RESUB = '<p style="margin:16px 0 0;"><a href="https://marsharbel.com/daily-prayer" style="color:#6d3b2a;">Subscribe again</a></p>';

function confirmForm(token: string): string {
  return `<form method="post" action="" style="margin:20px 0 0;">
<input type="hidden" name="token" value="${token.replace(/[^A-Za-z0-9.-]/g, '')}">
<button type="submit" style="background:#6d3b2a;color:#fffdf8;border:0;border-radius:8px;padding:12px 24px;font-size:15px;cursor:pointer;">Yes, unsubscribe me</button>
<a href="https://marsharbel.com" style="margin-left:14px;color:#6d5a43;font-size:14px;">Keep my subscription</a>
</form>`;
}

Deno.serve(async request => {
  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL'); const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if (!supabaseUrl || !key) return html(503, landingPage('Unavailable', '<p>The unsubscribe service is temporarily paused. Please try again later.</p>', HOME));
    const db = createClient(supabaseUrl, key, { auth: { persistSession: false } });
    const requestUrl = new URL(request.url);

    if (request.method === 'GET') {
      const token = requestUrl.searchParams.get('token') || '';
      if (!token || token.length > 200) return html(400, landingPage('Link not recognized', '<p>This unsubscribe link is incomplete. Please copy the full link from your email.</p>', HOME));
      const subscriberId = await verifySubscriberToken(token);
      if (!subscriberId) return html(400, landingPage('Link not recognized', '<p>This unsubscribe link is not valid. Please use the exact link from your email.</p>', HOME));
      const { data, error } = await db.rpc('prayer_manage_peek', { p_id: subscriberId });
      if (error) throw error;
      if (!data?.found) return html(200, landingPage('Link not recognized', '<p>This unsubscribe link is no longer valid. If you are still receiving the daily prayer, tell us through the feedback page so we can fix it.</p>', HOME));
      if (data.status === 'unsubscribed') return html(200, landingPage('Already unsubscribed', '<p>This address is already off the daily prayer list. No further emails will arrive.</p>', RESUB));
      return html(200, landingPage('Unsubscribe from the daily prayer?', '<p>Are you sure? You will stop receiving the daily rosary mystery, the Maronite prayers of the day, and the Saint Charbel prayer.</p>', confirmForm(token)));
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
      if (!token || token.length > 200) return html(400, landingPage('Link not recognized', '<p>This unsubscribe link is incomplete.</p>', HOME));
      const subscriberId = await verifySubscriberToken(token);
      if (!subscriberId) return html(400, landingPage('Link not recognized', '<p>This unsubscribe link is not valid.</p>', HOME));
      const { data, error } = await db.rpc('prayer_unsubscribe', { p_id: subscriberId });
      if (error) throw error;
      if (data?.ok || data?.already) {
        return html(200, landingPage('You are unsubscribed', '<p>Done - no further daily prayer emails will arrive. Thank you for praying with us.</p>', RESUB));
      }
      return html(200, landingPage('Link not recognized', '<p>This unsubscribe link is no longer valid.</p>', HOME));
    }

    return new Response('Method not allowed', { status: 405 });
  } catch {
    return html(503, landingPage('Unavailable', '<p>The unsubscribe service is temporarily unavailable. Please try again later.</p>', HOME));
  }
});
