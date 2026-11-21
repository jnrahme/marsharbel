import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { intakeRateAllowed } from '../_shared/intake-rate-limit.ts';
import { IntakeError, readJsonLimited } from '../_shared/validation.ts';
import { sendEmail } from '../_shared/email-adapter.ts';
import { confirmEmail } from '../_shared/prayer-email-templates.ts';
import { mintSubscriberToken } from '../_shared/subscriber-token.ts';

const LOCALES = ['en', 'ar', 'de', 'es', 'fr', 'it', 'pl', 'pt', 'ru'];

function validateSignup(body: Record<string, unknown>) {
  if (body.website) throw new IntakeError(400, 'Subscription blocked.');
  const email = typeof body.email === 'string' ? body.email.trim() : '';
  if (email.length < 3 || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) throw new IntakeError(400, 'Check your email address.');
  const locale = typeof body.locale === 'string' && LOCALES.includes(body.locale) ? body.locale : 'en';
  return { email, locale, source: 'daily-prayer' };
}

Deno.serve(async request => {
  const origins = (Deno.env.get('TESTIMONY_ALLOWED_ORIGINS') || '').split(',').map(s => s.trim()).filter(Boolean);
  const origin = request.headers.get('origin') || '';
  const allowed = origins.includes(origin);
  const headers: Record<string, string> = { 'content-type': 'application/json', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff', 'vary': 'Origin' };
  if (allowed) Object.assign(headers, { 'access-control-allow-origin': origin, 'access-control-allow-headers': 'authorization, apikey, content-type, x-client-info', 'access-control-allow-methods': 'POST, OPTIONS' });
  const reply = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers });
  if (!allowed) return reply(403, { message: 'Origin not allowed.' });
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
  if (request.method !== 'POST') return reply(405, { message: 'Method not allowed.' });
  try {
    const url = Deno.env.get('SUPABASE_URL'); const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    const captchaSecret = Deno.env.get('TURNSTILE_SECRET_KEY');
    if (!url || !key || !captchaSecret) return reply(503, { message: 'Subscriptions are temporarily paused.' });
    const db = createClient(url, key, { auth: { persistSession: false } });
    const rateAllowed = await intakeRateAllowed(request.headers, {
      enabled: Deno.env.get('TESTIMONY_TRUST_CF_CONNECTING_IP') === 'true',
      secret: Deno.env.get('TESTIMONY_RATE_HMAC_KEY')
    }, async hash => {
      const result = await db.rpc('prayer_check_intake_rate', { p_ip_hash: hash }).abortSignal(AbortSignal.timeout(1500));
      if (result.error || typeof result.data !== 'boolean') throw new Error('Rate counter unavailable');
      return result.data;
    });
    if (!rateAllowed) return new Response(JSON.stringify({ message: 'Too many attempts. Please wait a few minutes and try again.' }), { status: 429, headers: { ...headers, 'retry-after': '300' } });

    const body = await readJsonLimited(request); const payload = validateSignup(body);
    const token = typeof body.turnstile_token === 'string' ? body.turnstile_token : '';
    if (!token || token.length > 8192) return reply(400, { message: 'Complete the human verification.' });
    const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST', body: new URLSearchParams({ secret: captchaSecret, response: token }), signal: AbortSignal.timeout(8000)
    });
    if (!response.ok) throw new Error('verification unavailable');
    const verdict = await response.json();
    if (!verdict.success || verdict.action !== 'subscribe_prayer' || verdict.hostname !== new URL(origin).hostname) return reply(403, { message: 'Human verification expired or failed. Please try again.' });

    const { data, error } = await db.rpc('prayer_subscribe_guest', {
      p_email: payload.email, p_locale: payload.locale, p_source: payload.source
    });
    if (error) throw error;
    if (data?.error === 'already_subscribed') return reply(202, { accepted: true });
    if (data?.error) {
      const messages: Record<string, string> = { rate_limited: 'Subscription limit reached. Please try another day.', signup_paused: 'Subscriptions are temporarily paused.', invalid_email: 'Check your email address.' };
      return reply(data.error === 'signup_paused' ? 503 : data.error === 'invalid_email' ? 400 : 429, { message: messages[data.error] || 'Subscription unavailable.' });
    }
    const confirmUrl = `${url}/functions/v1/confirm-subscription?token=${await mintSubscriberToken(data.id)}`;
    const email = confirmEmail(confirmUrl);
    const sent = await sendEmail({ to: payload.email, subject: email.subject, html: email.html, text: email.text });
    if (!sent.ok) return reply(503, { message: 'Could not send the confirmation email. Please try again in a few minutes.' });
    return reply(202, { accepted: true });
  } catch (error) {
    return reply(error instanceof IntakeError ? error.status : 503, { message: error instanceof IntakeError ? error.message : 'Subscription service is unavailable. Please try again.' });
  }
});
