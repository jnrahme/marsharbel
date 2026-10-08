import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { landingPage } from '../_shared/prayer-email-templates.ts';
import { verifySubscriberToken } from '../_shared/subscriber-token.ts';

function html(status: number, page: string): Response {
  return new Response(page, { status, headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' } });
}

Deno.serve(async request => {
  if (request.method !== 'GET') return new Response('Method not allowed', { status: 405 });
  const home = '<p style="margin:16px 0 0;"><a href="https://marsharbel.com" style="color:#6d3b2a;">Back to marsharbel.com</a></p>';
  try {
    const url = Deno.env.get('SUPABASE_URL'); const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if (!url || !key) return html(503, landingPage('Unavailable', '<p>The confirmation service is temporarily paused. Please try the link again later.</p>', home));
    const token = new URL(request.url).searchParams.get('token') || '';
    if (!token || token.length > 200) return html(400, landingPage('Link not recognized', '<p>This confirmation link is incomplete. Please copy the full link from your email.</p>', home));
    const subscriberId = await verifySubscriberToken(token);
    if (!subscriberId) return html(400, landingPage('Link not recognized', '<p>This confirmation link is not valid. Please use the exact link from your email.</p>', home));
    const db = createClient(url, key, { auth: { persistSession: false } });
    const { data, error } = await db.rpc('prayer_confirm', { p_id: subscriberId });
    if (error) throw error;
    if (data?.ok || data?.already) {
      return html(200, landingPage('You are subscribed', '<p>Your subscription is confirmed. Tomorrow morning you will receive the rosary mystery of the day, a link to the Maronite prayers of the day, and a prayer to Saint Charbel.</p>', home));
    }
    if (data?.error === 'unsubscribed') {
      return html(200, landingPage('Subscription ended', '<p>This subscription was ended. You can subscribe again any time from the daily prayer page.</p>', '<p style="margin:16px 0 0;"><a href="https://marsharbel.com/daily-prayer" style="color:#6d3b2a;">Subscribe again</a></p>'));
    }
    return html(200, landingPage('Link already used or expired', '<p>This confirmation link has already been used or is no longer valid. If you already confirmed, you are all set - nothing more to do. Otherwise, sign up again to get a fresh link.</p>', '<p style="margin:16px 0 0;"><a href="https://marsharbel.com/daily-prayer" style="color:#6d3b2a;">Daily prayer page</a></p>'));
  } catch {
    return html(503, landingPage('Unavailable', '<p>The confirmation service is temporarily unavailable. Please try the link again later.</p>', home));
  }
});
